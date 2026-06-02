# Bruce SaaS Design System

## 1. Introduction

The Bruce SaaS Design System is the product design layer for `bruce_lms_custom`.
It defines how custom interfaces should look, behave, communicate, and scale
inside a Frappe LMS ecosystem for an online Humanities/ENEM course with live
classes, educational materials, exercise lists, student progress, WhatsApp
operations, and operational dashboards.

This is not a replacement for Frappe, Frappe LMS, or Frappe UI.

- Frappe, Frappe LMS, and Frappe UI are the base layer.
- The Bruce SaaS Design System is the product layer: product rules, UX patterns,
  visual rules, educational flows, status language, mobile behavior, operational
  patterns, and consistency guidance.
- Future product-specific themes can be added on top of this layer for other
  SaaS products, but this document focuses on the Bruce LMS product.

Use Frappe Desk for teacher and operational admin tasks whenever it creates a
clear and maintainable workflow. Use Frappe UI components whenever they solve
the interaction well. Custom UI should exist only when Desk creates a poor user
experience, especially for students on mobile.

The design system exists to keep the product consistent as it grows. It should
help Codex and future developers avoid breaking typography, colors, menus,
cards, spacing, hierarchy, mobile layout, accessibility, permissions, and UX
consistency.

The central rule:

> The student should not feel like they are using the administrative Desk.

This document is the source of truth before improving the paused mobile student
portal again.

## 2. Product Principles

- Students are mobile-first. Design student flows for small phones before large
  desktop screens.
- Teachers and operational admins are desktop-first. Their work usually happens
  in Desk, forms, logs, dashboards, and support views.
- Keep one primary action per screen or major block.
- User-facing visible text must be in Brazilian Portuguese.
- Markdown documentation must be written in English from now on.
- Do not show technical details to students or teachers.
- Permissions must always be validated on the backend.
- Status must always use text, not color alone.
- Every critical screen must have empty, loading, and error states.
- Do not break Frappe patterns without a clear product or usability reason.
- Do not modify `frappe/`, `lms/`, `frappe-ui/`, or `jitsi-meet/` directly.
- Prefer boring consistency over visually impressive inconsistency.
- Custom CSS must be scoped and token-based.
- The student should never feel like they are inside an admin system.
- The teacher should never need to understand `room_name`, Jitsi internals,
  webhook payloads, API keys, or stack traces to run a class.
- The operational admin should see actionable operational signals, not vanity
  metrics.
- Financial operations do not belong in the pedagogical LMS core unless they are
  explicitly implemented later.

## 3. User Groups

### 3.1 Student

The student wants to:

- enter the live class;
- access educational materials;
- answer exercise lists;
- see progress;
- understand access status;
- know what to do when access is unavailable.

The student should not see:

- `DocType`;
- logs;
- payloads;
- `room_name`;
- API keys;
- webhook names or URLs;
- stack traces;
- internal IDs;
- technical status;
- raw permission names;
- implementation errors.

The interface that fits the student:

- mobile-first;
- one-column layout;
- clear cards;
- large buttons;
- short copy;
- visible access status;
- strong primary action, such as `Entrar na aula`;
- no dense tables;
- no default Desk-like navigation in custom student pages.

UX mistakes to avoid:

- hidden action buttons;
- empty menus;
- small buttons;
- too much scrolling before the main action;
- technical messages;
- links that unexpectedly send the student to external systems;
- showing copied external Jitsi links as the main path when an embedded live room
  exists;
- using desktop table layouts as the primary mobile experience.

Student-facing examples must stay in Brazilian Portuguese:

- `Entrar na aula`
- `Copiar link`
- `Meu progresso`
- `Nenhum material disponível no momento.`
- `Seu acesso está bloqueado. Fale com o suporte.`

### 3.2 Teacher

The teacher wants to:

- see the next class;
- start class;
- open room;
- copy link when needed;
- preview WhatsApp messages;
- publish material;
- create ENEM questions and exercise lists;
- view class progress;
- identify inactive students;
- understand communication failures without reading technical logs.

The teacher should not see:

- API keys;
- raw payloads;
- endpoints;
- stack traces;
- technical configuration unless needed for a specific operational reason;
- generated technical room names as editable required fields.

The interface that fits the teacher:

- Desk-based dashboard;
- clear cards;
- actionable status;
- short lists;
- minimal technical noise;
- direct actions such as `Iniciar aula`, `Abrir sala`, `Copiar link`,
  `Pré-visualizar WhatsApp`, and `Enviar aviso`;
