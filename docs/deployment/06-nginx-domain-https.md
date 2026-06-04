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

The Jitsi launch path is recorded in
`docs/decisions/ADR-0001-jitsi-launch-path.md`. Managed Jitsi/JaaS and
self-hosted Jitsi have different domain, reverse proxy, WebSocket, firewall,
media, and support requirements; validate the selected path separately from the
Frappe LMS domain.

If the selected production Jitsi path uses a self-hosted Jitsi endpoint behind
a reverse proxy, validate the Jitsi web frontend, `external_api.js`, WebSocket
upgrade behavior, XMPP/WebSocket paths, media connectivity, and timeouts in
staging before go-live. Keep exact production domains, IPs, ports, and firewall
rules in private deployment notes.

## WebSocket Considerations

Frappe/socketio may require WebSocket upgrade headers. If socketio is used,
validate:

- reverse proxy supports `Upgrade` and `Connection` headers;
- browser console has no repeated socket connection failures;
- process manager supervises socketio;
- Redis socketio service is running where required.

Jitsi may also require WebSocket support depending on the selected deployment
or provider. Do not assume that a reverse proxy working for Frappe/socketio is
automatically sufficient for self-hosted Jitsi; validate browser console logs,
Jitsi connection state, and mobile network behavior separately.

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
