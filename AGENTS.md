# AGENTS.md — melura_lms

## 1. Mission

`melura_lms` customizes Frappe Learning/LMS for Professor Bruce's online
ENEM / Ciências Humanas pedagogical operation. AI coding agents must preserve
architecture, security, maintainability, and product consistency while keeping
the app upgrade-friendly.

Correct permissions and safe data boundaries matter more than speed. The
preferred path is extension, not core modification.

The product must remain simple for:

- students;
- Professor Bruce;
- operational admins.

## 2. Product Boundary

This app handles pedagogical LMS features: live classes, embedded Jitsi rooms,
teacher and operational dashboards, `Minha Aula`, Bruce Student Access,
educational materials, ENEM questions, exercise lists, student answers,
progress, WhatsApp notification preparation, protected Evolution API / n8n
flows, logs, and Portuguese user-facing interfaces.

External billing/financial SaaS handles checkout, subscriptions, CRM, lead
capture, blog, newsletter, financial operations, and commercial flows.

Do not bring financial SaaS responsibilities into this Frappe LMS app by
default. Do not implement billing, checkout, or subscription logic here unless
the user explicitly asks for a scoped integration task. A future external SaaS
integration may update pedagogical access status and opaque references, but it
must not turn this app into the financial system.

## 3. Non-Negotiable Rules

- Do not modify `frappe/`, `lms/`, `frappe-ui/`, or `jitsi-meet/`.
- Work inside `apps/melura_lms` unless explicitly instructed otherwise.
- Do not bypass authentication or authorization.
- Do not trust frontend data for sensitive decisions.
- Do not expose secrets, tokens, API keys, passwords, provider credentials,
  private data, or student data.
- Do not commit `.env`, `site_config.json`, `common_site_config.json`, database
  dumps, backups, logs with secrets, or real student data.
- Do not use `Administrator` as the normal operational teacher account.
- Do not make broad unrelated refactors.
- Do not add large dependencies without justification.
- Do not silently ignore failing tests or validation errors.
- Do not delete existing tests unless truly obsolete and explained.
- Do not commit, merge, delete branches, or push unless explicitly asked.

## 4. Required Reading Before Work

Use this file as the routing layer. Do not duplicate long policy details here;
the docs are the source of detail.

- `SECURITY.md`: security policy, secrets, authorization, and vulnerability
  rules.
- `ROADMAP.md`: product direction and scope boundaries.
- `docs/design-system.md`: UI, UX, visual, and language rules.
- `docs/roles-permissions.md`: authorization and account separation rules.
- `docs/student-access-integration.md`: Bruce Student Access rules.
- `docs/jitsi-integration.md`: live class and Jitsi rules.
- `docs/ux-flows.md`: teacher, student, admin, Jitsi, WhatsApp, and progress
  flows.
- `docs/testing-checklist.md`: manual and automated validation guidance.
- `docs/kpis-admin.md`: KPI guidance when populated.

## 5. Architecture Rules

- Use Frappe extension points.
- Prefer custom DocTypes, hooks, pages, whitelisted methods, scripted
  permissions, fixtures, and patches/migrations when needed.
- Avoid editing core Frappe LMS files.
- Avoid monkey-patching without strong justification.
- Avoid duplicate systems that fight Frappe patterns.
- Keep business logic out of frontend-only code.
- Use backend methods for sensitive logic.
- Keep custom CSS and JS scoped to `melura_lms`.

The preferred path is extension, not core modification.

## 6. Security and Permission Rules

- Validate every sensitive operation server-side.
- Treat frontend checks as UX helpers only.
- Derive the current user from `frappe.session.user`.
- Do not accept `student_user` from the frontend for authorization.
- Do not allow frontend parameters to decide course, batch, or access scope.
- Validate role and ownership before returning protected data.
- Return only fields needed by the UI.
- Do not expose stack traces, payloads, tokens, API keys, provider secrets, or
  private configuration.
- Log sensitive operations safely, with enough context for support and without
  leaking secrets.

## 7. Student Access Rules

`Bruce Student Access` is the source of pedagogical access.

Allowed statuses:

- `Ativo`
- `Pendente`
- `Bloqueado`
- `Expirado`

Rules:

- Only `Ativo` unlocks pedagogical content.
- `Pendente`, `Bloqueado`, and `Expirado` must not unlock classes, materials,
  questions, exercise lists, answers, or progress metrics.
- Student pages must validate the logged-in user on the backend.
- Student content must be scoped to the allowed course and/or batch.
- Future external financial SaaS integration may update pedagogical status and
  opaque references, but must not bring billing logic into this app.

## 8. Role and Account Rules

