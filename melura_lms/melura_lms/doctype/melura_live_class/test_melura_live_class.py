# Copyright (c) 2026, Estevão Oliveira Portes and contributors
# For license information, please see LICENSE

import unittest
from unittest.mock import Mock, patch

from melura_lms.melura_lms.doctype.melura_live_class.melura_live_class import (
	MeluraLiveClass,
	start_live_class,
)
from melura_lms.services.live_class_automation import validate_google_meet_url

start_live_class_without_frappe_wrapper = getattr(start_live_class, "__wrapped__", start_live_class)


class TestMeluraLiveClass(unittest.TestCase):
	def make_doc(self, **values):
		doc = object.__new__(MeluraLiveClass)
		doc.starts_at = None
		doc.ends_at = None
		doc.room_name = ""
		doc.meeting_url = "https://meet.google.com/abc-defg-hij"
		doc.whatsapp_phone = ""
		doc.generated_from_schedule = ""

		for fieldname, value in values.items():
			setattr(doc, fieldname, value)

		return doc

	def test_validate_google_meet_url_accepts_standard_url(self):
		self.assertEqual(validate_google_meet_url("https://meet.google.com/abc-defg-hij"), "https://meet.google.com/abc-defg-hij")

	def test_validate_google_meet_url_accepts_lookup_url(self):
		self.assertEqual(validate_google_meet_url("https://meet.google.com/lookup/aula123"), "https://meet.google.com/lookup/aula123")

	def test_validate_google_meet_url_rejects_invalid_urls(self):
		invalid_urls = [
			"http://meet.google.com/abc-defg-hij",
			"https://evil.com/abc-defg-hij",
			"javascript:alert(1)",
			"data:text/html,abc",
			"file:///tmp/aula",
			"ftp://meet.google.com/abc-defg-hij",
			"",
		]

		for url in invalid_urls:
			with self.subTest(url=url):
				with (
					patch(
						"melura_lms.services.live_class_automation.frappe.throw",
						side_effect=Exception("url inválida"),
					),
					patch("melura_lms.services.live_class_automation._", side_effect=lambda message, *args, **kwargs: message),
				):
					with self.assertRaisesRegex(Exception, "url inválida"):
						validate_google_meet_url(url)

	def test_validate_does_not_require_room_name(self):
		doc = self.make_doc(room_name="")

		doc.validate()

		self.assertEqual(doc.room_name, "")
		self.assertEqual(doc.meeting_url, "https://meet.google.com/abc-defg-hij")

	def test_validate_loads_default_google_meet_url_from_schedule(self):
		doc = self.make_doc(meeting_url="", generated_from_schedule="MLCS-2026-00001")

		with patch(
			"melura_lms.melura_lms.doctype.melura_live_class.melura_live_class.frappe.db",
			Mock(get_value=Mock(return_value="https://meet.google.com/abc-defg-hij")),
		):
			doc.validate()

		self.assertEqual(doc.meeting_url, "https://meet.google.com/abc-defg-hij")

	def test_validate_normalizes_manual_whatsapp_phone(self):
		doc = self.make_doc(whatsapp_phone="(11) 99999-9999")

		doc.validate()

		self.assertEqual(doc.whatsapp_phone, "5511999999999")

	def test_start_live_class_marks_scheduled_class_as_live(self):
		doc = Mock(status="Agendada", meeting_url="https://meet.google.com/abc-defg-hij")
		doc.name = "BLC-2026-00001"

		with (
			patch(
				"melura_lms.melura_lms.doctype.melura_live_class.melura_live_class.frappe.get_doc",
				return_value=doc,
			),
			patch("melura_lms.melura_lms.doctype.melura_live_class.melura_live_class._", side_effect=lambda message, *args, **kwargs: message),
			patch("melura_lms.melura_lms.doctype.melura_live_class.melura_live_class.create_notice_log") as create_notice_log,
		):
			result = start_live_class_without_frappe_wrapper("BLC-2026-00001")

		doc.check_permission.assert_called_once_with("write")
		doc.save.assert_called_once_with()
		create_notice_log.assert_called_once()
		self.assertEqual(doc.status, "Ao vivo")
		self.assertEqual(result["meeting_url"], "https://meet.google.com/abc-defg-hij")
		self.assertEqual(result["live_room_route"], "/app/melura-live-room/BLC-2026-00001")

	def test_start_live_class_requires_meeting_url(self):
		doc = Mock(status="Agendada", meeting_url="")

		with (
			patch(
				"melura_lms.melura_lms.doctype.melura_live_class.melura_live_class.frappe.get_doc",
				return_value=doc,
			),
			patch(
				"melura_lms.melura_lms.doctype.melura_live_class.melura_live_class.frappe.throw",
				side_effect=Exception("sem link"),
			),
			patch("melura_lms.melura_lms.doctype.melura_live_class.melura_live_class._", side_effect=lambda message, *args, **kwargs: message),
		):
			with self.assertRaisesRegex(Exception, "sem link"):
				start_live_class_without_frappe_wrapper("BLC-2026-00001")

		doc.check_permission.assert_called_once_with("write")
		doc.save.assert_not_called()

	def test_start_live_class_rejects_closed_class(self):
		doc = Mock(status="Encerrada", meeting_url="https://meet.google.com/abc-defg-hij")

		with (
			patch(
				"melura_lms.melura_lms.doctype.melura_live_class.melura_live_class.frappe.get_doc",
				return_value=doc,
			),
			patch(
				"melura_lms.melura_lms.doctype.melura_live_class.melura_live_class.frappe.throw",
				side_effect=Exception("status inválido"),
			),
			patch("melura_lms.melura_lms.doctype.melura_live_class.melura_live_class._", side_effect=lambda message, *args, **kwargs: message),
		):
			with self.assertRaisesRegex(Exception, "status inválido"):
				start_live_class_without_frappe_wrapper("BLC-2026-00001")

		doc.check_permission.assert_called_once_with("write")
		doc.save.assert_not_called()


if __name__ == "__main__":
	unittest.main()
