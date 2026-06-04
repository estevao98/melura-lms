# Production Checklist

Use this checklist before treating a VPS as production-ready. Keep environment
values, real domains, IP addresses, and secrets outside Git.

## Repository State

- [ ] Branch and commit intended for deployment are identified.
- [ ] `git status --short` is clean or only expected deployment-local files are
      present outside the repository.
- [ ] No changes were made to `frappe/`, `lms/`, `frappe-ui/`, `payments/`, or
      `jitsi-meet/`.
- [ ] No `.env`, `site_config.json`, `common_site_config.json`, database dump,
      backup, log with secrets, or real student data is in the diff.
- [ ] Deployment docs and runbook have been reviewed by the operator.

## App Installation

- [ ] Frappe bench exists on the target VPS.
- [ ] Frappe LMS is installed and compatible with the site.
- [ ] `melura_lms` is fetched inside the bench `apps/` directory.
- [ ] The app is installed on the intended site.
- [ ] App installation is verified with the Frappe site app list.

## Bench Setup

- [ ] Bench path is known, for example `/home/<deploy-user>/frappe-bench`.
- [ ] Commands run as the deploy user, not root.
- [ ] Site name is the production site, for example `app.example.com`.
- [ ] Production configuration is not copied from `curso.localhost`.
- [ ] Debug settings are disabled for production.

## Python Dependencies

- [ ] Bench virtual environment exists.
- [ ] Python dependencies are installed through the bench/Frappe process.
- [ ] No new external dependencies were added by this feature.
- [ ] `./env/bin/python -m compileall apps/melura_lms/melura_lms` passes.

## Node And Yarn Build

- [ ] Node/Yarn versions match the Frappe bench requirements.
- [ ] Frontend assets build with `bench build --app melura_lms`.
- [ ] Build output does not include secrets or environment-specific values.

## Database

- [ ] Database service is installed and supervised.
- [ ] Database credentials are stored outside Git.
- [ ] Database user has only the required privileges.
- [ ] Production uses the database engine supported by the installed Frappe
      version and bench configuration, commonly MariaDB for Frappe benches.
- [ ] PostgreSQL is used only if the full Frappe stack and site were installed
      and validated for it.

## Redis Services

- [ ] Redis cache service is running.
- [ ] Redis queue service is running.
- [ ] Redis socketio service is running when required by the bench.
- [ ] Redis is not exposed publicly.
- [ ] Cache clearing works with `bench --site <site> clear-cache`.

## Workers

- [ ] Default, short, and long workers expected by the bench are supervised.
- [ ] Failed jobs are reviewed.
- [ ] Workers run as the deploy user with least required privilege.
- [ ] Background jobs do not log secrets or full sensitive payloads.

## Scheduler

- [ ] Scheduler is intentionally enabled or intentionally disabled with a
      documented reason.
- [ ] Scheduler status is checked after deployment.
- [ ] Scheduled jobs do not replace backend permission checks.

## Socketio

- [ ] Socketio process is running if required by the installed Frappe stack.
- [ ] Reverse proxy supports WebSocket upgrade headers.
- [ ] Browser console has no repeated socket connection failures.

## Domain And HTTPS

- [ ] Real domain points to the VPS.
- [ ] Nginx or equivalent reverse proxy routes HTTPS traffic to bench.
- [ ] HTTPS certificate is valid and renewed automatically.
- [ ] Production does not rely on `localhost`, `curso.localhost`, or plain HTTP.

## Logs

- [ ] Web, worker, scheduler, socketio, database, Redis, and reverse proxy logs
      are readable by the operator.
- [ ] Logs do not contain API keys, tokens, auth headers, database passwords,
      private keys, full provider payloads, or unnecessary personal data.
- [ ] Incident notes include timestamps, affected service, impact, and action.

## Backups And Restore

- [ ] Database backups are configured outside Git.
- [ ] Private files are included in backup strategy when needed.
- [ ] Public files are included when needed.
- [ ] Backup storage is access-controlled.
- [ ] Restore test has been performed on a non-production site.
- [ ] Retention rules are documented.

## Secrets Outside Git

- [ ] Evolution API key is in environment, `site_config.json`, or secret store.
- [ ] n8n webhook URL is stored outside Git if sensitive.
- [ ] Database passwords are outside Git.
- [ ] Encryption keys are outside Git and backed up securely.
- [ ] Jitsi/JaaS credentials, if any, are outside Git.

## Admin Account Hardening

- [ ] `Administrator` password is strong and rotated from any default.
- [ ] Professor uses a separate human account, not `Administrator`.
- [ ] Operational admin users are separate from technical root/admin users.
- [ ] Integration/bot users have minimal scope.
- [ ] Dormant accounts are disabled before go-live.

## Update And Rollback

- [ ] Pre-deploy backup is taken when deploying risky changes.
- [ ] Rollback commit or release is known.
- [ ] Migrations are run only when schema, DocType, fixture, patch, or hook
      changes require them.
- [ ] Rollback limits are understood when migrations have already changed data.
- [ ] Smoke tests are defined and run after deployment.
