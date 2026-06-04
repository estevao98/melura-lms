# Backup Policy

This policy is a technical draft for Melura LMS operations. It uses placeholders
only and requires human/legal review before production adoption.

## Objectives

- Recover from database loss, file loss, bad deployment, corrupted migration,
  accidental deletion, VPS loss, and operational mistakes.
- Preserve pedagogical records needed for student access, live classes,
  materials, questions, exercise lists, answers, progress, and support.
- Keep backups outside Git and protected from unauthorized access.
- Validate restore in staging/test before relying on backups for production.

## Database Backups

Database backups should include the full Frappe site database for
`<site-name>`. The operator should confirm backup completion, artifact size,
timestamp, and storage location after each scheduled run.

Database backups may contain personal data and sensitive operational records.
They must not be copied into this repository, tickets, chats, or public storage.

## File Backups

Private files must be included when Melura stores protected materials, uploads,
or attachments needed by students, teachers, or admins.

Public files must be included when the site depends on uploaded assets,
publicly served materials, or Frappe file records that point to public file
paths.

The backup plan should clearly state whether files are captured by
`bench --site <site-name> backup --with-files`, storage snapshots, or another
approved mechanism.

## Site Configuration

`site_config.json` and related environment configuration are outside the
`melura_lms` repository but are required for recovery. The operator must back
up the values needed to restore the site safely, including database connection
settings and the Frappe encryption key.

Configuration backups must be stored separately from Git and protected more
strictly than ordinary operational notes.

## Secrets Handling

Secrets must never be committed, pasted into chats, or included in repository
examples. This includes API keys, tokens, passwords, provider credentials,
webhook secrets, database passwords, private keys, and Frappe encryption keys.

If a backup contains configuration with secrets, store it in an approved secret
manager or encrypted operational vault. Rotate any secret that is accidentally
exposed.

## Frequency Recommendations

Initial draft:

- production database backup: at least daily;
- production file backup: at least daily when files change frequently, or after
  bulk content uploads;
- pre-deployment backup: before risky deployments, migrations, or data changes;
- staging/test backup: as needed before restore drills or migration rehearsals.

Final frequency depends on accepted recovery point objective, content update
volume, student activity, storage cost, and legal decisions.

## Retention Draft

Initial draft:

- keep recent daily backups for short-term operational recovery;
- keep a smaller number of weekly or monthly recovery points when approved;
- delete expired backups through a documented retention process;
- document how deletion/anonymization requests interact with backup retention.

Exact periods require human/legal approval and must respect LGPD and the
privacy retention policy.

## Encryption And Storage

Backups should be encrypted at rest and stored outside the VPS when production
risk requires it. Storage access must be limited to approved technical
maintenance roles.

External storage should provide access control, auditability where available,
and a recovery process that does not depend on a single operator's personal
machine.

## Restore Testing Cadence

Initial draft:

- perform a restore test before go-live;
- repeat restore tests after major Frappe, Frappe LMS, or `melura_lms`
  upgrades;
- repeat restore tests after backup storage changes;
- schedule periodic restore drills, at least quarterly when production usage is
  active.

Every restore test must run in staging/test, include smoke tests, and record the
result.

## Pending Human / Legal Decisions

- Recovery point objective and recovery time objective.
- Approved backup frequency and retention periods.
- Approved encrypted storage provider or storage class.
- Backup access owner and emergency access process.
- Whether production data may ever be restored into staging, and what
  anonymization is required first.
- How LGPD deletion, correction, blocking, and export requests interact with
  backup retention.
- Incident evidence retention expectations.

