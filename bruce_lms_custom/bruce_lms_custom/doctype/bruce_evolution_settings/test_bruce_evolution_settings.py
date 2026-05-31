# Copyright (c) 2026, Estevão Oliveira Portes and contributors
# For license information, please see license.txt

import unittest
from unittest.mock import patch

from bruce_lms_custom.bruce_lms_custom.doctype.bruce_evolution_settings.bruce_evolution_settings import (
	BruceEvolutionSettings,
)


class TestBruceEvolutionSettings(unittest.TestCase):
	def make_doc(self, **values):
		doc = object.__new__(BruceEvolutionSettings)
		doc.enabled = 0
		doc.provider_mode = "Evolution API"
		doc.api_url = ""
		doc.instance_name = ""
		doc.n8n_webhook_url = ""

		for fieldname, value in values.items():
			setattr(doc, fieldname, value)

		return doc

	def test_validate_normalizes_urls(self):
		doc = self.make_doc(
			api_url=" evolution.local:8080/ ",
			n8n_webhook_url=" https://n8n.local/webhook/bruce/ ",
		)

		doc.validate()

		self.assertEqual(doc.api_url, "https://evolution.local:8080")
		self.assertEqual(doc.n8n_webhook_url, "https://n8n.local/webhook/bruce")

	def test_enabled_evolution_api_requires_api_url_and_instance_name(self):
		doc = self.make_doc(enabled=1, provider_mode="Evolution API")

		with (
			patch(
				"bruce_lms_custom.bruce_lms_custom.doctype.bruce_evolution_settings.bruce_evolution_settings.frappe.throw",
				side_effect=Exception("configuração incompleta"),
			),
			patch(
				"bruce_lms_custom.bruce_lms_custom.doctype.bruce_evolution_settings.bruce_evolution_settings._",
				side_effect=lambda message, *args, **kwargs: message,
			),
		):
			with self.assertRaisesRegex(Exception, "configuração incompleta"):
				doc.validate()

	def test_enabled_n8n_requires_webhook_url(self):
		doc = self.make_doc(enabled=1, provider_mode="n8n")

		with (
			patch(
				"bruce_lms_custom.bruce_lms_custom.doctype.bruce_evolution_settings.bruce_evolution_settings.frappe.throw",
				side_effect=Exception("sem webhook"),
			),
			patch(
				"bruce_lms_custom.bruce_lms_custom.doctype.bruce_evolution_settings.bruce_evolution_settings._",
				side_effect=lambda message, *args, **kwargs: message,
			),
		):
			with self.assertRaisesRegex(Exception, "sem webhook"):
				doc.validate()
