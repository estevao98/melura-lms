# Copyright (c) 2026, Estevão Oliveira Portes and contributors
# For license information, please see LICENSE

import unittest
from unittest.mock import patch

from melura_lms.melura_lms.doctype.melura_live_class_schedule.melura_live_class_schedule import (
	MeluraLiveClassSchedule,
)


class TestMeluraLiveClassSchedule(unittest.TestCase):
	def make_doc(self, **values):
		doc = object.__new__(MeluraLiveClassSchedule)
		doc.google_meet_url = "https://meet.google.com/abc-defg-hij"
		doc.duration_minutes = 60
		doc.generate_days_ahead = 14
		doc.notify_minutes_before = 30
		doc.professor_notify_minutes_before = 30

		for fieldname, value in values.items():
			setattr(doc, fieldname, value)

		return doc

	def test_validate_accepts_valid_google_meet_schedule(self):
		doc = self.make_doc()

		doc.validate()

		self.assertEqual(doc.google_meet_url, "https://meet.google.com/abc-defg-hij")

	def test_validate_rejects_invalid_google_meet_url(self):
		doc = self.make_doc(google_meet_url="https://evil.com/aula")

		with (
			patch("melura_lms.services.live_class_automation.frappe.throw", side_effect=Exception("url inválida")),
			patch("melura_lms.services.live_class_automation._", side_effect=lambda message, *args, **kwargs: message),
		):
			with self.assertRaisesRegex(Exception, "url inválida"):
				doc.validate()

	def test_validate_rejects_invalid_duration(self):
		doc = self.make_doc(duration_minutes=0)

		with (
			patch(
				"melura_lms.melura_lms.doctype.melura_live_class_schedule.melura_live_class_schedule.frappe.throw",
				side_effect=Exception("duração inválida"),
			),
			patch(
				"melura_lms.melura_lms.doctype.melura_live_class_schedule.melura_live_class_schedule._",
				side_effect=lambda message, *args, **kwargs: message,
			),
		):
			with self.assertRaisesRegex(Exception, "duração inválida"):
				doc.validate()

	def test_validate_rejects_generate_days_outside_range(self):
		doc = self.make_doc(generate_days_ahead=91)

		with (
			patch(
				"melura_lms.melura_lms.doctype.melura_live_class_schedule.melura_live_class_schedule.frappe.throw",
				side_effect=Exception("período inválido"),
			),
			patch(
				"melura_lms.melura_lms.doctype.melura_live_class_schedule.melura_live_class_schedule._",
				side_effect=lambda message, *args, **kwargs: message,
			),
		):
			with self.assertRaisesRegex(Exception, "período inválido"):
				doc.validate()


if __name__ == "__main__":
	unittest.main()
