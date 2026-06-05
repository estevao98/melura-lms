# Security Policy

## 1. Security Overview

This project customizes Frappe LMS for an academic Humanities/ENEM online
course operation. Frappe LMS remains the pedagogical core.
Billing, subscriptions, lead capture, blog, newsletter, CRM, and financial
operations are intentionally outside this Frappe app and belong to an external
SaaS.

The main security rule is simple:

> Secrets stay out of the repository, and sensitive operations are validated
> server-side.

Frontend visibility is not authorization. Hiding a button in Vue, Desk, or a
custom page does not protect the action. Every sensitive operation must be
protected by backend checks, and student access must be controlled through
student access records. The implementation still uses the legacy internal
DocType currently named `Bruce Student Access`.

Core principles:

- Never commit secrets.
- Never trust the frontend for authorization.
- Never expose API keys to the browser.
- Never let user-controlled parameters decide student, course, batch, or access
  scope.
- Every query that returns student content must be scoped to the authenticated
  user and the allowed course or batch.
- Logs must help debugging without becoming a sensitive data dump.

Project examples:

- `Minha Aula` must show only content allowed for the logged-in student.
- `Painel do Professor` and `Painel Operacional` must use backend permission
  checks before returning operational data.
- live classes and the live-room route must validate access before returning a
  Google Meet link.
- Materials, ENEM questions, exercise lists, student answers, and student
  progress APIs must be scoped by active student access. The current internal
  technical DocTypes still use legacy names such as `Bruce Educational
  Material`, `Bruce ENEM Question`, `Bruce Exercise List`, `Bruce Student
  Answer`, and `Bruce Student Access`.

## 2. Supported Versions

| Version / Branch | Supported |
| ---------------- | --------- |
| main / production | Yes |
| development branches | Limited |
| old local branches | No |

Only the latest production or `main` version receives security fixes by default.
Development branches may receive fixes while they are active. Abandoned feature
branches and old local branches are not security-supported.

## 3. Reporting a Vulnerability

Do not open a public GitHub issue for security vulnerabilities.

Use a private contact channel instead:

- `security@example.com`
- `contact@example.com`

These addresses are placeholders and must be replaced before public production
use.

Please include:

- vulnerability description;
- steps to reproduce;
- affected route, endpoint, DocType, API method, page, or package;
- expected behavior;
- actual behavior;
- potential impact;
- screenshots, logs, request/response examples, or proof of concept when safe;
- reporter contact information if follow-up is desired.

Response targets:

| Stage | Target |
| ----- | ------ |
| Acknowledge report | Within 48 hours |
| Initial assessment | Within 5 business days |
| Critical fixes | As soon as possible |
| High severity fixes | Within 7-14 days when feasible |
| Medium severity fixes | Within 30 days when feasible |
| Low severity fixes | Best effort |

## 4. Vulnerability Scope

Valid vulnerability categories include:

- authentication bypass;
- authorization flaws;
- access to another user's student data;
- access to another course or batch without permission;
- insecure direct object references;
- privilege escalation;
- server-side permission bypass;
- SQL injection;
- command injection;
- cross-site scripting;
- CSRF on sensitive actions;
- SSRF;
- sensitive data exposure;
- API keys or secrets committed to the repository;
- insecure API endpoints;
- file upload vulnerabilities;
- private file exposure;
- broken student access control;
- live-class link access bypass;
- WhatsApp/Evolution API secret exposure;
- webhook spoofing;
- external financial SaaS webhook bypass;
- dependency vulnerabilities with real impact.

## 5. Out of Scope

Reports are usually out of scope unless real impact is demonstrated:

- automated scanner output without explanation;
- missing security headers without exploitability;
- clickjacking on pages with no sensitive action;
- unrealistic denial-of-service claims;
- social engineering;
- physical attacks;
- self-XSS;
- issues affecting outdated browsers only;
- vulnerabilities in third-party services outside this project's control;
- rate limiting suggestions without an abuse scenario;
- reports requiring access to accounts or infrastructure not owned by the
  project.

## 6. Severity Classification

