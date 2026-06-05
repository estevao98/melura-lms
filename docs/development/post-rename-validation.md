# Post-Rename Validation

This checklist validates the app after the legacy `Bruce ...` technical
DocTypes were migrated to `Melura ...` technical DocTypes.

## Source Of Truth

The current technical DocTypes are the source of truth:

- `Melura Live Class`
- `Melura Student Access`
- `Melura WhatsApp Settings`
- `Melura WhatsApp Message Template`
- `Melura WhatsApp Notification Log`
- `Melura Educational Material`
- `Melura ENEM Question`
- `Melura Exercise List`
- `Melura Student Answer`

Remaining `bruce-*` references should be limited to temporary compatibility
routes, compatibility page module folders, visual-only CSS selectors, and
historical migration documentation.

## Manual Checks

Open these routes after `migrate`, cache clear, and build:

- `/app/melura`
- `/app/melura-live-class`
- `/app/melura-student-access`
- `/app/melura-whatsapp-settings`
- `/app/melura-educational-material`
- `/app/melura-enem-question`
- `/app/melura-exercise-list`
- `/app/melura-student-answer`
- `/app/melura-live-room/BLC-2026-00017`
- `/app/melura-professor-dashboard`
- `/app/melura-operational-dashboard`

Confirm these old compatibility pages still work if intentionally preserved:

- `/app/bruce-live-room/BLC-2026-00017`
- `/app/bruce-professor-dashboard`
- `/app/bruce-operational-dashboard`

## Expected Results

- New generated live-room links use `/app/melura-live-room/<class>`.
- Student access checks query `Melura Student Access`.
- Live-class services query and update `Melura Live Class`.
- WhatsApp settings, templates, and logs use `Melura WhatsApp ...` DocTypes.
- Content access uses `Melura Educational Material`,
  `Melura ENEM Question`, `Melura Exercise List`, and
  `Melura Student Answer`.
- No page exposes `Bruce` in user-facing labels.
- Compatibility pages keep the same backend permission checks as Melura pages.

## Future Cleanup

After production/staging links have been audited and no old links are needed,
the compatibility routes and visual-only `bruce-*` CSS selectors can be removed
in a separate cleanup. That cleanup must not delete data and must include route
validation before removal.
