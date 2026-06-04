# Nginx, Domain, And HTTPS

Production Melura LMS must use a real domain and HTTPS. Localhost and
`curso.localhost` are development-only assumptions.

## Domain Setup

Conceptual steps:

1. Choose a production domain, represented in docs as `app.example.com`.
2. Point DNS records to the VPS or load balancer.
3. Configure the Frappe site for that domain.
4. Configure the reverse proxy to route the domain to the bench web process.
5. Validate the site from a browser and from server logs.

Do not commit real domains, IP addresses, DNS provider tokens, or certificate
account credentials.

## HTTPS Requirements

Production should enforce HTTPS for login, student content, live class pages,
admin dashboards, and integration callbacks.

Validate:

- certificate is valid;
- certificate auto-renewal is configured;
- HTTP redirects to HTTPS when appropriate;
- cookies are protected according to Frappe and deployment settings;
- no sensitive page is served over plain HTTP.

## Reverse Proxy Notes

Nginx or an equivalent reverse proxy should handle:

- incoming HTTPS;
- static and private file rules according to Frappe guidance;
- proxying to the Frappe web process;
- request size/timeouts appropriate for LMS usage;
- safe logging without secrets.

Private files must not become publicly accessible through reverse proxy
misconfiguration.

The live-class launch path is recorded in
`docs/decisions/ADR-0002-google-meet-only-live-flow.md`. Google Meet opens as
an external link, so Melura does not configure video reverse proxy, media
services, provider APIs, SDKs, or self-hosted video infrastructure.

Validate in staging that the Melura page opens the configured Google Meet URL
only after backend authorization. Keep exact production domains, IPs, ports, and
firewall rules in private deployment notes.

## WebSocket Considerations

Frappe/socketio may require WebSocket upgrade headers. If socketio is used,
validate:

- reverse proxy supports `Upgrade` and `Connection` headers;
- browser console has no repeated socket connection failures;
- process manager supervises socketio;
- Redis socketio service is running where required.

Google Meet itself is outside Melura infrastructure; validate only that the
authorized Melura launch page opens the configured external URL.

## Why Production Must Not Rely On Localhost

Localhost assumptions bypass the real operational surface:

- public DNS;
- HTTPS certificate validation;
- reverse proxy behavior;
- browser cookie/security behavior;
- firewall exposure;
- logs and monitoring;
- external integrations and callbacks.

Use `curso.localhost` only for local development. Use placeholders such as
`app.example.com` in docs until the real domain is configured outside Git.
