# Restore Runbook

This runbook is intentionally conservative. Restore into staging/test first.
Never run a destructive restore against production without a reviewed rollback
plan, confirmed backups, and an explicit decision owner.

## Safety Rules

- Restore only into staging/test before production use.
- Verify the app versions before restoring.
- Verify the site name and database target before every command.
- Do not restore production data into local development unless sanitized and
  approved.
- Keep secrets, backup paths, and real domains outside Git.
- Stop workers or scheduler if they could process restored data unexpectedly.

## Pre-Restore Checklist

- [ ] Restore target is non-production: `<test-site-name>`.
- [ ] Target bench path is confirmed: `/home/<deploy-user>/frappe-bench`.
- [ ] Target database is safe to overwrite.
- [ ] Target site name is not the production site.
- [ ] Backup database artifact is present.
- [ ] File backup artifacts are present if needed.
- [ ] `frappe`, `lms`, and `melura_lms` versions match the restore plan.
- [ ] `site_config.json` and encryption key handling are ready outside Git.
- [ ] Rollback path for the restore test environment is known.

## Stop Workers Or Scheduler If Needed

Use the target environment's process manager. Place real service names only in
private notes.

```bash
sudo supervisorctl stop <bench-process-group>:*
```

or:

```bash
sudo systemctl stop <service-name>
```

For local test benches, stop only the processes that could mutate restored data.

## Restore Database

Use the Frappe restore command appropriate for the installed bench version.
Placeholder pattern:

```bash
cd /home/<deploy-user>/frappe-bench
bench --site <test-site-name> restore /path/to/<database-backup-file>
```

Confirm the command target before accepting any destructive prompt.

## Restore Files If Applicable

If the backup includes private and public files, restore them according to the
backup format and Frappe/bench version. Placeholder pattern:

```bash
cd /home/<deploy-user>/frappe-bench
bench --site <test-site-name> restore /path/to/<database-backup-file> \
  --with-private-files /path/to/<private-files-backup> \
  --with-public-files /path/to/<public-files-backup>
```

If the installed bench version uses different flags, use the official command
for that version and record the exact tested command in private operational
notes.

## Migrate If Needed

Run migration only when the restored database needs to align with the current
installed app versions.

```bash
cd /home/<deploy-user>/frappe-bench
bench --site <test-site-name> migrate
```

Do not use migration to hide an incompatible restore. Investigate version
mismatches first.

## Clear Cache

```bash
cd /home/<deploy-user>/frappe-bench
bench --site <test-site-name> clear-cache
bench --site <test-site-name> clear-website-cache
```

## Restart Services

Use the process manager configured for the test bench:

```bash
sudo supervisorctl start <bench-process-group>:*
```

or:

```bash
sudo systemctl start <service-name>
```

## Smoke Tests

After restore:

- open the test site over the expected URL;
- log in with a safe test account;
- confirm `melura_lms` is installed;
- confirm key DocTypes load;
- confirm student access records exist as expected;
- confirm live class records and Google Meet URLs are present;
- confirm materials, exercises, questions, answers, and progress are usable;
- confirm WhatsApp settings do not expose secrets;
- inspect logs for restore errors without copying personal data into tickets.

Record the restore result, including failures, elapsed time, and follow-up
actions.

## Production Restore Warning

Production restore is a high-risk operation. Before production restore:

- freeze or pause writes where feasible;
- notify the decision owner and operator;
- confirm the rollback plan;
- confirm the selected backup timestamp;
- confirm expected data loss window;
- confirm file and database compatibility;
- document smoke tests and communication plan.

Do not run production restore from this repository checklist alone.
