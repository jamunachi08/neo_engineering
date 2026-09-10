import frappe
from frappe import _
from frappe.model.document import Document


class ProjectHandover(Document):
	def before_workflow_action(self):
		if frappe.form_dict.get("action") in ("Accept",):
			self.block_acceptance_with_missing_documents()

	def before_submit(self):
		self.block_acceptance_with_missing_documents()

	def block_acceptance_with_missing_documents(self):
		"""BR-013: handover cannot be accepted until mandatory documents are
		delivered or formally waived."""
		if self.waiver_applied and self.waiver_reason:
			return
		missing = [d.document_name for d in self.documents
			if d.required and not d.delivered]
		if missing:
			frappe.throw(_(
				"Project Handover cannot be accepted; mandatory documents not "
				"delivered: {0} (BR-013)").format(", ".join(missing)))
