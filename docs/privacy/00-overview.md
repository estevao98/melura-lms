# Privacy and Permission Audit Overview

This folder is the working privacy and permission audit foundation for Melura.
It connects the current `melura_lms` permission/security rules with the LGPD
knowledge base in `docs/knowledge/lgpd/`.

This is an implementation planning and audit area. It is not legal advice, and
it does not replace a privacy policy, contract review, data protection impact
assessment, or legal decision by the controller.

## Purpose

The audit has four practical goals:

- map the personal data handled by the pedagogical LMS core;
- document role boundaries and backend permission expectations;
- translate LGPD knowledge chunks into technical requirements for this app;
- keep an implementation-facing report of current controls, tests, and open
  permission/privacy risks.

The most important security rule remains unchanged: frontend visibility is not
authorization. Sensitive access decisions must be made on the backend, using
the authenticated user from `frappe.session.user` and the pedagogical access
record in Acesso do aluno. The implementation still uses the legacy internal
DocType currently named `Bruce Student Access`.

## Product Boundary

Melura is the public product name. `melura_lms` is the technical Frappe app/package
name. This repository is the pedagogical LMS core.

In scope for `melura_lms`:

- student access to pedagogical content;
- `Minha Aula`;
- live classes with external Google Meet links;
- teacher and operational dashboards;
- educational materials;
- ENEM questions and exercise lists;
- student answers and progress;
- WhatsApp notification preparation and logs;
- protected Evolution API / n8n integration code;
- custom DocTypes, pages, hooks, services, fixtures, patches, and tests inside
  this app.

Out of scope for `melura_lms`:

- checkout;
- subscription billing;
- payment processing;
- CRM;
- lead capture;
- blog/newsletter;
- financial secretary workflows;
- fiscal/accounting operations;
- card data or full financial payload storage.

A future external financial/commercial SaaS may update only pedagogical access
status and opaque references in Melura. It must not turn this Frappe app into the
financial system.

## System Relationships

Melura is the product experienced by students, the professor, and operational
admins. `melura_lms` is the custom app that implements Melura-specific pedagogical
features on top of Frappe LMS.

Frappe LMS remains the underlying LMS base. This app should extend it through
Frappe extension points instead of modifying `frappe/`, `lms/`, or
`frappe-ui/`.

Google Meet external links are used for live classes. `melura_lms` stores class
metadata and must validate permission before returning `meeting_url` or
`external_url`.

WhatsApp/Evolution/n8n are operational communication integrations. Provider
calls must happen through backend logic or protected flows. Evolution API keys,
webhook secrets, provider tokens, auth headers, and private configuration must
not be exposed to frontend responses, HTML, repository files, or logs.

The future external financial SaaS is outside this app. It may send protected
access-status updates to Acesso do aluno, implemented for now by the legacy
internal DocType currently named `Bruce Student Access`, but only after
server-side origin validation and payload minimization.

## LGPD Knowledge Usage

Use `docs/knowledge/lgpd/00-index.md` as the entry point and
`docs/knowledge/lgpd/source-map.md` to locate relevant articles and topic
chunks.

For this audit foundation, the most relevant chunks are:

- `topics/01-escopo-fundamentos-definicoes-principios.md` for scope,
  definitions, and principles such as purpose, necessity, transparency,
  security, prevention, and accountability;
- `topics/02-bases-legais-consentimento-transparencia-legitimo-interesse.md`
  for legal bases, consent, transparency, and legitimate interest;
- `topics/03-dados-sensiveis-criancas-adolescentes-termino.md` for sensitive
  data, anonymization, children/adolescents, and termination of processing;
- `topics/04-direitos-dos-titulares.md` for access, correction, deletion,
  anonymization, portability, and request handling;
- `topics/07-agentes-encarregado-responsabilidade.md` for controller/operator,
  processor instructions, DPO/privacy contact, records, and responsibility;
- `topics/08-seguranca-incidentes-governanca.md` for security, incidents,
  governance, logs, and security by design;
- `topics/12-implicacoes-para-saas-educacional.md` for the education SaaS
  translation;
- `topics/13-checklist-lgpd-melura.md` for the practical checklist.

When using these chunks, separate:

- legal source or article reference;
- technical interpretation for Melura;
- human/legal decision still needed.

## Files In This Folder

- `01-data-inventory.md`: personal data categories and technical controls.
- `02-role-access-matrix.md`: role boundaries, sensitive assets, checks, and
  future tests.
- `03-lgpd-technical-requirements.md`: LGPD-to-technical planning matrix.
- `04-retention-and-deletion-policy.md`: technical draft for retention,
  anonymization, deletion, and backups.
- `05-permission-audit-report.md`: implementation-facing scan of pages,
  services, whitelisted methods, protected DocTypes, tests, and risks.
