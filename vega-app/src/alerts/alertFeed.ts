// ALERTSVC long poll behind GET /v1/alerts. Pages are untrusted: a bad page (error status,
// malformed body, an invalid alert, or an over-long cursor) delivers nothing and keeps the cursor.
// The queue keeps at most alert_queue_max = 20 alerts, one entry per id at its newest revision.
import type {ApiClient} from '../net/apiClient';
import {decodeAlert, decodeEnvelope} from '../net/dto';
import type {Alert} from '../net/dto';

const QUEUE_MAX = 20;
const MAX_CURSOR_LENGTH = 256;

export class AlertFeed {
  cursor: string | null = null;
  queue: Alert[] = [];

  private readonly held = new Map<string, Alert>();
  private readonly dismissed = new Map<string, number>();

  constructor(private readonly client: ApiClient) {}

  /** One GET /v1/alerts long poll; returns the newly delivered alerts. */
  async poll(): Promise<Alert[]> {
    let body: unknown;
    try {
      const path = '/v1/alerts' + (this.cursor !== null ? `?cursor=${encodeURIComponent(this.cursor)}` : '');
      const response = await this.client.request('GET', path);
      if (response.status < 200 || response.status > 299 || response.body === null) return [];
      body = response.body;
    } catch {
      return [];
    }
    const page = decodePage(body);
    if (page === null || page.cursor.length > MAX_CURSOR_LENGTH) return [];

    const latest = new Map<string, Alert>();
    for (const alert of page.alerts) {
      const previous = latest.get(alert.envelope.id);
      if (previous === undefined || alert.envelope.revision > previous.envelope.revision) {
        latest.set(alert.envelope.id, alert);
      }
    }
    const delivered = [...latest.values()].filter(alert => {
      const known = Math.max(
        this.held.get(alert.envelope.id)?.envelope.revision ?? -1,
        this.dismissed.get(alert.envelope.id) ?? -1,
      );
      return alert.envelope.revision > known;
    });
    for (const alert of delivered) {
      this.held.delete(alert.envelope.id);
      this.held.set(alert.envelope.id, alert);
      this.dismissed.delete(alert.envelope.id);
    }
    while (this.held.size > QUEUE_MAX) this.held.delete(this.held.keys().next().value as string);
    this.cursor = page.cursor;
    this.queue = [...this.held.values()];
    return delivered;
  }

  /** Local acknowledgement only. */
  dismiss(alertId: string): boolean {
    const alert = this.held.get(alertId);
    if (alert === undefined) return false;
    this.held.delete(alertId);
    this.dismissed.set(alertId, alert.envelope.revision);
    while (this.dismissed.size > QUEUE_MAX) this.dismissed.delete(this.dismissed.keys().next().value as string);
    this.queue = [...this.held.values()];
    return true;
  }
}

/** One invalid entry rejects the page, so nothing is partially applied. */
function decodePage(body: unknown): {alerts: Alert[]; cursor: string} | null {
  if (typeof body !== 'object' || body === null || Array.isArray(body)) return null;
  const page = body as Record<string, unknown>;
  if (!Array.isArray(page.alerts) || typeof page.cursor !== 'string') return null;
  const alerts: Alert[] = [];
  for (const item of page.alerts) {
    const envelope = decodeEnvelope(item);
    if (envelope === null) return null;
    const alert = decodeAlert(envelope);
    if (alert === null) return null;
    alerts.push(alert);
  }
  return {alerts, cursor: page.cursor};
}
