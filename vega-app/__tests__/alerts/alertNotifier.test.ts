// AFC-PR-015 notifier content (mirrors androidTest AlertNotifierDeviceTest.kt). The Vega delivery route over playback
// is unverified on RN 0.83 (DES-AFC-P2-VEGA); on-VVD display stays with PROC-VISUAL-REVIEW, never claimed here.
import {AlertNotifier, PostedNotification} from '../../src/alerts/alertNotifier';
import {alert} from '../support/alerts';

describe('AlertNotifierDeviceTest', () => {
  test('headsUpAlertPostsWatchAndDismissOnAHighImportanceChannel', () => {
    const posted: PostedNotification[] = [];
    new AlertNotifier({post: notification => posted.push(notification)}).show(alert());
    expect(posted).toHaveLength(1);
    expect(posted[0].actions).toEqual(['Watch', 'Dismiss']);
    expect(posted[0].importance).toBe('high');
  });
});
