# Go-Live Checklist

Use this checklist before opening production access to real students and
operations.

## Final Checklist

- [ ] Production branch or release is selected.
- [ ] Deployment runbook has been rehearsed on staging/test VPS.
- [ ] Production site uses the real domain over HTTPS.
- [ ] `curso.localhost` assumptions are absent from production config.
- [ ] Workers, scheduler, Redis, socketio, database, and reverse proxy are
      supervised.
- [ ] Smoke tests pass for student, teacher, and operational admin flows.
- [ ] Production Jitsi path is documented for launch.
- [ ] WhatsApp sending is disabled, test-only, or explicitly approved for real
      sends.

## Security Checklist

- [ ] No secrets are committed.
- [ ] `site_config.json` and `common_site_config.json` are outside Git.
- [ ] Evolution API key is outside Git and not exposed to frontend.
- [ ] n8n webhook URL is protected when sensitive.
- [ ] Database password and encryption key are backed up securely outside Git.
- [ ] Debug mode is disabled.
- [ ] `Administrator` is not used as Professor Bruce's daily account.
- [ ] Technical, teacher, operational admin, integration/bot, and student
      accounts are separated.
- [ ] Dormant or test users with elevated permissions are disabled.

## LGPD And Privacy Checklist

- [ ] Privacy/legal owner has reviewed data handling.
- [ ] Real student data is not present in repository docs, tests, logs, or
      examples.
- [ ] Logs avoid secrets and unnecessary personal data.
- [ ] Backup storage is access-controlled.
- [ ] Retention expectations are documented outside code where needed.
- [ ] WhatsApp phone use and consent expectations are reviewed before mass
      sending.

## Permissions Checklist

- [ ] `Bruce Student Access` remains the source of pedagogical access.
- [ ] Only `Ativo` unlocks classes, materials, questions, lists, answers, and
      progress.
- [ ] `Pendente`, `Bloqueado`, and `Expirado` do not unlock protected content.
- [ ] Student APIs derive user from `frappe.session.user`.
- [ ] Students cannot access operational dashboard APIs.
- [ ] Teacher/admin actions validate roles server-side.
- [ ] Jitsi room context is returned only after backend permission checks.
- [ ] WhatsApp preview/send/test methods do not expose provider secrets.

## Backup And Restore Checklist

- [ ] Pre-go-live backup is created.
- [ ] Scheduled backups are configured.
- [ ] Private files are covered when needed.
- [ ] Backup storage is outside Git and access-controlled.
- [ ] Restore test has been completed on non-production.
- [ ] Restore owner and procedure are known.

## Domain And HTTPS Checklist

- [ ] DNS points to production infrastructure.
- [ ] HTTPS certificate is valid.
- [ ] Certificate renewal is automated or operationally scheduled.
- [ ] HTTP redirects to HTTPS where appropriate.
- [ ] Reverse proxy handles WebSocket requirements when socketio is used.
- [ ] Private files are not unintentionally exposed by Nginx.

## Operational Handoff Checklist

- [ ] Professor account is ready and does not use `Administrator`.
- [ ] Operational admin account is ready.
- [ ] Integration/bot account, if used, has minimal scope.
- [ ] Support process for blocked/expired access is documented.
- [ ] Runbook owner knows deploy, rollback, backup, and restore steps.
- [ ] Incident contact path is known.
- [ ] Future work is tracked for production Jitsi decision, backup automation
      hardening, CI, and any Docker evaluation.
