# AWS and Yahoo setup for the dev stack

How the `afc-dev` AWS account and the Yahoo Fantasy app are wired for this
project, as set up on 2026-10-16. No secret values belong in this file.

## AWS CLI access

- Profile `afc-dev`, region `us-east-2`, IAM user `afc-dev`. The profile uses
  `aws login` (console-credential sign-in), not long-lived access keys.
- Sign in from a normal terminal, not a tool runner with a short timeout:

  ```
  aws login --profile afc-dev
  ```

  The command opens the AWS sign-in page and waits for the browser to call back
  to `localhost:<port>`. Check it worked with
  `aws sts get-caller-identity --profile afc-dev`.
- Known failure (2026-10-16): choosing **Continue with an active session** on
  the sign-in page ends on `signin.aws.amazon.com/oauth?...iam_user=true` with
  **400 Bad Request**. Choose **Sign in to new session**, then **Continue to
  sign in**, and sign in as the IAM user. Running `aws login` twice at once also
  breaks the flow: stop the old one first.
- Stack: CloudFormation stack `afc-dev` (SAM, `backend/template.yaml`).

## SSM parameters

| Name | Type | Holds | Who writes it |
|---|---|---|---|
| `/afc/dev/yahoo-client-id` | String | Yahoo app Client ID | owner |
| `/afc/dev/yahoo-client-secret` | SecureString | Yahoo app Client Secret | owner |
| `/afc/dev/yahoo-token` | SecureString | Yahoo OAuth refresh token | `spikes/sp6-yahoo/yahoo_oauth.py exchange` |

The secret and token parameter names are the template defaults
`YahooClientSecretParameter` and `YahooTokenParameter`. Owners write secrets
from their own terminal, for example:

```
aws ssm put-parameter --profile afc-dev --type SecureString \
  --name /afc/dev/yahoo-client-secret --value '<secret>'
```

## Yahoo app

- The app in use is **Amazon Fantasy Companion**, App ID `md4Tp1VN`, created
  by the owner after Yahoo's 2026-10-16 approval (see "Yahoo 403: API access
  approval" below). Homepage `https://github.com/1wgrumph/amazon-fantasy-companion`.
  Do not create another app and do not submit the confirmation form again.
- Two other apps exist and stay unused: the original `AyogcOTv` (2026-10-13,
  created before approval) and `TZRCt46p` "Amazon Fantasy Companion 2026"
  (created and submitted by an agent on 2026-10-20 by mistake). Owner decision
  2026-10-21: keep both, do not delete.
- OAuth client type: Confidential. API permission: **Fantasy Sports - Read**.
- Redirect URI: `https://localhost:8443/link`. Yahoo rejects `oob` and requires
  `https`. Add the deployed `<ApiUrl>/link` later if the backend takes over the
  flow.
- The app description may not contain the word "Yahoo".
- The Client ID is the long `dj0y...` value (96 characters); the Client Secret
  is about 40 characters.

## Getting the Yahoo token (one command)

Run in a normal terminal window, not through a tool runner's `!` prefix (that
has no keyboard input and fails with `EOFError`):

```
cd <worktree with spikes/sp6-yahoo>
python3 spikes/sp6-yahoo/yahoo_oauth.py setup
```

1. Copy the **Client ID** from the app page, paste it at the first prompt
   (Ctrl+Shift+V; nothing is shown), Enter.
2. Go back and copy the **Client Secret**, paste it at the second prompt, Enter.
   Copy right before each paste; on 2026-10-16 the ID was pasted twice.
3. It prints `saved to SSM (client id 96 chars, secret 40 chars)` and an
   approval URL. Open it, approve, then on the certificate warning click
   **Advanced -> Proceed to localhost**. The script catches the redirect on
   `https://localhost:8443/link` with a throwaway self-signed certificate.
4. It prints `stored`: the refresh token is in `/afc/dev/yahoo-token`.

`capture` repeats steps 3-4 with the stored ID and secret.
`read` uses the stored token to read leagues, roster and settings.

### Errors seen and their meaning

| Output | Cause | Fix |
|---|---|---|
| `token exchange: INVALID_CLIENT_SECRET` | wrong value in `/afc/dev/yahoo-client-secret` (a placeholder, or the Client ID pasted twice) | run `setup` again |
| `no code given` / `EOFError` | paste did not land, or run without a terminal | use Ctrl+Shift+V in a real terminal |
| HTTP 400 on exchange with an old code | authorization codes expire in about 10 minutes and are single use | run `capture` again |

The plan intended the Yahoo read to run under the deployed backend role; the
P2-X06 spike runs it locally as the `afc-dev` user (recorded in its verdict).
Token stored 2026-10-16T14:18Z.

## Yahoo 403: API access approval

OAuth can succeed and the Fantasy API can still refuse the call. Since July
2026, Yahoo gates Fantasy API access, including public endpoints, behind its
API access program. An app that is not approved gets HTTP 403
`This application is not authorized` while token refresh still returns 200.

Seen on this app on 2026-10-16: token refresh HTTP 200, then Fantasy API
HTTP 403 `This application is not authorized to perform this action.`, both
with no scope and with `fspt-r`
([attempts.json](../../spikes/sp6-yahoo/evidence/attempts.json) lines 8-12
and 17-23). Same report, including public endpoints:
[yfpy issue #84](https://github.com/uberfastman/yfpy/issues/84) (since
2026-07-22) and the
[yahoo-fantasy-mcp README](https://github.com/krger/yahoo-fantasy-mcp).
Request access at <https://sports.yahoo.com/developer/access/>.

The owner submitted that application on 2026-10-16 for App ID `AyogcOTv`.
Approval could not arrive before T_yahoo `2026-10-16T19:00:00Z`, so
[the SP-6 verdict](../../spikes/sp6-yahoo/VERDICT.md) is FAILS and the lineup
source stays manual (`backend/src/lineup/manual.py`).

Approval history (owner records, 2026-10-16 to 2026-10-21):

| Date (CDT) | Event |
|---|---|
| 2026-10-16 10:05 | Yahoo acknowledged the access request for `AyogcOTv`. |
| 2026-10-16 17:59 | Yahoo approved access. Its instructions: sign the API Access and Use Agreement, create a **new** app with Fantasy Sports - Read (existing apps do not pick up the permission), and submit the new app's Client ID on the confirmation form. |
| 2026-10-16/17 | The owner created app `md4Tp1VN`, submitted its Client ID, and signed the agreement (Personal Use, read-only, effective 2026-10-23). This was not recorded in the repository at the time. |
| 2026-10-20 | An agent, unaware of `md4Tp1VN`, created `TZRCt46p` and submitted its Client ID. Yahoo replied with a second "Access Request Received". |
| 2026-10-20 20:55 | At the owner's direction, an email to Yahoo's Fantasy API applications contact named `md4Tp1VN` as the intended Client ID and asked Yahoo to disregard `TZRCt46p`. |
| 2026-10-21 | Owner decisions: point `/afc/dev/yahoo-client-id` and `/afc/dev/yahoo-client-secret` at `md4Tp1VN` now; keep `TZRCt46p` unused. |

Once Yahoo confirms access for `md4Tp1VN`:

1. Confirm the SSM client parameters hold `md4Tp1VN`'s Client ID and Secret.
2. In a normal terminal, run `python3 spikes/sp6-yahoo/yahoo_oauth.py setup`
   to get a token for that app, then `read`. A Fantasy API HTTP 200 means the
   gate is open.
3. Leave the lineup source manual until a later change selects yahoo. This
   verdict does not switch it.
