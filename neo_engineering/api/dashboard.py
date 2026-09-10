"""Management dashboard aggregates — one whitelisted call returns everything
the dashboard page needs, so the page renders with a single round-trip."""

import frappe
from frappe.utils import flt, get_first_day, nowdate


@frappe.whitelist()
def get_dashboard_data():
    frappe.only_for(("System Manager", "Engineering Management",
                     "Project Manager", "Engineering App Administrator",
                     "Technical Manager", "Supervision Manager",
                     "Design Lead", "Engineering Finance Reviewer"), message=True)

    active_projects = frappe.db.count("Project", {
        "status": ("in", ["Open"]),
        "custom_project_stage": ("not in", ["Closed", "Cancelled", ""]),
    })

    cards = {
        "active_projects": active_projects,
        "open_submissions": frappe.db.count("Design Submission", {
            "docstatus": ("<", 2),
            "workflow_state": ("in", ["Sent to Client", "Submitted for Internal Review",
                                      "Ready for Client"])}),
        "pending_reviews": frappe.db.count("Technical Review", {
            "docstatus": 0}),
        "tenders_in_progress": frappe.db.count("Tender Package", {
            "docstatus": ("<", 2),
            "workflow_state": ("in", ["Shortlisting", "Issued", "Bids Received",
                                      "Evaluation", "Negotiation", "Award Recommended"])}),
        "open_observations": frappe.db.sql("""
            SELECT COUNT(*) FROM `tabInspection Observation` o
            JOIN `tabSite Inspection` si ON si.name = o.parent
            WHERE o.status IN ('Open', 'Rectified') AND si.docstatus < 2
        """)[0][0],
        "certified_this_month": flt(frappe.db.sql("""
            SELECT COALESCE(SUM(net_certified_amount), 0)
            FROM `tabContractor Progress Certificate`
            WHERE docstatus = 1 AND modified >= %s
        """, (get_first_day(nowdate()),))[0][0]),
        "open_warranty": frappe.db.count("Issue", {
            "status": ("not in", ["Closed", "Resolved"]),
            "custom_issue_category": ("in", ["Warranty", "Defect", "Maintenance"])}),
        "licenses_pending": frappe.db.count("License Application", {
            "docstatus": ("<", 2),
            "workflow_state": ("in", ["Documents Pending", "Ready to Submit",
                                      "Submitted", "Authority Comments"])}),
    }

    by_stage = frappe.db.sql("""
        SELECT COALESCE(NULLIF(custom_project_stage, ''), 'Unset') AS stage,
               COUNT(*) AS qty
        FROM `tabProject`
        WHERE status != 'Cancelled'
        GROUP BY stage ORDER BY qty DESC
    """, as_dict=True)

    doc_status = frappe.db.sql("""
        SELECT COALESCE(NULLIF(document_status, ''), 'Draft') AS status,
               COUNT(*) AS qty
        FROM `tabEngineering Document`
        GROUP BY status ORDER BY qty DESC
    """, as_dict=True)

    certified_trend = frappe.db.sql("""
        SELECT DATE_FORMAT(period_to, '%%Y-%%m') AS month,
               SUM(net_certified_amount) AS amount
        FROM `tabContractor Progress Certificate`
        WHERE docstatus = 1 AND period_to >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
        GROUP BY month ORDER BY month
    """, as_dict=True)

    projects = frappe.get_all("Project",
        filters={"status": ("!=", "Cancelled")},
        fields=["name", "project_name", "custom_project_stage",
                "custom_service_type", "customer",
                "custom_document_completion_pct", "custom_site_progress_pct"],
        order_by="modified desc", limit=8)

    return {"cards": cards, "by_stage": by_stage, "doc_status": doc_status,
            "certified_trend": certified_trend, "projects": projects}
