# Role Access Matrix

This matrix describes privacy and permission boundaries for the current
pedagogical LMS core and the planned external access integration. It should be
kept aligned with `docs/roles-permissions.md`, `SECURITY.md`, and the hooks in
`melura_lms/hooks.py`.

## Role Boundaries

| Role | Can Access | Must Not Access | Sensitive Assets To Protect | Backend Checks Expected | Future Tests |
| --- | --- | --- | --- | --- | --- |
| Student / LMS Student | Own `Minha Aula` dashboard; published materials, ENEM questions, exercise lists, own progress, and live-room context only when `Bruce Student Access` is `Ativo` and in course/batch scope | Operational dashboard; WhatsApp logs/settings; other students' answers/progress; unpublished/internal materials; answer keys in list payloads; Jitsi room data outside scope | `Bruce Student Access`; `Bruce Live Class`; `Bruce Educational Material`; `Bruce ENEM Question`; `Bruce Exercise List`; `Bruce Student Answer`; `bruce-live-room`; `minha-aula` | Use `frappe.session.user`; reject Guest; require `Ativo`; enforce course/batch scope; return locked progress for non-active status; compute answer correctness server-side | Direct API calls as LMS Student for each whitelisted method; blocked/expired/pending status matrix for live room, materials, questions, lists, answers, progress |
| Professor / instructor role | Professor dashboard; own or assigned live class operations; relevant class notices; progress summaries only where the role is in the progress manager set | Evolution API keys; global provider secrets; unrelated courses/batches unless explicitly authorized; operational dashboard unless also assigned admin role; financial/commercial data | `bruce-professor-dashboard`; `Bruce Live Class`; `Bruce Live Class Notice Log`; WhatsApp preview/send methods | Rely on Frappe DocType permissions for class list/read/write; use live-room staff check for instructor; keep progress summary guarded by manager roles | Test professor cannot open another instructor's room unless another permitted role grants it; test professor dashboard data respects DocType permissions in integration environment |
| Operational admin | Operational dashboard aggregates; live class operational status; content counts; inactive student alerts; WhatsApp operational logs when allowed | Provider secrets; full financial payloads; unrestricted system maintenance; raw production dumps; student content outside operational need | `bruce-operational-dashboard`; `Bruce Student Access`; `Bruce Student Answer`; `Bruce WhatsApp Notification Log`; `Bruce Live Class Notice Log` | Explicit role gate in operational dashboard; return only needed aggregate/detail fields; avoid secrets and full provider payloads | Tests for each operational role; tests that LMS Student, Guest, and unrelated roles are denied |
| System Manager / Administrator | Technical maintenance, migrations, app configuration, emergency recovery, high-privilege diagnostics | Routine teaching or daily operations as `Administrator`; committing secrets or dumps; using admin power to bypass product permission design without audit | All custom DocTypes, settings, logs, hooks, patches, site config outside Git | Frappe built-in permissions plus operational discipline; secrets must stay in environment/site config, not frontend or repository | Smoke tests for settings methods; manual review that `Administrator` is not required for teacher operations |
| Integration/bot user | Future protected automation: WhatsApp callbacks, n8n/Evolution status updates, external access-status webhooks, scheduled jobs with minimal scope | Human Desk screens; broad admin actions; user/course/batch edits outside integration contract; secrets in frontend; financial payload storage | Future webhook endpoints; `Bruce WhatsApp Notification Log`; `Bruce Student Access.external_reference`; notification status updates | Authenticate origin; verify webhook signature/secret; idempotent writes; minimal payload; scoped technical credential; safe logs | Tests for invalid signature, replay/idempotency, forbidden fields, and no payload/secret logging |
| Future external financial SaaS | Future server-to-server update of pedagogical access status and opaque references after verification | Checkout/billing implementation inside Frappe; direct student UI authorization; card data; subscription internals; CRM/lead/newsletter data; full financial payloads | Future external access endpoint; `Bruce Student Access` status/source/external reference fields | Verify webhook; map student/course/batch server-side; accept only allowed statuses; reject billing data; log minimal correlation | Contract tests for payload schema, invalid status, spoofing, idempotency, and no commercial data persistence |

