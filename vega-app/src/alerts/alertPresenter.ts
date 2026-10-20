// Interface scaffolding for P2-V01T (red). Behavior lands in P2-V01.
import type {Alert} from '../net/dto';
import type {Presentation, ProfileState} from '../profile/profile';

export interface AlertText {
  headline: string;
  context: string;
  access: string;
  commentary: string | null;
}

export type AlertAction = 'Watch' | 'Dismiss';

export interface AlertView {
  presentation: Presentation;
  actions: AlertAction[];
  speak: boolean;
}

export function alertText(_alert: Alert): AlertText | null {
  return null;
}

export function alertView(_alert: Alert, _profile: ProfileState, _voiceRouteVerified = false): AlertView | null {
  return null;
}
