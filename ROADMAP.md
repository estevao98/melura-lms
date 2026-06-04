# Roadmap — melura_lms

## 1. Product Direction

`melura_lms` customizes Frappe Learning/LMS for Professor Bruce's online
ENEM / Ciências Humanas course.

The goal is to deliver a clean pedagogical LMS layer for students, Professor
Bruce, and operational admins. The app should stay upgrade-friendly by using
Frappe extension points and avoiding direct changes to Frappe, Frappe LMS,
Frappe UI, or Jitsi Meet core.

The product focus is teaching, pedagogical access control, educational
materials, exercise lists, student answers, progress, live classes, WhatsApp
notification preparation, and operational visibility.

## 2. Product Boundary

This app handles the pedagogical LMS core.

The external SaaS handles billing, checkout, subscriptions, CRM, blog,
newsletter, lead capture, and financial/commercial flows.

A future integration with the external SaaS may update pedagogical access
status and opaque external references, but it must not turn this app into the
financial system.

**Rule:** Do not bring financial SaaS responsibilities into this Frappe LMS app
by default.

## 3. Product Principles

- Security before convenience.
- Backend permissions before frontend visibility.
- Student simplicity before admin complexity.
- Frappe extension over core modification.
- Brazilian Portuguese for user-facing UI.
- English for internal documentation.
- Small focused features before broad rewrites.
- Reliable pedagogical data before advanced analytics.
- Manual operational control before complex automation.
- Production readiness before scale.

## 4. Current Stage

MVP core is mostly built. Pedagogical features are functional, while production
readiness, permission audit, cache/performance, external access integration,
deployment, and operational hardening still need work.

Done / mostly done:

- project documentation foundation;
- Jitsi settings and live class records;
- teacher dashboard;
- WhatsApp/Evolution preparation and logs;
- student access control;
- `Minha Aula`;
- educational materials;
- ENEM question bank;
- exercise lists;
- student answers;
- student progress;
- operational/admin dashboard;
- embedded live room;
- design system documentation;
- security policy;
- `AGENTS.md` instructions.

Needs refinement:

- paused mobile student portal;
- production Jitsi decision validation after the decision foundation;
- WhatsApp real sending/retry foundation;
- permission audit;
- cache/performance strategy;
- deployment readiness foundation and production validation.

## 5. Phase 0 — Foundation

Status: Done / Mostly done.

Goal: create a safe customization foundation for Frappe LMS.

Deliverables:

- `AGENTS.md`;
- `SECURITY.md`;
- `ROADMAP.md`;
- design system documentation;
- roles/permissions documentation;
- architecture and UX flow documentation;
- custom app boundaries.

Definition of Done:

- custom work stays inside `melura_lms`;
- core Frappe/LMS/Frappe UI/Jitsi are not modified;
- security and design rules are documented;
- future agents know which docs to read.

## 6. Phase 1 — Pedagogical Core

Status: Done / Mostly done.

Goal: build the main LMS experience for student, teacher, and operational admin.

Deliverables:

- Bruce Student Access;
- `Minha Aula`;
- educational materials;
- ENEM question bank;
- exercise lists;
- student answers;
- student progress;
- teacher dashboard;
- operational/admin dashboard.

Definition of Done:

- students with `Ativo` access can see permitted content;
- `Pendente`, `Bloqueado`, and `Expirado` do not unlock content;
- teacher/admin have operational visibility;
- backend permissions protect sensitive flows.

## 7. Phase 2 — Live Classes and Communication

Status: Functional, needs production hardening.

Goal: support live classes and communication around classes.

Deliverables:

- Jitsi room generation;
- live class records;
- embedded live room;
- external Jitsi fallback;
- WhatsApp/Evolution API preparation;
- notification logs;
- manual resend flow where applicable.

Definition of Done:

- teacher can start/open class without technical steps;
- student opens the correct class from the LMS;
- Jitsi data is returned only after backend permission checks;
- WhatsApp provider secrets are never exposed to frontend;
- failed communication attempts are logged.

