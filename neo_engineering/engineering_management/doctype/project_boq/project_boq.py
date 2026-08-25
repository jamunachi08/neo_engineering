import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class ProjectBOQ(Document):
	def validate(self):
		self.validate_items()
		self.calculate_totals()

	def validate_items(self):
		"""BR-006: BOQ requires at least one item with valid UOM/quantity."""
		if not self.items:
			frappe.throw(_(
				"Project BOQ requires at least one BOQ Item (BR-006)."))
		for row in self.items:
			if flt(row.qty) <= 0:
				frappe.throw(_(
					"Row {0}: quantity must be greater than zero (BR-006)."
				).format(row.idx))

	def calculate_totals(self):
		total = 0.0
		for row in self.items:
			row.amount = flt(row.qty) * flt(row.rate)
			total += row.amount
		self.total_amount = total

	def on_submit(self):
		self.supersede_previous_boqs()

	def supersede_previous_boqs(self):
		for name in frappe.get_all("Project BOQ", pluck="name", filters={
			"project": self.project, "docstatus": 1,
			"name": ("!=", self.name), "is_superseded": 0}):
			frappe.db.set_value("Project BOQ", name, "is_superseded", 1)
