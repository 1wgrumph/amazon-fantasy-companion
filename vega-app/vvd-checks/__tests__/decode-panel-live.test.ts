// Replays recorded GET /v1/panel bodies through the app's own pipeline (App.tsx panel refresh):
// decodeEnvelope -> decodePanel -> PanelController.onFetched -> controller.snapshot.
// usage: PANEL_DIR=<probe-panel.py out-dir> npx jest --roots=./vvd-checks -- decode-panel-live
import {existsSync, readFileSync} from 'fs';
import {join} from 'path';
import {decodeEnvelope} from '../../src/net/dto';
import {decodePanel, PanelController} from '../../src/panel/panel';

const dir = process.env.PANEL_DIR ?? '';
const read = (name: string) => JSON.parse(readFileSync(join(dir, `${name}.json`), 'utf8'));

function replay(name: string, initial: string, teamLeagues: string[]) {
  const envelope = decodeEnvelope(read(name));
  const decoded = envelope !== null ? decodePanel(envelope) : null;
  const controller = new PanelController(teamLeagues, initial, true);
  if (decoded !== null) controller.onFetched(decoded, Date.now());
  const result = {
    body: name,
    controllerTeamLeague: controller.teamLeague,
    envelopeDecoded: envelope !== null,
    panelDecoded: decoded !== null,
    decodedTeamLeague: decoded?.teamLeague ?? null,
    teamLeagueMatches: decoded !== null && decoded.teamLeague === controller.teamLeague,
    snapshotHeld: controller.snapshot !== null,
  };
  console.log(JSON.stringify(result));
  return result;
}

test('recorded panel bodies through the app pipeline', () => {
  expect(existsSync(join(dir, '05-panel-no-teamleague.json'))).toBe(true);
  // The linked synthetic profile: no saved teamLeague, no selections, so App.tsx builds ([], '').
  const live = replay('05-panel-no-teamleague', '', []);
  expect(live.envelopeDecoded && live.panelDecoded).toBe(true);
  if (existsSync(join(dir, '06-panel-teamleague-explicit.json'))) {
    const team = read('06-panel-teamleague-explicit').data.teamLeague as string;
    replay('06-panel-teamleague-explicit', team, [team]);
  }
});
