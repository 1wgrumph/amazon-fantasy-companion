---
spike: SP-6 Yahoo
slice: P2-X06
verdict: FAILS
device:
  model: none
  fire_os: none
  api_level: none
started_at: 2026-10-16T14:18:52Z
ended_at: 2026-10-16T15:48:18Z
first_install_at: not applicable (SP-1 and SP-4 only)
unblocks: [AFC-PR-006, AFC-PR-007]
conditional: C6
---

# SP-6 Yahoo verdict

**Verdict: FAILS** for the Yahoo route. Selected fallback: `manual`
(`backend/src/lineup/manual.py` returns
`"manual"` when Yahoo is not approved and the time is at or after
`2026-10-16T19:00:00Z`). AFC-PR-001 (Yahoo read of leagues, teams, roster by
week, and settings) is not unblocked. C6 selects labeled manual entry
(AFC-PR-006) as the single active source (AFC-PR-007).

Recorded at 2026-10-16T15:48:18Z, before T_yahoo. Approval of an application
submitted the same day cannot arrive before `2026-10-16T19:00:00Z`.

## Routes tried

1. OAuth refresh-token grant against `https://api.login.yahoo.com/oauth2/get_token`.
   Source: Yahoo OAuth 2.0 guide (https://developer.yahoo.com/oauth2/guide/).
   Both attempts returned `token_refresh_http` 200
   ([attempts.json](evidence/attempts.json) lines 8 and 19). Attempt 1 stored
   the refresh token at 2026-10-16T14:18:52Z (`ssm_token_version` 1, line 7).
   Attempt 2 used version 2 (line 18). No token value is in this tree.
2. Fantasy read of `users;use_login=1/games;game_keys=nfl/leagues` and
   `users;use_login=1/games` (attempts.json lines 27-28) through
   `https://fantasysports.yahooapis.com/fantasy/v2/`.
   Source: Yahoo Sports developer portal (https://sports.yahoo.com/developer/);
   the former Fantasy guide URL redirects there.
   Attempt 1 (`auth_url_scope` `none`, line 6) returned HTTP 403
   `This application is not authorized to perform this action.` and
   `read_exit` 1 (lines 10-12).
3. The same Fantasy reads after a consent URL that requested scope `fspt-r`
   (line 17). Token refresh was again HTTP 200 and `token_response_scope`
   was null (lines 19-20). The Fantasy API again returned HTTP 403 with the
   same error and `read_exit` 1 (lines 21-23).

## Observed result

OAuth succeeds. The Fantasy API does not. The 403 is Yahoo's API access
program, in place since July 2026, and it applies to public endpoints as
well as user endpoints. An app that has not been approved receives
`403` with `This application is not authorized` while token refresh still
returns 200.

Sources:

- yfpy issue #84, opened 2026-07-22: every Fantasy endpoint, including public
  `/fantasy/v2/game/mlb`, returns that 403 while OAuth still mints and
  refreshes tokens (https://github.com/uberfastman/yfpy/issues/84).
- krger/yahoo-fantasy-mcp README, "Get Yahoo API access, credentials, and
  authenticate": the gate changed around 2026-07-24; until approval, every
  call returns `403 "This application is not authorized to perform this
  action"` (https://github.com/krger/yahoo-fantasy-mcp).
  Access requests go to https://sports.yahoo.com/developer/access/.

This spike did not probe a public game resource. The public-endpoint claim
is the yfpy report, not attempts.json. The two probed paths are lines 27-28.

The owner submitted an access application on 2026-10-16 for App ID
`AyogcOTv`. That submission is not in attempts.json; this verdict is the
committed record of it. The owner also decided on 2026-10-16 to keep the
Yahoo option in the app. That decision is recorded here and is not in
attempts.json.

`attempts.json` line 30 classifies the failure as app-level permission or
scope missing at consent. Attempt 2 requested `fspt-r` and still received
403, so a missing scope does not explain the result.

## Evidence paths

- [spikes/sp6-yahoo/evidence/attempts.json](evidence/attempts.json)
- Offline checks, no network: [test_yahoo_oauth.py](test_yahoo_oauth.py)
  (auth URL, redaction, response normalization).
- Selected source: `backend/src/lineup/manual.py`.

## Limits

- No league, roster, or settings body was read (`read_exit` 1 on both
  attempts).
- The spike did not call Yahoo under the deployed backend role.
- Client secret, refresh token, SSM values, account email, account name,
  and IP addresses are not in `spikes/sp6-yahoo/` or
  `docs/operations/aws-and-yahoo-setup.md` (nor in any file changed by this
  slice).
- App ID `AyogcOTv` is the public Yahoo developer-console id.

## developer_feedback

none