## Sensitive Methods And Pages

Student-facing or student-reachable methods/pages:

- `melura_lms.melura_lms.page.minha_aula.minha_aula.get_student_dashboard_data`
- `melura_lms.melura_lms.page.minha_aula.minha_aula.get_student_materials`
- `melura_lms.melura_lms.page.minha_aula.minha_aula.get_student_exercise_lists`
- `melura_lms.services.student_access.get_progress_for_current_student`
- `melura_lms.services.student_access.get_permitted_enem_questions_for_current_student`
- `melura_lms.services.student_access.get_exercise_list_for_current_student`
- `melura_lms.services.student_access.save_student_answer`
- `melura_lms.melura_lms.page.bruce_live_room.bruce_live_room.get_live_room_context`

Teacher/admin methods/pages:

- `melura_lms.melura_lms.page.bruce_professor_dashboard.bruce_professor_dashboard.get_next_live_class`
- `melura_lms.melura_lms.page.bruce_professor_dashboard.bruce_professor_dashboard.get_dashboard_data`
- `melura_lms.melura_lms.page.bruce_operational_dashboard.bruce_operational_dashboard.get_dashboard_data`
- `melura_lms.melura_lms.doctype.bruce_live_class.bruce_live_class.start_live_class`
- `melura_lms.services.student_access.get_class_progress_summary`
- `melura_lms.services.whatsapp.preview_live_class_link`
- `melura_lms.services.whatsapp.send_live_class_link`
- `melura_lms.melura_lms.doctype.bruce_live_class_notice_log.bruce_live_class_notice_log.record_live_class_notice_event`
- `melura_lms.melura_lms.doctype.bruce_live_class_notice_log.bruce_live_class_notice_log.get_live_class_notice_logs`

Settings/test methods:

- `melura_lms.services.whatsapp.test_evolution_configuration`
- `melura_lms.services.whatsapp.send_evolution_test_message`

## Protected DocTypes

High-priority protection:

- `Bruce Student Access`
- `Bruce Student Answer`
- `Bruce Live Class`
- `Bruce Educational Material`
- `Bruce ENEM Question`
- `Bruce Exercise List`
- `Bruce WhatsApp Notification Log`
- `Bruce Live Class Notice Log`
- `Bruce Evolution Settings`
- `Bruce Jitsi Settings`
- `Bruce WhatsApp Message Template`

Child tables that inherit parent sensitivity:

- `Bruce ENEM Question Alternative`
- `Bruce Exercise List Item`

## Backend Checks Expected

- Student identity comes from `frappe.session.user`, never trusted frontend
  `student_user`.
- Active access means only `Ativo` and within date bounds.
- `Pendente`, `Bloqueado`, and `Expirado` do not unlock classes, materials,
  questions, exercise lists, answers, or progress metrics.
- Course/batch scope is derived from `Bruce Student Access`.
- Live-room context validates login, class status, room data, URL shape, and
  staff/student permission before returning Jitsi data.
- Student question payloads exclude answer keys and commented resolutions.
- Student answer correctness is computed server-side.
- Operational dashboards reject normal students and guests.
- WhatsApp preview/send methods use backend permissions and must not return or
  log provider secrets.
- Settings methods must check `Bruce Evolution Settings` read/write permission.

## Notes For Future Tests

- Add integration tests with real Frappe permissions for Desk list/form access
  to student-readable DocTypes.
- Add tests for expired access windows, not only blocked/pending status.
- Add tests for professor/instructor scope on `bruce-professor-dashboard` once
  instructor ownership rules are finalized.
- Add webhook tests when the external SaaS access integration is implemented.
- Add tests for provider response redaction with nested sensitive keys.
