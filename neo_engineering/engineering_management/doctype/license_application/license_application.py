import frappe
from frappe import _
from frappe.model.document import Document


class LicenseApplication(Document):
	def before_workflow_action(self):
		action = frappe.form_dict.get("action")
		if action in ("Mark Ready to Submit", "Submit to Authority"):
			self.block_if_mandatory_documents_missing()

	def block_if_mandatory_documents_missing(self):
		"""Section 20: missing mandatory documents block Ready to Submit."""
		missing = [d.document_name for d in self.documents
			if d.is_mandatory and not d.received]
		if missing:
			frappe.throw(_(
				"Cannot proceed: mandatory license documents not received: {0}"
			).format(", ".join(missing)))

	def on_update_after_submit(self):
		self.sync_project_license_status()

	def on_submit(self):
		self.sync_project_license_status()

	def sync_project_license_status(self):
		if self.project and self.get("workflow_state"):
			frappe.db.set_value(
				"Project", self.project, "custom_license_status",
				self.get("workflow_state"), update_modified=False)
