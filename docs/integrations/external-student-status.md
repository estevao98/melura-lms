# External Student Status Integration

This document defines the safe foundation for an external
financial/commercial SaaS to update Melura LMS pedagogical access status.

Melura LMS remains the pedagogical system. The external SaaS remains
responsible for billing, checkout, subscriptions, CRM, blog, newsletter, lead
capture, and financial/commercial workflows.

## Purpose

The integration exists only to let a trusted external system update
Acesso do aluno (legacy internal DocType currently named `Bruce Student Access`) `access_status` after a commercial decision has already
been made outside this app.

Allowed Melura LMS statuses:

- `Ativo`
- `Pendente`
- `Bloqueado`
- `Expirado`

Only `Ativo` unlocks pedagogical content. `Pendente`, `Bloqueado`, and
`Expirado` must not unlock classes, materials, questions, exercise lists,
answers, or progress metrics.

## Product Boundary

Melura LMS may receive:

- one safe target identifier, preferably `access_name` or
  `bruce_student_access`;
- or an existing opaque `external_reference`;
- a pedagogical status value;
- an optional opaque `external_reference` for future correlation.

Melura LMS must never receive or store:

- card data;
- card tokens;
- CVV or card number fragments;
- checkout payloads;
- payment payloads;
- transaction payloads;
- invoice payloads;
- subscription payloads;
- customer financial profiles;
- prices, amounts, currency, tax, fiscal, or reconciliation data;
- API keys, webhook secrets, passwords, or provider credentials;
- complete provider payloads.

The current foundation updates existing Acesso do aluno (legacy internal DocType currently named `Bruce Student Access`) records only.
It does not create subscriptions, invoices, leads, CRM records, billing
entities, or financial records.

## Status Mapping

The service accepts these external status values:

| External values | Melura status |
| --- | --- |
| `active`, `paid`, `approved` | `Ativo` |
| `pending`, `waiting` | `Pendente` |
| `blocked`, `cancelled`, `canceled`, `suspended` | `Bloqueado` |
| `expired`, `overdue`, `ended` | `Expirado` |

The Portuguese Melura status values are also accepted as already-normalized
inputs. Unknown statuses are rejected.

## Webhook Security

The webhook endpoint is:

```text
melura_lms.services.external_student_status.handle_external_student_status
```

It is intentionally minimal and guest-callable only because it verifies an HMAC
signature before parsing, locating, or updating any access record.

Requirements:

- configure the shared secret outside Git;
- sign the exact JSON request body with HMAC-SHA256;
- send the signature in `X-Melura-Signature`;
- missing configured secret fails closed;
- missing request signature fails closed;
- invalid signature fails closed;
- do not send the shared secret in the payload, URL, logs, or frontend.

Accepted secret configuration keys:

- `external_student_status_webhook_secret` in `site_config.json`;
- `EXTERNAL_STUDENT_STATUS_WEBHOOK_SECRET` in `site_config.json` or environment;
- `MELURA_EXTERNAL_STUDENT_STATUS_WEBHOOK_SECRET` in `site_config.json` or
  environment.

Example placeholder only:

```json
{
  "external_student_status_webhook_secret": "<external-status-webhook-secret>"
}
```

Do not commit real values.

## Minimal Payload

Example with placeholders only:

```json
{
  "access_name": "BSA-YYYY-00000",
  "external_reference": "<opaque-external-reference>",
  "status": "active"
}
```

If `access_name` is not sent, the service can locate exactly one existing
Acesso do aluno (legacy internal DocType currently named `Bruce Student Access`) record by `external_reference`.

The response is intentionally small:

```json
{
  "ok": true,
  "status": "Ativo",
  "updated": true
}
```

It does not return student data, secrets, provider payloads, or financial data.

## Idempotency

The update is naturally idempotent: processing the same valid event again sets
the same Melura status and opaque external reference. If no allowed field
changes, the document is not saved again.

There is no dedicated stored event-id field in the current DocType. This means
the service cannot persist replay history or exactly-once event processing yet.
If the external SaaS provides event IDs later, add storage only after a scoped
schema decision.

## Logging

Do not log full webhook payloads.

Operational logging, when added, should store only:

- timestamp;
- result status;
- target Acesso do aluno (legacy internal DocType currently named `Bruce Student Access`) reference or opaque correlation ID;
- short error category.

It must not store secrets, signatures, card data, payment payloads, customer
financial profiles, or full provider responses.

## Failure Handling

Rejected events must not partially update access records.

Failure cases include:

- missing configured secret;
- missing signature;
- invalid signature;
- invalid JSON;
- unknown status;
- overbroad financial payload fields;
- missing safe target identifier;
- duplicate `external_reference`;
- missing target access record.

Errors should remain minimal and should not expose the configured secret,
signature, provider payload, or student private data.

## Manual Verification Checklist

- Confirm the secret is configured outside Git.
- Confirm missing secret fails closed.
- Confirm missing signature fails closed.
- Confirm invalid signature fails closed.
- Confirm a valid signed payload updates only Acesso do aluno (legacy internal DocType currently named `Bruce Student Access`).
- Confirm `Ativo` unlocks only normal pedagogical access through existing
  backend checks.
- Confirm `Pendente`, `Bloqueado`, and `Expirado` do not unlock content.
- Confirm card/payment/checkout/invoice/subscription/customer financial fields
  are rejected.
- Confirm repeated delivery of the same event is safe.
- Confirm the response does not expose the secret, signature, student data, or
  provider payload.
- Confirm no billing, checkout, subscription, CRM, blog, newsletter, or lead
  capture behavior was added.

## Current Limitations

- The integration updates existing Acesso do aluno (legacy internal DocType currently named `Bruce Student Access`) records only.
- There is no persistent idempotency-event table or replay history.
- There is no provider-specific parser.
- There is no billing, checkout, subscription, CRM, blog, newsletter, or lead
  capture implementation in this app.