- forms grouped by meaning, not by internal implementation.

UX mistakes to avoid:

- too many equal-weight buttons;
- operational actions hidden behind technical forms;
- unclear class status;
- making the teacher manually fill technical room names;
- making WhatsApp errors look like developer errors;
- relying on `Administrator` as the teacher's operational user.

### 3.3 Operational Admin

The operational admin wants to:

- monitor operation health;
- see students by status;
- see classes, materials, ENEM questions, exercise lists, answers, and progress;
- identify operational alerts;
- access logs when needed;
- support students and the teacher without seeing secrets unnecessarily.

The admin should not see:

- financial dashboards inside the pedagogical core unless explicitly implemented
  later;
- unnecessary raw payloads in normal views;
- API keys or tokens in browser-rendered screens.

The interface that fits the operational admin:

- Desk dashboard;
- KPI cards;
- alert sections;
- tables when useful;
- filters for growing datasets;
- links to DocTypes;
- concise operational logs.

UX mistakes to avoid:

- mixing financial operations with pedagogical operations;
- hiding operational problems;
- dashboards with metrics that do not lead to action;
- showing raw integration details by default;
- giving students or teachers access to admin dashboards.

### 3.4 Developer / Technical Operator

Developers and technical operators need:

- clear rules;
- safe customization boundaries;
- scoped CSS;
- backend permission checks;
- documentation in English;
- predictable names;
- status names and user-facing copy preserved in Brazilian Portuguese;
- a clear distinction between current functionality and future work.

They must avoid:

- changing core apps;
- exposing secrets;
- trusting the frontend for access control;
- adding hardcoded colors everywhere;
- creating inconsistent custom pages;
- creating a parallel component system when Frappe UI already solves the need;
- adding global CSS that breaks Desk.

## 4. Visual Personality

The product personality is:

- educational;
- trustworthy;
- simple;
- modern;
- operational;
- lightweight B2B SaaS;
- calm;
- readable;
- not childish;
- not gamer-like;
- not heavy corporate.

The desired visual feel:

- clean cards;
- clear hierarchy;
- few colors;
- strong primary actions;
- visible status;
- useful dashboards;
- calm interface density;
- readable content;
- practical educational workflow.

Use visual emphasis to answer operational questions:

- What is the next class?
- Can the student enter now?
- Is access active?
- What material is available?
- Which exercise list needs an answer?
- Which students are inactive?
- Which operational alerts require action?

Avoid:

- serif fonts in the app UI;
- neon-heavy visuals;
- tiny mobile buttons;
- dense tables for students;
- empty menus;
- technical copy;
- colors scattered without tokens;
- inconsistent layouts across screens;
- mobile students navigating through Desk-like UI;
- decorative visuals that compete with class, material, or progress information.

## 5. Relationship With Frappe, Frappe LMS, and Frappe UI

Use Frappe Desk for:

- teacher dashboards;
- operational admin dashboards;
- DocTypes;
- logs;
- forms;
- settings;
- support views;
- technical and operational configuration;
- controlled administrative workflows.

Use custom portal UI for:

- student mobile experiences;
- `Minha Aula`;
- embedded live room;
- future PWA screens;
- future Capacitor app shell;
- mobile-first student flows;
- highly simplified educational flows.

Use Frappe UI components whenever possible:

- buttons;
- cards;
- alerts;
- dialogs;
- fields;
- select controls;
- tables;
- badges;
- tabs;
- skeleton/loading patterns where available.

Do not create a custom component if a Frappe UI component solves the problem
well.

Create custom UI only for:

- student portal;
- embedded live room;
- PWA;
- Capacitor app shell;
- mobile-first experiences;
- highly simplified student flows;
- cases where Desk would make the product feel like an administrative system to
  students.

Decision guide:

| Question | Decision |
| --- | --- |
| Is the user a teacher or operational admin doing an operational task? | Use Desk first. |
| Is the user a student doing a mobile-first task? | Use custom UI. |
| Does Frappe UI already provide the component? | Use Frappe UI. |
| Does the flow need custom CSS? | Scope it and use tokens. |
| Is the task a DocType form, log, setting, or support view? | Use Desk. |
| Would Desk navigation confuse or intimidate a student? | Build a custom student experience. |

Central rule:

> The student should not feel like they are using the administrative Desk.

## 6. Design Tokens

Tokens are conceptual values that can later become CSS variables. Do not create
CSS files in this task. These references are future implementation guidance for:

`bruce_lms_custom/public/css/bruce_tokens.css`

Future token categories:

