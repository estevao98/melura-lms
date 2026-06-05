# Copyright (c) 2026, Estevão Oliveira Portes and contributors
# For license information, please see LICENSE

import re

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_datetime

from melura_lms.melura_lms.doctype.bruce_live_class_notice_log.bruce_live_class_notice_log import (
	EVENT_CLASS_STARTED,
	STATUS_SUCCESS,
	create_notice_log,
)
from melura_lms.services.live_class_automation import validate_google_meet_url
from melura_lms.services.routes import get_live_room_route


JITSI_SETTINGS_CACHE_KEY = "melura_lms:v1:jitsi-settings:public"


class BruceLiveClass(Document):
	def validate(self):
		if self.starts_at and self.ends_at and get_datetime(self.ends_at) <= get_datetime(self.starts_at):
			frappe.throw(_("A data de término deve ser posterior ao início da aula."))

		if getattr(self, "whatsapp_phone", None):
			self.whatsapp_phone = self.normalize_whatsapp_phone(self.whatsapp_phone)

		if not self.meeting_url:
			self.meeting_url = self.get_default_google_meet_url()

		if self.meeting_url:
			validate_google_meet_url(self.meeting_url)

	def normalize_whatsapp_phone(self, phone):
		phone = re.sub(r"\D+", "", phone or "")

		if len(phone) in (10, 11) and not phone.startswith("55"):
			return f"55{phone}"

		return phone

	def get_default_google_meet_url(self):
		schedule_name = getattr(self, "generated_from_schedule", None)
		if not schedule_name:
			return ""

		try:
			return frappe.db.get_value("Melura Live Class Schedule", schedule_name, "google_meet_url") or ""
		except Exception:
			return ""


@frappe.whitelist()
def start_live_class(name):
	doc = frappe.get_doc("Bruce Live Class", name)
	doc.check_permission("write")

	if not doc.meeting_url:
		frappe.throw(_("Esta aula ainda não tem link do Google Meet configurado."))

	validate_google_meet_url(doc.meeting_url)

	if doc.status == "Ao vivo":
		return {
			"name": doc.name,
			"status": doc.status,
			"meeting_url": doc.meeting_url,
			"live_room_route": get_live_room_route(doc.name),
			"message": _("A aula já está ao vivo."),
		}

	if doc.status != "Agendada":
		frappe.throw(_("Somente aulas agendadas podem ser iniciadas."))

	doc.status = "Ao vivo"
	doc.save()
	create_notice_log(
		doc,
		EVENT_CLASS_STARTED,
		_("Aula iniciada"),
		_("A aula foi marcada como ao vivo pelo usuário."),
		STATUS_SUCCESS,
	)

	return {
		"name": doc.name,
		"status": doc.status,
		"meeting_url": doc.meeting_url,
		"live_room_route": get_live_room_route(doc.name),
		"message": _("A aula foi marcada como ao vivo."),
	}
