# Backup Runbook

This runbook is a safe template. Replace placeholders in private operational
notes, not in committed files. Do not run backup commands with real production
values from repository documentation.

## Pre-Backup Checks

- Confirm the target site name is correct: `<site-name>`.
- Confirm the bench path is correct: `/home/<deploy-user>/frappe-bench`.
- Confirm enough disk space exists for database, private files, and public
  files.
- Confirm the operator has permission to access backup artifacts.
- Confirm no backup artifact will be committed to Git.

## Database Backup

```bash
cd /home/<deploy-user>/frappe-bench
bench --site <site-name> backup
```

This creates a database backup for the selected Frappe site.

## Database And Files Backup

```bash
cd /home/<deploy-user>/frappe-bench
bench --site <site-name> backup --with-files
```

Use this when private and public files are required for a usable restore.

## Backup Artifact Location

Frappe commonly stores site backup artifacts under a site-private backup
folder similar to:

```text
/home/<deploy-user>/frappe-bench/sites/<site-name>/private/backups/
```

Treat this as a generic pattern only. Confirm the exact location in the target
environment before relying on it.

## List Recent Backups

```bash
cd /home/<deploy-user>/frappe-bench
ls -lah sites/<site-name>/private/backups/
```

Check timestamps, sizes, and expected database/file artifacts.

## Copy Backups To External Storage

Use the approved storage mechanism for the environment. Keep commands in
private operational notes when they include real destinations, bucket names,
hostnames, usernames, or credentials.

Generic placeholder:

```bash
cp sites/<site-name>/private/backups/<backup-file> /path/to/<encrypted-storage>/
```

For remote or managed storage, use an approved tool with placeholders in shared
docs:

```bash
<storage-cli> copy sites/<site-name>/private/backups/<backup-file> <storage-target>
```

## What Must Not Be Committed

Never commit:

- database backups;
- private file archives;
- public file archives that contain real user data;
- `site_config.json`;
- `common_site_config.json`;
- `.env` files;
- provider credentials;
- API keys, tokens, passwords, or private keys;
- logs with secrets or personal data;
- real student data or customer data.

## Backup Completion Record

Record the result outside public Git when it includes operational details:

- timestamp;
- environment and site;
- backup type: database only or with files;
- artifact names or private references;
- storage destination;
- encryption status;
- operator;
- errors or warnings;
- next restore test due date.

