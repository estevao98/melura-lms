# Copyright (c) 2026, Estevão Oliveira Portes and contributors
# For license information, please see license.txt

import unittest
from unittest.mock import Mock, patch

import frappe

from bruce_lms_custom.bruce_lms_custom.doctype.bruce_live_class.bruce_live_class import BruceLiveClass


class TestBruceLiveClass(unittest.TestCase):
	def make_doc(self, **values):
		doc = object.__new__(BruceLiveClass)
		doc.starts_at = None
		doc.ends_at = None
		doc.room_name = ""
		doc.meeting_url = ""

		for fieldname, value in values.items():
			setattr(doc, fieldname, value)

		return doc

	def test_generate_room_name_uses_configured_prefix_and_secure_token(self):
		settings = Mock(room_prefix="bruce-enem", domain="meet.jit.si")
		doc = self.make_doc()

		with (
			patch(
				"bruce_lms_custom.bruce_lms_custom.doctype.bruce_live_class.bruce_live_class.frappe.get_single",
				return_value=settings,
			),
			patch(
				"bruce_lms_custom.bruce_lms_custom.doctype.bruce_live_class.bruce_live_class.BruceLiveClass.room_name_exists",
				return_value=False,
			),
			patch(
				"bruce_lms_custom.bruce_lms_custom.doctype.bruce_live_class.bruce_live_class.secrets.token_urlsafe",
				return_value="token-seguro_123",
			),
		):
			room_name = doc.generate_room_name()

		self.assertEqual(room_name, "bruce-enem-token-seguro_123")

	def test_build_meeting_url_uses_safe_fallback_when_settings_do_not_exist(self):
		doc = self.make_doc(room_name="bruce-token-seguro")

		with patch(
			"bruce_lms_custom.bruce_lms_custom.doctype.bruce_live_class.bruce_live_class.frappe.get_single",
			side_effect=frappe.DoesNotExistError("Bruce Jitsi Settings"),
		):
			meeting_url = doc.build_meeting_url()

		self.assertEqual(meeting_url, "https://meet.jit.si/bruce-token-seguro")

	def test_validate_does_not_overwrite_existing_meeting_url(self):
		doc = self.make_doc(
			room_name="sala-existente",
			meeting_url="https://meet.jit.si/sala-existente",
		)

		doc.validate()

		self.assertEqual(doc.room_name, "sala-existente")
		self.assertEqual(doc.meeting_url, "https://meet.jit.si/sala-existente")
