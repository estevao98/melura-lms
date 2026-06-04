# Naming Debt

Melura is the public product name. User-facing labels, messages, pages, and
documentation should use Melura or neutral Portuguese names such as `Aula ao
vivo`, `Painel do professor`, `Painel operacional`, and `Configurações de
WhatsApp`.

Some internal legacy identifiers still contain the old personal name or old
video-provider terminology. This includes DocType names, Python classes, module
paths, routes, fieldnames, cache keys, fixture file paths, tests that exercise
legacy compatibility, and historical documentation filenames that would require
a careful migration to rename safely.

Known compatibility names kept for this phase:

- `Bruce ...` DocTypes and related Python/JavaScript class names.
- `/app/bruce-live-room/<class>` and other `bruce_*` route/module paths.
- `Bruce Student Access`, because it remains the technical source of
  pedagogical access until a DocType migration is planned.
- `Bruce Evolution Settings`, because WhatsApp configuration still uses this
  technical DocType.
- `Bruce Jitsi Settings`, `bruce_jitsi_settings`, `section_break_jitsi`,
  `column_break_jitsi`, and old cache-key constants, because removing or
  renaming them requires a data migration and fixture cleanup.
- Historical filenames such as `docs/jitsi-integration.md` and
  `docs/integrations/jitsi-production-decision.md`, kept as obsolete pointers
  for old links.

For this phase, keep those internal identifiers for compatibility. Do not expose
legacy personal names or old video-provider names in new visible product copy.
A future migration can rename technical DocTypes and routes with patches,
redirects, fixture updates, and regression tests.

The `Melura` Workspace intentionally links to some legacy technical DocTypes
and routes while displaying neutral labels such as `Aulas ao vivo`,
`Configurações de WhatsApp`, `Acessos dos alunos`, `Painel do professor`, and
`Painel operacional`. This avoids a risky technical rename while giving users a
Melura-branded navigation entry in Frappe Desk.
