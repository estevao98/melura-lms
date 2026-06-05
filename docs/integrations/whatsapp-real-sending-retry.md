# WhatsApp Real Sending And Retry

## Purpose

WhatsApp/Evolution sending in Melura LMS exists only to support pedagogical live
class communication. The current foundation lets an authorized operator preview
or send the live-class link through backend logic, record a safe notification
log, and retry a failed or pending live-class notification without exposing
provider secrets.

## Scope

In scope:

- live-class link notifications for `Melura Live Class`;
- manual preview with no provider call;
- manual real sending after backend permission checks;
- provider calls through Evolution API or protected n8n webhook;
- safe `Melura WhatsApp Notification Log` updates;
- manual retry for failed or pending live-class logs.

Out of scope:

- marketing automation;
- CRM workflows;
- billing, checkout, subscriptions, invoices, or payment status;
- mass campaigns;
- newsletters;
- sales funnels;
- lead capture or nurture flows.

## Provider Configuration

`Melura WhatsApp Settings` stores non-secret operational configuration only.
When enabled, the provider mode must be one of:

- `Evolution API`, requiring `api_url`, `instance_name`, and
  `EVOLUTION_API_KEY` from environment or site config;
- `n8n`, requiring a protected `n8n_webhook_url`.

Disabled provider mode fails closed: the backend records a failed log and does
not call Evolution API or n8n.

## Secrets

Provider secrets must stay outside Git. Use environment variables,
`site_config.json`, deployment secrets, or an approved secret manager.

Never commit or expose:

- `EVOLUTION_API_KEY`;
- n8n webhook URLs that authorize sending by possession;
- authorization headers;
- provider tokens;
- real production phone numbers or student data in test fixtures.

Browser responses must never include API keys, authorization headers, full
provider payloads, or sensitive webhook URLs.

## Safe Logging

Notification logs store only the fields needed for operation and support:
recipient summary, phone, message, status, related live class, short error, and
a redacted provider response summary.

Provider payloads are recursively redacted before storage. Sensitive keys such
as `apikey`, `api_key`, `authorization`, `token`, `access_token`,
`clientSecret`, `password`, and `secret` are replaced with `***`.

Provider exceptions are reduced to short safe summaries. Stack traces, auth
headers, and raw tokens must not be stored in notification logs or returned to
the frontend.

## Retry Rules

Retry is intentionally conservative:

- only logs linked to `Melura Live Class` can be retried;
- only `Pendente` and `Falhou` logs are retryable;
- `Enviado` and `Reenviado` logs are not retryable and must not trigger another
  provider call;
- retry requires backend write permission on the notification log or related
  live class;
- missing phone, missing live class, disabled integration, or incomplete
  provider configuration fails safely without external calls;
- successful retry marks the existing log as `Reenviado`.

The current DocType does not have retry count, next retry time, provider
message ID, or idempotency key fields. Because of that, retry updates the
existing log instead of creating a rich attempt history. This preserves the
safest possible behavior with the current schema, but exact attempt counting
and provider-level idempotency remain future work.

## Failure Handling

Failures must:

- not raise raw provider details to the user;
- not expose credentials in exceptions, logs, responses, or tests;
- mark the notification log as `Falhou`;
- store a short redacted error summary;
- keep the live class WhatsApp status aligned with the failed attempt.

Operators should inspect failed logs in Desk and retry only after confirming the
recipient and provider configuration.

## Manual Resend Expectations

Manual resend is for operational repair of a small number of live-class
notifications. It is not a campaign tool. Any future UI action should:

- require explicit confirmation;
- avoid accidental batch resend;
- show short Portuguese user-facing messages;
- keep detailed provider payloads out of the browser;
- preserve enough history to understand the original failure.

## Operational Checklist

- Confirm `Melura WhatsApp Settings.enabled` is intentional before testing.
- Confirm provider mode and required fields are configured.
- Confirm `EVOLUTION_API_KEY` is present outside Git for Evolution API mode.
- Confirm n8n webhook URL is protected and not exposed to students or teachers.
- Use preview first; preview must not call providers or create notification
  logs.
- Send only with mocked/test recipients in staging.
- Retry only `Pendente` or `Falhou` logs.
- Review logs for redaction before production use.
- Avoid production sends unless explicitly approved by the operator.

## Production Risks

- The provider may accept a message but fail delivery later; callback handling
  is not implemented in this foundation.
- Retry count and provider idempotency are not tracked in current fields.
- n8n webhook URLs may be sensitive and require deployment-level protection.
- Phone consent, privacy notices, retention periods, and support procedures
  need human operational decisions.
- Bulk resend, provider delivery callbacks, retry counts, and marketing
  automation are intentionally not implemented.