- colors;
- light theme;
- dark theme;
- typography;
- spacing;
- radius;
- shadows;
- z-index;
- breakpoints;
- minimum touch sizes.

### 6.1 Color Categories

Use these categories instead of hardcoded one-off colors:

- `primary`: main product action and brand emphasis;
- `background`: page background;
- `surface`: cards and panels;
- `surface-muted`: subtle blocks and secondary backgrounds;
- `border`: borders and dividers;
- `text`: primary readable text;
- `text-muted`: secondary text;
- `text-soft`: tertiary text and placeholders;
- `success`: completed or healthy status;
- `warning`: attention needed;
- `danger`: destructive, blocked, failed, or critical status;
- `info`: neutral guidance.

### 6.2 Light Theme Reference

Future CSS reference only:

```css
:root {
  --bruce-color-primary-50: #eff6ff;
  --bruce-color-primary-100: #dbeafe;
  --bruce-color-primary-200: #bfdbfe;
  --bruce-color-primary-300: #93c5fd;
  --bruce-color-primary-400: #60a5fa;
  --bruce-color-primary-500: #3b82f6;
  --bruce-color-primary-600: #2563eb;
  --bruce-color-primary-700: #1d4ed8;
  --bruce-color-primary-800: #1e40af;
  --bruce-color-primary-900: #1e3a8a;

  --bruce-color-bg: #f8fafc;
  --bruce-color-surface: #ffffff;
  --bruce-color-surface-muted: #f1f5f9;
  --bruce-color-border: #e2e8f0;

  --bruce-color-text: #0f172a;
  --bruce-color-text-muted: #64748b;
  --bruce-color-text-soft: #94a3b8;
}
```

### 6.3 Dark Theme Reference

Future CSS reference only:

```css
[data-bruce-theme="dark"] {
  --bruce-color-bg: #020617;
  --bruce-color-surface: #0f172a;
  --bruce-color-surface-muted: #111827;
  --bruce-color-border: #1e293b;

  --bruce-color-text: #f8fafc;
  --bruce-color-text-muted: #cbd5e1;
  --bruce-color-text-soft: #94a3b8;

  --bruce-color-primary-600: #60a5fa;
  --bruce-color-primary-700: #3b82f6;
}
```

### 6.4 Typography

Use this font stack:

```css
font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
```

Rules:

- Student mobile UI should use at least `16px` for body text.
- Teacher/admin UI can use `14px` to `16px` depending on density.
- Never use serif fonts for the main UI.
- Do not use tiny text for critical status, access, or class information.
- Avoid long paragraphs in mobile flows.

Typography scale:

| Token | Size / Line height / Weight |
| --- | --- |
| Display | 40px / 48px / 700 |
| H1 | 32px / 40px / 700 |
| H2 | 24px / 32px / 700 |
| H3 | 20px / 28px / 600 |
| Body | 16px / 24px / 400 |
| Small | 14px / 20px / 400 |
| Caption | 12px / 16px / 500 |

### 6.5 Spacing

Use this spacing scale:

```text
4, 8, 12, 16, 20, 24, 32, 40, 48, 64
```

Rules:

- Avoid arbitrary spacing such as `17px`, `23px`, or `37px` unless there is a
  strong reason.
- Student mobile pages should feel open enough to tap and scan.
- Teacher/admin dashboards can be denser but must remain readable.
- Use consistent vertical rhythm between cards, sections, headers, and actions.

### 6.6 Radius

| Token | Value |
| --- | --- |
| `sm` | 6px |
| `md` | 10px |
| `lg` | 14px |
| `xl` | 20px |
| `full` | 999px |

Rules:

- Cards should not look overly playful.
- Use rounded corners consistently.
- Do not mix many radius values in the same screen.

### 6.7 Shadows

Rules:

- Use subtle shadows only.
- Cards should not look heavy.
- Avoid excessive blur or dramatic depth.
- Prefer borders and spacing before heavy shadows.

### 6.8 Z-Index

Future token categories:

| Token | Use |
| --- | --- |
| `base` | normal page content |
| `sticky` | sticky topbars |
| `dropdown` | menus and popovers |
| `modal` | dialogs |
| `toast` | temporary feedback |

Rules:

- Do not solve layout problems by adding arbitrary high z-index values.
- Embedded Jitsi screens must not be covered by unrelated UI.
- Dialogs must trap focus and remain above the page content.

### 6.9 Breakpoints and Touch Size

Breakpoints should be mobile-first for custom pages.

Rules:

