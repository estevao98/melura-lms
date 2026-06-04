# Permission Audit Report

This report is based on an implementation scan of `melura_lms` for the
`feat/privacy-permission-audit` foundation. It is implementation-facing and
should be updated as permissions, DocTypes, pages, or integrations change.

No core Frappe, Frappe LMS, Frappe UI, payments, or Jitsi Meet files were
modified for this audit foundation.

## Current Custom Pages

| Page | Files | Roles In Page JSON | Main Data Flow |
| --- | --- | --- | --- |
| `minha-aula` | `melura_lms/melura_lms/page/minha_aula/` | `LMS Student`, `System Manager`, `Moderator` | Student dashboard for next class, materials, exercise lists, progress |
| `bruce-live-room` | `melura_lms/melura_lms/page/bruce_live_room/` | `LMS Student`, `Professor`, `System Manager`, `Moderator`, `Batch Evaluator`, `Course Creator`, `Administrador LMS`, `LMS Admin`, `Admin operacional` | Embedded Jitsi room context after backend authorization |
| `bruce-professor-dashboard` | `melura_lms/melura_lms/page/bruce_professor_dashboard/` | `System Manager`, `Moderator`, `Batch Evaluator` | Teacher/academic operations dashboard |
| `bruce-operational-dashboard` | `melura_lms/melura_lms/page/bruce_operational_dashboard/` | `System Manager`, `Administrador LMS`, `Admin operacional`, `LMS Admin` | Operational aggregates, content counts, active/inactive student indicators |

## Current Services

- `melura_lms.services.student_access`: central student access service, student
  content filters, progress, answer saving, and permission hooks.
- `melura_lms.services.whatsapp`: WhatsApp preview/send/test helpers, Evolution
  API/n8n provider calls, recipient resolution, notification logs, provider
  response redaction.

## Whitelisted Methods Found

Student access and progress:

- `melura_lms.services.student_access.get_progress_for_current_student`
- `melura_lms.services.student_access.get_class_progress_summary`
- `melura_lms.services.student_access.get_permitted_enem_questions_for_current_student`
- `melura_lms.services.student_access.get_exercise_list_for_current_student`
- `melura_lms.services.student_access.save_student_answer`

Student page:

- `melura_lms.melura_lms.page.minha_aula.minha_aula.get_student_dashboard_data`
- `melura_lms.melura_lms.page.minha_aula.minha_aula.get_student_materials`
- `melura_lms.melura_lms.page.minha_aula.minha_aula.get_student_exercise_lists`

Live room:

- `melura_lms.melura_lms.page.bruce_live_room.bruce_live_room.get_live_room_context`

Professor dashboard:

- `melura_lms.melura_lms.page.bruce_professor_dashboard.bruce_professor_dashboard.get_next_live_class`
- `melura_lms.melura_lms.page.bruce_professor_dashboard.bruce_professor_dashboard.get_dashboard_data`

Operational dashboard:

- `melura_lms.melura_lms.page.bruce_operational_dashboard.bruce_operational_dashboard.get_dashboard_data`

Live class and notice logs:

- `melura_lms.melura_lms.doctype.bruce_live_class.bruce_live_class.start_live_class`
- `melura_lms.melura_lms.doctype.bruce_live_class_notice_log.bruce_live_class_notice_log.record_live_class_notice_event`
- `melura_lms.melura_lms.doctype.bruce_live_class_notice_log.bruce_live_class_notice_log.get_live_class_notice_logs`

WhatsApp:

- `melura_lms.services.whatsapp.send_live_class_link`
- `melura_lms.services.whatsapp.preview_live_class_link`
- `melura_lms.services.whatsapp.test_evolution_configuration`
- `melura_lms.services.whatsapp.send_evolution_test_message`

## Permission Hooks Found

`melura_lms/hooks.py` defines permission query conditions and `has_permission`
hooks for:

- `Bruce Live Class`
- `Bruce Educational Material`
- `Bruce ENEM Question`
- `Bruce Exercise List`

These hooks restrict `LMS Student` users by active `Bruce Student Access`
records and course/batch scope. Users with unrestricted roles such as
`System Manager`, `Moderator`, `Batch Evaluator`, and `Course Creator` are not
restricted by these student filters.

## DocTypes That Should Be Protected

Highest sensitivity:

