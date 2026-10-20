// Interface scaffolding for P2-V01T (red). Behavior lands in P2-V01.
import type {Alert} from '../net/dto';

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
  constructor(_port: NotificationPort) {}

  show(_alert: Alert): void {}
}
