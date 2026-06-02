# Copyright (c) 2026, Estevão Oliveira Portes and contributors
# For license information, please see LICENSE

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class BruceExerciseList(Document):
	def validate(self):
		self._validate_title()
		self._validate_published_items()
		self._set_published_at()

	def _validate_title(self):
		if not (self.title or "").strip():
			frappe.throw(_("Informe o título da lista."))

	def _validate_published_items(self):
		if self.published and not self.get("items"):
			frappe.throw(_("Inclua pelo menos uma questão antes de publicar a lista."))

	def _set_published_at(self):
		if self.published and not self.published_at:
			self.published_at = now_datetime()
