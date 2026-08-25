import frappe
from frappe import _
from frappe.model.document import Document


class DesignSubmission(Document):
	def validate(self):
		self.validate_documents()

	def validate_documents(self):
		"""BR-003: a Design Submission requires at least one Engineering
		Document revision, and only the latest non-superseded revision may be
		included as the current approved revision (BR-004)."""
		if not self.documents:
			frappe.throw(_(
				"A Design Submission cannot be saved without at least one "
				"Engineering Document revision (BR-003)."))
		for row in self.documents:
			doc_current = frappe.db.get_value(
				"Engineering Document", row.engineering_document, "current_revision")
			if doc_current and row.revision != doc_current:
				frappe.throw(_(
					"Row {0}: revision {1} of {2} is not the current revision "
					"({3}). Only the latest non-superseded revision can be "
					"submitted (BR-004).").format(
					row.idx, row.revision, row.engineering_document, doc_current))

	def before_submit(self):
		if not self.documents:
			frappe.throw(_("Cannot submit without documents (BR-003)."))

	def on_update_after_submit(self):
		from neo_engineering.api.project import on_design_submission_update
		on_design_submission_update(self)