| Severity | Examples |
| -------- | -------- |
| Critical | Remote code execution, authentication bypass, full database exposure, cross-student or cross-batch data exposure at scale, exposed production secrets, arbitrary file read/write, unauthorized admin access |
| High | Privilege escalation, student accessing another student's data, student accessing another batch/course, payment/access bypass from external SaaS integration, account takeover, live-class link access without authorization, sensitive logs exposed |
| Medium | Stored XSS with limited scope, CSRF on sensitive academic actions, IDOR with limited data exposure, private file exposure with limited scope, webhook validation weakness without confirmed exploitation |
| Low | Minor information disclosure, missing headers with limited impact, low-risk misconfiguration, non-sensitive verbose errors in admin-only views |

CVSS may be used as a reference when appropriate, but this project prioritizes
practical impact and exploitability.

## 7. Disclosure Policy and Safe Harbor

Reporters should give the project reasonable time to fix a vulnerability before
public disclosure.

When testing or reporting:

- do not access, modify, delete, or exfiltrate real student data;
- do not disrupt availability;
- do not perform high-volume automated scanning;
- do not use the vulnerability for extortion, financial gain, or unauthorized
  access.

After a fix, the project may publish an advisory or changelog entry when
appropriate.

## 8. Repository Security Rules

The following must never be committed:

- real `.env` files;
- `site_config.json`;
- `common_site_config.json`;
- API keys;
- tokens;
- passwords;
- private certificates;
- OAuth client secrets;
- webhook secrets;
- database dumps;
- Frappe site backups;
- files with real student data;
- complete integration payloads containing personal or sensitive data;
- production logs with secrets.

`.env.example` may exist only with non-sensitive placeholder values.

Removing a secret from Git history is not enough. If a secret was exposed, revoke
and rotate it immediately.

## 9. Secrets and Configuration

Sensitive values must be configured through:

- environment variables;
- `site_config.json` outside Git;
- secure deployment secret manager;
- equivalent approved secure mechanism.

Examples of sensitive values:

- `EVOLUTION_API_KEY`;
- webhook secrets;
- provider credentials;
- internal protected URLs;
- signing keys;
- technical user passwords;
- future external SaaS webhook secrets;
No live-video credentials are expected for the Melura MVP. Google Meet links
are configured manually as external links; do not add Google OAuth, Google
Workspace credentials, Google Calendar API, Google Meet API, video SDK, paid
video infrastructure, or self-hosted video infrastructure.

Rules:

- never send secrets to Vue components;
- never render secrets in HTML;
- never return secrets through browser APIs;
- never log full secrets;
- mask secrets if they must be referenced.

Safe masking example:

```text
EVOLUTION_API_KEY=ev_************9f2a
```

Unsafe example:

```text
EVOLUTION_API_KEY=real-production-secret-value
```

## 10. Authentication and Authorization

Every sensitive route must verify authentication and authorization on the
backend.

Rules:

- admin-only actions must be protected server-side;
- frontend-hidden buttons are not security;
- IDs in URLs must be checked against the authenticated user's allowed scope;
- backend must decide `student_user`, course, batch, and permission scope;
- students cannot provide another user ID to view progress or answers.

Relevant Frappe and project-specific roles include:

- `Administrator`;
- `System Manager`;
- `Administrador LMS`;
- `Admin operacional`;
- `LMS Admin`;
- `LMS Instructor` or teacher role if used;
- `LMS Student`.

`Administrator` must not be used as the normal teacher account.

Accounts should be separated by responsibility:

- technical root/admin;
- teacher;
- operational admin;
- integration/bot user;
- student.

## 11. Student Access Security

Student access is the source of pedagogical access inside this Frappe app. The
implementation still uses the legacy internal DocType currently named
`Bruce Student Access`.

User-facing statuses must stay in Brazilian Portuguese:

- `Pendente`
- `Ativo`
- `Bloqueado`
- `Expirado`

Rules:

- only `Ativo` unlocks pedagogical content;
- `Pendente`, `Bloqueado`, and `Expirado` do not unlock live classes,
  materials, questions, exercise lists, or progress metrics;
- student pages must validate the logged-in user on the backend;
- student pages must not accept user, course, or batch from the frontend as
  authorization;
