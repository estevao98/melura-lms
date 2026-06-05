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
- Preferred Desk routes now use Melura aliases:
  `/app/melura-live-room/<class>`, `/app/melura-professor-dashboard`, and
  `/app/melura-operational-dashboard`.
- `/app/bruce-live-room/<class>`, `/app/bruce-professor-dashboard`,
  `/app/bruce-operational-dashboard`, and other `bruce_*` route/module paths
  remain temporarily for compatibility with existing links and internal module
  paths.
- `Bruce Live Class`, whose visible label should be Aula ao vivo.
- `Bruce Student Access`, whose visible label should be Acesso do aluno or
  Acessos dos alunos and which remains the technical source of pedagogical
  access until a DocType migration is planned.
- `Bruce Evolution Settings`, whose visible label should be Configurações de
  WhatsApp and which remains the technical WhatsApp settings DocType.
- `Bruce WhatsApp Message Template`, whose visible label should be Modelo de
  mensagem or Modelos de mensagem.
- `Bruce WhatsApp Notification Log`, whose visible label should be Log de
  WhatsApp or Logs de WhatsApp.
- `Bruce Live Class Notice Log`, whose visible label should be Histórico da
  aula ao vivo.
- `Bruce Educational Material`, whose visible label should be Material
  didático or Materiais didáticos.
- `Bruce ENEM Question`, whose visible label should be Questão ENEM or Questões
  ENEM.
- `Bruce Exercise List`, whose visible label should be Lista de exercícios or
  Listas de exercícios.
- `Bruce Student Answer`, whose visible label should be Resposta do aluno or
  Respostas dos alunos.
- `Bruce Jitsi Settings`, `bruce_jitsi_settings`, `section_break_jitsi`,
  `column_break_jitsi`, and old cache-key constants, whose visible label should
  be Configuração legada de vídeo because removing or renaming them requires a
  data migration and fixture cleanup.
- Historical filenames such as `docs/jitsi-integration.md` and
  `docs/integrations/jitsi-production-decision.md`, kept as obsolete pointers
  for old links.

For this phase, keep those internal identifiers for compatibility. Do not expose
legacy personal names or old video-provider names in new visible product copy.
Translations in `melura_lms/translations/pt-BR.csv` map the legacy technical
DocType names and common generated Desk labels to neutral Portuguese labels
where Frappe applies translations. These translations are UI-only and must not
be used for technical code behavior. A future migration can rename technical
DocTypes, tables, Python modules, folders, and routes with patches, redirects,
fixture updates, and regression tests.

The `Melura` Workspace intentionally links to some legacy technical DocTypes
while displaying neutral labels such as `Aulas ao vivo`, `Configurações de
WhatsApp`, and `Acessos dos alunos`. Dashboard Workspace links should prefer
the Melura page aliases. This avoids a risky technical rename while giving users
a Melura-branded navigation entry in Frappe Desk.

The `feat/melura-desk-form-polish` phase adds Desk UI polish only. It keeps
`Bruce Live Class` as the technical DocType and preserves `/app/bruce-live-class`
and the older `/app/bruce-*` page routes, while generated user-facing links use
the preferred Melura aliases. The Aula ao vivo form and listview have lightweight
JavaScript title overrides, and translation rows cover common Frappe-generated
labels such as `Bruce Live Class`, `Bruce Live Class List`,
`Add Bruce Live Class`, and `New Bruce Live Class`.

Remaining visible debt is expected in Frappe-native surfaces that derive labels
directly from DocType metadata or route names before custom JavaScript or
translations can run. This includes some breadcrumbs, browser routes, permission
screens, metadata dialogs, export/import tools, developer utilities, and any
third-party Desk component that renders raw DocType names. Those are accepted
until a dedicated technical rename feature plans database migrations, fixture
updates, redirects, and regression coverage.
