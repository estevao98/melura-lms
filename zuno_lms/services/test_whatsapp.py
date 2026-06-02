# Copyright (c) 2026, Estevão Oliveira Portes and contributors
# For license information, please see LICENSE

import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from zuno_lms.services.whatsapp import (
	CONFIG_STATUS_DISABLED,
	CONFIG_STATUS_MISSING_API_KEY,
	CONFIG_STATUS_MISSING_API_URL,
	CONFIG_STATUS_MISSING_INSTANCE,
	CONFIG_STATUS_MISSING_SETTINGS,
	CONFIG_STATUS_VALID,
	LOG_STATUS_FAILED,
	LOG_STATUS_SENT,
	build_live_class_link_preview,
	build_live_class_message,
	get_live_class_batch_recipient_candidates,
	get_live_class_recipients,
	normalize_phone,
	redact_sensitive_values,
	send_evolution_test_message,
	send_live_class_link_for_doc,
	validate_evolution_configuration,
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

	def make_settings(self, **values):
		settings = SimpleNamespace(
			enabled=1,
			api_url="https://evolution.example",
			instance_name="bruce",
			provider_mode="Evolution API",
		)

		for fieldname, value in values.items():
			setattr(settings, fieldname, value)

		return settings

	def test_normalize_phone_removes_symbols_and_adds_brazil_code(self):
		self.assertEqual(normalize_phone("(11) 99999-9999"), "5511999999999")
		self.assertEqual(normalize_phone("+55 (11) 99999-9999"), "5511999999999")

	def test_get_live_class_recipients_uses_manual_whatsapp_recipient_first(self):
		live_class = self.make_live_class()
		live_class.whatsapp_recipient_name = "Contato Teste"
		live_class.whatsapp_phone = "(11) 99999-9999"

		with patch("zuno_lms.services.whatsapp._", side_effect=lambda message, *args, **kwargs: message):
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

		with patch("zuno_lms.services.whatsapp.get_live_class_batch_recipient_candidates", return_value=[]):
			self.assertEqual(get_live_class_recipients(live_class), [])

	def test_get_live_class_recipients_falls_back_to_batch_students(self):
		live_class = self.make_live_class()

		with patch(
			"zuno_lms.services.whatsapp.get_live_class_batch_recipient_candidates",
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
			patch("zuno_lms.services.whatsapp.get_batch_members", return_value=members) as get_batch_members,
			patch("zuno_lms.services.whatsapp.get_user_contact", side_effect=lambda user: contacts[user]),
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
			patch("zuno_lms.services.whatsapp.get_active_template", return_value=template),
			patch("zuno_lms.services.whatsapp._", side_effect=lambda message, *args, **kwargs: message),
		):
			message = build_live_class_message(live_class, recipient)

		self.assertEqual(message, "Olá Ana, entre na aula Aula de História: https://meet.jit.si/bruce-token")

	def test_build_live_class_link_preview_resolves_recipients_and_message_without_external_call(self):
		live_class = self.make_live_class()
		settings = Mock(enabled=0)
		template = Mock(
			message_body=(
				"Olá {nome}, a aula {aula} do curso {curso} para a turma {turma} "
				"começa em {inicio}. Link: {link}"
			)
		)

		with (
			patch("zuno_lms.services.whatsapp.get_live_class_recipients", return_value=[
				{"recipient_name": "Ana", "phone": "5511999999999", "user": "ana@example.com"}
			]),
			patch("zuno_lms.services.whatsapp.get_active_template", return_value=template),
			patch("zuno_lms.services.whatsapp.get_settings", return_value=settings),
			patch("zuno_lms.services.whatsapp.requests.post") as post,
			patch("zuno_lms.services.whatsapp._", side_effect=lambda message, *args, **kwargs: message),
		):
			result = build_live_class_link_preview(live_class)

		post.assert_not_called()
		self.assertEqual(result["recipient_count"], 1)
		self.assertEqual(result["recipients"], [{"recipient_name": "Ana", "phone": "5511999999999"}])
		self.assertIn("Aula de História", result["message"])
		self.assertIn("historia-enem", result["message"])
		self.assertIn("turma-2026", result["message"])
		self.assertIn("https://meet.jit.si/bruce-token", result["message"])
		self.assertFalse(result["integration_enabled"])
		self.assertIn("desativada", result["integration_warning"])

	def test_validate_evolution_configuration_requires_settings(self):
		with patch("zuno_lms.services.whatsapp._", side_effect=lambda message, *args, **kwargs: message):
			result = validate_evolution_configuration(settings=None)

		self.assertFalse(result["valid"])
		self.assertEqual(result["status"], CONFIG_STATUS_MISSING_SETTINGS)
		self.assertIn("Bruce Evolution Settings", result["message"])

	def test_validate_evolution_configuration_requires_enabled_integration(self):
		settings = self.make_settings(enabled=0)

		with patch("zuno_lms.services.whatsapp._", side_effect=lambda message, *args, **kwargs: message):
			result = validate_evolution_configuration(settings=settings)

		self.assertFalse(result["valid"])
		self.assertEqual(result["status"], CONFIG_STATUS_DISABLED)
		self.assertIn("desativada", result["message"])

	def test_validate_evolution_configuration_requires_api_url(self):
		settings = self.make_settings(api_url="")

		with patch("zuno_lms.services.whatsapp._", side_effect=lambda message, *args, **kwargs: message):
			result = validate_evolution_configuration(settings=settings)

		self.assertFalse(result["valid"])
		self.assertEqual(result["status"], CONFIG_STATUS_MISSING_API_URL)
		self.assertIn("URL da API", result["message"])

	def test_validate_evolution_configuration_requires_instance_name(self):
		settings = self.make_settings(instance_name="")

		with patch("zuno_lms.services.whatsapp._", side_effect=lambda message, *args, **kwargs: message):
			result = validate_evolution_configuration(settings=settings)

		self.assertFalse(result["valid"])
		self.assertEqual(result["status"], CONFIG_STATUS_MISSING_INSTANCE)
		self.assertIn("instância", result["message"])

	def test_validate_evolution_configuration_requires_api_key_without_exposing_value(self):
		settings = self.make_settings()

		with (
			patch("zuno_lms.services.whatsapp.get_evolution_api_key", return_value=""),
			patch("zuno_lms.services.whatsapp.requests.post") as post,
			patch("zuno_lms.services.whatsapp._", side_effect=lambda message, *args, **kwargs: message),
		):
			result = validate_evolution_configuration(settings=settings)

		post.assert_not_called()
		self.assertFalse(result["valid"])
		self.assertEqual(result["status"], CONFIG_STATUS_MISSING_API_KEY)
		self.assertIn("EVOLUTION_API_KEY", result["message"])

	def test_validate_evolution_configuration_returns_valid_without_external_call(self):
		settings = self.make_settings()

		with (
			patch("zuno_lms.services.whatsapp.get_evolution_api_key", return_value="secret-value"),
			patch("zuno_lms.services.whatsapp.requests.post") as post,
			patch("zuno_lms.services.whatsapp._", side_effect=lambda message, *args, **kwargs: message),
		):
			result = validate_evolution_configuration(settings=settings)

		post.assert_not_called()
		self.assertTrue(result["valid"])
		self.assertEqual(result["status"], CONFIG_STATUS_VALID)
		self.assertNotIn("secret-value", result["message"])

	def test_provider_response_redaction_removes_nested_secrets(self):
		response = {
			"ok": True,
			"apikey": "secret-api-key",
			"nested": {
				"Authorization": "Bearer secret-token",
				"items": [
					{"token": "secret-token"},
					{"safe": "value"},
				],
			},
		}

		result = redact_sensitive_values(response)

		self.assertEqual(result["apikey"], "***")
		self.assertEqual(result["nested"]["Authorization"], "***")
		self.assertEqual(result["nested"]["items"][0]["token"], "***")
		self.assertEqual(result["nested"]["items"][1]["safe"], "value")
		self.assertNotIn("secret-api-key", str(result))
		self.assertNotIn("secret-token", str(result))

	def test_disabled_settings_registers_failed_log_without_external_call(self):
		live_class = self.make_live_class()
		settings = Mock(enabled=0, provider_mode="Evolution API")
		logs = []

		def fake_get_doc(values):
			log = FakeLog(values)
			logs.append(log)
			return log

		with (
			patch("zuno_lms.services.whatsapp.get_live_class_recipients", return_value=[
				{"recipient_name": "Ana", "phone": "5511999999999", "user": "ana@example.com"}
			]),
			patch("zuno_lms.services.whatsapp.get_active_template", return_value=None),
			patch("zuno_lms.services.whatsapp.get_settings", return_value=settings),
			patch("zuno_lms.services.whatsapp.frappe.get_doc", side_effect=fake_get_doc),
			patch("zuno_lms.services.whatsapp.frappe.db", Mock()),
			patch("zuno_lms.services.whatsapp.now_datetime", return_value="2026-05-30 12:00:00"),
			patch("zuno_lms.services.whatsapp.requests.post") as post,
			patch("zuno_lms.services.whatsapp._", side_effect=lambda message, *args, **kwargs: message),
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
			patch("zuno_lms.services.whatsapp.get_live_class_recipients", return_value=[
				{"recipient_name": "Ana", "phone": "+55 (11) 99999-9999", "user": "ana@example.com"}
			]),
			patch("zuno_lms.services.whatsapp.get_active_template", return_value=None),
			patch("zuno_lms.services.whatsapp.get_settings", return_value=settings),
			patch("zuno_lms.services.whatsapp.frappe.get_doc", side_effect=fake_get_doc),
			patch("zuno_lms.services.whatsapp.frappe.db", Mock()),
			patch("zuno_lms.services.whatsapp.now_datetime", return_value="2026-05-30 12:00:00"),
			patch("zuno_lms.services.whatsapp.requests.post", return_value=FakeResponse()) as post,
			patch("zuno_lms.services.whatsapp._", side_effect=lambda message, *args, **kwargs: message),
		):
			result = send_live_class_link_for_doc(live_class)

		self.assertEqual(result["status"], "sent")
		self.assertEqual(result["sent_count"], 1)
		self.assertEqual(logs[0].status, LOG_STATUS_SENT)
		post.assert_called_once()
		self.assertEqual(post.call_args.kwargs["json"]["phone"], "5511999999999")
		self.assertNotIn("apikey", post.call_args.kwargs["headers"])

	def test_send_evolution_test_message_sends_single_real_test_and_marks_log_as_sent(self):
		settings = self.make_settings()
		logs = []

		def fake_get_doc(values):
			log = FakeLog(values)
			logs.append(log)
			return log

		with (
			patch("zuno_lms.services.whatsapp.frappe.has_permission", return_value=True),
			patch("zuno_lms.services.whatsapp.get_settings", return_value=settings),
			patch("zuno_lms.services.whatsapp.get_evolution_api_key", return_value="secret-value"),
			patch("zuno_lms.services.whatsapp.frappe.get_doc", side_effect=fake_get_doc),
			patch("zuno_lms.services.whatsapp.now_datetime", return_value="2026-05-30 12:00:00"),
			patch("zuno_lms.services.whatsapp.requests.post", return_value=FakeResponse()) as post,
			patch("zuno_lms.services.whatsapp._", side_effect=lambda message, *args, **kwargs: message),
		):
			result = send_evolution_test_message.__wrapped__("(11) 99999-9999")

		self.assertTrue(result["sent"])
		self.assertEqual(logs[0].status, LOG_STATUS_SENT)
		self.assertEqual(logs[0].phone, "5511999999999")
		self.assertFalse(hasattr(logs[0], "related_live_class"))
		post.assert_called_once()
		self.assertEqual(post.call_args.args[0], "https://evolution.example/message/sendText/bruce")
		self.assertEqual(post.call_args.kwargs["json"]["number"], "5511999999999")
		self.assertIn("Teste de integração", post.call_args.kwargs["json"]["text"])
		self.assertEqual(post.call_args.kwargs["headers"]["apikey"], "secret-value")

	def test_send_evolution_test_message_uses_configuration_validation_before_external_call(self):
		settings = self.make_settings(api_url="")
		logs = []

		def fake_get_doc(values):
			log = FakeLog(values)
			logs.append(log)
			return log

		with (
			patch("zuno_lms.services.whatsapp.frappe.has_permission", return_value=True),
			patch("zuno_lms.services.whatsapp.get_settings", return_value=settings),
			patch("zuno_lms.services.whatsapp.get_evolution_api_key", return_value="secret-value"),
			patch("zuno_lms.services.whatsapp.frappe.get_doc", side_effect=fake_get_doc),
			patch("zuno_lms.services.whatsapp.now_datetime", return_value="2026-05-30 12:00:00"),
			patch("zuno_lms.services.whatsapp.requests.post") as post,
			patch("zuno_lms.services.whatsapp._", side_effect=lambda message, *args, **kwargs: message),
		):
			result = send_evolution_test_message.__wrapped__("(11) 99999-9999")

		post.assert_not_called()
		self.assertFalse(result["sent"])
		self.assertEqual(logs[0].status, LOG_STATUS_FAILED)
		self.assertIn("URL da API", logs[0].error_message)


if __name__ == "__main__":
	unittest.main()