- Test small phones first.
- Test desktop width for teacher/admin dashboards.
- Clickable mobile areas should be at least `44px` by `44px`.
- Use one-column cards on mobile.
- Avoid horizontal tables for student-facing pages.
- Keep critical content above the fold when possible.

Required test targets:

- 1366x768 desktop;
- iPhone SE-sized viewport;
- iPhone 12/13-sized viewport;
- common Pixel/Galaxy-sized viewport.

## 7. Core Components

This section documents product rules. It does not claim that custom components
already exist.

### 7.1 Button

Use buttons for clear commands.

Variants:

- Primary;
- Secondary;
- Ghost;
- Danger;
- Link.

When to use:

- Primary: the main action on a screen or major block.
- Secondary: useful action that is not the main path.
- Ghost: low-emphasis interface action.
- Danger: blocking, deleting, canceling, ending, or destructive actions.
- Link: navigation-style action or low-emphasis external fallback.

When not to use:

- Do not use a button for static status.
- Do not use many primary buttons in the same block.
- Do not use Danger for ordinary navigation.

UX rules:

- One primary action per screen or major block.
- Danger actions require confirmation.
- Sensitive actions require confirmation.
- Disabled buttons must explain why they are disabled.
- Mobile buttons must be easy to tap.
- Labels must use clear verbs.
- Icon-only buttons need an accessible label.

Product examples:

| Context | Variant | Label |
| --- | --- | --- |
| Student primary | Primary | `Entrar na aula` |
| Student secondary | Secondary | `Copiar link` |
| Teacher primary | Primary | `Iniciar aula` |
| Teacher secondary | Secondary | `Pré-visualizar WhatsApp` |
| Teacher secondary | Secondary | `Abrir sala` |
| Teacher secondary | Secondary | `Enviar aviso` |
| Admin danger | Danger | `Bloquear aluno` |

### 7.2 Card

Use cards for:

- next class;
- material;
- exercise list;
- student progress;
- KPI;
- operational alert.

Card structure:

- eyebrow;
- title;
- short description;
- metadata;
- action.

When not to use:

- Do not use cards as fake tables.
- Do not place too many unrelated actions in one card.
- Do not nest cards inside cards.

UX rules:

- Student cards must be simple and large.
- Admin metric cards can be denser.
- Cards should not become tables.
- Keep the main action visible.
- Use predictable metadata order, such as course, class, date, status.

Product examples:

- `Próxima aula` card for `Minha Aula`;
- `Material` card for `Apostila`, `Resumo`, or `PDF`;
- `Lista de exercícios` card with number of questions and due date;
- `Meu progresso` card with answered questions and accuracy;
- `Alunos ativos` KPI card in `Painel Operacional`.

### 7.3 Badge

Use badges for short status labels.

Mandatory status examples:

- `Ativo`
- `Pendente`
- `Bloqueado`
- `Expirado`
- `Agendada`
- `Ao vivo`
- `Encerrada`
- `Cancelada`
- `Publicado`
- `Rascunho`
- `Enviado`
- `Falhou`
- `Reenviado`

Rules:

- Always use text and color.
- Never rely on color alone.
- Status text must be in Brazilian Portuguese.
- Use consistent color semantics across the product.
- Do not invent a new status label when an existing status fits.

### 7.4 Alert

Use alerts for important feedback that needs attention.

Types:

- Info;
- Success;
- Warning;
- Error.

Examples:

- Info: `A aula ainda não começou.`
- Success: `Material publicado com sucesso.`
- Warning: `Este aluno está sem atividade há 7 dias.`
- Error: `Você não tem permissão para acessar esta aula.`

Rules:

- Alerts must be short and actionable.
- Error alerts must not expose stack traces or secrets.
- Alerts on student screens should explain what to do next.
- Alerts should not replace backend validation.

### 7.5 Empty State

Every list or dashboard section must have an empty state.

Examples:

- `Nenhuma aula agendada.`
- `Nenhum material disponível no momento.`
- `Nenhuma lista de exercícios publicada.`
- `Nenhuma resposta registrada.`
- `Nenhum alerta operacional identificado.`

Structure:

- simple icon or visual marker;
- title;
- short explanation;
- optional action.

Rules:

- Empty states are not errors.
- Use calm language.
- Do not leave blank dashboard sections.
- Student empty states should explain whether there is nothing available or
  access is not active.

### 7.6 Loading State

Use loading states whenever data is being fetched or an action is running.

Rules:

- Use skeletons for cards.
- Use a small spinner inside buttons.
- Use simple text such as `Carregando...`.
- Never leave a blank screen without feedback.
- Prevent duplicate submits while a sensitive action is running.

### 7.7 Error State

Error states must explain:

- what happened;
- why it may have happened;
- what the user can do next.

Example:

```text
Não foi possível carregar sua aula. Verifique sua conexão e tente novamente.
```

Rules:

- User-facing errors must be in Brazilian Portuguese.
- Do not show `PermissionError`, stack traces, `roomName missing`, payloads, or
  internal identifiers to students or teachers.
- Technical details can appear in logs for authorized technical users.

### 7.8 Modal/Dialog

Use modals/dialogs for:

- confirmations;
- short edits;
- critical actions;
- previews, such as `Pré-visualizar WhatsApp`.

Do not use modals/dialogs for:

- long forms;
- complex flows;
- full pages hidden inside a modal;
- embedded live rooms.

Rules:

- Sensitive actions require confirmation.
- Dialogs must support keyboard navigation.
- Dialog titles must be clear.
- Primary and cancel actions must be visually distinct.

### 7.9 Table

Use tables for:

- admin logs;
- operational data;
- dense teacher/admin records;
- support views.

Do not use tables for:

- primary student mobile experience.

Rules:

- Tables need empty states.
- Tables need filters when data grows.
- Avoid horizontal scrolling for student-facing pages.
- Use human-readable values, not raw payloads.
- Keep action columns concise.

### 7.10 Filter Bar

Use filter bars for:

- admin dashboards;
- logs;
- student status lists;
- content management;
- materials, questions, lists, and answers when data grows.

Do not overuse filters in teacher/student flows.

Rules:

- Filters must match real operational decisions.
- Keep defaults useful.
- Do not expose technical fields as primary filters unless the screen is
  technical.

### 7.11 Metric Card

Use metric cards for:

- total active students;
- blocked students;
- classes this week;
- published materials;
- published exercise lists;
- average progress.

Rules:

- Each metric must lead to action or insight.
- Avoid vanity metrics.
- Use short labels.
- Include status or trend only when it helps the operator decide what to check.

### 7.12 Activity Feed

Use activity feeds for:

- class notice history;
- recent operational actions;
- recent student activity;
- events such as `Link copiado`, `Aula iniciada`, `Falha de envio`, and
  `Pré-visualização de WhatsApp gerada`.

Rules:

- Show human-readable events.
- Do not expose raw payloads.
- Include actor, date/time, and short result when useful.
- Keep technical detail in logs, not in the main feed.

### 7.13 Page Header

Structure:

- title;
- short description;
- primary action when needed;
- optional metadata.

Rules:

- Student page headers should be compact.
- Teacher/admin page headers can include operational context.
- Avoid generic headings when product-specific names exist, such as
  `Minha Aula`, `Painel do Professor`, and `Painel Operacional`.

### 7.14 Navigation/Menu

Rules:

- Never create an empty menu.
- Menu items must be useful and tested.
- Student mobile menu must be custom, not the default Frappe Desk menu.
- Professor/admin can use Desk navigation.
- Menu visibility is not security. Backend must validate access.
- Do not add menu links to future features until there is a useful destination.

### 7.15 Tabs

Use tabs for:

- dashboard sections;
- content grouping;
- admin views.

Do not use tabs to hide required actions.

Rules:

- Tab labels must be short.
- The default tab should answer the most common question.
- On mobile, ensure tabs do not create cramped horizontal navigation.

### 7.16 Form Section

Use form sections for grouping fields in DocTypes and custom forms.

Suggested sections:

- main information;
- pedagogical scope;
- publication;
- optional settings;
- comments/log.

Examples:

- `Bruce Live Class`: main information, pedagogical scope, Jitsi data, WhatsApp,
  history.
- `Bruce Educational Material`: main information, pedagogical scope,
  publication, attachment.
- `Bruce ENEM Question`: main information, classification, alternatives, answer
  key, commented resolution, publication.
- `Bruce Student Access`: student, scope, status, access window, external
  reference.

## 8. Page Patterns

### 8.1 Dashboard

Structure:

- Page Header;
- short description;
- KPI cards;
- main section;
- short table/list;
- alerts;
- quick actions.

Example: `Painel Operacional`

- active students;
- blocked students;
- classes this week;
- average progress;
- operational alerts.

Rules:

- Dashboards must support action.
- KPIs should answer "what should I check now?"
- Do not include financial operation metrics in the pedagogical dashboard unless
  explicitly implemented later.

### 8.2 List Page

Structure:

- title;
- short description;
- primary action;
- search;
- filters;
- table/list;
- pagination;
- empty state.

Use for:

- admin records;
- materials;
- ENEM questions;
- exercise lists;
- logs;
- student access records.

Rules:

- Use tables for operational density.
- Use cards for student-facing lists.
- Keep filters meaningful.

### 8.3 Form Page

Structure:

- main information;
- pedagogical scope;
- publication;
- optional settings;
- comments/log.

Use for:

- live class;
- material;
- ENEM question;
- exercise list;
- student access.

Rules:

- Ask only for necessary fields.
- The system must generate Jitsi technical room names in the backend.
- Do not force the teacher to fill `room_name`.
- Keep sensitive configuration out of ordinary forms.

### 8.4 Student Mobile Page

Structure:

- custom topbar;
- access status;
- next class;
- materials;
- exercise lists;
- progress;
- help/support.

Rules:

- Do not use default Frappe navbar.
- Do not use default Frappe footer in custom student portal.
- Keep license/credits in repository/documentation when applicable.
- Do not create an empty menu.
- Custom menu must work.
- The main action must be visible without anxiety-inducing scrolling.
- Use one-column cards.
- Keep body text at least `16px`.
- Use buttons at least `44px` high.

Current reference:

- `/app/minha-aula` is the current initial student route.
- It shows live class access, materials, exercise lists, and progress based on
  backend validation and `Bruce Student Access`.

Future:

- A dedicated mobile/PWA student portal can reuse this pattern.

### 8.5 Embedded Live Room

Structure:

- compact header;
- minimal class metadata;
- large Jitsi area;
- fallback button `Abrir em nova aba`;
- no excessive scroll before the video.

Rules:

- Embedded room must prioritize video.
- Jitsi external link is explicit fallback only.
- Do not automatically open `meet.jit.si` in another tab.
- Keep camera/mic permission flow clear.
- Do not place the actual class far below several cards.
- Do not cover Jitsi with unrelated sticky UI.

Current reference:

- `/app/bruce-live-room/<aula>` embeds Jitsi through the Jitsi IFrame API.
- The backend validates user, status, room data, student access, course/batch
  scope, teacher responsibility, or admin role before returning room context.

### 8.6 Operational/Admin Dashboard

Structure:

- overview;
- classes;
- content;
- exercises and progress;
- operational alerts;
- recent logs.

Rules:

- Dashboard shows pedagogical operation health, not financial metrics.
- Every KPI should answer "what should I check now?"
- Use alert sections for missing room/link, inactive students, failed WhatsApp,
  and other operational problems.
- Link from metrics to relevant DocTypes or filtered records when possible.

## 9. Product-Specific Educational Patterns

### 9.1 Live Class

States:

- `Agendada`
- `Ao vivo`
- `Encerrada`
- `Cancelada`

Actions by role:

| Role | Actions |
| --- | --- |
| Student | `Entrar na aula`, `Copiar link` when it makes sense |
| Teacher | `Iniciar aula`, `Abrir sala`, `Copiar link`, `Enviar aviso` |
| Admin | `Ver detalhes`, `Ver logs`, `Corrigir sala` |

Rules:

- Embedded room must prioritize video.
- Do not place the actual class far below several cards.
- External Jitsi must be fallback only.
- The system should generate technical room names, not the teacher.
- `room_name` must be unique and not predictable.
- Backend validates permission and access before returning the live room context.

### 9.2 Educational Material

Types:

- `Apostila`
- `Resumo`
- `Mapa mental`
- `Lista`
- `Simulado`
- `PDF`
- `Outro`

Card should include:

- type;
- title;
- topic;
- related class;
- action: `Abrir` or `Baixar`.

Empty state:

```text
Nenhum material disponível no momento.
```

Rules:

- Student only sees published material with `Aluno` visibility and active
  compatible access.
- Teacher/admin can manage publication and internal materials.
- Do not show unpublished or internal materials to students.

### 9.3 ENEM Question

Visual fields:

- discipline;
- topic;
- difficulty;
- year;
- answer key;
- commented resolution.

Rules:

- Teacher/admin can see answer key and resolution.
- Student should not see answer key/resolution before answering if future
  controlled attempts are implemented.
- Published questions must have a statement and answer key.
- Student APIs must not return answer key or commented resolution in the initial
  student listing.

### 9.4 Exercise List

Card should include:

- title;
- number of questions;
- due date;
- status;
- action: `Responder`.

States:

- `Não iniciada`
- `Em andamento`
- `Respondida`
- `Prazo encerrado`