- student access must be scoped to course and/or batch;
- future financial SaaS integration must update only pedagogical status and
  opaque references, not card data or full financial payloads.

## 12. Live Class And Google Meet Security

Live-class Google Meet URLs must be protected as classroom access, not as
public links.

Rules:

- backend must validate permission before returning `meeting_url` or
  `external_url`;
- Google Meet URLs must use `https://meet.google.com/...`;
- reject `http`, `javascript:`, `data:`, `file:`, `ftp:`, and non-Google Meet
  hosts;
- do not iframe Google Meet;
- do not load external video SDK scripts;
- do not use Google OAuth, Google Workspace credentials, Google Calendar API,
  or Google Meet API for this feature;
- do not add paid, managed, self-hosted, or embedded video infrastructure;
- do not expose unnecessary internal settings to the browser.

The live-room route must validate:

- logged-in user;
- live class exists;
- class has a valid Google Meet `meeting_url`;
- student has active access with status `Ativo` for the correct course or
  batch, stored for now in the legacy internal DocType currently named
  `Bruce Student Access`;
- teacher/admin has the correct role;
- class status allows access.

The compatibility route `/app/bruce-live-room/<class>` remains for now, but it
must render a Melura launch page and open Google Meet externally.

## 13. WhatsApp, Evolution API, and n8n Security

WhatsApp operations must keep provider credentials away from the browser.

Rules:

- Evolution API keys must stay outside Git;
- WhatsApp sending must happen in backend or a protected n8n flow;
- frontend can request an action, but provider calls must happen
  server-side/protected;
- do not expose sensitive endpoints to teacher/student UI;
- log attempts with status, date/time, short error summary, and reference to
  class/course/batch;
- avoid saving full payloads when a summary is enough;
- manual resend must require an authorized user;
- preserve original failure history;
- never log authentication headers or provider tokens.

User-facing examples such as `Enviar aviso`, `Pré-visualizar WhatsApp`,
`Reenviar aviso`, `Pendente`, `Enviado`, `Falhou`, and `Reenviado` must remain
in Brazilian Portuguese.

## 14. Educational Materials Security

Rules for Material didático, implemented by the legacy internal DocType
currently named `Bruce Educational Material`:

- student materials must be published;
- student materials must have visibility `Aluno`;
- `Professor` and `Interno` visibility must not be returned to `LMS Student`;
- `published_at` is set server-side when published;
- frontend must not define student/course/batch access;
- student receives only materials compatible with active student access;
- `Pendente`, `Bloqueado`, and `Expirado` do not unlock materials;
- private file access must require authorization;
- avoid public URLs for private student-only files unless intentionally public.

## 15. ENEM Question Bank Security

Rules for Questão ENEM, implemented by the legacy internal DocType currently
named `Bruce ENEM Question`:

- student-visible questions must be published;
- published questions must have answer key configured;
- `published_at` is set server-side;
- student listing is generated from the authenticated user and access scope;
- frontend must not define student/course/batch access;
- student receives only questions compatible with active access;
- initial student API must not return answer key or commented resolution before
  answer flow allows it;
- `Pendente`, `Bloqueado`, and `Expirado` do not unlock questions.

## 16. Exercise Lists and Student Answers Security

Rules for Lista de exercícios and Resposta do aluno, implemented by the legacy
internal DocTypes currently named `Bruce Exercise List` and
`Bruce Student Answer`:

- student-visible lists must be published;
- published list must have at least one question;
- `published_at` is set server-side;
- student receives only lists compatible with active student access;
- student can fetch only questions from allowed published lists;
- student question API must not return answer key or commented resolution before
  answer submission when controlled attempts are implemented;
- `selected_option` may come from frontend;
- `student_user` must always be `frappe.session.user`;
- `is_correct` must be computed server-side;
- student cannot submit answers for another student;
- `Pendente`, `Bloqueado`, and `Expirado` cannot list, read, or answer exercise
  lists.

## 17. Student Progress Security

Rules:

- progress is calculated server-side;
- student cannot provide another `student_user` to view progress;
- student sees only their own progress;
- student progress is shown only when student access is `Ativo`;
- `Pendente`, `Bloqueado`, and `Expirado` return blocked state without
  pedagogical metrics;
