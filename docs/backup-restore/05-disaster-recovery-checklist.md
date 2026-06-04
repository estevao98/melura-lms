# Disaster Recovery Checklist

Use this checklist during incidents. Keep real incident notes outside public
Git when they include infrastructure details, personal data, or secrets.

## Initial Triage

- [ ] Identify incident start time.
- [ ] Identify affected environment: local, staging/test, or production.
- [ ] Identify affected scope: database, files, deployment, migration, cache,
      workers, scheduler, provider, or VPS.
- [ ] Assign decision owner and technical operator.
- [ ] Preserve logs safely without copying secrets or personal data into chat.
- [ ] Decide whether to freeze writes or pause workers.

## Database Loss

- [ ] Confirm database service state.
- [ ] Confirm whether data is unavailable, corrupted, or deleted.
- [ ] Identify latest usable database backup.
- [ ] Confirm expected data loss window.
- [ ] Restore into staging/test first.
- [ ] Run smoke tests.
- [ ] Approve production restore only with a reviewed rollback plan.

## File Loss

- [ ] Identify whether private files, public files, or both are affected.
- [ ] Confirm file records in the database still point to expected paths.
- [ ] Locate matching file backup artifacts.
- [ ] Restore files into staging/test first when feasible.
- [ ] Verify materials, attachments, and protected content.
- [ ] Confirm private files are not publicly exposed after restore.

## Bad Deployment

- [ ] Identify deployed branch, commit, or release.
- [ ] Review deploy logs and build output.
- [ ] Confirm whether migration ran.
- [ ] If no data migration occurred, consider rollback to previous release.
- [ ] If migration occurred, assess forward fix versus restore.
- [ ] Run smoke tests after rollback or fix.

## Corrupted Migration

- [ ] Stop further deployments.
- [ ] Confirm migration logs and failing patch or schema step.
- [ ] Identify whether data changed partially.
- [ ] Restore a backup into staging/test and reproduce safely.
- [ ] Prefer a reviewed forward fix when production data is partially changed.
- [ ] Restore production only with explicit approval and rollback plan.

## Accidental Data Deletion

- [ ] Identify deleted DocType, records, and timestamp.
- [ ] Confirm whether deletion affected student access, answers, progress,
      materials, live classes, or logs.
- [ ] Check whether audit logs or backups can identify the affected records.
- [ ] Restore into staging/test to inspect recoverable data.
- [ ] Decide between selective reconstruction and full restore.
- [ ] Document privacy implications of restored personal data.

## Redis Or Cache Problems

- [ ] Confirm Redis cache, queue, and socketio service health.
- [ ] Clear cache for the affected site.
- [ ] Confirm permission checks still run server-side.
- [ ] Check worker and web logs for Redis connection errors.
- [ ] Restart Redis or bench services through the approved process manager.
- [ ] Run smoke tests for student access and live-room context.

## Worker Or Scheduler Problems

- [ ] Check worker process status.
- [ ] Check scheduler status.
- [ ] Review failed jobs and queue backlog.
- [ ] Confirm WhatsApp jobs or future automations did not expose secrets.
- [ ] Restart workers or scheduler if safe.
- [ ] Confirm background jobs do not process stale restored data.

## External Provider Outage

- [ ] Identify provider: Google Meet, Evolution API, n8n, storage, DNS, or HTTPS.
- [ ] Confirm Melura permissions remain enforced during outage.
- [ ] Disable or pause risky sends if provider behavior is unstable.
- [ ] Use Google Meet external links only after backend access checks.
- [ ] Log short operational summaries without provider secrets.
- [ ] Communicate impact and workaround through approved channels.

## VPS Loss

- [ ] Confirm provider incident and expected recovery time.
- [ ] Identify latest off-VPS database and file backups.
- [ ] Provision replacement environment from deployment docs.
- [ ] Restore into staging/test or replacement production environment as
      approved.
- [ ] Reconfigure secrets outside Git.
- [ ] Validate domain, HTTPS, Redis, workers, scheduler, and smoke tests.

## Rollback Decision

- [ ] Is production data still trustworthy?
- [ ] Did a migration run?
- [ ] Is a forward fix safer than restore?
- [ ] Is the selected backup recent enough?
- [ ] Are private and public files aligned with the database backup?
- [ ] Who approves user-visible downtime or data loss?
- [ ] What smoke tests must pass before reopening access?
