# Copyright (c) 2026, Estevão Oliveira Portes and contributors
# For license information, please see LICENSE

import unittest
from unittest.mock import patch

from melura_lms.melura_lms.doctype.bruce_jitsi_settings.bruce_jitsi_settings import BruceJitsiSettings
from melura_lms.melura_lms.doctype.bruce_live_class.bruce_live_class import JITSI_SETTINGS_CACHE_KEY


class TestBruceJitsiSettings(unittest.TestCase):
	def make_doc(self, **values):
		doc = object.__new__(BruceJitsiSettings)
		doc.domain = ""

		for fieldname, value in values.items():
			setattr(doc, fieldname, value)

		return doc

	def test_validate_normalizes_domain_and_invalidates_legacy_cache(self):
		doc = self.make_doc(domain="https://legacy-video.example.com/")

		with patch(
			"melura_lms.melura_lms.doctype.bruce_jitsi_settings.bruce_jitsi_settings.delete_cached_value"
		) as delete_cached_value:
			doc.validate()

		self.assertEqual(doc.domain, "legacy-video.example.com")
		delete_cached_value.assert_called_once_with(JITSI_SETTINGS_CACHE_KEY)


if __name__ == "__main__":
	unittest.main()
