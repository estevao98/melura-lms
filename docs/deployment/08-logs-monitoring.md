# Logs And Monitoring

Production logs should help operators diagnose issues without becoming a dump
of secrets, provider payloads, or unnecessary personal data.

## Logs To Check

Check logs for:

- Frappe web requests and errors;
- worker errors and failed jobs;
- scheduler activity;
- socketio connection errors when relevant;
- Redis connectivity errors;
- database errors;
- Nginx/reverse proxy errors;
- Jitsi live-room failures;
- WhatsApp/Evolution/n8n send failures;
- permission denials and suspicious access attempts.

The exact file paths depend on the bench and process manager setup.

## Avoid Logging Secrets And Personal Data

Do not log:

- API keys;
- tokens;
- passwords;
- auth headers;
- private keys;
- full webhook URLs with embedded secrets;
- full provider payloads;
- database credentials;
- full student data dumps;
- unnecessary phone, email, or message body data.

Safe logs should use short error summaries, related document references,
timestamp, responsible user when appropriate, and status.

## Basic Operational Monitoring

At minimum, monitor:

- site availability over HTTPS;
- disk usage;
- memory and swap pressure;
- database service health;
- Redis service health;
- worker queue backlog;
- scheduler status;
- backup completion;
- certificate expiration;
- repeated permission failures;
- repeated WhatsApp or Jitsi integration errors.

## Error Triage

When an error appears:

1. Identify affected route, DocType, background job, or integration.
2. Confirm whether users are affected.
3. Check recent deployment or configuration changes.
4. Review logs without copying secrets into tickets or chat.
5. Reproduce with a safe test account if possible.
6. Apply fix or rollback according to the runbook.
7. Document root cause and prevention.

## WhatsApp Safety Notes

WhatsApp provider errors should be summarized. Do not store or paste full
Evolution API tokens, authorization headers, full n8n webhook URLs, or complete
provider payloads into logs or support notes.

Notification attempts should preserve status, timestamp, related class, and a
short error summary.

## Jitsi Safety Notes

Jitsi room data is classroom access data. Backend permission checks must happen
before returning domain, `room_name`, `meeting_url`, or embedded room context.

Do not log predictable room-building inputs as a substitute for the generated
room name. Production should evaluate stronger Jitsi access controls when the
provider path is selected.

## Production Incident Notes

Incident notes should include:

- start and end time;
- user impact;
- affected service;
- suspected cause;
- actions taken;
- rollback or restore decision;
- credentials rotated, if any;
- follow-up tests or documentation updates.

Keep incident notes outside public repositories when they include operational
details, private infrastructure names, or personal data.