- `Bruce Student Access`: access status, course/batch scope, external opaque
  reference, notes.
- `Bruce Student Answer`: student, selected option, correctness, timestamp.
- `Bruce WhatsApp Notification Log`: recipient name/phone, message, status,
  provider response, error message.
- `Bruce Evolution Settings`: provider mode, API URL, n8n webhook URL, and
  credential note. API key is expected outside this DocType.
- `Bruce Live Class`: Jitsi room name, meeting URL, instructor, class scope.

Pedagogical sensitivity:

- `Bruce Educational Material`
- `Bruce ENEM Question`
- `Bruce Exercise List`
- `Bruce Live Class Notice Log`
- `Bruce WhatsApp Message Template`
- `Bruce Jitsi Settings`

Child table sensitivity:

- `Bruce ENEM Question Alternative`
- `Bruce Exercise List Item`

## Likely Student-Facing Data Flows

- `Minha Aula` calls backend methods for access status, next permitted live
  class, recent materials, exercise lists, and own progress.
- ENEM question list returns published, scoped questions and alternatives, but
  omits `correct_option` and `commented_resolution`.
- Exercise list detail validates current student access before returning list
  and visible questions.
- Student answer submission validates current active access, list visibility,
  question membership, and computes correctness server-side.
- Live-room context validates login, class status, room data, and staff/student
  permission before returning Jitsi domain, room name, and fallback URL.

## Admin / Teacher-Only Flows

- Operational dashboard aggregates student access counts, content counts,
  answer counts, average accuracy, and inactive active students after explicit
  role validation.
- Professor dashboard rejects guests and normal students through an explicit
  backend role check before returning next/week live classes, notice logs, or
  class progress. Class visibility still uses Frappe list permissions and the
  progress helper still returns data only for progress manager roles.
- Starting a live class calls `doc.check_permission("write")` before changing
  status to `Ao vivo`.
- WhatsApp preview/send loads the live class and calls
  `doc.check_permission("write")`.
- Evolution configuration test requires `Bruce Evolution Settings` read
  permission.
- Evolution test send requires `Bruce Evolution Settings` write permission.
- Live class notice log methods call `doc.check_permission("read")` on the
  related live class.

## Permission Risks Found

- `bruce-professor-dashboard` now has an explicit backend role gate for page
  methods. It still relies on Frappe list permissions for detailed class
  visibility rather than a custom instructor-scope filter in the page
  controller, so it needs integration tests against a real site role setup.
- `Bruce Educational Material` and `Bruce Exercise List` grant read permission
  to `LMS Student`; the permission hooks restrict records, but field-level
  exposure in Desk list/form views should be manually verified.
- `Bruce Live Class` grants read permission to `LMS Student`; hooks restrict
  records, but the form/list exposure of `room_name` and `meeting_url` should
  be verified. The safer student path is `bruce-live-room`, which has backend
  checks.
- `Bruce WhatsApp Notification Log` grants read permission to `Batch Evaluator`.
  Confirm that this role is operationally trusted to see recipient names,
  phones, message bodies, errors, and provider response summaries.
- `Bruce Live Class Notice Log` grants read permission to `Batch Evaluator`.
  Confirm that notice messages never include secrets or excessive personal data.
- `Bruce Student Access.notes` can become a privacy risk if operators paste
  financial/commercial payloads, sensitive context, or support transcripts.
- Direct `Bruce Student Answer` writes now recompute `is_correct` on validation
  from the linked question's `correct_option`. This avoids trusting caller
  supplied correctness, including backend/API writes that bypass the student
  page service.
- Future external SaaS webhook is not implemented yet. Webhook spoofing,
  overbroad payloads, and unverified access activation remain future risks.
- Backup, framework log, file storage, and production infrastructure retention
  were not audited in code because they are outside this app folder.

## Tests Already Existing

Priority coverage already present:

- LMS Student cannot access operational dashboard data:
  `melura_lms/melura_lms/page/bruce_operational_dashboard/test_bruce_operational_dashboard.py`
  has `test_common_student_cannot_access_operational_dashboard`.
- Blocked/pending access does not unlock protected content:
  `melura_lms/services/test_student_access.py` covers blocked active status,
  no materials/questions/lists for no active records, and locked progress.
- Student identity comes from `frappe.session.user`:
  `test_active_student_progress_uses_only_current_student` asserts answer
  queries use the logged student; answer save tests assert `student_user` is
  set from session.