Rules:

- A published list must have at least one question.
- Student only sees published lists compatible with active access.
- The frontend must not send student, course, or batch to expand access.
- Student answers must be saved for the logged-in user by the backend.

### 9.5 Student Progress

Metrics:

- answered questions;
- correct answers;
- wrong answers;
- accuracy;
- last activity;
- answered lists.

Visual:

- simple cards;
- progress bar;
- no complex chart at first.

Rules:

- Student only sees their own progress.
- Students with `Pendente`, `Bloqueado`, or `Expirado` status do not receive
  pedagogical metrics.
- Teacher/admin progress summaries must be backend-authorized by role and scope.
- Do not create rankings, financial reports, or advanced grade reports unless
  explicitly planned later.

### 9.6 Student Access Control

Statuses:

- `Ativo`
- `Pendente`
- `Bloqueado`
- `Expirado`

Rules:

- `Ativo` can see allowed content.
- `Pendente`, `Bloqueado`, and `Expirado` cannot see pedagogical content.
- The UI must explain what to do.
- Backend always validates.
- Access state must not be trusted only from `localStorage` or frontend state.
- The frontend must not send student, course, or batch parameters to expand
  access.

Example messages:

- `Seu acesso está pendente. Fale com o suporte se precisar de ajuda.`
- `Seu acesso está bloqueado. Fale com o suporte.`
- `Seu acesso expirou. Fale com o suporte para regularizar.`

## 10. Microcopy and Language

Product voice:

- clear;
- short;
- polite;
- no jargon;
- not robotic;
- practical;
- calm.

Documentation language rule:

- Markdown documentation must be written in English.
- User-facing product copy, labels, buttons, alerts, status names, and messages
  must remain in Brazilian Portuguese.
- When documenting user-facing copy examples, keep those examples in Brazilian
  Portuguese and explain them in English.

Good user-facing examples:

- `Sua aula está disponível.`
- `Você ainda não tem materiais publicados.`
- `Seu acesso está bloqueado. Fale com o suporte.`
- `A lista foi respondida com sucesso.`
- `Não encontramos uma aula para sua turma.`
- `A aula ainda não começou.`
- `Nenhum alerta operacional identificado.`

Bad user-facing examples:

- `PermissionError.`
- `Invalid doctype.`
- `roomName missing.`
- `Webhook payload failed.`
- `Student access denied by backend.`

Bad examples may appear in technical logs for authorized operators, but they
must not appear in student or teacher UI.

Student messages should:

- explain availability;
- explain access status;
- give the next step;
- avoid technical detail.

Teacher messages should:

- explain operational state;
- make actions clear;
- avoid integration internals.

Admin messages should:

- show operational signal;
- preserve enough context for support;
- link to logs when needed;
- avoid secrets and raw payloads in normal views.

Success messages:

- `Aula iniciada com sucesso.`
- `Material publicado com sucesso.`
- `A lista foi respondida com sucesso.`
- `Link copiado.`

Blocked access messages:

- `Você não tem permissão para acessar esta aula.`
- `Seu acesso está bloqueado. Fale com o suporte.`
- `Seu progresso ainda não está liberado.`

Error messages:

- `Não foi possível carregar sua aula. Verifique sua conexão e tente novamente.`
- `Não foi possível enviar o aviso pelo WhatsApp. Tente reenviar ou verifique o log.`
- `A aula está cancelada e não pode ser iniciada.`

## 11. Accessibility

Rules:

- Use sufficient contrast.
- Use visible focus states.
- Add `aria-label` for icon-only buttons.
- Form fields must have labels.
- Field errors must be connected to fields.
- Status must include text.
- Dialogs must support keyboard navigation.
- Mobile buttons must be at least `44px` by `44px`.
- Do not rely only on color.
- Dark theme must have real contrast.
- Avoid tiny text for critical information.
- Avoid long paragraphs in mobile flows.
- Do not hide important actions behind hover-only interactions.
- Ensure loading and error states are announced or visible enough for assistive
  technology.

## 12. Responsiveness

Rules:

- Student is mobile-first.
- Teacher/admin is desktop-first.
- Test in 1366x768.
- Test iPhone SE.
- Test iPhone 12/13.
- Test Pixel/Galaxy.
- Do not use horizontal tables for students.
- Use one-column cards on mobile.
- Use large buttons.
- Keep critical content above the fold when possible.
- Embedded live room must keep video visible early.
- Avoid sticky elements that cover primary actions or the Jitsi area.
- Ensure text does not overflow buttons, cards, badges, or mobile nav.

