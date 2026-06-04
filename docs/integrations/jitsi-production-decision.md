# Jitsi Production Decision Foundation

This document defines the production decision foundation for live classes in
Melura LMS. It compares self-hosted Jitsi, Jitsi as a Service, and the current
public `meet.jit.si` fallback, and it sets the boundaries for safe production
implementation.

The concrete launch-path selection is recorded in
`docs/decisions/ADR-0001-jitsi-launch-path.md`: early production should follow
a managed Jitsi / Jitsi as a Service style path while keeping `melura_lms`
provider-neutral and preserving self-hosted Jitsi as a future option.

It does not implement a paid provider integration, Docker/Jitsi automation,
schema changes, or final production domains.

## Current Status

Melura LMS currently supports live classes through:

- `Bruce Jitsi Settings`, storing non-sensitive operational settings such as
  Jitsi domain and room prefix;
- `Bruce Live Class`, storing class metadata, server-generated room names,
  meeting URLs, class status, instructor, course, and batch scope;
- `/app/bruce-live-room/<class>`, embedding the Jitsi IFrame API after backend
  authorization;
- explicit external URL fallback through `Abrir em nova aba`.

Current safety boundaries:

- room names are generated server-side with non-predictable tokens;
- the frontend does not generate room names or decide access scope;
- live-room context is returned only after backend permission checks;
- only students with active `Bruce Student Access` in the correct scope can
  access protected class data;
- Jitsi settings cached by the app are limited to public `domain` and
  `room_prefix` values;
- `meet.jit.si` is acceptable for local development, testing, and demos.

The current foundation does not provide production-grade meeting admission
control inside Jitsi itself. Melura checks authorization before returning room
data, but once a participant has a valid external meeting URL, enforcement also
depends on the selected Jitsi deployment or provider controls.

## Production Decision Problem

Production must decide where Melura live classes run and which party owns the
operational and security controls:

- a self-hosted Jitsi deployment operated by Melura/Professor Bruce's
  infrastructure team;
- a managed Jitsi as a Service provider;
- a temporary public `meet.jit.si` fallback accepted explicitly for limited
  development/demo use only.

The decision affects cost, operational workload, privacy responsibilities,
support response, scaling limits, recording behavior, network requirements, and
student/teacher reliability.

## Option A: Self-Hosted Jitsi

Self-hosted Jitsi means operating a dedicated Jitsi environment under a
placeholder domain such as `jitsi.example.com`.

Expected production work:

- provision infrastructure sized for class concurrency;
- configure HTTPS and DNS;
- configure Jitsi Videobridge, Prosody, web frontend, TURN/STUN where needed,
  and WebSocket/XMPP behavior;
- harden firewall rules and admin access;
- monitor CPU, memory, bandwidth, packet loss, logs, and service health;
- define backup and restore expectations for configuration;
- decide how authentication, lobby, moderation, JWT, or token-based access will
  work;
- document incident response for class outages.

Advantages:

- strongest infrastructure control;
- clearer ability to choose hosting region and data handling posture;
- flexible configuration for moderation, recording, branding, retention, and
  authentication;
- no dependency on a paid meeting provider roadmap.

Tradeoffs and risks:

- higher operational burden;
- production video reliability depends on internal expertise;
- scaling and bandwidth can become expensive or fragile during peaks;
- recording storage and retention become an infrastructure responsibility;
- security patches and Jitsi upgrades must be operated correctly;
- firewall, NAT, TURN, and mobile network issues need real operational support.

Self-hosting is attractive when Melura needs direct infrastructure control,
specific privacy commitments, customized authentication, or predictable
high-volume usage. It is risky for early production if there is no operator
ready to own real-time video infrastructure.

## Option B: Jitsi as a Service

Jitsi as a Service means using a managed Jitsi provider with a customer-owned
configuration and provider-supported controls.

Expected production work:

- choose provider and plan;
- document data processing, support, uptime, region, recording, and privacy
  terms;
- configure a non-secret public domain or provider domain in
  `Bruce Jitsi Settings`;
- keep all provider credentials, app IDs, JWT signing keys, and secrets outside
  Git and outside frontend payloads;
- implement provider authentication/JWT only in a future scoped backend
  feature;
- validate class concurrency and mobile/browser behavior in staging.

Advantages:

