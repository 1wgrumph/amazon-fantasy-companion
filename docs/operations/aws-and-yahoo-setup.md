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
  to `127.0.0.1:<port>`. Check it worked with
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

- Created at `developer.yahoo.com/apps/create` as **Amazon Fantasy Companion**.
- OAuth client type: Confidential. API permission: **Fantasy Sports - Read**.
- Redirect URI: `https://localhost/link`. Yahoo rejects `oob` and requires an
  `https` URI. After approval the browser lands on a page that does not load;
  the authorization `code` is in its address bar. Add the deployed
  `<ApiUrl>/link` later in the app settings if the backend takes over the flow.
- The description may not contain the word "Yahoo".

## Consent and token (P2-X06)

1. `python3 spikes/sp6-yahoo/yahoo_oauth.py url` prints the approval URL.
2. Open it, approve, copy `code` from the address bar.
3. `python3 spikes/sp6-yahoo/yahoo_oauth.py exchange` and paste the code at the
   prompt. It stores the refresh token in `/afc/dev/yahoo-token` and prints only
   `stored`.
4. The spike reads roster and settings; its result is
   `spikes/sp6-yahoo/VERDICT.md`.

The plan intended the Yahoo read to run under the deployed backend role; the
spike runs it locally as the `afc-dev` user (recorded in the X06 verdict).
