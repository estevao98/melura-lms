# Copyright (c) 2026, Estevão Oliveira Portes and contributors
# For license information, please see LICENSE

from urllib.parse import urlparse

import frappe
from frappe import _
from frappe.model.document import Document


class MeluraWhatsAppSettings(Document):
	def validate(self):
		self.api_url = self.normalize_url(self.api_url)
		self.n8n_webhook_url = self.normalize_url(self.n8n_webhook_url)

		if self.enabled:
			if self.provider_mode == "Evolution API" and not self.api_url:
				frappe.throw(_("Informe a URL da Evolution API."))

			if self.provider_mode == "Evolution API" and not self.instance_name:
				frappe.throw(_("Informe o nome da instância da Evolution API."))

			if self.provider_mode == "n8n" and not self.n8n_webhook_url:
				frappe.throw(_("Informe a URL do webhook n8n."))

	@staticmethod
	def normalize_url(url):
		if not url:
			return url

		value = url.strip()
		parsed = urlparse(value if "://" in value else f"https://{value}")

		if not parsed.netloc:
			frappe.throw(_("Informe uma URL válida."))

		return parsed.geturl().rstrip("/")
