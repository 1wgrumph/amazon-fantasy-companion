// Interface scaffolding for P2-V01T (red). Behavior lands in P2-V01.
import type {ApiClient} from '../net/apiClient';
import type {Alert} from '../net/dto';

export class AlertFeed {
  cursor: string | null = null;
  queue: Alert[] = [];

  constructor(_client: ApiClient) {}

  /** One GET /v1/alerts long poll; returns the newly delivered alerts. */
  async poll(): Promise<Alert[]> {
    return [];
  }

  /** Local acknowledgement only. */
  dismiss(_alertId: string): boolean {
    return false;
  }
}
