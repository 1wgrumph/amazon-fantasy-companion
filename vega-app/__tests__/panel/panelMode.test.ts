// AFC-PR-041/-047: the P2-X04 verdict fixes the mode; modeB leaves the video unobscured at its aspect ratio
// (mirrors PanelModeTest.kt). On the VVD only fullScreen can be demonstrated; modeB needs provider video.
import {Box, panelLayout, panelModeFor} from '../../src/panel/panel';

const right = (b: Box) => b.left + b.width;
const bottom = (b: Box) => b.top + b.height;

describe('PanelModeTest', () => {
  test('onlyAModeBVerdictSelectsModeB', () => {
    expect(panelModeFor('modeB')).toBe('modeB');
    for (const other of [null, '', 'fullScreen', 'partial', 'timebox', 'MODEB', 'modeB ']) {
      expect({verdict: other, mode: panelModeFor(other)}).toEqual({verdict: other, mode: 'fullScreen'});
    }
  });

  test('fullScreenHostsThePanelAloneWithNoStandInVideo', () => {
    const layout = panelLayout('fullScreen', 1920, 1080);
    expect(layout.video).toBeNull();
    expect(layout.panel).toEqual({left: 0, top: 0, width: 1920, height: 1080});
  });

  test('modeBPutsThePanelRightAndFitsTheVideoLeftAtItsAspect', () => {
    const {panel, video} = panelLayout('modeB', 1920, 1080);
    expect(video).not.toBeNull();
    expect(right(panel)).toBe(1920);
    expect(panel.top).toBe(0);
    expect(panel.height).toBe(1080);
    expect(panel.width).toBeGreaterThanOrEqual(1);
    expect(panel.width).toBeLessThan(1920);
    expect(video!.left).toBeGreaterThanOrEqual(0);
    expect(right(video!)).toBeLessThanOrEqual(panel.left);
    expect(video!.top).toBeGreaterThanOrEqual(0);
    expect(bottom(video!)).toBeLessThanOrEqual(1080);
    expect(Math.abs(video!.width / video!.height - 16 / 9)).toBeLessThanOrEqual(0.01);
    expect(video!.width >= panel.left - 1 || video!.height >= 1079).toBe(true);
  });
});
