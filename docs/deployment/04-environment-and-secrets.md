# Environment And Secrets

Production configuration must keep sensitive values outside Git. This document
uses placeholders only. Replace placeholders in the deployment environment, not
in committed files.

## Values That Must Stay Outside Git

Never commit:

- real `.env` files;
- `site_config.json`;
- `common_site_config.json`;
- database passwords;
- encryption keys;
- API keys;
- webhook secrets;
- Evolution API keys;
- sensitive n8n webhook URLs;
- Jitsi/JaaS credentials;
- private certificates or keys;
- backups, database dumps, or files containing real student data;
- production logs with secrets or personal data.

## `site_config.json`

Frappe sites commonly store site-specific configuration in
`sites/<site>/site_config.json`. This file is outside the `melura_lms`
repository and must remain uncommitted.

Example with placeholders only:

```json
{
  "db_name": "<database-name>",
  "db_password": "<database-password>",
  "encryption_key": "<frappe-encryption-key>",
  "evolution_api_key": "<evolution-api-key>",
  "external_student_status_webhook_secret": "<external-status-webhook-secret>"
}
```

Use the exact key names expected by the current implementation. For Evolution
API, the app accepts `evolution_api_key`, `EVOLUTION_API_KEY`, or the
`EVOLUTION_API_KEY` environment variable.

For the external student status webhook, the app accepts
`external_student_status_webhook_secret`,
`EXTERNAL_STUDENT_STATUS_WEBHOOK_SECRET`, or
`MELURA_EXTERNAL_STUDENT_STATUS_WEBHOOK_SECRET` from site config or
environment.

## Environment Variable Examples

Use placeholders in docs and scripts:

```bash
export EVOLUTION_API_KEY="<evolution-api-key>"
export EXTERNAL_STUDENT_STATUS_WEBHOOK_SECRET="<external-status-webhook-secret>"
export MELURA_N8N_WEBHOOK_URL="<protected-n8n-webhook-url>"
export MELURA_JITSI_DOMAIN="<jitsi-domain>"
```

Do not commit a file containing real values. If a secret is accidentally
committed, revoke and rotate it immediately.

## Evolution API Key Handling

The Evolution API key must be read only by backend logic or a protected flow.
It must not be:

- returned by browser APIs;
- rendered in HTML;
- placed in Vue, JavaScript, or desk client code;
- logged in full;
- stored in a public DocType field.

`Bruce Evolution Settings` may store non-secret operational fields, but the API
key belongs in environment configuration, `site_config.json`, or a secret
manager.

## n8n Webhook URL Handling

An n8n webhook URL can be sensitive if possession of the URL allows triggering
an action. Treat protected webhook URLs like secrets:

- store outside Git when sensitive;
- do not expose to students or teachers;
- do not log full URLs if they include tokens or unguessable paths;
- validate backend permission before calling the webhook.

## Jitsi Domain And Config Handling

Non-secret Jitsi settings such as a public domain can live in
`Bruce Jitsi Settings`. Production should evaluate self-hosted Jitsi or JaaS
when stronger access controls are required.

Any future Jitsi/JaaS credentials, JWT signing keys, app IDs, or provider
secrets must stay outside Git and out of frontend payloads.

## External Student Status Webhook Secret Handling

The external student status webhook secret signs access-status updates from the
external financial/commercial SaaS. It must stay outside Git and must not be:

- sent in the webhook payload;
- included in URLs;
- returned by browser APIs;
- rendered in HTML;
- logged in full;
- stored in a DocType field.

Rotate the secret if it is exposed. Missing or invalid webhook signatures must
fail closed before `Bruce Student Access` is located or updated.

## Database Passwords

Database passwords belong in Frappe site configuration or the approved secret
mechanism. They must not appear in docs, tests, fixtures, logs, or committed
config examples except as placeholders.

## Encryption Keys

Frappe encryption keys protect sensitive site data. They must be backed up
securely outside Git. Losing the key can make encrypted data unrecoverable.
Exposing the key can expose protected data.

## Commit Review

Before deployment or merge, inspect the diff for:

- `EVOLUTION_API_KEY`;
- `api_key`;
- `token`;
- `password`;
- `secret`;
- `authorization`;
- real domains, IPs, emails, phone numbers, and student data;
- `site_config.json`;
- `common_site_config.json`;
- backups and dumps.
