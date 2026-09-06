import frappe
from frappe import _
from frappe.model.document import Document
from neo_engineering.utils.settings import get_settings


class TenderPackage(Document):
	def validate(self):
		self.validate_shortlist_prequalification()

	def validate_shortlist_prequalification(self):
		"""BR-008: only prequalified/valid suppliers may be shortlisted when
		prequalification control is enabled."""
		settings = get_settings()
		if not settings.enable_contractor_prequalification:
			return
		today = frappe.utils.nowdate()
		for row in self.contractors:
			status, expiry = frappe.db.get_value(
				"Supplier", row.supplier,
				["custom_prequalification_status", "custom_prequalification_expiry"],
			) or (None, None)
			if status != "Approved" or (expiry and str(expiry) < today):
				frappe.throw(_(
					"Row {0}: Supplier {1} is not a valid prequalified "
					"contractor (BR-008).").format(row.idx, row.supplier))

	def before_workflow_action(self):
		action = frappe.form_dict.get("action")
		if action == "Issue":
			self.block_issue_without_approved_boq()
		if action in ("Recommend Award", "Award"):
			self.block_award_without_approved_evaluation()

	def block_issue_without_approved_boq(self):
		"""BR-007: cannot issue tender without an approved BOQ or waiver."""
		if self.waiver_applied and self.waiver_reason:
			return
		if not self.project_boq:
			frappe.throw(_(
				"Tender Package cannot be issued without an approved Project "
				"BOQ or an authorized waiver (BR-007)."))
		state = frappe.db.get_value("Project BOQ", self.project_boq,
			["docstatus", "workflow_state"], as_dict=True)
		if not state or state.docstatus != 1 or (
				state.workflow_state and state.workflow_state != "Approved"):
			frappe.throw(_(
				"Linked Project BOQ is not approved (BR-007)."))

	def block_award_without_approved_evaluation(self):
		"""BR-009: award requires an approved Tender Evaluation or waiver."""
		if self.waiver_applied and self.waiver_reason:
			return
		approved = frappe.get_all("Tender Evaluation", filters={
			"tender_package": self.name, "docstatus": 1}, limit=1)
		if not approved:
			frappe.throw(_(
				"Tender award requires an approved Tender Evaluation unless a "
				"management waiver is recorded with reason (BR-009)."))

	def on_update_after_submit(self):
		if self.project and self.get("workflow_state"):
			frappe.db.set_value("Project", self.project, "custom_tender_status",
				self.get("workflow_state"), update_modified=False)
