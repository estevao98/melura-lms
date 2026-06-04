# VPS Setup Notes

These notes are high-level guidance for preparing a VPS for a Frappe bench that
hosts Melura LMS. They are not a complete infrastructure automation script.
Adapt them to the chosen hosting provider, operating system, Frappe version,
and operator policy.

## System Packages

Install the packages required by the selected Frappe bench version, typically
covering:

- Python and development headers;
- MariaDB or the database engine supported by the bench;
- Redis;
- Node.js and Yarn;
- Nginx or another reverse proxy;
- supervisor/systemd support as required by the bench;
- build tools and common libraries required by Frappe;
- backup and certificate tooling.

Use the official Frappe/bench installation guidance for exact package names and
versions. Do not copy local machine assumptions into production.

## Non-Root Deploy User

Create a dedicated deploy user for the bench.

Expected rules:

- do not run the bench as root;
- keep SSH access limited to authorized operators;
- give sudo only when required for service management;
- keep the bench directory owned by the deploy user;
- separate technical maintenance accounts from professor and operational admin
  accounts inside Frappe.

## SSH Key Access

Use SSH keys instead of password-only login where possible.

Recommended checks:

- disable unused keys;
- rotate keys when an operator leaves;
- avoid committing private keys or SSH configs with real host details;
- document emergency access outside this repository.

## Firewall Assumptions

Expose only the services required for production access.

Common pattern:

- SSH from approved operator networks;
- HTTP/HTTPS to the reverse proxy;
- database and Redis bound locally or to a private network only;
- no public Redis;
- no public database port.

Do not hard-code the operator's personal IP address in repository docs.

## Swap And Resources

Small VPS instances can fail during builds or migrations if memory is too low.
Plan CPU, RAM, disk, and swap for:

- Frappe web process;
- workers;
- scheduler;
- Redis services;
- database;
- build process;
- backups and restore tests.

Monitor disk usage because Frappe files, logs, and backups can grow quickly.

## ARM VPS Caution

ARM instances can be cost-effective, but some package versions, wheels, Node
tooling, or Frappe dependencies may behave differently from x86_64. Validate
the full install, build, migration, backup, restore, and worker flow before
using ARM for production.

## Oracle Always Free And Generic VPS Notes

Oracle Always Free and similar VPS offerings can be useful for staging or small
production workloads, but confirm:

- resource limits;
- disk persistence and backup behavior;
- outbound email/network restrictions;
- firewall and security list configuration;
- ARM versus x86_64 architecture;
- provider maintenance and recovery expectations.

Do not place provider-specific credentials, tenancy identifiers, public IPs, or
real domains in this repository.
