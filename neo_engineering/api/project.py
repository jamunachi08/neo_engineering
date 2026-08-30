"""Server-side controls on the standard Project DocType.

Wired via doc_events in hooks.py. Implements BR-001, BR-002, BR-015 and the
KPI/stage summary updates of Sections 8 and 9.1. All ledger and transactional
logic stays in standard core transactions (Section 4.1); these hooks only validate and
summarize.
"""

import frappe
from frappe import _
from frappe.utils import flt

from neo_engineering.utils.settings import get_settings

ACTIVE_LIFECYCLE_STAGES = {
    "Design", "Technical Review", "Licensing", "Tendering",
    "Execution", "Supervision", "Handover", "Closure", "Post-Completion",
}


def validate_project(doc, method=None):
    validate_mandatory_control_fields(doc)   # BR-001
    validate_supervision_only_origin(doc)    # BR-002
    validate_completion_requires_closure(doc)  # BR-015


def validate_mandatory_control_fields(doc):
    """BR-001: a Project with an active engineering lifecycle must have
    Service Type, Project Stage, Project Manager and Project Location."""
    if (doc.custom_project_stage or "") not in ACTIVE_LIFECYCLE_STAGES:
        return
    missing = [label for field, label in (
        ("custom_service_type", _("Service Type")),
        ("custom_project_stage", _("Project Stage")),
        ("custom_project_manager", _("Project Manager")),
        ("custom_project_location", _("Project Location")),
    ) if not doc.get(field)]
    if missing:
        frappe.throw(_(
            "An active engineering project requires: {0} (BR-001)."
        ).format(", ".join(missing)))


def validate_supervision_only_origin(doc):
    """BR-002: Supervision Only projects must have Design Origin = External
    or an explicit internal design reference (Project Brief)."""
    if doc.custom_service_type != "Supervision Only":
        return
    if doc.custom_design_origin == "External":
        return
    if doc.custom_design_origin == "Internal" and doc.custom_project_brief:
        return
    frappe.throw(_(
        "Supervision Only projects must have Design Origin = External, or "
        "Design Origin = Internal with a linked Project Brief as the internal "
        "design reference (BR-002)."))


def validate_completion_requires_closure(doc):
    """BR-015: Project may only become Completed after an approved Project
    Closure. Design Only projects are exempt when an accepted design handover
    exists instead."""
    if doc.status != "Completed":
        return
    if doc.is_new():
        previous_status = None
    else:
        previous_status = frappe.db.get_value("Project", doc.name, "status")
    if previous_status == "Completed":
        return
    settings = get_settings()
    if not settings.require_project_closure_before_completion:
        return
    has_closure = frappe.db.exists(
        "Project Closure", {"project": doc.name, "docstatus": 1})
    if has_closure:
        return
    if doc.custom_service_type == "Design Only":
        has_design_handover = frappe.db.exists(
            "Project Handover", {"project": doc.name, "docstatus": 1})
        if has_design_handover:
            return
    frappe.throw(_(
        "Project cannot be set to Completed before an approved Project "
        "Closure (BR-015). For Design Only projects, an accepted Project "
        "Handover is sufficient."))


def update_project_kpis(doc, method=None):
    """Recompute summary KPIs (Section 8: read-only calculated fields).
    Runs enqueued to keep saves fast (Section 16.2)."""
    settings = get_settings()
    if not settings.auto_update_project_kpis:
        return
    if frappe.flags.in_install or frappe.flags.in_migrate or frappe.flags.in_patch:
        return
    frappe.enqueue(
        "neo_engineering.api.project.recompute_kpis",
        project=doc.name, queue="short", enqueue_after_commit=True,
        deduplicate=True, job_id=f"eng-kpis::{doc.name}")


def recompute_kpis(project):
    if not frappe.db.exists("Project", project):
        return

    # Document Completion %: share of engineering documents whose status is
    # Approved / Approved with Comments / As-Built.
    total_docs = frappe.db.count("Engineering Document", {"project": project})
    approved_docs = frappe.db.count("Engineering Document", {
        "project": project,
        "document_status": ("in", ["Approved", "Approved with Comments", "As-Built"]),
    })
    doc_pct = (approved_docs / total_docs * 100) if total_docs else 0

    # Engineering Progress %: average progress of non-site engineering tasks.
    eng_rows = frappe.get_all("Task",
        filters={"project": project,
                 "custom_engineering_stage": ("in", ["Design", "Technical", "Tender"])},
        pluck="progress")
    eng_pct = (sum(flt(p) for p in eng_rows) / len(eng_rows)) if eng_rows else 0

    # Site Progress %: latest approved progress certificate average cumulative.
    latest_cpc = frappe.get_all("Contractor Progress Certificate",
        filters={"project": project, "docstatus": 1},
        order_by="modified desc", limit=1, pluck="name")
    site_pct = 0
    if latest_cpc:
        lines = frappe.get_all("Progress Certificate Line",
            filters={"parent": latest_cpc[0]}, pluck="cumulative_pct")
        if lines:
            site_pct = min(100, sum(flt(v) for v in lines) / len(lines))

    frappe.db.set_value("Project", project, {
        "custom_document_completion_pct": doc_pct,
        "custom_engineering_progress_pct": eng_pct,
        "custom_site_progress_pct": site_pct,
    }, update_modified=False)


def on_design_submission_update(submission):
    """Section 9.1: approval of the final Design Submission may advance the
    project stage to Technical Review or Licensing depending on scope."""
    if submission.get("workflow_state") != "Approved" or not submission.project:
        return
    stage, service_type = frappe.db.get_value(
        "Project", submission.project,
        ["custom_project_stage", "custom_service_type"]) or (None, None)
    if stage != "Design":
        return
    next_stage = ("Technical Review"
                  if service_type != "Design Only" else "Licensing")
    frappe.db.set_value("Project", submission.project,
        "custom_project_stage", next_stage, update_modified=False)
