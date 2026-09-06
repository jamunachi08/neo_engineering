"""Daily SLA and overdue alerts (Section 12).

One scheduled entry point sends System Notifications (and email where users
have it enabled) for the overdue conditions in the specification. Each block
is defensive: a failure in one alert type never blocks the others.
"""

import frappe
from frappe import _
from frappe.utils import add_days, nowdate

from neo_engineering.utils.settings import get_settings


def send_daily_alerts():
    for fn in (
        alert_overdue_technical_comments,
        alert_prequalification_expiry,
        alert_overdue_observations,
        alert_bid_deadlines,
        alert_warranty_due,
    ):
        try:
            fn()
        except Exception:
            frappe.log_error(title=f"Engineering alerts: {fn.__name__}")


def _notify(users, subject, doctype, name):
    for user in {u for u in users if u}:
        frappe.get_doc({
            "doctype": "Notification Log",
            "for_user": user,
            "type": "Alert",
            "subject": subject,
            "document_type": doctype,
            "document_name": name,
        }).insert(ignore_permissions=True)


def alert_overdue_technical_comments():
    """Technical comments overdue: due date passed and status Open."""
    rows = frappe.db.sql(
        """
        SELECT c.parent, c.responsible, c.comment, tr.project
        FROM `tabTechnical Review Comment` c
        JOIN `tabTechnical Review` tr ON tr.name = c.parent
        WHERE c.status = 'Open'
          AND c.closure_date IS NULL
          AND tr.review_date < %s
          AND tr.docstatus < 2
        """,
        (add_days(nowdate(), -(get_settings().default_review_due_days or 7)),),
        as_dict=True)
    for row in rows:
        technical_manager = frappe.db.get_value(
            "Project", row.project, "custom_technical_manager")
        _notify([row.responsible, technical_manager],
                _("Overdue technical comment on {0}").format(row.parent),
                "Technical Review", row.parent)


def alert_prequalification_expiry():
    """Supplier prequalification expiring in 30/15/7 days."""
    for days in (30, 15, 7):
        target = add_days(nowdate(), days)
        suppliers = frappe.get_all("Supplier", filters={
            "custom_prequalification_status": "Approved",
            "custom_prequalification_expiry": target,
        }, pluck="name")
        if not suppliers:
            continue
        users = frappe.get_all("Has Role",
            filters={"role": "Contracts Specialist", "parenttype": "User"},
            pluck="parent")
        for supplier in suppliers:
            _notify(users,
                    _("Prequalification for {0} expires in {1} days").format(
                        supplier, days),
                    "Supplier", supplier)


def alert_overdue_observations():
    """Inspection observations past due date and still open."""
    rows = frappe.db.sql(
        """
        SELECT o.parent, si.project
        FROM `tabInspection Observation` o
        JOIN `tabSite Inspection` si ON si.name = o.parent
        WHERE o.status IN ('Open', 'Rectified')
          AND o.due_date IS NOT NULL AND o.due_date < %s
          AND si.docstatus < 2
        GROUP BY o.parent, si.project
        """, (nowdate(),), as_dict=True)
    for row in rows:
        pm, sm = frappe.db.get_value("Project", row.project,
            ["custom_project_manager", "custom_supervision_manager"]) or (None, None)
        _notify([pm, sm],
                _("Overdue site observation(s) on {0}").format(row.parent),
                "Site Inspection", row.parent)


def alert_bid_deadlines():
    """Tender bid deadline approaching (3 days ahead)."""
    rows = frappe.get_all("Tender Package", filters={
        "bid_deadline": add_days(nowdate(), 3),
        "docstatus": ("<", 2),
    }, fields=["name", "project"])
    for row in rows:
        pm = frappe.db.get_value("Project", row.project, "custom_project_manager")
        users = frappe.get_all("Has Role",
            filters={"role": "Contracts Specialist", "parenttype": "User"},
            pluck="parent")
        _notify(users + [pm],
                _("Bid deadline in 3 days for tender {0}").format(row.name),
                "Tender Package", row.name)


def alert_warranty_due():
    """Warranty issue nearing its due date."""
    lead_days = get_settings().warranty_reminder_days or 14
    rows = frappe.get_all("Issue", filters={
        "status": ("not in", ["Closed", "Resolved"]),
        "custom_issue_category": ("in", ["Defect", "Warranty", "Maintenance"]),
        "custom_warranty_due_date": ("<=", add_days(nowdate(), lead_days)),
    }, fields=["name", "custom_project"])
    for row in rows:
        pm = frappe.db.get_value("Project", row.custom_project,
            "custom_project_manager") if row.custom_project else None
        _notify([pm],
                _("Warranty issue {0} is nearing its due date").format(row.name),
                "Issue", row.name)
