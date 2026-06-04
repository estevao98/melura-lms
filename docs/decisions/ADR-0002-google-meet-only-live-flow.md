# ADR-0002: Google Meet Only Live Flow

## Status

Accepted.

## Decision

Google Meet external link is the only live-class video path for Melura MVP.

## Reason

Melura targets zero live-video infrastructure cost. The product owns the
pedagogical flow before and after class, while the video call itself opens
outside Melura in Google Meet.

## Consequences

- no embedded call UI;
- no video SDK;
- no provider API;
- no self-hosted video infra;
- no automatic creation of new Google Meet rooms by API;
- Google Meet URLs are configured as external links;
- automation happens inside Melura around scheduling, reminders, permissions,
  and notifications.

## Operational Model

- each course/batch can have a default Google Meet URL;
- Melura generates class records automatically from schedule rules;
- Melura sends reminders before the class;
- professor receives a class-start reminder;
- students receive the link only when allowed by access rules.
