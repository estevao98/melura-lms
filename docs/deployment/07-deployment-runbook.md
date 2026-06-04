# Deployment Runbook

This runbook is a safe template. Replace placeholders in the operator's private
deployment notes, not in committed documentation.

## Pre-Deploy Checks

```bash
cd /home/<deploy-user>/frappe-bench/apps/melura_lms
git status --short
git branch --show-current
```

Check:

- target branch or tag is correct;
- no secrets or production-local files are in Git;
- backup plan is ready for risky changes;
- migration need is known;
- rollback commit or release is known.

## Pull Latest Code

```bash
cd /home/<deploy-user>/frappe-bench
git -C apps/melura_lms pull --ff-only
```

If the deployment process uses releases instead of `git pull`, use the approved
release fetch step.

## Install Or Update App Dependencies

Use the dependency update process required by the installed Frappe bench.

```bash
cd /home/<deploy-user>/frappe-bench
bench setup requirements
```

This feature adds no external dependencies.

## Build Assets

```bash
cd /home/<deploy-user>/frappe-bench
bench build --app melura_lms
```

Review build failures before continuing. Do not ignore build errors.

## Migrate Only When Needed

Run migration only when schema, DocType, fixture, patch, hook, or app metadata
changes require it.

```bash
cd /home/<deploy-user>/frappe-bench
bench --site <site> migrate
```

This deployment-readiness documentation feature does not require migration.

## Clear Cache

```bash
cd /home/<deploy-user>/frappe-bench
bench --site <site> clear-cache
bench --site <site> clear-website-cache
```

## Restart Services

Use the process manager configured for the bench:

```bash
sudo supervisorctl restart <bench-process-group>:*
```

or:

```bash
sudo systemctl restart <service-name>
```

Use the real service names only in private operational notes.

## Smoke Tests

After deploy:

- open the login page over HTTPS;
- log in as a non-`Administrator` operational user;
- open `Minha Aula` with an active test student;
- confirm blocked/expired access does not unlock content;
- open `Painel do Professor` as an authorized teacher;
- open `Painel Operacional` as an authorized operational admin;
- validate Google Meet launch context for an authorized class;
- confirm WhatsApp configuration test does not expose `EVOLUTION_API_KEY`;
- confirm external student status webhook secret is configured outside Git when
  the integration is enabled;
- confirm missing or invalid external status webhook signatures fail closed;
- inspect web, worker, scheduler, socketio, Redis, database, and Nginx logs.

Use test or anonymized data outside production. When testing production, avoid
real provider sends unless explicitly approved.

## Rollback Notes

Rollback is easiest before migrations and data changes. If a migration has
changed data, rollback may require a restore or a forward fix.

Prepare:

- previous commit or release identifier;
- pre-deploy database backup;
- private files backup when relevant;
- command sequence for rebuilding assets and clearing cache;
- decision owner for restoring production data.

Example placeholder:

```bash
cd /home/<deploy-user>/frappe-bench
git -C apps/melura_lms checkout <previous-release>
bench build --app melura_lms
bench --site <site> clear-cache
bench --site <site> clear-website-cache
```

Avoid destructive rollback commands unless the operator has confirmed the plan
and backup state.