Remaining work:

- validate the production Jitsi decision foundation and choose the launch path:
  self-hosted Jitsi or Jitsi as a Service;
- refine WhatsApp retry history, provider callbacks, and automation after the
  real sending/retry foundation is validated.

## 8. Phase 3 — Security, Permissions, and Reliability

Status: Planned.

Goal: harden the product before production use.

Priority work:

- permission audit;
- route/API authorization review;
- student access edge cases;
- blocked/expired access testing;
- operational dashboard access review;
- log safety review;
- cache safety plan;
- backup/restore process foundation;
- production configuration checklist.

Definition of Done:

- students cannot access content outside their course/batch;
- students cannot access admin dashboards or APIs;
- teacher/admin actions are role-checked server-side;
- blocked/expired users cannot access pedagogical content;
- logs do not expose secrets or unnecessary personal data;
- backup and restore flow is documented and tested in staging/test.

## 9. Phase 4 — External Access Integration

Status: Started / Foundation added.

Goal: allow the external financial/commercial SaaS to update pedagogical access
safely.

Current foundation:

- signed, provider-neutral status webhook service;
- conservative external status mapping into Melura pedagogical statuses;
- updates existing `Bruce Student Access` records only;
- rejects overbroad financial/card/customer payload fields;
- no billing, checkout, subscription, CRM, blog, newsletter, or lead capture
  logic.

Scope:

- receive external access status updates;
- map external customer/plan references to Bruce Student Access;
- update only pedagogical status and opaque external IDs;
- keep billing, checkout, subscriptions, CRM, blog, newsletter, and financial
  logic outside this app.

Security rules:

- verify webhook signature or shared secret server-side;
- do not trust access/payment status from frontend;
- make webhook processing idempotent;
- log minimal correlation data;
- do not store card data or full financial payloads.

Definition of Done:

- external SaaS can activate, block, expire, or update pedagogical access;
- Frappe LMS app remains pedagogical only;
- webhook is verified and logged safely;
- access updates do not corrupt student state.

## 10. Phase 5 — Deployment and Production Readiness

Status: Future / Planned.

Goal: prepare the app for stable production use.

Priority work:

- domain and HTTPS;
- production bench setup;
- Redis/services validation;
- workers and scheduler;
- environment configuration;
- backup automation;
- restore testing;
- logging and monitoring;
- dependency update process;
- security checklist;
- deployment documentation.
- repository-only deployment documentation validation helper.

Definition of Done:

- production environment is documented;
- secrets stay outside Git;
- backups are created and restorable;
- workers and scheduler are running correctly;
- deployment does not depend on local-only assumptions.

## 11. Phase 6 — Student Mobile Experience

Status: Future / Paused.

Goal: create a polished mobile-first student experience without making students
feel they are inside Frappe Desk.

Current status:

- mobile student portal was started and paused because the visual/menu structure
  needs stronger design-system guidance.

Future scope:

- custom student portal;
- clean mobile navigation;
- large primary actions;
- no empty menus;
- no default Desk feeling;
- PWA shell when the portal is stable.

Definition of Done:

- student can access class, materials, lists, and progress comfortably on
  mobile;
- interface follows `docs/design-system.md`;
- user-facing UI remains in Brazilian Portuguese;
- permissions remain backend-enforced.

## 12. Prioritized Backlog

