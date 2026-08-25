# NeoEngineering

Single consolidated Frappe app for ERPNext v15 implementing the Alwathaeq
Engineering technical development specification v1.0: full engineering project
lifecycle from customer intake through design, technical review, licensing,
tendering, execution, supervision, closure and post-completion warranty.

**Design principle:** standard-first. ERPNext remains the system of record for
CRM, selling, buying, projects, suppliers and accounting. This app extends —
never duplicates — standard transactions (spec Sections 4 and 4.1).

## Installation

```bash
cd $BENCH_HOME
bench get-app /path/to/neo_engineering   # or a git URL
bench --site <site> install-app neo_engineering
bench --site <site> migrate
```

Installation is idempotent (Section 20 acceptance: migrate succeeds twice).
`after_install` / `after_migrate` create roles, apply custom fields via
`create_custom_fields` (never fails on an existing fieldname, Section 17.1),
create the eleven workflows, and seed Engineering Management Settings.

## What's inside

| Layer | Contents |
| --- | --- |
| Custom DocTypes (13, submittable) | Project Brief, Engineering Site Visit, Engineering Document, Design Submission, Technical Review, Project BOQ, License Application, Tender Package, Tender Evaluation, Site Inspection, Contractor Progress Certificate, Project Handover, Project Closure |
| Child tables (13) | Services, document checklists, revisions, review comments, BOQ items, tender contractors/evaluation lines, observations, certificate lines, closure checklist |
| Settings | Engineering Management Settings (Single) — prequalification toggle, tender weights, SLA days, waiver role, closure enforcement (Appendix A) |
| Custom fields | Lead, Opportunity, Quotation, Project, Task, Supplier, RFQ, Supplier Quotation, Purchase Order, Purchase Invoice, Issue (Section 8) |
| Workflows | Eleven workflows exactly per Section 9, created programmatically with role-bound transitions |
| Roles | Fourteen engineering roles (Section 10) |
| Business rules | BR-001…BR-016 enforced **server-side** (Section 16.2) — see mapping below |
| Notifications | Daily scheduler job for overdue comments, prequalification expiry, overdue observations, bid deadlines, warranty due (Section 12) |
| Workspace | "Engineering Management" workspace with app + standard shortcuts (Section 13.1) |

## Business-rule mapping

| Rule | Enforced in |
| --- | --- |
| BR-001, BR-002, BR-015 | `api/project.py` (Project validate hook) |
| BR-003, BR-004 | `design_submission.py`, `engineering_document.py` |
| BR-005 | `technical_review.py` |
| BR-006 | `project_boq.py` |
| BR-007, BR-008, BR-009 | `tender_package.py` (+ Settings prequalification toggle) |
| BR-010 | `site_inspection.py` |
| BR-011 | `contractor_progress_certificate.py` |
| BR-012 | `api/progress.py` (Purchase Invoice validate hook) |
| BR-013 | `project_handover.py` |
| BR-014 | `project_closure.py` |
| BR-016 | `api/issue.py` (Issue validate hook) |

## Explicit non-duplication guarantees (Section 4.1)

- No custom ledger, payment, invoice or purchase transaction is created.
- Progress Certificates *certify*; the Purchase Invoice *posts* — the app only
  validates the invoice against the certified amount (BR-012).
- Custom workflow states never override `docstatus`; each controlled DocType
  keeps Frappe draft/submitted/cancelled alongside `workflow_state`.

## Stage automation (Section 9.1)

- Approved final Design Submission → Project Stage advances to Technical
  Review (or Licensing for Design Only).
- License Application / Tender Package workflow states sync to the read-only
  Project summary fields.
- Approved Project Closure → Project Stage = Closed and ERPNext Project
  status = Completed (blocked otherwise by BR-015).

## Not yet included (per spec open items / later phases)

- Script/query reports and dashboard number cards (Section 13 — Phase 3+).
- Print formats (Section 19 — several legacy source forms are still marked
  "not received"; they must not be fabricated).
- Authority-specific license checklists, tender scoring weights and
  retention/variation commercial rules pending business confirmation
  (Section 23.1).

## Development

- Server-side validations only in Python; client scripts are UX sugar
  (Section 16.2).
- No ERPNext core files are modified; no monkey-patching.
- Run `bench --site <site> migrate` after every update; patches go in
  `patches.txt` and must stay idempotent (Section 17.2).
