# Deployment Readiness Overview

Deployment readiness for Melura LMS means the project can move from local
development toward a VPS or production environment with clear operational
checks, documented boundaries, and no secrets in Git. It is a foundation for
repeatable deployment, not a replacement for infrastructure ownership.

## Responsibility Boundary

This repository contains the pedagogical LMS core:

- student access through the DocType `Melura Student Access`;
- `Minha Aula`;
- live classes with external Google Meet links;
- educational materials, ENEM questions, exercise lists, answers, and progress;
- teacher and operational dashboards;
- WhatsApp notification preparation, protected Evolution API/n8n flows, and
  safe logs.

The external financial/commercial SaaS remains responsible for:

- checkout;
- subscriptions and billing;
- CRM;
- lead capture;
- blog and newsletter;
- commercial automations;
- financial operations.

A future external SaaS integration may update pedagogical access status and
opaque references in the DocType `Melura Student Access`, but it must not move billing or
commercial logic into `melura_lms`.

## Out Of Scope

This deployment foundation intentionally does not add:

- real production secrets, domains, IPs, credentials, or customer data;
- billing or subscription logic;
- fragile VPS automation;
- GitHub Actions;
- production Docker setup;
- schema, DocType, fixture, patch, or hook changes;
- changes to Frappe, Frappe LMS, Frappe UI, payments, or external apps.

## Why This Is Separate From Feature Development

Feature development answers what the LMS does for students, the professor, and
operational admins. Production readiness answers how the same behavior runs
safely in a real environment. Keeping these tracks separate avoids mixing
secrets, hosting assumptions, deployment commands, or commercial SaaS
responsibilities into pedagogical features.

Before production use, the team should validate environments, services,
workers, scheduler, HTTPS, backups, restore, logs, permissions, and rollback
process using the documents in this folder.