- teacher/admin summary by class requires authorized role;
- course/batch parameters from frontend do not grant access;
- do not expose answer keys, commented resolutions, financial data, secrets, or
  raw payloads through progress APIs.

## 18. Operational Dashboard Security

Rules for `Painel Operacional` / `bruce-operational-dashboard`:

- backend API must validate permission before querying data;
- only `Administrator`, `System Manager`, `Administrador LMS`,
  `Admin operacional`, or `LMS Admin` can access aggregates;
- `LMS Student` must not access dashboard or API;
- return only counts, summaries, and minimal operational lists;
- do not return API keys, tokens, sensitive endpoints, financial data, full
  integration payloads, or unnecessary personal data;
- frontend is not authorization.

## 19. External Financial SaaS Integration Security

Future:

The Frappe app should not implement billing, checkout, subscriptions, lead
capture, newsletter, blog, or CRM. The external SaaS will eventually send access
status updates to Frappe.

Rules for future webhooks:

- verify webhook signature or shared secret server-side;
- do not trust payment/access status from frontend;
- store only necessary pedagogical status and opaque external IDs;
- do not store card data;
- do not store full financial payloads unless strictly necessary;
- log minimal webhook result and correlation ID;
- handle replay protection when possible;
- make activation/blocking idempotent;
- failed webhook should not partially corrupt access state.

Future data that may be received:

- `external_customer_id`;
- plan identifier;
- pedagogical status;
- course;
- batch;
- expiration date;
- cancellation status.

## 20. Multi-Tenant / Multi-Organization Security

Even if the current project starts with one course, future scaling must enforce
tenant isolation.

Rules:

- if multiple schools, courses, companies, creators, or organizations use the
  system, every query must enforce tenant isolation;
- users from tenant A must never access tenant B data;
- IDs from URL must be checked against tenant/account/school scope;
- background jobs must preserve tenant context;
- webhooks must validate ownership before updating records;
- broken tenant isolation is high or critical severity.

Future multi-tenant expansion must be designed before selling to multiple
independent operators on the same instance.

## 21. File Upload and Private File Security

Rules:

- limit file size;
- restrict allowed file types when possible;
- do not trust file extension alone;
- store sensitive files outside public paths;
- require authorization before private file download;
- prevent path traversal;
- avoid exposing private files through public URLs;
- rename files on upload when needed;
- do not allow executable uploads;
- consider scanning or validating files when production requires it.

Apply this to:

- PDFs;
- educational materials;
- attachments;
- future student uploads;
- future support files.

## 22. Logging and Monitoring

Logs should help audit operation without leaking sensitive data.

Log:

- action origin;
- responsible user;
- date/time;
- status;
- minimal recipient/reference;
- short provider error;
- reference to class/course/batch/material/list when useful;
- permission failures when useful.

Do not log:

- API keys;
- tokens;
- passwords;
- auth headers;
- private keys;
- full provider payloads;
- unnecessary personal data;
- full student data dumps.

Security-relevant events to consider:

- login attempts;
- failed login attempts;
- password reset requests;
- permission changes;
- admin actions;
- class start/open events;
- WhatsApp send failures;
- external webhook failures;
- suspicious access denials;
- API authentication failures;
- changes to sensitive settings.

## 23. Dependency Security

Rules:

- dependencies must be necessary and trusted;
- security updates should be prioritized;
- dependency changes should be reviewed carefully.

Prioritize vulnerabilities that:

- are remotely exploitable;
- have a proof of concept;
- affect authentication/authorization;
- affect file upload;
- affect server-side rendering or request handling;
- affect data access;
- are actively exploited.

Use GitHub security alerts or dependency alerts when available. Production
deployments should have a process for security updates.

## 24. Cache and Performance Security

This project may add cache later. Cache must never weaken access control.

Rules:

- cache must never bypass permissions;
- cache keys for student data must include user and access scope;
- do not use generic keys like `student_home` or `progress` for user-specific
  data;
- operational aggregates can use short TTL cache;
- access status should be treated carefully and invalidated quickly;
- when in doubt, prefer correctness and access control over speed.

Safe example:

```text
student_progress:<user>:<course_or_batch>
```

Unsafe example:

```text
student_progress
```

## 25. Deployment Security

Future production deployment must ensure:

- HTTPS enabled;
- secure database credentials;
- Redis services protected;
- workers running with least required privilege;
- scheduler running intentionally;
- backups configured;
- logs monitored;
- production secrets outside Git;
- debug mode disabled;
- admin credentials rotated from defaults;
- system users separated by responsibility;
- private files not exposed by Nginx unintentionally;
- security headers considered where appropriate.

## 26. Backup and Restore Security

Rules:

- backups may contain sensitive data;
- backups must not be committed to Git;
- backups must be protected at rest;
- backups should be stored outside the application repository;
- production backups should be encrypted or access-controlled;
- restore process must be tested;
- old backups should have retention rules;
- backup filenames/logs should not expose unnecessary sensitive data.

## 27. Incident Response

When a security incident is suspected:

1. Confirm the issue.
2. Assess impact.
3. Contain the problem.
4. Revoke or rotate exposed credentials if needed.
5. Patch the vulnerability.
6. Review logs.
7. Identify affected users/data.
8. Notify affected users when necessary.
9. Document root cause.
10. Add tests or controls to prevent recurrence.

If a secret was committed:

1. Revoke it immediately.
2. Generate a new secret.
3. Remove it from code/configuration.
4. Review logs for misuse.
5. Document the incident.
6. Do not reuse the old secret.

## 28. Security Checklist for Contributors

- [ ] No real secrets were committed.
- [ ] `.env` real files are not in the diff.
- [ ] `site_config.json` is not in the diff.
- [ ] `common_site_config.json` is not in the diff.
- [ ] No API keys, tokens, passwords, or private certificates appear in
      code/docs/tests.
- [ ] New endpoints validate authentication.
- [ ] New endpoints validate authorization server-side.
- [ ] Student data queries are scoped to `frappe.session.user` and
      the legacy internal DocType currently named `Bruce Student Access`.
- [ ] Course/batch parameters from frontend do not grant access.
- [ ] Admin-only APIs reject `LMS Student`.
- [ ] Teacher/admin actions validate role.
- [ ] Sensitive actions are logged safely.
- [ ] Errors do not expose stack traces or secrets to users.
- [ ] File uploads/downloads are protected when private.
- [ ] Webhooks are verified server-side.
- [ ] Payment/access status is not trusted from frontend.
- [ ] Cache does not bypass permissions.
- [ ] Logs do not contain secrets or full sensitive payloads.
- [ ] New dependencies are necessary and trusted.
- [ ] Tests cover important permission checks when code changes.

## 29. Project-Specific Security Rules Summary

| Area | Main Rule | Risk if Broken |
| ---- | --------- | -------------- |
| Student access | Student access controls pedagogical access; the implementation still uses the legacy internal DocType currently named `Bruce Student Access`. | Blocked or unauthorized students may access protected content. |
| Live class/Google Meet | Google Meet links are returned only after backend permission checks. | Unauthorized users may enter live classes. |
| Materials | Student materials must be published and allowed for the user scope. | Private or internal materials may leak. |
| ENEM questions | Student APIs must not expose answer keys too early. | Students may see answers before attempting questions. |
| Exercise lists | Answers are tied to `frappe.session.user` and validated server-side. | Students may submit or view answers for others. |
| Student answers | `is_correct` is computed server-side. | Frontend may manipulate results. |
| Student progress | Progress is calculated server-side for the authenticated user. | Student metrics may leak across users. |
| Operational dashboard | Only authorized operational roles can access aggregates. | Students may access admin data. |
| WhatsApp/Evolution | Provider secrets stay backend/protected. | API keys or endpoints may leak. |
| External financial SaaS | Future webhooks must be verified server-side. | Payment/access status may be spoofed. |
| Logs | Logs must be useful but minimal. | Sensitive data may be stored unnecessarily. |
| Backups | Backups must stay outside Git and be protected. | Full data exposure. |
| Cache | Cache must include permission scope. | Cached private data may leak. |

## 30. Contact

- `security@example.com`
- `contact@example.com`

Replace these placeholders before public production use.