| Priority | Item | Status | Why it matters | Dependencies |
| -------- | ---- | ------ | -------------- | ------------ |
| P0 | Permission audit | Planned | Confirms students, teachers, and admins only access their allowed scope. | Current DocTypes, pages, and APIs |
| P0 | Cache/performance basics | Planned | Improves reliability without weakening access control. | Permission model and cache key plan |
| P0 | Deployment readiness | Foundation added | Removes local-only assumptions before production use. | Production bench checklist |
| P0 | Backup/restore validation | Foundation added | Protects operational and student data from unrecoverable loss. | Production storage and restore process |
| P1 | External student status integration | Future / Planned | Keeps pedagogical access synchronized with the external SaaS. | Signed webhook or protected integration endpoint |
| P1 | Financial SaaS webhook for pedagogical access only | Future / Planned | Allows activation/block/expiration updates without importing billing logic. | External SaaS contract and webhook secret |
| P1 | Real WhatsApp sending/retry flow | Started / Foundation added | Turns prepared communication flows into reliable operations. | Provider configuration, retry history, and provider callback policy |
| P1 | Production Jitsi decision | Started / Foundation added | Chooses the right live-class hosting and access-control path. | Production requirements, budget, and privacy review |
| P2 | Refactor paused mobile student portal | Future / Paused | Gives students a polished mobile-first experience. | Design system guidance and portal scope |
| P2 | PWA shell | Future | Improves mobile access after the web portal is stable. | Stable student portal |
| P2 | User documentation with screenshots | Future | Helps teacher/admin operate the product consistently. | Stable screens |
| P2 | Support panel | Future | Gives operation a focused place to resolve common access/content issues. | Permission audit and operational workflows |
| P3 | Capacitor app shell | Future | Native wrapper only after mobile web/PWA proves stable. | Stable PWA |
| P3 | Advanced analytics | Future | Adds deeper insight after reliable pedagogical data exists. | Clean data model and production usage |
| P3 | AI-assisted study/support features | Future | Adds guided support after core flows are stable and safe. | Data/privacy rules and support process |
| P3 | Multi-product theming | Future | Supports future product variants without breaking this LMS. | Tokenized design system |

## 13. Out of Scope for This Frappe App

- full financial secretary system;
- checkout;
- subscription billing;
- split payment logic;
- banking reconciliation;
- invoice/fiscal logic;
- CRM;
- blog;
- newsletter;
- lead capture;
- advanced marketing automation;
- marketplace;
- changing Frappe/LMS/Frappe UI/Jitsi core directly;
- native mobile app before the mobile web/PWA experience is stable.

Some of these may exist in a separate external SaaS, but they should not be
implemented inside `melura_lms` by default.

## 14. Decision Log

| Date | Decision | Reason |
| ---- | -------- | ------ |
| 2026-06-02 | Keep `melura_lms` as pedagogical LMS core. | The app should focus on teaching, access, materials, exercises, progress, live classes, and operation. |
| 2026-06-02 | Keep financial/commercial workflows in external SaaS. | Billing, checkout, subscriptions, CRM, blog, newsletter, and financial operations are outside this Frappe app. |
| 2026-06-02 | Use Frappe extension points instead of modifying core. | Extension keeps Frappe LMS upgrade-friendly. |
| 2026-06-02 | Keep user-facing UI in Brazilian Portuguese. | Students, teacher, and admins operate the product in Portuguese. |
| 2026-06-02 | Keep internal docs in English. | English documentation improves maintainability for future contributors and agents. |
| 2026-06-02 | Pause mobile portal until design system is stronger. | The mobile student experience needs stronger visual/menu guidance before continuing. |
| 2026-06-02 | Use `meet.jit.si` for development/testing, evaluate production Jitsi later. | Development can move with a safe default while production access control is decided separately. |
| 2026-06-03 | Add production Jitsi decision foundation. | Early production should compare self-hosted Jitsi and Jitsi as a Service before treating public `meet.jit.si` as anything beyond development/demo fallback. |

## 15. Related Documents

- `AGENTS.md`
- `SECURITY.md`
- `README.md`
- `docs/design-system.md`
- `docs/roles-permissions.md`
- `docs/student-access-integration.md`
- `docs/jitsi-integration.md`
- `docs/integrations/jitsi-production-decision.md`
- `docs/ux-flows.md`
- `docs/testing-checklist.md`
- `docs/deployment/00-overview.md`
- `docs/backup-restore/00-overview.md`
- `docs/kpis-admin.md`
