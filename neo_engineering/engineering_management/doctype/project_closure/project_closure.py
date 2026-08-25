import frappe
from frappe import _
from frappe.model.document import Document


class ProjectClosure(Document):
	def before_workflow_action(self):
		if frappe.form_dict.get("action") in ("Approve", "Close"):
			self.block_approval_with_incomplete_items()

	def before_submit(self):
		self.block_approval_with_incomplete_items()

	def block_approval_with_incomplete_items(self):
		"""BR-014: closure cannot be approved while mandatory clearance items
		are incomplete."""
		incomplete = [c.requirement for c in self.checklist
			if c.is_mandatory and not c.completed]
		if incomplete:
			frappe.throw(_(
				"Project Closure cannot be approved; incomplete mandatory "
				"items: {0} (BR-014)").format(", ".join(incomplete)))
		if not (self.financial_cleared and self.technical_cleared):
			frappe.throw(_(
				"Both Financial and Technical clearance must be confirmed "
				"before closure approval (BR-014)."))

	def on_submit(self):
		"""Section 9.1: approved closure sets Project Stage = Closed and
		ERPNext Project Status = Completed."""
		if self.project:
			frappe.db.set_value("Project", self.project, {
				"custom_closure_status": "Closed",
				"custom_project_stage": "Closed",
				"status": "Completed",
			}, update_modified=False)