## 13. Light and Dark Theme

Light theme is the initial default.

Dark theme is intended for:

- custom portal;
- future custom screens;
- future PWA;
- future Capacitor app shell.

Rules:

- User preference should be saved in `localStorage` when implemented.
- If no preference exists, respect `prefers-color-scheme`.
- Do not apply custom theme globally to Desk without planning.
- Portal theme must not break Desk.
- All dark theme colors must use tokens.
- Do not hardcode dark colors per component.

Future:

- Implement token-based theme switching for custom contexts only.
- Validate both themes with real pages, not isolated color samples.

## 14. Future CSS Rules

Future token file:

```text
bruce_lms_custom/public/css/bruce_tokens.css
```

Future context-specific CSS files:

```text
student_portal.css
live_room.css
dashboards.css
```

Rules:

- Do not scatter hardcoded colors.
- Use tokens.
- Do not apply tokens globally to Desk in a way that breaks Frappe.
- Custom CSS must be scoped under product context classes.
- Prefer Frappe UI styles when they fit.
- Add CSS only when the interface needs product-specific behavior or layout.

Future scoped classes:

```css
.bruce-student-portal {}
.bruce-live-room {}
.bruce-dashboard {}
.bruce-operational-dashboard {}
```

Do not create these CSS files in this documentation task. They are future
implementation references.

## 15. Visual and UX Security Rules

Frontend does not grant access.

Rules:

- Menu does not decide permission.
- Hiding a button is not security.
- Backend always validates.
- Do not show sensitive data.
- Do not expose token, API key, payload, webhook, stack trace, or internal
  technical errors.
- Links for teacher/admin may be hidden based on role, but backend must still
  validate.
- Student access state must never be trusted only from `localStorage` or
  frontend state.
- Student pages must use the logged-in user from the backend.
- Student pages must not accept frontend parameters to expand course, batch, or
  student access.
- Jitsi room context must be returned only after backend validation.
- WhatsApp sending must happen in the backend or protected n8n flow.
- Logs should help support without becoming a sensitive data dump.

Examples of data that must not appear in student/teacher UI:

- API keys;
- tokens;
- webhook secrets;
- provider auth headers;
- complete integration payloads;
- stack traces;
- raw `room_name` as an editable operational requirement;
- internal permission implementation details.

## 16. Pre-Commit Checklist for New UI

- [ ] User-facing text is in Brazilian Portuguese.
- [ ] Markdown documentation is in English.
- [ ] There is one clear primary action.
- [ ] Frappe UI is used when possible.
- [ ] No component was reinvented without reason.
- [ ] Empty state exists.
- [ ] Loading state exists.
- [ ] Friendly error state exists.
- [ ] Permission is validated on the backend.
- [ ] No technical detail is shown to student/teacher.
- [ ] Works at 1366x768.
- [ ] Works on mobile.
- [ ] Buttons are at least 44px on mobile.
- [ ] Status uses text, not color alone.
- [ ] Dark theme did not break.
- [ ] `frappe/`, `lms/`, `frappe-ui/`, and `jitsi-meet/` were not modified.
- [ ] `/app/minha-aula` still works.
- [ ] `/app/bruce-professor-dashboard` still works.
- [ ] `/app/bruce-operational-dashboard` still works.
- [ ] Embedded live room still works.
- [ ] No empty menu was created.
- [ ] Custom student portal does not use default Frappe navbar/footer.
- [ ] Sensitive information is not exposed.
- [ ] CSS is scoped to the custom context.

## 17. Design System Roadmap

### Phase 1 - Now

- Strong `docs/design-system.md`.
- Documented tokens.
- Button patterns.
- Card patterns.
- Badge patterns.
- State patterns.
- Dashboard patterns.
- Student area patterns.

### Phase 2 - After

- Future: `bruce_tokens.css`.
- Future: refactor mobile portal.
- Future: light/dark theme implementation.
- Future: PWA shell.
- Future: documentation with screenshots.

### Phase 3 - Scale

- Future: Capacitor app shell.
- Future: product-specific themes.
- Future: brand tokens.
- Future: internal component library.
- Future: Storybook-like documentation.
- Future: visual regression tests.

## 18. Recommended Next Steps

1. Future: create `bruce_tokens.css` in a separate feature.
2. Future: apply tokens only to new custom screens first.
3. Future: refactor the paused mobile student portal using this design system.
4. Future: create user documentation with screenshots.
5. Future: add a visual checklist to the PR/commit process.

