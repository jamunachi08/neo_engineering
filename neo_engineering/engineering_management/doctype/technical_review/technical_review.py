import frappe
from frappe import _
from frappe.model.document import Document


class TechnicalReview(Document):
	def validate(self):
		for row in self.comments:
			if row.status == "Closed" and not row.closure_date:
				row.closure_date = frappe.utils.nowdate()

	def before_submit(self):
		self.block_approval_with_open_mandatory_comments()

	def before_workflow_action(self):
		if frappe.form_dict.get("action") in ("Approve",):
			self.block_approval_with_open_mandatory_comments()

	def block_approval_with_open_mandatory_comments(self):
		"""BR-005: cannot approve while mandatory comments remain Open."""
		if (self.result or "").startswith("Approved") or self.get("workflow_state") == "Approved":
			open_rows = [r for r in self.comments
				if r.is_mandatory and r.status == "Open"]
			if open_rows:
				frappe.throw(_(
					"Technical Review cannot be approved while {0} mandatory "
					"comment(s) remain Open (BR-005).").format(len(open_rows)))
