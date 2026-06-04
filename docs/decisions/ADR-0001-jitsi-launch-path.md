# ADR-0001: Jitsi Launch Path

## Status

Accepted for early production planning.

## Date

`<YYYY-MM-DD>`

## Context

Melura uses `melura_lms` to run the pedagogical LMS core on top of Frappe LMS.
Live classes are represented by `Bruce Live Class`, configured through
non-sensitive `Bruce Jitsi Settings`, and embedded in
`/app/bruce-live-room/<class>` after backend permission checks.

The current implementation is provider-neutral:

- room names are generated server-side and are not predictable;
- the browser receives only the Jitsi domain, room name, class metadata, and
  explicit fallback URL after authorization;
- `Bruce Student Access` remains the source of pedagogical access;
- Jitsi/JaaS credentials, JWT signing keys, API keys, provider tokens, and
  meeting secrets are not stored in committed docs or exposed to frontend
  payloads;
- public `meet.jit.si` can be used for local development, testing, demos, or an
  explicitly approved temporary fallback.

The production foundation compared self-hosted Jitsi, managed Jitsi/JaaS, and
public `meet.jit.si`. This ADR records the launch-path selection for Melura.

## Decision

Use a managed Jitsi / Jitsi as a Service style path for early production while
keeping `melura_lms` provider-neutral.

Self-hosted Jitsi remains a future option if cost, privacy, customization,
regional control, recording requirements, scale, or provider risk make it the
better long-term path.

Public `meet.jit.si` remains local/dev/demo only, or a temporary fallback that
requires explicit risk acceptance before any real production use.

## Considered Options

### Option A: Self-Hosted Jitsi

Operate a dedicated Jitsi environment under an approved production endpoint
configured outside Git.

Benefits:

- strongest infrastructure and configuration control;
- clearer ownership over hosting region, firewall, retention, and operations;
- flexible path for moderation, authentication, lobby, recording, branding, and
  privacy controls.

Tradeoffs:

- requires real-time video infrastructure expertise;
- shifts uptime, monitoring, upgrades, security patches, bandwidth, TURN/STUN,
  firewall, and incident response to the Melura operation;
- increases launch risk if no operator is ready to own Jitsi production
  support during class hours.

### Option B: Jitsi As A Service / Managed Jitsi

Use a managed Jitsi provider or JaaS-style deployment with production settings
configured outside Git.

Benefits:

- lower operational burden for early production;
- faster launch path while the LMS remains focused on pedagogy;
- provider can own scaling, updates, and part of live-video reliability;
- may enable stronger meeting controls later through provider-supported JWT or
  equivalent backend-generated credentials.

Tradeoffs:

- recurring cost;
- provider terms define parts of data handling, logs, retention, subprocessors,
  regions, support, and availability;
- future provider authentication still requires a scoped backend feature with
  safe secret handling;
- pricing, limits, and plan details must be manually verified before purchase
  or go-live.

### Option C: Public `meet.jit.si` For Development/Demo Only

Continue using the public service for local development, tests, short demos, or
temporary troubleshooting fallback.

Benefits:

- simplest setup;
- useful for development and fake-data validation;
- keeps the current fallback path easy to test.

Tradeoffs:

- not an accepted default production control boundary;
- Melura does not control capacity, support, access-control guarantees, data
  handling, recording options, retention, or availability;
- production use with real classes requires explicit business, privacy, and
  operational risk acceptance.

## Decision Criteria

The launch path is evaluated against:

- speed to safe early production;
- expected concurrent classes and participants;
- teacher and student reliability on desktop and mobile browsers;
- operational support burden during live class hours;
- acceptable recurring cost versus infrastructure work;
- LGPD/privacy review, subprocessors, data location, logs, and retention;
- ability to keep provider credentials outside Git and frontend payloads;
- future support for lobby, moderation, JWT, or equivalent admission controls;
- recording consent, storage, retention, and deletion requirements if recording
  becomes part of scope;
- HTTPS, domain, reverse proxy, WebSocket, firewall, and `external_api.js`
  behavior in staging;
- rollback and fallback options during class outages.

## Selected Launch Path

Early production should use a managed Jitsi / Jitsi as a Service style path.

The selected provider, plan, production domain, credentials, JWT signing keys,
app IDs, tokens, and operational contact details must be configured and
documented outside this repository. Committed files must use placeholders only.

## Rationale

Managed Jitsi/JaaS gives Melura the most pragmatic early-production path:

- it avoids taking on full live-video infrastructure operations before the LMS
  launch has proven real usage;
