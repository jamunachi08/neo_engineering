import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt
from neo_engineering.utils.settings import get_settings


class TenderEvaluation(Document):
	def validate(self):
		self.set_project()
		self.apply_default_weights()
		self.score_and_rank()

	def set_project(self):
		if self.tender_package and not self.project:
			self.project = frappe.db.get_value(
				"Tender Package", self.tender_package, "project")

	def apply_default_weights(self):
		settings = get_settings()
		if not flt(self.technical_weight) and not flt(self.commercial_weight):
			self.technical_weight = flt(settings.default_tender_technical_weight) or 60
			self.commercial_weight = flt(settings.default_tender_commercial_weight) or 40
		if flt(self.technical_weight) + flt(self.commercial_weight) != 100:
			frappe.throw(_("Technical + Commercial weights must equal 100%."))

	def score_and_rank(self):
		for row in self.lines:
			row.total_score = (
				flt(row.technical_score) * flt(self.technical_weight)
				+ flt(row.commercial_score) * flt(self.commercial_weight)) / 100
		ranked = sorted(self.lines, key=lambda r: flt(r.total_score), reverse=True)
		for i, row in enumerate(ranked, 1):
			row.rank = i

	def before_submit(self):
		if not self.lines:
			frappe.throw(_("Add at least one evaluation line before approval."))
		if not self.recommended_supplier:
			frappe.throw(_("Select the recommended contractor before approval."))

	def on_submit(self):
		frappe.db.set_value("Tender Package", self.tender_package,
			"tender_evaluation", self.name, update_modified=False)
