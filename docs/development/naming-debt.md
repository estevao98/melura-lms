# Naming Debt

Melura is the public product name. User-facing labels, messages, pages, and
documentation should use Melura or neutral Portuguese names such as `Aula ao
vivo`, `Painel do professor`, `Painel operacional`, and `Configurações de
WhatsApp`.

The `feat/remove-legacy-bruce-technical-naming` migration renamed the legacy
`Bruce ...` technical DocTypes to `Melura ...` DocTypes and moved the matching
DocType Python/JavaScript/test module paths from `bruce_*` to `melura_*`.

The `Melura ...` technical DocTypes are now the source of truth for runtime
code, hooks, fixtures, service helpers, tests, and new documentation.

Migrated DocTypes:

- `Melura Live Class`
- `Melura Student Access`
- `Melura Educational Material`
- `Melura ENEM Question`
- `Melura ENEM Question Alternative`
- `Melura Exercise List`
- `Melura Exercise List Item`
- `Melura Student Answer`
- `Melura WhatsApp Settings`
- `Melura WhatsApp Message Template`
- `Melura WhatsApp Notification Log`
- `Melura Live Class Notice Log`
- `Melura Legacy Video Settings`

Compatibility names kept temporarily:

- `/app/bruce-live-room/<class>`, `/app/bruce-professor-dashboard`, and
  `/app/bruce-operational-dashboard` remain route aliases for existing links.
- `bruce_*` page module folders for those aliases remain as compatibility
  entry points. Preferred Desk routes are `/app/melura-live-room/<class>`,
  `/app/melura-professor-dashboard`, and `/app/melura-operational-dashboard`.
- Existing `bruce-*` CSS classes and CSS-token examples remain compatibility
  selectors until a separate visual cleanup can change templates and styles
  without breaking rendered pages.
- Historical filenames such as `docs/jitsi-integration.md` and
  `docs/integrations/jitsi-production-decision.md` are kept as obsolete
  pointers for old links.
- The migration patch keeps old `Bruce ...` names only as historical source
  names passed to Frappe rename operations.

New generated links, new DocType references, new service code, and new tests
must use the Melura names. Do not add new `Bruce ...` DocTypes or new `bruce_*`
technical modules except when explicitly maintaining the compatibility aliases
listed above.

Post-rename validation lives in
`docs/development/post-rename-validation.md`. Future cleanup may remove
compatibility routes and visual-only `bruce-*` selectors after route/link
validation proves they are no longer needed. That cleanup must be separate from
the technical DocType migration and must not delete data.

`Melura Legacy Video Settings`, `melura_legacy_video_settings`,
`section_break_jitsi`, `column_break_jitsi`, and old cache-key constants are
legacy-video compatibility names. They exist only because the MVP uses Google
Meet external links and older video-provider configuration must not become a
new active video path.
