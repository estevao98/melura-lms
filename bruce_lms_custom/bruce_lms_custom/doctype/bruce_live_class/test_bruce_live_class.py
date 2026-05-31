# Copyright (c) 2026, Estevão Oliveira Portes and contributors
# For license information, please see license.txt

import unittest
from unittest.mock import Mock, patch

import frappe

from bruce_lms_custom.bruce_lms_custom.doctype.bruce_live_class.bruce_live_class import (
	BruceLiveClass,
	start_live_class,
)

start_live_class_without_frappe_wrapper = getattr(start_live_class, "__wrapped__", start_live_class)


class TestBruceLiveClass(unittest.TestCase):
	def make_doc(self, **values):
		doc = object.__new__(BruceLiveClass)
		doc.starts_at = None
		doc.ends_at = None
		doc.room_name = ""
		doc.meeting_url = ""
		doc.whatsapp_phone = ""

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

	def test_validate_normalizes_manual_whatsapp_phone(self):
		doc = self.make_doc(
			room_name="sala-existente",
			meeting_url="https://meet.jit.si/sala-existente",
			whatsapp_phone="(11) 99999-9999",
		)

		doc.validate()

		self.assertEqual(doc.whatsapp_phone, "5511999999999")

	def test_start_live_class_marks_scheduled_class_as_live(self):
		doc = Mock(status="Agendada", meeting_url="https://meet.jit.si/sala-existente")

		with (
			patch(
				"bruce_lms_custom.bruce_lms_custom.doctype.bruce_live_class.bruce_live_class.frappe.get_doc",
				return_value=doc,
			),
			patch(
				"bruce_lms_custom.bruce_lms_custom.doctype.bruce_live_class.bruce_live_class._",
				side_effect=lambda message, *args, **kwargs: message,
			),
		):
			result = start_live_class_without_frappe_wrapper("BLC-2026-00001")

		doc.check_permission.assert_called_once_with("write")
		doc.save.assert_called_once_with()
		self.assertEqual(doc.status, "Ao vivo")
		self.assertEqual(result["meeting_url"], "https://meet.jit.si/sala-existente")

	def test_start_live_class_requires_meeting_url(self):
		doc = Mock(status="Agendada", meeting_url="")

		with (
			patch(
				"bruce_lms_custom.bruce_lms_custom.doctype.bruce_live_class.bruce_live_class.frappe.get_doc",
				return_value=doc,
			),
			patch(
				"bruce_lms_custom.bruce_lms_custom.doctype.bruce_live_class.bruce_live_class.frappe.throw",
				side_effect=Exception("sem link"),
			),
			patch(
				"bruce_lms_custom.bruce_lms_custom.doctype.bruce_live_class.bruce_live_class._",
				side_effect=lambda message, *args, **kwargs: message,
			),
		):
			with self.assertRaisesRegex(Exception, "sem link"):
				start_live_class_without_frappe_wrapper("BLC-2026-00001")

		doc.check_permission.assert_called_once_with("write")
		doc.save.assert_not_called()

	def test_start_live_class_rejects_closed_class(self):
		doc = Mock(status="Encerrada", meeting_url="https://meet.jit.si/sala-existente")

		with (
			patch(
				"bruce_lms_custom.bruce_lms_custom.doctype.bruce_live_class.bruce_live_class.frappe.get_doc",
				return_value=doc,
			),
			patch(
				"bruce_lms_custom.bruce_lms_custom.doctype.bruce_live_class.bruce_live_class.frappe.throw",
				side_effect=Exception("status inválido"),
			),
			patch(
				"bruce_lms_custom.bruce_lms_custom.doctype.bruce_live_class.bruce_live_class._",
				side_effect=lambda message, *args, **kwargs: message,
			),
		):
			with self.assertRaisesRegex(Exception, "status inválido"):
				start_live_class_without_frappe_wrapper("BLC-2026-00001")

		doc.check_permission.assert_called_once_with("write")
		doc.save.assert_not_called()
