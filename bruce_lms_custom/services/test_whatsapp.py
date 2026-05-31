# Copyright (c) 2026, Estevão Oliveira Portes and contributors
# For license information, please see license.txt

import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from bruce_lms_custom.services.whatsapp import (
	LOG_STATUS_FAILED,
	LOG_STATUS_SENT,
	build_live_class_message,
	get_live_class_batch_recipient_candidates,
	get_live_class_recipients,
	normalize_phone,
	send_live_class_link_for_doc,
)


class FakeLog:
	def __init__(self, values):
		self.__dict__.update(values)
		self.name = "BWN-2026-00001"
		self.insert_called = False
		self.save_called = False

	def insert(self, ignore_permissions=False):
		self.insert_called = True
		self.insert_ignore_permissions = ignore_permissions
		return self

	def save(self, ignore_permissions=False):
		self.save_called = True
		self.save_ignore_permissions = ignore_permissions
		return self


class FakeResponse:
	status_code = 200
	text = "ok"

	def raise_for_status(self):
		return None

	def json(self):
		return {"ok": True}


class TestWhatsAppService(unittest.TestCase):
	def make_live_class(self):
		return SimpleNamespace(
			name="BLC-2026-00001",
			title="Aula de História",
			course="historia-enem",
			batch="turma-2026",
			starts_at=None,
			meeting_url="https://meet.jit.si/bruce-token",
			whatsapp_recipient_name="",
			whatsapp_phone="",
		)

	def test_normalize_phone_removes_symbols_and_adds_brazil_code(self):
		self.assertEqual(normalize_phone("(11) 99999-9999"), "5511999999999")
		self.assertEqual(normalize_phone("+55 (11) 99999-9999"), "5511999999999")

	def test_get_live_class_recipients_uses_manual_whatsapp_recipient_first(self):
		live_class = self.make_live_class()
		live_class.whatsapp_recipient_name = "Contato Teste"
		live_class.whatsapp_phone = "(11) 99999-9999"

		with patch("bruce_lms_custom.services.whatsapp._", side_effect=lambda message, *args, **kwargs: message):
			recipients = get_live_class_recipients(live_class)

		self.assertEqual(
			recipients,
			[
				{
					"user": None,
					"recipient_name": "Contato Teste",
					"phone": "5511999999999",
				}
			],
		)

	def test_get_live_class_recipients_returns_empty_without_manual_phone(self):
		live_class = self.make_live_class()

		with patch("bruce_lms_custom.services.whatsapp.get_live_class_batch_recipient_candidates", return_value=[]):
			self.assertEqual(get_live_class_recipients(live_class), [])

	def test_get_live_class_recipients_falls_back_to_batch_students(self):
		live_class = self.make_live_class()

		with patch(
			"bruce_lms_custom.services.whatsapp.get_live_class_batch_recipient_candidates",
			return_value=[{"user": "ana@example.com", "recipient_name": "Ana", "phone": "5511999999999"}],
		):
			recipients = get_live_class_recipients(live_class)

		self.assertEqual(
			recipients,
			[{"user": "ana@example.com", "recipient_name": "Ana", "phone": "5511999999999"}],
		)

	def test_get_live_class_batch_recipient_candidates_uses_user_phones_without_duplicates(self):
		live_class = self.make_live_class()
		members = [
			SimpleNamespace(member="ana@example.com", member_name="Ana"),
			SimpleNamespace(member="ana.duplicada@example.com", member_name="Ana Duplicada"),
			SimpleNamespace(member="bia@example.com", member_name=""),
			SimpleNamespace(member="semtelefone@example.com", member_name="Sem Telefone"),
		]
		contacts = {
			"ana@example.com": {"full_name": "Ana Silva", "mobile_no": "(11) 99999-9999", "phone": ""},
			"ana.duplicada@example.com": {"full_name": "Ana Outra", "mobile_no": "+55 11 99999-9999", "phone": ""},
			"bia@example.com": {"full_name": "Bia Souza", "mobile_no": "", "phone": "21 3333-4444"},
			"semtelefone@example.com": {"full_name": "Sem Telefone", "mobile_no": "", "phone": ""},
		}

		with (
			patch("bruce_lms_custom.services.whatsapp.get_batch_members", return_value=members) as get_batch_members,
			patch("bruce_lms_custom.services.whatsapp.get_user_contact", side_effect=lambda user: contacts[user]),
		):
			recipients = get_live_class_batch_recipient_candidates(live_class)

		get_batch_members.assert_called_once_with("turma-2026")
		self.assertEqual(
			recipients,
			[
				{"user": "ana@example.com", "recipient_name": "Ana", "phone": "5511999999999"},
				{"user": "bia@example.com", "recipient_name": "Bia Souza", "phone": "552133334444"},
			],
		)

	def test_build_live_class_message_uses_active_template(self):
		live_class = self.make_live_class()
		recipient = {"recipient_name": "Ana", "phone": "5511999999999"}
		template = Mock(message_body="<p>Olá {nome}, entre na aula {aula}: {link}</p>")

		with (
			patch("bruce_lms_custom.services.whatsapp.get_active_template", return_value=template),
			patch("bruce_lms_custom.services.whatsapp._", side_effect=lambda message, *args, **kwargs: message),
		):
			message = build_live_class_message(live_class, recipient)

		self.assertEqual(message, "Olá Ana, entre na aula Aula de História: https://meet.jit.si/bruce-token")

	def test_disabled_settings_registers_failed_log_without_external_call(self):
		live_class = self.make_live_class()
		settings = Mock(enabled=0, provider_mode="Evolution API")
		logs = []

		def fake_get_doc(values):
			log = FakeLog(values)
			logs.append(log)
			return log

		with (
			patch("bruce_lms_custom.services.whatsapp.get_live_class_recipients", return_value=[
				{"recipient_name": "Ana", "phone": "5511999999999", "user": "ana@example.com"}
			]),
			patch("bruce_lms_custom.services.whatsapp.get_active_template", return_value=None),
			patch("bruce_lms_custom.services.whatsapp.get_settings", return_value=settings),
			patch("bruce_lms_custom.services.whatsapp.frappe.get_doc", side_effect=fake_get_doc),
			patch("bruce_lms_custom.services.whatsapp.frappe.db", Mock()),
			patch("bruce_lms_custom.services.whatsapp.now_datetime", return_value="2026-05-30 12:00:00"),
			patch("bruce_lms_custom.services.whatsapp.requests.post") as post,
			patch("bruce_lms_custom.services.whatsapp._", side_effect=lambda message, *args, **kwargs: message),
		):
			result = send_live_class_link_for_doc(live_class)

		post.assert_not_called()
		self.assertEqual(result["status"], "failed")
		self.assertEqual(result["failed_count"], 1)
		self.assertEqual(logs[0].status, LOG_STATUS_FAILED)
		self.assertIn("desativada", logs[0].error_message)

	def test_n8n_provider_sends_message_and_marks_log_as_sent(self):
		live_class = self.make_live_class()
		settings = Mock(enabled=1, provider_mode="n8n", n8n_webhook_url="https://n8n.example/webhook")
		logs = []

		def fake_get_doc(values):
			log = FakeLog(values)
			logs.append(log)
			return log

		with (
			patch("bruce_lms_custom.services.whatsapp.get_live_class_recipients", return_value=[
				{"recipient_name": "Ana", "phone": "+55 (11) 99999-9999", "user": "ana@example.com"}
			]),
			patch("bruce_lms_custom.services.whatsapp.get_active_template", return_value=None),
			patch("bruce_lms_custom.services.whatsapp.get_settings", return_value=settings),
			patch("bruce_lms_custom.services.whatsapp.frappe.get_doc", side_effect=fake_get_doc),
			patch("bruce_lms_custom.services.whatsapp.frappe.db", Mock()),
			patch("bruce_lms_custom.services.whatsapp.now_datetime", return_value="2026-05-30 12:00:00"),
			patch("bruce_lms_custom.services.whatsapp.requests.post", return_value=FakeResponse()) as post,
			patch("bruce_lms_custom.services.whatsapp._", side_effect=lambda message, *args, **kwargs: message),
		):
			result = send_live_class_link_for_doc(live_class)

		self.assertEqual(result["status"], "sent")
		self.assertEqual(result["sent_count"], 1)
		self.assertEqual(logs[0].status, LOG_STATUS_SENT)
		post.assert_called_once()
		self.assertEqual(post.call_args.kwargs["json"]["phone"], "5511999999999")
		self.assertNotIn("apikey", post.call_args.kwargs["headers"])


if __name__ == "__main__":
	unittest.main()
