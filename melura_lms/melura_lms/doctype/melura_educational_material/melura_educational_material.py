# Copyright (c) 2026, Estevão Oliveira Portes and contributors
# For license information, please see LICENSE

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class MeluraEducationalMaterial(Document):
	def validate(self):
		if not (self.title or "").strip():
			frappe.throw(_("Informe o título do material."))

		if self.published and not self.published_at:
			self.published_at = now_datetime()
