// NOTIFIER: one alert as a heads-up notification on a high-importance channel, with Watch and
// Dismiss actions. The text comes from the presenter; an alert without triggering context posts nothing.
import type {Alert} from '../net/dto';
import {alertText} from './alertPresenter';

export interface PostedNotification {
  id: string;
  title: string;
  body: string;
  actions: string[];
  importance: 'high' | 'default';
}

/** Vega delivery route (RN 0.83 has no verified local-notification route; see DES-AFC-P2-VEGA). */
export interface NotificationPort {
  post(notification: PostedNotification): void;
}

export class AlertNotifier {
  constructor(private readonly port: NotificationPort) {}

  show(alert: Alert): void {
    const text = alertText(alert);
    if (text === null) return;
    this.port.post({
      id: alert.envelope.id,
      title: text.headline,
      body: [text.context === '' ? null : text.context, text.access, text.commentary]
        .filter((line): line is string => line !== null)
        .join('\n'),
      actions: ['Watch', 'Dismiss'],
      importance: 'high',
    });
  }
}
