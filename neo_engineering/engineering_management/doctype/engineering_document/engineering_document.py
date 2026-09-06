import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import nowdate


class EngineeringDocument(Document):
	def validate(self):
		self.enforce_single_current_revision()
		self.set_current_revision()

	def enforce_single_current_revision(self):
		"""BR-004 / Section 15: only one revision may be Current; when a new
		revision becomes current the prior one is superseded automatically."""
		current_rows = [r for r in self.revisions if r.is_current and not r.superseded]
		if len(current_rows) > 1:
			# keep the last row flagged current; supersede the rest
			for row in current_rows[:-1]:
				row.is_current = 0
				row.superseded = 1
		for row in self.revisions:
			if row.superseded and row.is_current:
				row.is_current = 0

	def set_current_revision(self):
		current = next(
			(r for r in self.revisions if r.is_current and not r.superseded), None)
		self.current_revision = current.revision if current else None
		if current and not current.revision_date:
			current.revision_date = nowdate()

	def before_submit(self):
		if not self.revisions:
			frappe.throw(_("An Engineering Document requires at least one revision."))
		if not self.current_revision:
			frappe.throw(_("Mark exactly one revision as Current before submitting."))
