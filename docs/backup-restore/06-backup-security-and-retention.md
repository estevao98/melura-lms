# Backup Security And Retention

Backups are sensitive assets. They may contain personal data, secrets,
pedagogical records, operational logs, and files that are not safe to share.

## Personal Data In Backups

Melura backups may include:

- student identity and access status;
- student answers and progress;
- course, batch, and live class participation history;
- WhatsApp recipient names, phone numbers, message summaries, provider
  responses, and error logs;
- uploaded educational materials and attachments;
- operational notes and support context.

Treat these backups as personal data under LGPD and the project's privacy
rules.

## Do Not Upload Or Share

Never upload backups to:

- GitHub;
- public issue trackers;
- public object storage;
- chat tools;
- email threads without approved encryption and recipient controls;
- local folders that are synced to unmanaged personal storage.

Never paste backup contents, database dumps, `site_config.json`, provider
tokens, or real student records into chat.

## Encryption At Rest

Backups should be encrypted at rest. Encryption keys must be stored separately
from backup artifacts and outside Git. Losing the encryption key can make a
backup unusable; exposing it can expose protected data.

The operator should document where encrypted backups are stored, who can access
them, and how emergency access works.

## Access Limits

Backup access should be limited to approved technical maintenance roles. Daily
teacher, operational admin, integration/bot, and student accounts should not
have direct backup storage access.

Review access periodically and remove operators who no longer need recovery
responsibilities.

## Retention

Backup retention must respect privacy and legal decisions. Keep backups only
for defined operational, support, security, audit, or legal purposes.

Retention policy must define:

- how long daily, weekly, and monthly backups are kept;
- who approves retention changes;
- how expired backups are deleted;
- how deletion, anonymization, correction, and export requests interact with
  backup retention;
- how incident evidence is preserved when needed.

## Sensitive Melura Records

Use extra care with:

- `Bruce Student Answer` and progress records;
- `Bruce Student Access` status and notes;
- `Bruce WhatsApp Notification Log`;
- Google Meet live-class link data;
- private files and uploaded materials;
- settings DocTypes that reference provider configuration.

WhatsApp logs and student answers/progress are sensitive even when they do not
contain passwords or API keys.

## Secrets And Site Configs

`site_config.json`, `common_site_config.json`, `.env` files, database
passwords, Frappe encryption keys, API keys, webhook secrets, provider tokens,
private keys, and protected provider credentials require special handling.

Store these values outside Git through environment configuration, site config,
secret manager, or an approved encrypted vault. Do not render them in HTML,
return them through browser APIs, log them in full, or include them in examples.

If a secret appears in a backup that is shared incorrectly, revoke and rotate it
immediately.
