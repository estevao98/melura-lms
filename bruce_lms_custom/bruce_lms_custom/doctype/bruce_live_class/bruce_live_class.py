# Copyright (c) 2026, Estevão Oliveira Portes and contributors
# For license information, please see license.txt

import re
import secrets
from dataclasses import dataclass
from urllib.parse import quote

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_datetime


@dataclass(frozen=True)
class JitsiSettings:
	domain: str = "meet.jit.si"
	room_prefix: str = "bruce"


class BruceLiveClass(Document):
	def before_insert(self):
		if not self.room_name:
			self.room_name = self.generate_room_name()

	def validate(self):
		if self.starts_at and self.ends_at and get_datetime(self.ends_at) <= get_datetime(self.starts_at):
			frappe.throw(_("A data de término deve ser posterior ao início da aula."))

		if not self.room_name:
			self.room_name = self.generate_room_name()

		if not self.meeting_url:
			self.meeting_url = self.build_meeting_url()

	def generate_room_name(self):
		settings = self.get_jitsi_settings()
		prefix = re.sub(r"[^a-z0-9]+", "-", (settings.room_prefix or "bruce").strip().lower()).strip("-")
		prefix = prefix or "bruce"

		for _attempt in range(5):
			room_name = f"{prefix}-{secrets.token_urlsafe(18)}"
			if not self.room_name_exists(room_name):
				return room_name

		frappe.throw(_("Não foi possível gerar uma sala Jitsi única. Tente novamente."))

	def build_meeting_url(self):
		if not self.room_name:
			return self.meeting_url

		settings = self.get_jitsi_settings()
		domain = (settings.domain or "meet.jit.si").strip().rstrip("/")

		if "://" not in domain:
			domain = f"https://{domain}"

		return f"{domain}/{quote(self.room_name, safe='')}"

	@staticmethod
	def get_jitsi_settings():
		try:
			return frappe.get_single("Bruce Jitsi Settings")
		except frappe.DoesNotExistError:
			return JitsiSettings()

	@staticmethod
	def room_name_exists(room_name):
		return frappe.db.exists("Bruce Live Class", {"room_name": room_name})


@frappe.whitelist()
def start_live_class(name):
	doc = frappe.get_doc("Bruce Live Class", name)
	doc.check_permission("write")

	if not doc.meeting_url:
		frappe.throw(_("Esta aula ainda não tem link Jitsi. Salve a aula novamente ou revise a configuração do Jitsi."))

	if doc.status == "Ao vivo":
		return {
			"status": doc.status,
			"meeting_url": doc.meeting_url,
			"message": _("A aula já está ao vivo."),
		}

	if doc.status != "Agendada":
		frappe.throw(_("Somente aulas agendadas podem ser iniciadas."))

	doc.status = "Ao vivo"
	doc.save()

	return {
		"status": doc.status,
		"meeting_url": doc.meeting_url,
		"message": _("A aula foi marcada como ao vivo."),
	}
