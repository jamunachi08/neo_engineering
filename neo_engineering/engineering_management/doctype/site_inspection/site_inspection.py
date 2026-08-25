import frappe
from frappe import _
from frappe.model.document import Document


class SiteInspection(Document):
	def before_workflow_action(self):
		if frappe.form_dict.get("action") in ("Close", "Verify and Close"):
			self.block_close_with_open_observations()

	def before_submit(self):
		self.block_close_with_open_observations()

	def block_close_with_open_observations(self):
		"""BR-010: cannot close while mandatory or High/Critical observations
		remain unverified."""
		blocking = [r for r in self.observations
			if r.status not in ("Verified", "Closed")
			and (r.is_mandatory or r.severity in ("High", "Critical"))]
		if blocking:
			frappe.throw(_(
				"Site Inspection cannot be closed: {0} mandatory/high/critical "
				"observation(s) are not yet verified (BR-010).").format(len(blocking)))

	def on_submit(self):
		self.notify_critical_observations()

	def notify_critical_observations(self):
		critical = [r for r in self.observations if r.severity == "Critical"]
		if not critical or not self.project:
			return
		recipients = set()
		for field in ("custom_supervision_manager", "custom_project_manager"):
			user = frappe.db.get_value("Project", self.project, field)
			if user:
				recipients.add(user)
		if recipients:
			frappe.sendmail(
				recipients=list(recipients),
				subject=_("Critical site observation on {0}").format(self.project),
				message=_("Site Inspection {0} recorded {1} critical "
					"observation(s).").format(self.name, len(critical)),
				reference_doctype=self.doctype, reference_name=self.name,
			)
