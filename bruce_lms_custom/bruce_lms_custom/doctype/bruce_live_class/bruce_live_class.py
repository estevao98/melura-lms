# Copyright (c) 2026, Estevão Oliveira Portes and contributors
# For license information, please see license.txt

import secrets
import re
from urllib.parse import quote

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_datetime


class BruceLiveClass(Document):
	def before_insert(self):
		if not self.room_name:
			self.room_name = self.generate_room_name()

	def validate(self):
		if self.starts_at and self.ends_at and get_datetime(self.ends_at) <= get_datetime(self.starts_at):
			frappe.throw(_("A data de término deve ser posterior ao início da aula."))

		if not self.room_name:
			self.room_name = self.generate_room_name()

		self.meeting_url = self.build_meeting_url()

	def generate_room_name(self):
		settings = frappe.get_single("Bruce Jitsi Settings")
		prefix = re.sub(r"[^a-z0-9]+", "-", (settings.room_prefix or "bruce").strip().lower()).strip("-")
		prefix = prefix or "bruce"

		for _attempt in range(5):
			room_name = f"{prefix}-{secrets.token_urlsafe(18)}"
			if not frappe.db.exists("Bruce Live Class", {"room_name": room_name}):
				return room_name

		frappe.throw(_("Não foi possível gerar uma sala Jitsi única. Tente novamente."))

	def build_meeting_url(self):
		if not self.room_name:
			return self.meeting_url

		settings = frappe.get_single("Bruce Jitsi Settings")
		domain = (settings.domain or "meet.jit.si").strip().rstrip("/")

		if "://" not in domain:
			domain = f"https://{domain}"

		return f"{domain}/{quote(self.room_name, safe='')}"
