import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class ContractorProgressCertificate(Document):
	def validate(self):
		self.validate_cumulative(self)
		self.calculate_amounts()

	@staticmethod
	def validate_cumulative(doc):
		"""BR-011: cumulative certified % cannot exceed 100 unless the line is
		explicitly configured as a variation item."""
		for row in doc.lines:
			row.cumulative_pct = flt(row.previous_pct) + flt(row.current_pct)
			if flt(row.cumulative_pct) > 100 and not row.allow_over_100:
				frappe.throw(_(
					"Row {0}: cumulative certified progress {1}% exceeds 100% "
					"and the line is not marked as a variation (BR-011)."
				).format(row.idx, row.cumulative_pct))

	def calculate_amounts(self):
		total = sum(flt(r.certified_value) for r in self.lines)
		self.total_certified_amount = total
		self.retention_amount = total * flt(self.retention_pct) / 100
		for row in self.lines:
			row.retention = flt(row.certified_value) * flt(self.retention_pct) / 100
		self.net_certified_amount = total - flt(self.retention_amount)

	def before_submit(self):
		if not self.lines:
			frappe.throw(_("Add at least one certificate line before approval."))
