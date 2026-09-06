import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class EngineeringManagementSettings(Document):
	def validate(self):
		tech = flt(self.default_tender_technical_weight)
		comm = flt(self.default_tender_commercial_weight)
		if (tech or comm) and tech + comm != 100:
			frappe.throw(_("Default tender technical and commercial weights must total 100%."))