- Do not use `Administrator` as the normal teacher account.
- Separate technical/admin maintenance, teacher, operational admin,
  integration/bot user, and student accounts.
- Operational dashboards and aggregate APIs must reject normal students.
- Teacher/admin actions must validate role server-side.
- Permission behavior changes must update `docs/roles-permissions.md`.

## 9. UI and Design System Rules

- Follow `docs/design-system.md`.
- Use Frappe UI when it fits.
- Use Frappe Desk for teacher and admin operational flows.
- Use custom mobile-first UI for student flows when Desk would feel
  administrative.
- User-facing product copy must be Brazilian Portuguese.
- Internal Markdown documentation must be English.
- Do not translate existing user-facing labels/statuses such as `Entrar na
  aula`, `Iniciar aula`, `Minha Aula`, `Painel do Professor`,
  `Painel Operacional`, `Ativo`, `Pendente`, `Bloqueado`, `Expirado`,
  `Agendada`, `Ao vivo`, `Encerrada`, and `Cancelada`.
- Every important screen needs loading, empty, and error states.
- Status must use text, not color alone.
- Destructive actions require confirmation.
- Do not create empty menus.
- Do not create one-off visual inconsistency.
- The student should not feel like they are using the administrative Desk.

## 10. Jitsi and Live Class Rules

- Generate `roomName` server-side.
- Use unique and non-predictable room names.
- Do not use plain course, batch, or date values as room names.
- Validate permission before returning Jitsi domain, room name, meeting URL, or
  embedded room data.
- Student access to `/app/bruce-live-room/<class>` must require active
  pedagogical access.
- External Jitsi link must be explicit fallback only.
- Do not automatically open `meet.jit.si` in another tab.
- Development/testing may use `meet.jit.si`.
- Future production should evaluate self-hosted Jitsi or Jitsi as a Service.

## 11. WhatsApp / Evolution / n8n Rules

- WhatsApp sending must happen through backend logic or a protected n8n flow.
- Never expose Evolution API keys to frontend.
- Never render provider secrets in HTML.
- Never log auth headers or full provider tokens.
- Record notification attempts with status, timestamp, short error summary, and
  related class/course/batch.
- Manual resend must require an authorized user.
- Preserve original failure history.

## 12. Data and Migration Rules

- Use Frappe DocType changes, fixtures, patches, or migrations as appropriate.
- Avoid destructive changes without an explicit plan.
- Check existing usages before renaming fields or changing behavior.
- Preserve data ownership and permission rules.
- Update related docs when behavior changes.

Relevant commands:

```bash
bench --site curso.localhost migrate
bench --site curso.localhost clear-cache
bench --site curso.localhost clear-website-cache
```

## 13. Validation Commands

Use real project commands, not generic commands copied from other stacks.

```bash
cd ~/Projetos/frappe-bench

./env/bin/python -m compileall apps/melura_lms/melura_lms
```

```bash
cd ~/Projetos/frappe-bench

./env/bin/python -m unittest discover \
  -s apps/melura_lms/melura_lms \
  -t apps/melura_lms \
  -p "test_*.py"
```

```bash
cd ~/Projetos/frappe-bench

bench --site curso.localhost clear-cache
bench --site curso.localhost clear-website-cache
bench build --app melura_lms
```

If validation cannot run because of sandbox or environment limits, explain it
clearly and list the exact commands for the user to run locally.

## 14. Git Rules

- Check git status before and after work.
- Keep changes focused.
- Do not include unrelated files.
- Do not commit secrets.
- Do not commit generated caches.
- Do not do broad formatting-only rewrites unless requested.
- Do not merge or push unless explicitly asked.

Use:

```bash
git status --short
git branch --show-current
```

And before final response:

```bash
git status --short
git --no-pager diff --stat
git --no-pager diff --name-only
```

Suggested commit style:

- `feat: short description`
- `fix: short description`
- `docs: short description`
- `chore: short description`
- `refactor: short description`

## 15. When to Ask vs When to Act

Act without asking when:

- the existing pattern is clear;
- documentation answers the question;
- the change is small and reversible;
- user intent is obvious.

Ask first when:

- the change affects security boundaries;
- the change affects student access rules;
- the change affects production deployment;
- the change could delete or migrate data destructively;
- the change would modify core Frappe/LMS/Frappe UI;
- the change would bring billing/financial logic into this Frappe app;
- multiple architectures are possible and the wrong choice would be costly.

## 16. Definition of Done

A task is complete only when:

- requested behavior is implemented or documentation updated;
- security-sensitive paths were considered;
- backend permission rules were preserved;
- student access rules were preserved;
- relevant validation was run or clearly listed;
- no unrelated files were changed;
- docs were updated when needed;
- final response lists changed files, validation, and remaining risks.
