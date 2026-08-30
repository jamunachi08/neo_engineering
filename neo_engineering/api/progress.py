"""Progress-claim controls on the standard Purchase Invoice.

BR-012: a Purchase Invoice linked to a Contractor Progress Certificate must
not exceed the approved certified amount net of prior invoicing, unless an
authorized variation (management waiver role) applies. Financial posting
itself remains 100% in standard core transactions (Section 14).
"""

import frappe
from frappe import _
from frappe.utils import flt

from neo_engineering.utils.settings import user_can_waive


def validate_progress_invoice(doc, method=None):
    if not doc.get("custom_progress_certificate"):
        return

    cpc = frappe.db.get_value(
        "Contractor Progress Certificate", doc.custom_progress_certificate,
        ["docstatus", "workflow_state", "net_certified_amount",
         "total_certified_amount", "supplier"],
        as_dict=True)
    if not cpc:
        frappe.throw(_("Linked Progress Certificate not found."))

    if cpc.docstatus != 1:
        frappe.throw(_(
            "Progress Certificate {0} is not approved; a Purchase Invoice "
            "cannot be raised against it (BR-012)."
        ).format(doc.custom_progress_certificate))

    if cpc.supplier and doc.supplier != cpc.supplier:
        frappe.throw(_(
            "Supplier on the invoice ({0}) does not match the certified "
            "contractor ({1}).").format(doc.supplier, cpc.supplier))

    certified = flt(cpc.net_certified_amount) or flt(cpc.total_certified_amount)

    prior = frappe.db.sql(
        """
        SELECT COALESCE(SUM(grand_total), 0)
        FROM `tabPurchase Invoice`
        WHERE custom_progress_certificate = %s
          AND docstatus = 1
          AND name != %s
        """,
        (doc.custom_progress_certificate, doc.name or ""))[0][0]

    remaining = certified - flt(prior)
    if flt(doc.grand_total) > remaining + 0.005:
        if user_can_waive():
            frappe.msgprint(_(
                "Warning: invoice amount {0} exceeds the remaining certified "
                "amount {1}. Proceeding under management waiver authority "
                "(BR-012).").format(
                frappe.format_value(doc.grand_total, {"fieldtype": "Currency"}),
                frappe.format_value(remaining, {"fieldtype": "Currency"})),
                indicator="orange")
            return
        frappe.throw(_(
            "Invoice amount {0} exceeds the approved certified amount net of "
            "prior invoicing ({1} remaining) for Progress Certificate {2} "
            "(BR-012).").format(
            frappe.format_value(doc.grand_total, {"fieldtype": "Currency"}),
            frappe.format_value(remaining, {"fieldtype": "Currency"}),
            doc.custom_progress_certificate))