- lower operational burden for early production;
- provider owns much of the video infrastructure, updates, and scaling;
- support and SLAs may be available depending on plan;
- easier path to stronger access controls such as JWT if supported;
- faster launch while the pedagogical LMS remains focused.

Tradeoffs and risks:

- recurring provider cost;
- provider terms define data handling, regions, logs, recording, retention, and
  subprocessors;
- Melura depends on provider availability and product changes;
- advanced integration still needs backend work and safe secret handling;
- provider limits can affect class size, recording, or feature availability.

Jitsi as a Service is the recommended default path for early production if the
budget accepts recurring cost and provider privacy terms are approved.

## Option C: Public `meet.jit.si` Fallback

Public `meet.jit.si` may remain useful for:

- local development;
- test sites with fake or anonymized data;
- short demos where participants understand the limitation;
- temporary fallback during controlled troubleshooting.

It is not the default production assumption.

Using public `meet.jit.si` for production would require an explicit business,
privacy, and operational acceptance because Melura does not control provider
capacity, support, access-control guarantees, data handling, recording options,
or availability. It must not be treated as the final production path merely
because it is the current development default.

## Decision Criteria

Choose the production path by comparing:

- expected concurrent classes and participants;
- acceptable monthly cost versus internal operations time;
- required uptime and support response;
- LGPD/privacy obligations and provider/subprocessor terms;
- desired hosting region and international transfer implications;
- need for lobby, moderator controls, JWT, or authenticated room access;
- need for recording, storage, retention, and deletion controls;
- student device/network profile, especially mobile browsers;
- teacher workflow simplicity;
- staging validation results;
- incident response capability during live class hours.

## Cost, Operations, Security, And Privacy Tradeoffs

Self-hosted Jitsi shifts cost from provider fees to infrastructure, monitoring,
maintenance, upgrade, incident response, and bandwidth. It can improve control
but only if the operator can maintain the video stack safely.

Jitsi as a Service shifts infrastructure work to a provider and may provide a
faster production path. It requires contract, privacy, and cost review, and any
credentials must be handled as secrets.

Public `meet.jit.si` minimizes setup effort but does not give Melura a stable
production control boundary. Treat it as development/demo only unless a
decision owner explicitly accepts the risk.

## Student Experience Implications

Students need a reliable, simple entry path from `Minha Aula` or the live-room
page. Production Jitsi choice affects:

- class join speed;
- mobile browser behavior;
- audio/video stability under weak networks;
- whether students see lobby, password, or provider-specific prompts;
- whether fallback to a new tab is needed;
- whether unauthorized participants can join if a link leaks.

Melura should keep the primary flow inside `/app/bruce-live-room/<class>` and
keep external link opening as an explicit fallback.

## Teacher Experience Implications

Professor Bruce should not need to understand `room_name`, provider secrets,
Jitsi internals, or deployment details.

Production choice affects:

- how reliably `Iniciar aula` opens a room;
- whether moderation, lobby, recording, mute controls, or participant removal
  are available;
- support path during a class outage;
- whether provider-specific teacher identity or moderator claims are required.

Any future provider authentication must be generated server-side and hidden from
normal teacher UI.

## LGPD And Privacy Considerations

Live classes can reveal personal data and educational participation metadata.
Before production, the decision owner should review:

- controller/operator and subprocessor roles for the selected Jitsi path;
- data location and possible international transfer;
- provider logs and retention;
- recording consent, storage, access, retention, and deletion;
- incident response and support access to meeting metadata;
- whether minors or guardians require additional handling;
- whether public privacy notices need to name the selected provider.

Melura must not expose Jitsi/JaaS credentials, JWT signing keys, app secrets, or
provider tokens to browser APIs, HTML, logs, docs, tests, or Git.

## Scaling Considerations

For either production option, validate:

- expected maximum concurrent classes;
- expected maximum participants per class;
- mobile and desktop browser compatibility;
- bandwidth and packet loss under realistic conditions;
- class start behavior during traffic peaks;
- fallback behavior when the Jitsi service is unavailable;
- monitoring signal available to support staff.

Self-hosting also requires capacity planning for videobridge resources, TURN
traffic, CPU, memory, bandwidth, and regional latency.

## Recording Considerations

Recording is not required by the current Jitsi foundation. If recording becomes
part of production scope, decide before implementation:

