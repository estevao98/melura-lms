# Copyright (c) 2026, Estevão Oliveira Portes and contributors
# For license information, please see LICENSE

import unittest
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import Mock, patch

from melura_lms.services.live_class_automation import (
	generate_live_classes_for_schedule,
	send_due_live_class_reminders,
	send_professor_reminder_for_live_class,
	send_student_reminders_for_live_class,
)


class FakeLiveClass:
	def __init__(self, values):
		self.__dict__.update(values)
		self.name = "BLC-2026-00001"
		self.doctype = "Bruce Live Class"
		self.insert_called = False

	def insert(self, ignore_permissions=False):
		self.insert_called = True
		self.insert_ignore_permissions = ignore_permissions
		return self


class FakeLog:
	name = "BWN-2026-00001"
	status = "Pendente"
	error_message = ""

	def save(self, ignore_permissions=False):
		self.save_ignore_permissions = ignore_permissions
		return self


class TestLiveClassAutomation(unittest.TestCase):
	def make_schedule(self, **values):
		schedule = SimpleNamespace(
			name="MLCS-2026-00001",
			title="História ENEM",
			enabled=1,
			course="COURSE-001",
			batch="BATCH-001",
			instructor="professor@example.com",
			google_meet_url="https://meet.google.com/abc-defg-hij",
			weekday="Segunda",
			starts_at_time="19:00:00",
			duration_minutes=60,
			generate_days_ahead=14,
			notify_minutes_before=30,
			professor_notify_minutes_before=30,
			auto_send_student_reminder=1,
			auto_send_professor_reminder=1,
		)
		for fieldname, value in values.items():
			setattr(schedule, fieldname, value)
		return schedule

	def make_live_class(self, **values):
		doc = SimpleNamespace(
			name="BLC-2026-00001",
			doctype="Bruce Live Class",
			title="História ENEM - 08/06/2026",
			course="COURSE-001",
			batch="BATCH-001",
			instructor="professor@example.com",
			starts_at=datetime(2026, 6, 8, 19, 0),
			meeting_url="https://meet.google.com/abc-defg-hij",
			generated_from_schedule="MLCS-2026-00001",
			reminder_sent_at=None,
			professor_reminder_sent_at=None,
		)
		for fieldname, value in values.items():
			setattr(doc, fieldname, value)
		return doc

	def test_enabled_schedule_generates_future_classes(self):
		schedule = self.make_schedule()
		created_docs = []

		def fake_get_doc(values):
			doc = FakeLiveClass(values)
			created_docs.append(doc)
			return doc

		with (
			patch("melura_lms.services.live_class_automation.find_existing_generated_class", return_value=None),
			patch("melura_lms.services.live_class_automation.frappe.get_doc", side_effect=fake_get_doc),
			patch("melura_lms.services.live_class_automation.frappe.db", Mock(set_value=Mock())),
			patch("melura_lms.services.live_class_automation.now_datetime", return_value="2026-06-04 10:00:00"),
		):
			result = generate_live_classes_for_schedule(schedule, today="2026-06-04")

		self.assertEqual(result, ["BLC-2026-00001", "BLC-2026-00001"])
		self.assertEqual(len(created_docs), 2)
		self.assertTrue(all(doc.insert_called for doc in created_docs))
		self.assertEqual(created_docs[0].meeting_url, "https://meet.google.com/abc-defg-hij")
		self.assertEqual(created_docs[0].auto_generated, 1)
		self.assertEqual(created_docs[0].generated_from_schedule, "MLCS-2026-00001")

	def test_disabled_schedule_generates_nothing(self):
		with patch("melura_lms.services.live_class_automation.frappe.get_doc") as get_doc:
			result = generate_live_classes_for_schedule(self.make_schedule(enabled=0), today="2026-06-04")

		get_doc.assert_not_called()
		self.assertEqual(result, [])

	def test_duplicate_class_is_not_generated(self):
		with (
			patch("melura_lms.services.live_class_automation.find_existing_generated_class", return_value="BLC-2026-00001"),
			patch("melura_lms.services.live_class_automation.frappe.get_doc") as get_doc,
			patch("melura_lms.services.live_class_automation.frappe.db", Mock(set_value=Mock())),
			patch("melura_lms.services.live_class_automation.now_datetime", return_value="2026-06-04 10:00:00"),
		):
			result = generate_live_classes_for_schedule(self.make_schedule(generate_days_ahead=7), today="2026-06-04")

		get_doc.assert_not_called()
		self.assertEqual(result, [])

	def test_invalid_google_meet_url_is_rejected(self):
		with (
			patch("melura_lms.services.live_class_automation.frappe.throw", side_effect=Exception("url inválida")),
			patch("melura_lms.services.live_class_automation._", side_effect=lambda message, *args, **kwargs: message),
		):
			with self.assertRaisesRegex(Exception, "url inválida"):
				generate_live_classes_for_schedule(self.make_schedule(google_meet_url="https://evil.com/aula"), today="2026-06-04")

	def test_reminder_job_skips_classes_without_valid_url(self):
		live_class = self.make_live_class(meeting_url="https://evil.com/aula")

		with (
			patch("melura_lms.services.live_class_automation.frappe.get_all", return_value=[live_class]),
			patch("melura_lms.services.live_class_automation.send_student_reminders_for_live_class") as send_students,
			patch("melura_lms.services.live_class_automation.send_professor_reminder_for_live_class") as send_professor,
		):
			result = send_due_live_class_reminders(now=datetime(2026, 6, 8, 18, 31))

		send_students.assert_not_called()
		send_professor.assert_not_called()
		self.assertEqual(result[0]["status"], "invalid_url")

	def test_reminder_job_does_not_crash_when_whatsapp_is_disabled(self):
		live_class = self.make_live_class()
		recipient = {"user": "aluno@example.com", "recipient_name": "Ana", "phone": "5511999999999"}
		log = FakeLog()

		with (
			patch("melura_lms.services.live_class_automation.whatsapp.get_live_class_recipients", return_value=[recipient]),
			patch("melura_lms.services.live_class_automation._student_has_active_access", return_value=True),
			patch("melura_lms.services.live_class_automation.whatsapp.build_live_class_message", return_value="Mensagem"),
			patch("melura_lms.services.live_class_automation.whatsapp.create_notification_log", return_value=log),
			patch("melura_lms.services.live_class_automation.whatsapp.send_logged_message", return_value={"status": "failed", "log": log.name}),
			patch("melura_lms.services.live_class_automation.whatsapp.update_live_class_whatsapp_status"),
			patch("melura_lms.services.live_class_automation.frappe.get_doc", return_value=live_class),
		):
			result = send_student_reminders_for_live_class(live_class.name)

		self.assertFalse(result["sent"])
		self.assertEqual(result["status"], "failed")

	def test_student_reminders_are_marked_after_successful_send(self):
		live_class = self.make_live_class()
		recipient = {"user": "aluno@example.com", "recipient_name": "Ana", "phone": "5511999999999"}
		log = FakeLog()

		with (
			patch("melura_lms.services.live_class_automation.whatsapp.get_live_class_recipients", return_value=[recipient]),
			patch("melura_lms.services.live_class_automation._student_has_active_access", return_value=True),
			patch("melura_lms.services.live_class_automation.whatsapp.build_live_class_message", return_value="Mensagem"),
			patch("melura_lms.services.live_class_automation.whatsapp.create_notification_log", return_value=log),
			patch("melura_lms.services.live_class_automation.whatsapp.send_logged_message", return_value={"status": "sent", "log": log.name}),
			patch("melura_lms.services.live_class_automation.whatsapp.update_live_class_whatsapp_status"),
			patch("melura_lms.services.live_class_automation.frappe.db", Mock(set_value=Mock())) as db,
			patch("melura_lms.services.live_class_automation.now_datetime", return_value="2026-06-08 18:30:00"),
		):
			result = send_student_reminders_for_live_class(live_class)

		self.assertTrue(result["sent"])
		db.set_value.assert_called_once()
		self.assertEqual(db.set_value.call_args.args[2], "reminder_sent_at")

	def test_professor_reminder_is_separate_from_student_reminders(self):
		live_class = self.make_live_class()
		log = FakeLog()

		with (
			patch(
				"melura_lms.services.live_class_automation.frappe.db",
				Mock(
					get_value=Mock(return_value={"full_name": "Professor", "mobile_no": "(11) 99999-9999", "phone": ""}),
					set_value=Mock(),
				),
			) as db,
			patch("melura_lms.services.live_class_automation.whatsapp.create_notification_log", return_value=log),
			patch("melura_lms.services.live_class_automation.whatsapp.send_logged_message", return_value={"status": "sent", "log": log.name}),
			patch("melura_lms.services.live_class_automation.get_url", return_value="https://app.example"),
			patch("melura_lms.services.live_class_automation.now_datetime", return_value="2026-06-08 18:30:00"),
			patch("melura_lms.services.live_class_automation._", side_effect=lambda message, *args, **kwargs: message),
			patch("melura_lms.services.live_class_automation.frappe.format", return_value="08/06/2026 19:00"),
		):
			result = send_professor_reminder_for_live_class(live_class)

		self.assertTrue(result["sent"])
		self.assertEqual(db.set_value.call_args.args[2], "professor_reminder_sent_at")


if __name__ == "__main__":
	unittest.main()
