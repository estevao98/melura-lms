# Environments

Melura LMS should be operated with clear separation between local development,
staging/test VPS, and production VPS. Each environment may use the same Frappe
app code, but configuration, secrets, data, and operational expectations must
differ.

## Local Development

Local development is for building and validating changes with non-production
data.

Expected traits:

- site name may be `curso.localhost`;
- `bench start` may run web, workers, Redis, scheduler, and socketio together;
- `meet.jit.si` may be used for Jitsi development/testing;
- test credentials and placeholder settings only;
- no real student data, production database dumps, production backups, or
  production provider secrets.

Local-only assumptions must not leak into production:

- `curso.localhost`;
- localhost URLs;
- debug behavior;
- default or weak passwords;
- permissive firewall expectations;
- manual background services started in an interactive shell;
- provider test keys or copied production payloads.

## Staging Or Test VPS

Staging/test VPS is for production-like validation with limited or anonymized
data.

Expected traits:

- real HTTPS-capable domain or subdomain using placeholders in docs, such as
  `staging.example.com`;
- separate Frappe site from production;
- separate database, Redis, backups, and provider settings;
- no shared production secrets unless explicitly approved and rotated;
- workers, scheduler, and socketio run under a production-like process manager;
- smoke tests are run before promoting changes to production.

Use staging to validate migrations, builds, cache clearing, backup/restore,
Jitsi configuration, WhatsApp disabled or test mode, permissions, and rollback
steps.

## Production VPS

Production VPS is the live environment for real users.

Expected traits:

- real domain, HTTPS, and reverse proxy;
- debug mode disabled;
- production secrets outside Git;
- production database credentials stored securely;
- Redis services protected from public access;
- workers and scheduler supervised;
- backups scheduled, protected, and restore-tested;
- logs monitored without storing secrets or excessive personal data;
- operational accounts separated from technical `Administrator`.

## `curso.localhost` Versus Production Domain

`curso.localhost` is a local development site name. It should be used only on a
developer machine or equivalent local bench. A production domain is publicly
routable, terminates HTTPS, participates in browser security rules, may be
indexed or attacked, and requires operational controls.

Production must not depend on localhost routes, local-only hostnames, or manual
browser trust. All production URLs should use placeholders in documentation,
for example `https://app.example.com`, until the real domain is configured
outside Git.