- who can start and stop recording;
- where recordings are stored;
- whether recordings include student personal data;
- consent and legal basis;
- retention and deletion period;
- who can access downloads;
- whether recordings must remain inside Melura or an external storage provider;
- whether provider recording APIs require secrets or webhooks.

Do not add recording automation without a separate privacy, permission, and
storage design.

## Domain, HTTPS, Firewall, And WebSocket Requirements

Production Melura LMS requires a real HTTPS domain for the app. A production
Jitsi path also requires its own approved HTTPS endpoint or managed provider
endpoint.

Validate:

- committed docs and code use placeholders only;
- DNS is configured outside Git;
- HTTPS certificate renewal is operationally owned;
- reverse proxy supports required WebSocket upgrade headers;
- firewall rules allow only the necessary web, media, and administration
  traffic;
- private admin ports are not public;
- browser console does not show repeated Jitsi API, WebSocket, or mixed-content
  failures;
- `external_api.js` loads from the configured domain over HTTPS.

Self-hosted Jitsi usually needs additional UDP/TCP media and TURN/STUN planning.
The exact firewall rules must be documented in private deployment notes because
they are infrastructure-specific.

## Secrets And Configuration Boundaries

Allowed in `Bruce Jitsi Settings`:

- public Jitsi domain;
- public room prefix;
- non-sensitive operational toggles.

Must stay outside Git and frontend payloads:

- JaaS credentials;
- app IDs when provider treats them as sensitive;
- JWT signing keys;
- API keys;
- private certificates;
- provider webhook secrets;
- recording/storage credentials;
- internal-only service URLs.

Backend rules:

- generate room names server-side;
- validate permission before returning domain, room name, meeting URL, or
  embedded room data;
- derive student identity from `frappe.session.user`;
- never trust frontend course, batch, class, or student parameters as
  authorization scope;
- return only fields needed by the live-room UI;
- log failures without secrets, tokens, or full provider payloads.

## Recommended Default Path For Early Production

Recommended default: choose Jitsi as a Service for early production, after
privacy/legal review and staging validation.

Reasoning:

- it avoids adding video infrastructure operations to the first production
  launch;
- it allows Melura LMS to stay focused on pedagogical access and class
  workflows;
- provider-supported access controls can be added later through a scoped
  backend integration;
- self-hosting remains available later if scale, cost, privacy, or control
  requirements justify it.

Exception: choose self-hosted Jitsi earlier only if there is a named operator,
budget, monitoring plan, patch process, and incident response path for real-time
video infrastructure.

Do not use public `meet.jit.si` as production default unless the decision owner
explicitly accepts that risk for a limited launch.

## Open Risks

- Final production Jitsi provider/domain is undecided.
- Provider privacy terms, subprocessors, data region, and support terms are not
  yet approved.
- Strong Jitsi-side room admission control is not implemented in Melura yet.
- JWT/JaaS integration is future work and must be backend-only.
- Recording scope, consent, storage, and retention are undecided.
- Self-hosted capacity, firewall, TURN/STUN, monitoring, and upgrade process
  are not designed.
- Public `meet.jit.si` remains a development/demo fallback, not a production
  guarantee.
- Real production testing must still validate mobile networks, browser support,
  and class concurrency.

## Final Decision Checklist

- [ ] Decision owner is named.
- [ ] Production path is selected: self-hosted Jitsi or Jitsi as a Service.
- [ ] Public `meet.jit.si` production use is rejected or explicitly accepted
      with a limited-risk sign-off.
- [ ] Privacy/legal review covers provider, subprocessors, data location,
      recordings, retention, and incident handling.
- [ ] Production Jitsi domain/provider endpoint is configured outside Git.
- [ ] No real domains, IPs, API keys, JWT secrets, provider credentials, or
      student data are committed.
- [ ] `Bruce Jitsi Settings` contains only non-sensitive public configuration.
- [ ] Live-room context still requires backend permission checks.
- [ ] Staging validates active, blocked, expired, other-course, teacher, and
      admin access paths.
- [ ] HTTPS, reverse proxy, WebSocket, firewall, and browser behavior are
      validated for the chosen path.
- [ ] Support runbook covers class-start failure and provider outage fallback.
- [ ] Recording is disabled or separately approved with privacy and retention
      controls.
- [ ] Future JWT/JaaS or self-hosting automation is tracked as a separate
      feature, not hidden inside this decision foundation.
