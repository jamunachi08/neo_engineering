"""Warranty / defect controls on the standard Issue DocType.

BR-016: a Warranty/Defect Issue cannot be closed without resolution details
and verification by the responsible internal role.
"""

import frappe
from frappe import _

WARRANTY_CATEGORIES = {"Defect", "Warranty", "Maintenance"}


def validate_issue(doc, method=None):
    if doc.status not in ("Closed", "Resolved"):
        return
    if (doc.get("custom_issue_category") or "") not in WARRANTY_CATEGORIES:
        return

    if not doc.get("custom_project"):
        frappe.throw(_(
            "A project warranty Issue must be linked to a Project "
            "(Section 8: custom_project is required for project warranty)."))

    if not (doc.get("resolution_details") or "").strip():
        frappe.throw(_(
            "A Warranty/Defect Issue cannot be closed without resolution "
            "details (BR-016)."))

    if not doc.get("custom_resolution_verified_by"):
        frappe.throw(_(
            "A Warranty/Defect Issue cannot be closed until the resolution is "
            "verified by the responsible internal role "
            "(Resolution Verified By) (BR-016)."))
