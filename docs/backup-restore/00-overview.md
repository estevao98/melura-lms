# Backup And Restore Overview

Backup and restore readiness protects Melura from unrecoverable loss of
pedagogical data, operational history, and student progress. A backup that has
never been restored is only an assumption, so restore validation must be part
of production readiness.

## Why It Matters

Melura is the pedagogical LMS core for students, the professor, and
operational admins. If database records or uploaded files are lost, students
may lose access history, class context, answers, progress, materials, and
support evidence. Operators also need reliable recovery paths for bad
deployments, corrupted migrations, accidental deletion, VPS loss, and provider
incidents.

## Data In Scope

Backup and restore planning must cover:

- Frappe site database data, including Acesso do aluno (legacy internal DocType currently named `Bruce Student Access`), aulas ao vivo,
  educational materials, ENEM questions, exercise lists, student answers,
  progress-related records, WhatsApp notification logs, and settings DocTypes;
- private files needed by protected pedagogical content;
- public files used by the site;
- site configuration required to make restored data usable, especially
  `site_config.json` values and Frappe encryption key handling;
- app code versions for `frappe`, `lms`, and `melura_lms`;
- operational notes that explain backup location, retention, encryption, and
  restore owner.

## Out Of Scope

This repository does not store or implement:

- real production backups, database dumps, uploaded files, or customer data;
- real domains, IP addresses, credentials, provider tokens, or passwords;
- financial SaaS backups, checkout data, CRM data, billing records, blog, or
  newsletter content;
- destructive production restore automation;
- provider-specific storage scripts or GitHub Actions.

## Deployment, Privacy, And Operations

Backup and restore readiness is part of deployment readiness. Production should
not go live until backups are scheduled, access-controlled, encrypted at rest,
covered by retention decisions, and validated through restore smoke tests.

Backups may contain personal data under LGPD, including student answers,
progress, access history, phone numbers in WhatsApp logs, and operational
notes. Backup access must be limited to approved technical maintenance roles,
and retention must be reviewed with the privacy/legal owner.

## Safe Restore Principle

Restore must be tested in a staging or isolated test environment before any
production use. Never run a destructive restore against production without a
reviewed rollback plan, confirmed backup artifacts, and an explicit decision
owner.