- Student answer correctness is server-computed:
  `test_correct_student_answer_is_marked_correct` and
  `test_wrong_student_answer_is_marked_wrong`.
- WhatsApp methods do not expose provider secrets in configuration validation:
  `test_validate_evolution_configuration_requires_api_key_without_exposing_value`
  and `test_validate_evolution_configuration_returns_valid_without_external_call`.
- Live room context requires backend permission:
  `melura_lms/melura_lms/page/bruce_live_room/test_bruce_live_room.py` covers
  active student access, blocked student denial, another-batch denial,
  professor own-room access, and admin access.
- Jitsi room names are server-generated with a secure token:
  `melura_lms/melura_lms/doctype/bruce_live_class/test_bruce_live_class.py`.
- WhatsApp disabled settings do not make external calls and create failed logs:
  `melura_lms/services/test_whatsapp.py`.

## Tests Added Or Changed In This Feature

- `melura_lms/melura_lms/page/bruce_professor_dashboard/test_bruce_professor_dashboard.py`
  now covers that `LMS Student` cannot call professor dashboard data methods
  and that `Professor` is an allowed backend role.
- `melura_lms/services/test_student_access.py` now covers expired access records,
  inactive answer submission blocking before protected content lookup, and the
  fact that `save_student_answer` does not accept frontend `student_user`.
- `melura_lms/melura_lms/doctype/bruce_student_answer/test_bruce_student_answer.py`
  covers DocType-level server-computed answer correctness and rejection when
  the linked question has no answer key.
- `melura_lms/services/test_whatsapp.py` now covers nested provider response
  redaction for API keys, authorization headers, and tokens.

## Cache Safety Update

The `feat/cache-and-performance-basics` foundation adds a small cache helper in
`melura_lms.services.cache` and documents cache rules in
`docs/performance/cache-and-performance-basics.md`.

Implemented cache behavior:

- cache keys use the `melura_lms:v1` namespace;
- user-scoped key construction requires `frappe.session.user`;
- obvious sensitive key token names such as `api_key`, `token`, `password`,
  `authorization`, and `secret` are rejected;
- only non-secret Jitsi public settings (`domain` and `room_prefix`) are cached
  globally for a short TTL;
- saving `Bruce Jitsi Settings` invalidates the Jitsi settings cache key.

Intentionally uncached permission-sensitive paths:

- `Minha Aula` dashboard context;
- student access status;
- student progress;
- student answers;
- exercise list context for a student;
- live-room context and Jitsi room payloads for a student;
- WhatsApp recipient resolution, previews, provider configuration, sends, and
  notification logs;
- operational dashboard aggregates that include inactive student identity.

Open cache risks:

- any future student-specific cache must include `frappe.session.user` and the
  resolved backend permission scope in the cache key;
- admin aggregate caching still needs a separate privacy review before it can
  include anything beyond anonymous counts;
- production Redis inspection and retention controls remain environment tasks
  outside this repository.

## Recommended Next Tests

- Expired access windows specifically for materials, questions, lists,
  progress, and live-room context beyond the added access-status unit coverage.
- Direct student calls to `save_student_answer` for each explicit inactive
  status value (`Pendente`, `Bloqueado`, and `Expirado`) in a real Frappe site
  permission context.
- Student direct Desk read/list/form access for `Bruce Live Class`,
  `Bruce Educational Material`, `Bruce ENEM Question`, and `Bruce Exercise
  List` in a real Frappe site.
- Professor dashboard class scope with real instructor and non-instructor users.
- Provider response redaction for broader mixed-case sensitive key aliases
  beyond the nested API key, authorization, and token cases now covered.
- Operational admin role matrix for each allowed admin role.
- Future external SaaS webhook invalid signature, replay/idempotency, forbidden
  payload fields, and no financial payload persistence.

## Open Risks

- Legal bases, controller/operator roles, privacy contact, and public privacy
  policy are not defined in code and need human/legal decisions.
- Retention periods are not implemented and remain a draft policy question.
- Backups, framework logs, and production infrastructure controls remain outside
  this repository-level audit.
- The future external SaaS integration needs a separate security design before
  implementation.
- Minor/guardian handling is undecided.
- Field-level exposure in Frappe Desk should be reviewed before production for
  every student-readable DocType.