- it keeps Professor Bruce's workflow simple and focused on `Iniciar aula`,
  `Entrar na aula`, and the embedded live-room flow;
- it lets the team validate real class behavior before investing in
  self-hosted Jitsi automation or custom infrastructure;
- it preserves provider neutrality because `melura_lms` currently stores only
  non-sensitive Jitsi domain and room prefix settings.

Self-hosted Jitsi remains valid later if Melura needs stronger direct control
or if provider costs/limits become unfavorable.

## Consequences

- Production configuration must not rely on `curso.localhost`, localhost-only
  assumptions, or the public development default.
- `Bruce Jitsi Settings.domain` should point to the approved managed endpoint
  or approved public domain configured for the target environment.
- Provider credentials and any future JWT/signing material must stay in
  environment configuration, `site_config.json` outside Git, or an approved
  secret manager.
- Any provider-specific authentication, JWT generation, recording integration,
  webhook handling, or paid-provider API call requires a future scoped backend
  feature.
- Deployment and go-live validation must include a real class flow in staging
  or production-like conditions.

## Risks

- Provider terms, subprocessors, data location, logs, recording behavior,
  retention, support, and uptime may not satisfy Melura's final privacy or
  operational requirements.
- Recurring cost and plan limits may change; pricing must be manually verified
  before commitment.
- Without future provider-side admission controls, leaked external meeting URLs
  can still create Jitsi-side access risk even when Melura protects the LMS
  route.
- Mobile browser, network, WebSocket, and firewall behavior can differ between
  local development, staging, and production.
- Self-hosting later may require migration work if the managed provider path
  adds provider-specific features.

## Migration Path

1. Keep current provider-neutral `Bruce Live Class` and `Bruce Jitsi Settings`
   behavior.
2. Configure only non-sensitive public Jitsi domain settings in the target
   environment.
3. Validate teacher and student live-room flows with fake or approved test
   data.
4. If the managed provider requires JWT or signed room access, implement a
   separate backend feature that generates credentials server-side and exposes
   only the minimum browser-safe data.
5. If self-hosting becomes the chosen future path, replace the configured Jitsi
   domain with the approved self-hosted endpoint and validate HTTPS, reverse
   proxy, WebSocket/XMPP, TURN/STUN, firewall, monitoring, and incident
   response before production use.

## What Must Be Validated Before Go-Live

- Decision owner accepts this ADR and the selected launch path.
- Provider/privacy owner reviews data processing, subprocessors, support,
  region, logs, retention, and recording behavior.
- Production Jitsi configuration uses placeholders in committed docs and real
  values only outside Git.
- No Jitsi/JaaS credentials, API keys, JWT signing keys, provider secrets, or
  meeting secrets appear in frontend responses, HTML, logs, tests, fixtures, or
  committed files.
- Teacher can start/open a class using a non-`Administrator` operational
  account.
- Student with `Ativo` access can enter the correct class.
- Students with `Pendente`, `Bloqueado`, `Expirado`, missing access, or
  another course/batch scope cannot receive room data or open the live room.
- External fallback remains explicit; the app must not automatically open a
  public Jitsi URL in another tab.
- `external_api.js` loads over HTTPS from the configured Jitsi endpoint.
- Browser console, reverse proxy, WebSocket, and mobile behavior are validated
  in staging or a production-like environment.
- Recording is disabled or separately approved with consent, storage,
  retention, access, and deletion rules.

## Rollback / Fallback Plan

- If the managed provider has an outage, keep the LMS live-room page available
  and communicate the operational fallback through approved support channels.
- A temporary fallback to public `meet.jit.si` may be used only with explicit
  business/privacy risk acceptance and fake/demo data unless production use is
  approved for the incident.
- Revert `Bruce Jitsi Settings.domain` to the previously approved endpoint when
  the provider or configuration issue is resolved.
- If provider-specific backend integration is added in the future, rollback
  must include disabling that integration and clearing cache before restoring
  the previous provider-neutral behavior.

## Explicitly Not Implemented In This Feature

- Paid provider integration.
- Provider-specific API calls.
- Jitsi/JaaS JWT generation or authentication.
- Self-hosted Jitsi deployment automation.
- Docker/Jitsi setup.
- Production domain selection.
- Real provider pricing, plan selection, or vendor commitment.
- Recording automation.
- Schema, DocType, fixture, patch, hook, or migration changes.
- Changes to `frappe/`, `lms/`, `frappe-ui/`, `payments/`, or `jitsi-meet/`.
