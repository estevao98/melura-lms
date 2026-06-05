# Copyright (c) 2026, Estevão Oliveira Portes and contributors
# For license information, please see LICENSE

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class MeluraStudentAnswer(Document):
	def validate(self):
		self._validate_required_fields()
		self._normalize_selected_option()
		self._compute_correctness()
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

	def _normalize_selected_option(self):
		self.selected_option = str(self.selected_option or "").strip().upper()
		if self.selected_option not in {"A", "B", "C", "D", "E"}:
			frappe.throw(_("Alternativa inválida."))

	def _compute_correctness(self):
		correct_option = frappe.db.get_value("Melura ENEM Question", self.question, "correct_option")
		if not correct_option:
			frappe.throw(_("A questão ainda não possui gabarito cadastrado."))

		self.is_correct = self.selected_option == str(correct_option).strip().upper()
