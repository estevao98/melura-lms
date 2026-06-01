# Copyright (c) 2026, Estevão Oliveira Portes and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class BruceStudentAnswer(Document):
	def validate(self):
		self._validate_required_fields()
		if not self.answered_at:
			self.answered_at = now_datetime()

	def _validate_required_fields(self):
		if not self.exercise_list:
			frappe.throw(_("Informe a lista de exercícios."))

		if not self.question:
			frappe.throw(_("Informe a questão."))

		if not self.student_user:
			frappe.throw(_("Informe o aluno."))

		if not self.selected_option:
			frappe.throw(_("Selecione uma alternativa."))
