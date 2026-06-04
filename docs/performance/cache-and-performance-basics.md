# Cache and Performance Basics

This document defines the first cache and performance rules for Melura. The
goal is to reduce repeated safe lookups without creating permission leaks,
cross-student data exposure, stale access decisions, or secret exposure.

## Principles

- Correct permissions are more important than speed.
- Backend authorization must run before any protected response is returned.
- Do not cache sensitive student data globally.
- Do not cache provider secrets, payloads, logs, recipient data, or message
  bodies.
- Prefer short TTLs and explicit invalidation for operational settings.
- If a cache key cannot be proven safe, do not add the cache.

## Safe To Cache

The following data can be cached when it is non-secret and does not depend on a
student's access scope:

- non-secret Jitsi public settings such as `domain` and `room_prefix`;
- non-sensitive static configuration;
- pure helper computations that do not depend on the logged-in user;
- small public metadata that is the same for every permitted caller;
- short-lived admin aggregates only after the caller role is checked and only
  when the response does not expose personal data.

The current implementation caches only public Jitsi settings.

## Do Not Cache Globally

Never add a global cache for:

- `Minha Aula` dashboard context;
- student progress;
- student answers;
- student access status;
- exercise list context for a student;
- live-room context for a student;
- WhatsApp notification logs;
- WhatsApp previews;
- Evolution API or n8n provider configuration that includes endpoint details
  or operational secrets;
- any response that includes phone, email, recipient, message body, access
  status, answer data, Jitsi room access context, or private file references.

`Bruce Student Access` remains the access source of truth. Its status must be
read fresh for protected student flows unless a future cache is explicitly
scoped to the authenticated user and invalidated on every relevant access
change.

## Cache Key Naming

Use `melura_lms.services.cache.build_cache_key` for global safe keys. Keys must
start with:

```text
melura_lms:v1:
```

Key parts should describe the domain and scope, for example:

```text
melura_lms:v1:jitsi-settings:public
```

Do not place secrets in key parts. The helper rejects obvious sensitive token
names such as `api_key`, `token`, `password`, `authorization`, and `secret`.

## User-Scoped Keys

If student-specific cache is ever added, use
`melura_lms.services.cache.build_user_cache_key`. It must include the
authenticated user from `frappe.session.user`, not a request parameter.

User-scoped keys must also include every relevant permission scope, such as
course, batch, list, class, or material:

```text
melura_lms:v1:user:<frappe.session.user>:course:<course>:batch:<batch>:...
```

Do not accept `student_user`, `user`, `student`, `course`, or `batch` from the
frontend as trusted cache scope. The backend must resolve the current user and
allowed scope first.

## Admin Aggregate Cache

Admin aggregate data may be cached only when all of these are true:

- the whitelisted method checks the caller's admin or operational role before
  reading or returning cached data;
- the cached payload contains aggregate counts only, not names, phones, emails,
  answer rows, message bodies, or recipient details;
- the TTL is short, normally 60 to 300 seconds;
- stale data would not affect authorization or student access decisions.

If an aggregate includes inactive student lists, student names, emails, or
support details, keep it uncached unless the cache key is tightly scoped and the
privacy impact is reviewed.

## Redis And Service Assumptions

Frappe cache APIs normally use Redis in a bench environment. Development and
production should run the Redis services expected by Frappe Bench.

The Melura helper wraps `frappe.cache()` and fails closed: if the cache backend
is unavailable, reads return `None`, writes/deletes return `False`, and the
caller computes the value normally. Tests can inject a fake cache backend and do
not require a real Redis server.

Production readiness should still validate:

- Redis is running and reachable by the site;
- cache eviction does not break page behavior;
- `bench --site <site> clear-cache` clears stale app data as expected;
- no secret or student payload is visible in cache inspection tools.

## Current Cached Function

`BruceLiveClass.get_jitsi_settings()` caches only:

- `Bruce Jitsi Settings.domain`;
- `Bruce Jitsi Settings.room_prefix`.

The key is:

```text
melura_lms:v1:jitsi-settings:public
```

The TTL is 300 seconds. `BruceJitsiSettings.validate()` deletes this key when
the settings document is saved.

## Intentionally Not Optimized Yet

This feature intentionally does not optimize:

- student dashboard queries;
- student access checks;
- student progress calculations;
- exercise list/question payloads for students;
- live-room authorization context;
- WhatsApp recipient resolution, previews, sends, provider settings, or logs;
- operational dashboard aggregates that include inactive student details;
- database indexes, query rewrites, background precomputation, or denormalized
  reporting tables.

Those areas can be revisited only after permission-safe scopes, invalidation
rules, and privacy impact are defined.
