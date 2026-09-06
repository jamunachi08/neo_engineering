# Changelog

All notable changes to the NeoEngineering app. Versioning follows
[SemVer](https://semver.org): MAJOR.MINOR.PATCH — breaking / feature / fix.

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
