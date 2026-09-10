# Changelog

All notable changes to the NeoEngineering app. Versioning follows
[SemVer](https://semver.org): MAJOR.MINOR.PATCH — breaking / feature / fix.

## [1.6.0] — 2026-09-08
### Added — full customer-demo dataset
- Demo generator now covers the **whole process** for a customer walkthrough:
  - Engineering Site Visits on every project.
  - Visible **revision loop** on each design: Rev A submitted → client
    "Revision Required" (with comments) → Rev B issued, A auto-superseded →
    resubmitted → approved. Two Design Submissions per project tell the story.
  - **Certificate history** on the executing project (3 monthly certificates:
    20% → 45% → 65%) so the dashboard's 6-month certified trend draws.
  - A live Site Inspection with an **open High observation** — lights the
    dashboard card and lets you demonstrate BR-010 blocking closure.
  - **Financial leg** on the executing project: demo service Item →
    submitted Purchase Order (Main Contract, linked to the tender) →
    submitted Purchase Invoice linked to the latest certificate, validated
    live by BR-012. Defensive: if the site's accounts aren't set up for
    direct PI creation, the engineering records still complete and guidance
    is logged instead of failing.
  - Cleanup extended: delete_demo_data now removes POs, PIs and the demo Item.

## [1.5.0] — 2026-09-08
### Added
- **Bilingual (Arabic)**: `translations/ar.csv` with 379 entries covering all
  26 DocType names, ~150 field labels, all workflow states and actions,
  select options (disciplines, severities, stages, service types), the
  process map, and the dashboard. Frappe renders Arabic RTL automatically
  (English stays LTR) when the user sets Language = العربية.
- **Engineering Dashboard** (`/app/engineering-dashboard`): 8 clickable
  number cards (active projects, submissions with client, pending reviews,
  licenses, tenders, open observations, certified this month, warranty),
  three charts (projects by stage, documents by status, 6-month certified
  trend) and a recent-projects table with Docs%/Site% — one API round-trip,
  role-guarded, fully translatable. Workspace shortcut added.
- **Demo data generator** (`setup/demo.py`): bilingual masters (project
  types, UOMs, 2 customers, 3 prequalified contractors) and four projects
  frozen at Design / Tendering / Execution / Closed, each with the full
  record chain built to satisfy BR-001…BR-016. Explicit commands only:
  `bench --site <site> execute neo_engineering.setup.demo.make_demo_data`
  and `...demo.delete_demo_data`. Never runs automatically.

## [1.4.0] — 2026-09-07
### Changed
- Process Map redesigned to match the office's classic flow chart: lane
  headers with department icons, filled lane-tinted step boxes with inline
  numbering, decision diamonds with Yes/No exits, revision note boxes
  ("Discuss Revisions / Alternatives", "Revise Design", "Send Back for
  Corrections") wired into the loops, chart title header, and a clickable
  "Key Outputs at Each Stage" strip (every output opens its record list).
  All transaction chips, BR tooltips, and the post-completion warranty path
  retained; strings wrapped for translation.

## [1.3.1] — 2026-09-06
### Added
- Process Map: hover (and keyboard-focus) tooltips on every BR-0xx reference,
  spelling out the full business rule in plain language.

## [1.3.0] — 2026-09-05
### Added
- Interactive **Engineering Process Map** desk page: five-department swimlane
  flow chart (Client/BD, Design, Technical, Tendering/Supervision, PM &
  Close-out) with 16 numbered steps, decision diamonds with Yes/No loops,
  parallel licensing path, and auto-drawn arrows. Every step carries direct
  links to open the transaction list or create a new record.
- Workspace now opens with a "Process Map (start here)" shortcut and hint.

## [1.2.0] — 2026-08-30
### Changed
- BOQ Items: "Item / Group" is now a Link to the standard Item master with
  auto-fetch of description, UOM (stock UOM) and rate (standard rate).
  The link is optional — free-text BOQ lines remain valid.
- Project Type on Project Brief and Lead now links to the standard
  Project Type master instead of free text.
- Removed "ERPNext" from all user-visible text (Settings descriptions,
  workspace legend, app description). Functional dependency declarations
  are unchanged.

## [1.1.0] — 2026-08-30
### Changed
- Workspace rebuilt as a numbered nine-stage process pathway with
  color-coded shortcuts, "⚠ Requires" dependency callouts (BR references)
  and "➜ Then" flow pointers per stage.
### Fixed
- Added `[tool.bench.frappe-dependencies]` to pyproject.toml
  (frappe / erpnext >=15,<16) — required by newer bench versions;
  installation previously failed its compatibility check.

## [1.0.1] — 2026-08-30
### Changed
- Rebranded app from Alwathaeq Engineering to NeoEngineering
  (package `neo_engineering`); removed all remaining company references.
  Custom fieldnames on standard DocTypes are unchanged.

## [1.0.0] — 2026-08-25
### Added
- Initial release per Technical Development Specification v1.0:
  13 submittable DocTypes + 13 child tables, Engineering Management
  Settings, ~60 custom fields on 11 standard DocTypes, 11 role-bound
  workflows, 14 roles, business rules BR-001…BR-016 enforced server-side,
  daily notification scheduler, Engineering Management workspace,
  idempotent install/migrate.
