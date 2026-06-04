# Copyright (c) 2026, Estevão Oliveira Portes and contributors
# For license information, please see LICENSE

from urllib.parse import urlparse

import frappe
from frappe import _
from frappe.model.document import Document


class BruceJitsiSettings(Document):
	def validate(self):
		self.domain = self.normalize_domain(self.domain)

	@staticmethod
	def normalize_domain(domain):
		if not domain:
			return domain

		value = domain.strip()
		parsed = urlparse(value if "://" in value else f"https://{value}")

		if not parsed.netloc:
			frappe.throw(_("Informe um domínio Jitsi válido."))

		return parsed.netloc.rstrip("/")
