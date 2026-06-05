# LGPD Technical Requirements

This document translates the LGPD knowledge chunks into technical planning
requirements for Melura's pedagogical LMS core. It is not legal advice. Legal
bases, controller/operator roles, privacy notices, consent text, and retention
periods require human/legal decisions.

Source chunks used:

- `docs/knowledge/lgpd/topics/01-escopo-fundamentos-definicoes-principios.md`
- `docs/knowledge/lgpd/topics/02-bases-legais-consentimento-transparencia-legitimo-interesse.md`
- `docs/knowledge/lgpd/topics/03-dados-sensiveis-criancas-adolescentes-termino.md`
- `docs/knowledge/lgpd/topics/04-direitos-dos-titulares.md`
- `docs/knowledge/lgpd/topics/07-agentes-encarregado-responsabilidade.md`
- `docs/knowledge/lgpd/topics/08-seguranca-incidentes-governanca.md`
- `docs/knowledge/lgpd/topics/12-implicacoes-para-saas-educacional.md`
- `docs/knowledge/lgpd/topics/13-checklist-lgpd-melura.md`

## Requirements Matrix

| Theme | Current Requirement | Future Requirement | Human / Legal Decision Needed |
| --- | --- | --- | --- |
| Purpose limitation | Keep `melura_lms` limited to pedagogical LMS flows: access, classes, materials, exercises, answers, progress, WhatsApp operational notices, and logs | Add a data-purpose register by DocType and integration | Define formal purposes and legal bases per processing operation |
| Data minimization | Return only fields needed by UI methods; do not store billing, card, CRM, lead, blog, or newsletter data | Review all whitelisted responses and DocType list/form exposure before production | Decide whether any optional fields are excessive and should be removed or hidden |
| Transparency | Internal docs explain product boundary, access rules, and technical data categories | Publish a Portuguese privacy notice/policy and concise student-facing explanations where appropriate | Approve controller identity, contact, shared data, processing purposes, and retention statements |
| Free access / access request | Preserve data in structured DocTypes that can be queried by user, course, batch, class, answers, and logs | Build an internal process or export helper to locate a student's personal data across Melura | Define official request channel, identity verification, response format, and SLA |
| Correction | Use Frappe admin flows for user/account and access record correction by authorized roles | Add a documented support workflow for correcting account, access, and pedagogical records | Decide which records students can self-correct and which require operational review |
| Deletion or anonymization | Do not physically delete protected educational records without review; use locked access states for access termination | Implement anonymization/blocking procedures for eligible answers/progress/logs when legally/operationally appropriate | Define what can be deleted, anonymized, blocked, or retained under obligation/legal defense |
| Portability/export | No dedicated portability export exists today | Plan an export of student account, access, answers, progress, and relevant communication metadata when applicable | Decide scope, format, exclusions for secrets/industrial secrets, and approval workflow |
| Consent when applicable | WhatsApp is currently operational class-notice preparation; secrets are backend-only | Separate operational communication from promotional/marketing communication if marketing is ever added | Decide legal basis for WhatsApp operational notices and whether consent/opt-out records are required |
| Children/adolescents care | Current app does not define age or responsible/legal guardian fields | If minors are served, design responsible consent and clearer child/adolescent transparency flows outside or inside proper scope | Decide whether Melura serves children/adolescents, minimum age, responsible consent process, and data limits |
| Security measures | Server-side access checks; permission query conditions for student-readable pedagogical DocTypes; secret redaction for provider responses; Google Meet URL validation server-side | Add production hardening checklist, backup/restore process, incident runbook, and deeper permission tests | Approve minimum security baseline and operational responsibilities |
| Incident response | `SECURITY.md` defines vulnerability reporting and severity; current logs avoid secrets by policy | Add incident response runbook, evidence preservation, secret rotation checklist, and notification decision tree | Decide who evaluates incidents, who communicates, and criteria for ANPD/titular notification |
| Logs | Notice and WhatsApp logs record operational events; provider responses are redacted for sensitive keys | Define retention, access review, and log minimization for Frappe logs, provider logs, and backups | Decide retention periods and acceptable personal data in logs |
| Controller/operator/processor boundary | Docs state future financial SaaS is external and this app is pedagogical | Maintain provider/suboperator map for hosting, Google Meet, Evolution API, n8n, email/storage/backup, and future SaaS | Define whether Melura, external SaaS, and providers act as controller/operator in each flow |
| Future external SaaS webhook risk | No webhook implemented in current feature; the Acesso do aluno `external_reference` field is documented as opaque and is currently implemented by the legacy internal DocType currently named `Bruce Student Access` | Implement signature/secret validation, idempotency, payload schema, allowed status mapping, and minimal logging | Decide trusted source, payload contract, allowed references, and failure handling |

## Current Technical Requirements

- Keep custom work inside `apps/melura_lms`.
- Do not modify `frappe/`, `lms/`, or `frappe-ui/`.
- Use Acesso do aluno as the source of pedagogical access. The implementation
  still uses the legacy internal DocType currently named `Bruce Student Access`.
- Unlock protected content only for `Ativo` access.
- Treat `Pendente`, `Bloqueado`, and `Expirado` as non-unlocking statuses.
- Derive current student from `frappe.session.user`.
- Validate course/batch scope server-side.
- Keep answer correctness server-computed.
- Keep Evolution API keys and webhook secrets outside frontend and Git.
- Redact provider response keys such as `apikey`, `api_key`, `authorization`,
  `token`, `password`, and `secret`.
- Return Google Meet links only after backend permission checks.
- Do not store financial payloads in this app.

## Future Technical Requirements

- Create a base-legal-purpose matrix per data flow.
- Create a data subject request process and, later, export helpers.
- Create retention/anonymization tooling after legal approval.
- Implement future external SaaS webhook validation before accepting access
  changes.
- Add production backup/restore and incident response documentation.
- Add provider/suboperator inventory.
- Review Frappe Desk list/form exposure for every student-readable DocType.
- Add integration tests with real site permissions.

## Human / Legal Decisions Needed

- Controller/operator roles for Melura, external SaaS, and providers.
- Official privacy contact or encarregado/DPO details.
- Legal basis for each flow, including WhatsApp operational notices.
- Whether the product serves minors and how guardian consent is handled.
- Public privacy policy text in Brazilian Portuguese.
- Retention periods and deletion/anonymization rules.
- Incident communication criteria.
- Whether any external AI, analytics, storage, or email provider will process
  student data.
