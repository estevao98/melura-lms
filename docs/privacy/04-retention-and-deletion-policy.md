# Retention and Deletion Policy Draft

This is a technical draft for internal planning. It is not a final legal
retention policy and should not be used as public policy text without
human/legal review.

The draft prioritizes preservation of auditability, educational integrity, and
student privacy. Physical deletion of linked pedagogical records should be
reviewed before implementation because Frappe DocTypes, LMS enrollment records,
logs, answers, and class history may have operational, support, audit, or legal
dependencies.

## General Principles

- Keep data only for defined pedagogical, support, security, audit, or legal
  purposes.
- Prefer blocking access over deleting records when the user is no longer
  entitled to pedagogical content.
- Prefer anonymization or aggregation for historical metrics when identity is no
  longer needed.
- Do not delete audit logs without review.
- Do not commit backups, dumps, logs with secrets, or real student data.
- Retention periods must be approved outside this technical draft.

## What Should Be Retained

- Acesso do aluno records, currently implemented by the legacy internal DocType
  currently named `Bruce Student Access`, needed to explain why a student had or did not
  have access at a given time.
- Aula ao vivo records, currently implemented by the legacy internal DocType
  currently named `Bruce Live Class`, needed for class history, support, and operational
  audit.
- Histórico da aula ao vivo entries, currently implemented by the legacy
  internal DocType currently named `Bruce Live Class Notice Log`, for class actions such
  as opening, starting, previewing, or send failures.
- Resposta do aluno records, currently implemented by the legacy internal
  DocType currently named `Bruce Student Answer`, while needed for student progress,
  course support, educational review, and accountability.
- Log de WhatsApp entries, currently implemented by the legacy internal DocType
  currently named `Bruce WhatsApp Notification Log`, while needed for communication
  support, resend history, provider dispute diagnosis, and incident review.
- Settings DocTypes as long as the integration/configuration is active.

## What May Be Anonymized

After human/legal review and after the operational purpose ends, these may be
candidates for anonymization or aggregation:

- historical student answer/progress records, if individual identity is no
  longer needed;
- inactive-student operational metrics after support/audit periods end;
- WhatsApp logs, by removing or hashing phone/name while preserving status,
  related class, timestamps, and short operational outcome;
- external opaque references after access/account reconciliation is no longer
  needed;
- exported analysis datasets, if any are ever created.

Anonymization must be technically reasonable and should account for
re-identification risk, especially when course, batch, timestamp, and rare
activity patterns remain.

## What Should Not Be Physically Deleted Without Review

- Student answers linked to active disputes, support cases, legal requests, or
  ongoing course operation.
- Access records that explain entitlement history.
- Live class records and notice logs that explain Google Meet access, class status,
  and operational actions.
- WhatsApp notification logs tied to failed sends, resend attempts, provider
  diagnosis, or incident review.
- Any record needed to satisfy a lawful obligation or defend rights.
- Backups that are under a defined backup retention process.

## Audit Logs

Audit and operational logs should be minimized but not casually deleted.

Expected controls:

- log event type, status, timestamp, related class/course/batch when needed,
  user who acted, and short error summaries;
- avoid full provider payloads where not needed;
- redact or exclude tokens, API keys, auth headers, passwords, webhook secrets,
  and private configuration;
- preserve original failure history for resend flows;
- restrict log access to authorized operational/admin roles.

## Student Answers And Progress

Student answers and progress are educational performance data. They should be
protected more strictly than generic content access data.

Initial technical proposal:

- keep records while the student has active or recently ended pedagogical
  relationship, subject to approved retention periods;
- do not let students change `student_user` or `is_correct`;
- preserve enough data to explain progress calculations;
- consider anonymization for long-term aggregate analytics after legal review;
- define a correction workflow for mistaken records without silently rewriting
  audit-relevant history.

## WhatsApp Notification Logs

WhatsApp logs can include recipient name, phone, message body, status,
timestamp, related class, error message, and provider response.

Initial technical proposal:

- retain recent logs for support and resend diagnosis;
- redact sensitive provider response keys before saving;
- keep short error summaries instead of full stack traces or auth payloads;
- consider later anonymization of phone/name while preserving operational
  status history;
- define whether message bodies must be retained or can be shortened after the
  support window.

## External SaaS Opaque References

External references should remain opaque correlation values only.

Initial technical proposal:

- retain only while needed to reconcile access status with the external SaaS;
- do not store card data, payment payloads, subscription details, CRM notes, or
  commercial lead data in `melura_lms`;
- document retention and deletion with the external SaaS owner before webhook
  implementation;
- treat webhook logs as sensitive operational logs.

## Backups

Backups are outside the custom app folder but are part of the privacy/security
boundary.

Initial technical proposal:

- keep backups outside Git;
- define retention periods and restore tests;
- restrict backup access to technical maintenance roles;
- avoid using production backups in development unless sanitized;
- document how deletion/anonymization requests interact with backup retention.

## Pending Human / Legal Decisions

- Approved retention period for account, access, answers, progress, live class,
  WhatsApp, operational, and framework logs.
- Whether student answers must be preserved for educational/legal purposes after
  account closure.
- Whether and when WhatsApp message bodies can be deleted or anonymized.
- Whether minors are served and whether additional retention limits apply.
- Process for data subject deletion, blocking, anonymization, correction, and
  export requests.
- Backup retention and restoration policy.
- Incident evidence retention requirements.
