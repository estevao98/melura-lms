# Copyright (c) 2026, Estevão Oliveira Portes and contributors
# For license information, please see LICENSE

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint

from melura_lms.services.live_class_automation import validate_google_meet_url


class MeluraLiveClassSchedule(Document):
	def validate(self):
		validate_google_meet_url(self.google_meet_url)

		if cint(self.duration_minutes) <= 0:
			frappe.throw(_("A duração da aula deve ser maior que zero."))

		generate_days_ahead = cint(self.generate_days_ahead)
		if generate_days_ahead < 1 or generate_days_ahead > 90:
			frappe.throw(_("O período de geração deve ficar entre 1 e 90 dias."))

		if cint(self.notify_minutes_before) < 0:
			frappe.throw(_("O lembrete dos alunos não pode ser negativo."))

		if cint(self.professor_notify_minutes_before) < 0:
			frappe.throw(_("O lembrete do professor não pode ser negativo."))
