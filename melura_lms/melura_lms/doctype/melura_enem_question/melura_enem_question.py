# Copyright (c) 2026, Estevão Oliveira Portes and contributors
# For license information, please see LICENSE

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class MeluraENEMQuestion(Document):
	def validate(self):
		self._validate_statement()
		self._validate_alternatives()
		self._set_published_at()

	def _validate_statement(self):
		if not (self.statement or "").strip():
			frappe.throw(_("Informe o enunciado da questão."))

	def _validate_alternatives(self):
		correct_alternatives = [alternative for alternative in (self.get("alternatives") or []) if alternative.is_correct]

		if len(correct_alternatives) > 1:
			frappe.throw(_("Marque no máximo uma alternativa correta."))

		if correct_alternatives:
			option_label = correct_alternatives[0].option_label
			if self.correct_option and self.correct_option != option_label:
				frappe.throw(_("A alternativa correta marcada precisa ser igual ao gabarito."))

			if not self.correct_option:
				self.correct_option = option_label

		if self.published and not self.correct_option:
			frappe.throw(_("Informe o gabarito antes de publicar a questão."))

	def _set_published_at(self):
		if self.published and not self.published_at:
			self.published_at = now_datetime()
