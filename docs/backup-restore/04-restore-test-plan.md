# Restore Test Plan

This test plan validates that Melura backups can be restored without touching
production. Use local or staging/test data unless production data use is
approved, minimized, and protected.

## Test Objective

Confirm that a backup can restore the database and files into an isolated test
site, that Melura app data is usable, and that secrets and personal data remain
protected during the test.

## Procedure

1. Create a backup from local or staging.

   ```bash
   cd /home/<deploy-user>/frappe-bench
   bench --site <source-site-name> backup --with-files
   ```

2. Create or identify an isolated test site.

   ```bash
   cd /home/<deploy-user>/frappe-bench
   bench new-site <restore-test-site>
   ```

3. Restore the backup into the isolated test site using the restore runbook.

4. Clear cache and restart services as needed.

5. Run smoke tests and record the result.

## Validation Checklist

- [ ] Login works with a safe test account.
- [ ] `melura_lms` appears in the installed app list.
- [ ] Key DocTypes are available, including `Bruce Student Access`,
      `Bruce Live Class`, `Bruce Educational Material`,
      `Bruce ENEM Question`, `Bruce Exercise List`, `Bruce Student Answer`,
      `Bruce Jitsi Settings`, `Bruce Evolution Settings`, and
      `Bruce WhatsApp Notification Log`.
- [ ] Student access records exist and statuses such as `Ativo`, `Pendente`,
      `Bloqueado`, and `Expirado` behave as expected.
- [ ] Live class records load and do not expose unauthorized room data.
- [ ] Materials, exercise lists, ENEM questions, student answers, and progress
      records are present when expected.
- [ ] WhatsApp settings do not expose Evolution API keys, tokens, auth headers,
      webhook secrets, or full provider credentials.
- [ ] Jitsi settings are present and use test-safe configuration.
- [ ] Privacy-sensitive logs are present only for authorized users and do not
      expose secrets or unnecessary personal data.
- [ ] Smoke tests cover `Minha Aula`, `Painel do Professor`,
      `Painel Operacional`, live-room context, and WhatsApp configuration test
      behavior.
- [ ] Backup retention and encryption expectations are reviewed for the tested
      artifacts.
- [ ] Rollback procedure for the test site is known.

## Result Record

Record outside public Git when details include site names, users, artifacts, or
personal data:

- test date;
- source environment;
- target environment;
- app versions;
- backup timestamp;
- whether database restore passed;
- whether file restore passed;
- smoke test result;
- errors or warnings;
- operator;
- next action.

## Future Automation

A future CI job may run repository-only documentation validation, but real
restore tests should remain a controlled staging procedure because they require
bench, database, files, and environment-specific safeguards.

