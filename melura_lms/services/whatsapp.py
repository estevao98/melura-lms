# Copyright (c) 2026, Estevão Oliveira Portes and contributors
# For license information, please see LICENSE

import json
import os
import re
from string import Formatter

import frappe
import requests
from frappe import _
from frappe.utils import get_url, now_datetime

from melura_lms.melura_lms.doctype.bruce_live_class_notice_log.bruce_live_class_notice_log import (
	EVENT_INTEGRATION_DISABLED,
	EVENT_MANUAL_SEND_ATTEMPT,
	EVENT_SEND_FAILED,
	EVENT_WHATSAPP_PREVIEW,
	STATUS_FAILED,
	STATUS_REGISTERED,
	STATUS_SUCCESS,
	STATUS_WARNING,
	create_notice_log,
)


TEMPLATE_EVENT_TYPE = "Link de aula disponível"
TEST_MESSAGE = (
	"Teste de integração do WhatsApp da Melura. "
	"Se você recebeu esta mensagem, a conexão está funcionando."
)
LOG_STATUS_PENDING = "Pendente"
LOG_STATUS_SENT = "Enviado"
LOG_STATUS_FAILED = "Falhou"
LOG_STATUS_RESENT = "Reenviado"
LOG_SUCCESS_STATUSES = {LOG_STATUS_SENT, LOG_STATUS_RESENT}
LOG_RETRYABLE_STATUSES = {LOG_STATUS_PENDING, LOG_STATUS_FAILED}
CONFIG_STATUS_VALID = "valid"
CONFIG_STATUS_MISSING_SETTINGS = "missing_settings"
CONFIG_STATUS_DISABLED = "disabled"
CONFIG_STATUS_MISSING_API_URL = "missing_api_url"
CONFIG_STATUS_MISSING_INSTANCE = "missing_instance"
CONFIG_STATUS_MISSING_API_KEY = "missing_api_key"
USE_STORED_SETTINGS = object()


class SafeFormatDict(dict):
	def __missing__(self, key):
		return "{" + key + "}"


@frappe.whitelist()
def send_live_class_link(live_class):
	"""Send the live-class link through the configured WhatsApp provider."""
	doc = frappe.get_doc("Bruce Live Class", live_class)
	doc.check_permission("write")
	create_notice_log(
		doc,
		EVENT_MANUAL_SEND_ATTEMPT,
		_("Tentativa de envio manual por WhatsApp"),
		_("O usuário solicitou manualmente o envio do link da aula por WhatsApp."),
		STATUS_REGISTERED,
	)
	return send_live_class_link_for_doc(doc)


@frappe.whitelist()
def preview_live_class_link(live_class):
	"""Preview the WhatsApp message for a live class without sending it."""
	doc = frappe.get_doc("Bruce Live Class", live_class)
	doc.check_permission("write")
	result = build_live_class_link_preview(doc)
	create_notice_log(
		doc,
		EVENT_WHATSAPP_PREVIEW,
		_("Pré-visualização de WhatsApp gerada"),
		_("Mensagem e destinatários foram pré-visualizados sem envio real."),
		STATUS_SUCCESS,
	)
	if result.get("integration_warning"):
		create_notice_log(
			doc,
			EVENT_INTEGRATION_DISABLED,
			_("Integração de WhatsApp desativada"),
			result.get("integration_warning"),
			STATUS_WARNING,
		)
	return result


@frappe.whitelist()
def test_evolution_configuration():
	"""Validate the stored Evolution API configuration without sending messages."""
	if not frappe.has_permission("Bruce Evolution Settings", "read"):
		frappe.throw(_("Você não tem permissão para testar a configuração da Evolution API."))

	result = validate_evolution_configuration()
	log_configuration_test_result(result)
	return result


@frappe.whitelist()
def send_evolution_test_message(phone):
	"""Send one controlled test message through Evolution API to a manually provided phone."""
	if not frappe.has_permission("Bruce Evolution Settings", "write"):
		frappe.throw(_("Você não tem permissão para enviar mensagem de teste pela Evolution API."))

	recipient = {
		"user": None,
		"recipient_name": _("Destinatário de teste"),
		"phone": normalize_phone(phone),
	}
	log = create_notification_log(None, recipient, TEST_MESSAGE)

	if not recipient["phone"]:
		return summarize_single_test_result(
			mark_log_failed(log, _("Informe um telefone para enviar a mensagem de teste."))
		)

	settings = get_settings()
	if settings and settings.provider_mode != "Evolution API":
		return summarize_single_test_result(
			mark_log_failed(
				log,
				_("Selecione o modo Evolution API nas configurações de WhatsApp para enviar a mensagem de teste."),
			)
		)

	configuration = validate_evolution_configuration(settings)
	if not configuration["valid"]:
		return summarize_single_test_result(mark_log_failed(log, configuration["message"]))

	try:
		provider_response = call_evolution_api(settings, recipient["phone"], TEST_MESSAGE)
	except Exception as error:
		log_safe_provider_error(error, _("Falha ao enviar mensagem de teste pela Evolution API"))
		return summarize_single_test_result(
			mark_log_failed(
				log,
				_("Não foi possível falar com a Evolution API. Tente novamente mais tarde."),
			)
		)

	return summarize_single_test_result(mark_log_sent(log, provider_response))


@frappe.whitelist()
def retry_live_class_notification(log_name):
	"""Retry a failed or pending live-class WhatsApp notification log."""
	log = frappe.get_doc("Bruce WhatsApp Notification Log", log_name)
	live_class = get_retry_live_class(log)
	check_retry_permission(log, live_class)

	if not is_retryable_notification_log(log):
		return {
			"status": "not_retryable",
			"sent": False,
			"log": log.name,
			"message": _("Esta notificação não pode ser reenviada pelo estado atual."),
		}

	recipient = {
		"user": None,
		"recipient_name": log.recipient_name,
		"phone": normalize_phone(log.phone),
	}
	result = send_logged_message(live_class, recipient, log.message, log, retry=True)
	update_live_class_whatsapp_status(live_class, [result], retry=True)

	if result["status"] == "sent":
		return {
			"status": "sent",
			"sent": True,
			"log": log.name,
			"message": _("Mensagem reenviada por WhatsApp."),
		}

	return {
		"status": "failed",
		"sent": False,
		"log": log.name,
		"message": result.get("error_message") or _("Não foi possível reenviar a mensagem pelo WhatsApp."),
	}


def retry_failed_live_class_link(log_name):
	return retry_live_class_notification(log_name)


def get_retry_live_class(log):
	if not getattr(log, "related_live_class", None):
		frappe.throw(_("Somente notificações vinculadas a uma aula ao vivo podem ser reenviadas."))

	return frappe.get_doc("Bruce Live Class", log.related_live_class)


def check_retry_permission(log, live_class):
	if frappe.has_permission("Bruce WhatsApp Notification Log", "write", doc=log):
		return

	if live_class and frappe.has_permission("Bruce Live Class", "write", doc=live_class):
		return

	frappe.throw(_("Você não tem permissão para reenviar esta notificação de WhatsApp."))


def is_retryable_notification_log(log_doc):
	if getattr(log_doc, "status", None) in LOG_SUCCESS_STATUSES:
		return False

	if getattr(log_doc, "status", None) not in LOG_RETRYABLE_STATUSES:
		return False

	return bool(getattr(log_doc, "related_live_class", None) and normalize_phone(getattr(log_doc, "phone", "")))


def validate_evolution_configuration(settings=USE_STORED_SETTINGS):
	settings = get_settings() if settings is USE_STORED_SETTINGS else settings

	if not settings:
		return configuration_result(
			CONFIG_STATUS_MISSING_SETTINGS,
			_("As configurações de WhatsApp não foram encontradas. Revise a instalação da app."),
		)

	if not settings.enabled:
		return configuration_result(
			CONFIG_STATUS_DISABLED,
			_("A integração de WhatsApp está desativada nas configurações de WhatsApp."),
		)

	if not settings.api_url:
		return configuration_result(
			CONFIG_STATUS_MISSING_API_URL,
			_("Informe a URL da API nas configurações de WhatsApp."),
		)

	if not settings.instance_name:
		return configuration_result(
			CONFIG_STATUS_MISSING_INSTANCE,
			_("Informe o nome da instância nas configurações de WhatsApp."),
		)

	if not get_evolution_api_key():
		return configuration_result(
			CONFIG_STATUS_MISSING_API_KEY,
			_("Configure EVOLUTION_API_KEY em variável de ambiente ou site_config.json."),
		)

	return configuration_result(
		CONFIG_STATUS_VALID,
		_("Configuração da Evolution API válida. A integração está ativa e a API key foi encontrada."),
	)


def configuration_result(status, message):
	return {
		"status": status,
		"valid": status == CONFIG_STATUS_VALID,
		"message": message,
	}


def log_configuration_test_result(result):
	frappe.logger("melura_lms.whatsapp").info(
		"Teste de configuração da Evolution API: %(status)s", {"status": result.get("status")}
	)


def send_live_class_link_for_doc(live_class):
	recipients = get_live_class_recipients(live_class)
	if not recipients:
		recipients = [
			{
				"recipient_name": _("Turma sem destinatários"),
				"phone": _("Não informado"),
				"user": None,
			}
		]

	results = []
	for recipient in recipients:
		message = build_live_class_message(live_class, recipient)
		log = create_notification_log(live_class, recipient, message)
		result = send_logged_message(live_class, recipient, message, log)
		results.append(result)

	update_live_class_whatsapp_status(live_class, results)
	create_send_result_notice_logs(live_class, results)

	return summarize_results(results)


def create_send_result_notice_logs(live_class, results):
	failed_results = [result for result in results if result["status"] == "failed"]
	if not failed_results:
		return

	first_error = failed_results[0].get("error_message") or _("Não foi possível enviar o link pelo WhatsApp.")
	if "desativada" in first_error.lower():
		create_notice_log(
			live_class,
			EVENT_INTEGRATION_DISABLED,
			_("Integração de WhatsApp desativada"),
			first_error,
			STATUS_WARNING,
		)

	create_notice_log(
		live_class,
		EVENT_SEND_FAILED,
		_("Falha no envio por WhatsApp"),
		first_error,
		STATUS_FAILED,
	)


def build_live_class_link_preview(live_class):
	recipients = get_live_class_recipients(live_class)
	recipient_messages = [
		{
			"recipient_name": recipient.get("recipient_name") or _("Destinatário não informado"),
			"phone": recipient.get("phone") or _("Não informado"),
			"message": build_live_class_message(live_class, recipient),
		}
		for recipient in recipients
	]
	settings = get_settings()
	integration_enabled = bool(settings and settings.enabled)

	return {
		"status": "preview",
		"recipient_count": len(recipients),
		"recipients": [
			{
				"recipient_name": item["recipient_name"],
				"phone": item["phone"],
			}
			for item in recipient_messages
		],
		"message": recipient_messages[0]["message"] if recipient_messages else build_live_class_message(live_class, {}),
		"recipient_messages": recipient_messages,
		"integration_enabled": integration_enabled,
		"integration_warning": ""
		if integration_enabled
		else _("A integração de WhatsApp está desativada nas configurações de WhatsApp."),
	}


def send_logged_message(live_class, recipient, message, log, retry=False):
	settings = get_settings()
	error_message = validate_send_request(live_class, recipient, settings)

	if error_message:
		return mark_log_failed(log, error_message)

	try:
		provider_response = call_provider(settings, recipient["phone"], message, live_class)
	except Exception as error:
		log_safe_provider_error(error, _("Falha ao enviar link de aula por WhatsApp"))
		return mark_log_failed(
			log,
			_("Não foi possível falar com o provedor de WhatsApp. Tente novamente mais tarde."),
		)

	return mark_log_sent(log, provider_response, retry=retry)


def get_settings():
	try:
		return frappe.get_single("Bruce Evolution Settings")
	except frappe.DoesNotExistError:
		return None


def validate_send_request(live_class, recipient, settings):
	if not live_class.meeting_url:
		return _("Esta aula ainda não tem link. Salve a aula novamente antes de enviar pelo WhatsApp.")

	if not recipient.get("phone") or recipient.get("phone") == _("Não informado"):
		return _("Nenhum telefone de WhatsApp foi encontrado para esta aula.")

	if not settings or not settings.enabled:
		return _("A integração de WhatsApp está desativada nas configurações de WhatsApp.")

	if settings.provider_mode == "Evolution API":
		if not settings.api_url or not settings.instance_name:
			return _("Configure URL da API e nome da instância nas configurações de WhatsApp.")

		if not get_evolution_api_key():
			return _("Configure EVOLUTION_API_KEY em variável de ambiente ou site_config.json.")

	if settings.provider_mode == "n8n" and not settings.n8n_webhook_url:
		return _("Configure a URL do webhook n8n nas configurações de WhatsApp.")

	if settings.provider_mode not in ("Evolution API", "n8n"):
		return _("Modo de provedor de WhatsApp inválido.")

	return None


def get_evolution_api_key():
	return (
		frappe.conf.get("evolution_api_key")
		or frappe.conf.get("EVOLUTION_API_KEY")
		or os.environ.get("EVOLUTION_API_KEY")
	)


def call_provider(settings, phone, message, live_class):
	if settings.provider_mode == "Evolution API":
		return call_evolution_api(settings, phone, message)

	return call_n8n(settings, phone, message, live_class)


def call_evolution_api(settings, phone, message):
	url = f"{settings.api_url.rstrip('/')}/message/sendText/{settings.instance_name}"
	response = requests.post(
		url,
		headers={
			"Content-Type": "application/json",
			"apikey": get_evolution_api_key(),
		},
		json={
			"number": normalize_phone(phone),
			"text": message,
		},
		timeout=20,
	)
	response.raise_for_status()
	return safe_response_json(response)


def call_n8n(settings, phone, message, live_class):
	response = requests.post(
		settings.n8n_webhook_url,
		headers={"Content-Type": "application/json"},
		json={
			"event": "live_class_link_manual",
			"live_class": live_class.name,
			"title": live_class.title,
			"meeting_url": live_class.meeting_url,
			"phone": normalize_phone(phone),
			"message": message,
		},
		timeout=20,
	)
	response.raise_for_status()
	return safe_response_json(response)


def safe_response_json(response):
	try:
		payload = response.json()
	except ValueError:
		payload = {"status_code": response.status_code, "text": response.text[:500]}

	return normalize_provider_response(payload)


def get_live_class_recipients(live_class):
	manual_recipient = get_manual_recipient(live_class)
	if manual_recipient:
		return [manual_recipient]

	return get_live_class_batch_recipient_candidates(live_class)


def get_live_class_batch_recipient_candidates(live_class):
	recipients = []
	seen_phones = set()

	for member in get_batch_members(getattr(live_class, "batch", "")):
		user = get_member_value(member, "member")
		if not user:
			continue

		contact = get_user_contact(user)
		phone = normalize_phone(contact.get("mobile_no") or contact.get("phone"))

		if not phone or phone in seen_phones:
			continue

		seen_phones.add(phone)
		recipients.append(
			{
				"user": user,
				"recipient_name": get_member_value(member, "member_name") or contact.get("full_name") or user,
				"phone": phone,
			}
		)

	return recipients


def get_member_value(member, fieldname):
	if isinstance(member, dict):
		return member.get(fieldname)

	return getattr(member, fieldname, None)


def get_manual_recipient(live_class):
	phone = normalize_phone(getattr(live_class, "whatsapp_phone", ""))
	if not phone:
		return None

	return {
		"user": None,
		"recipient_name": getattr(live_class, "whatsapp_recipient_name", "") or _("Destinatário de teste"),
		"phone": phone,
	}


def get_batch_members(batch):
	if not batch:
		return []

	return frappe.get_all(
		"LMS Batch Enrollment",
		filters={"batch": batch},
		fields=["member", "member_name"],
	)


def get_course_members(course):
	if not course:
		return []

	return frappe.get_all(
		"LMS Enrollment",
		filters={"course": course, "member_type": "Student"},
		fields=["member", "member_name"],
	)


def get_user_contact(user):
	return frappe.db.get_value("User", user, ["full_name", "mobile_no", "phone"], as_dict=True) or {}


def build_live_class_message(live_class, recipient):
	template = get_active_template()
	context = get_template_context(live_class, recipient)

	if template:
		body = strip_html(template.message_body or "")
		return format_template(body, context).strip()

	return _(
		"Olá {nome}, o link da aula {aula} já está disponível: {link}"
	).format_map(SafeFormatDict(context))


def get_active_template():
	templates = frappe.get_all(
		"Bruce WhatsApp Message Template",
		filters={"enabled": 1, "event_type": TEMPLATE_EVENT_TYPE},
		fields=["name", "message_body"],
		order_by="modified desc",
		limit_page_length=1,
	)

	if not templates:
		return None

	return frappe._dict(templates[0])


def get_template_context(live_class, recipient):
	link = get_live_class_public_link(live_class)
	return {
		"nome": recipient.get("recipient_name") or "",
		"aula": live_class.title or "",
		"curso": live_class.course or "",
		"turma": live_class.batch or "",
		"inicio": frappe.format(live_class.starts_at, {"fieldtype": "Datetime"}) if live_class.starts_at else "",
		"link": link,
		"meeting_url": live_class.meeting_url or "",
	}


def get_live_class_public_link(live_class):
	try:
		base_url = get_url()
	except Exception:
		base_url = ""

	if base_url and getattr(live_class, "name", None):
		return f"{base_url.rstrip('/')}/app/bruce-live-room/{live_class.name}"

	return live_class.meeting_url or ""


def format_template(template, context):
	field_names = [field_name for _, field_name, _, _ in Formatter().parse(template) if field_name]
	values = SafeFormatDict({field_name: context.get(field_name, "") for field_name in field_names})
	values.update(context)
	return template.format_map(values)


def strip_html(value):
	text = re.sub(r"<br\s*/?>", "\n", value, flags=re.IGNORECASE)
	text = re.sub(r"</p\s*>", "\n", text, flags=re.IGNORECASE)
	text = re.sub(r"<[^>]+>", "", text)
	return frappe.utils.strip_html(text) if hasattr(frappe.utils, "strip_html") else text


def create_notification_log(live_class, recipient, message):
	values = {
		"doctype": "Bruce WhatsApp Notification Log",
		"recipient_name": recipient.get("recipient_name") or _("Destinatário não informado"),
		"phone": recipient.get("phone") or _("Não informado"),
		"message": message,
		"status": LOG_STATUS_PENDING,
	}

	if live_class:
		values["related_live_class"] = live_class.name

	log = frappe.get_doc(values)
	log.insert(ignore_permissions=True)
	return log


def mark_log_sent(log, provider_response, retry=False):
	log.status = LOG_STATUS_RESENT if retry else LOG_STATUS_SENT
	log.sent_at = now_datetime()
	log.error_message = ""
	log.provider_response = json.dumps(normalize_provider_response(provider_response), ensure_ascii=False, default=str)
	log.save(ignore_permissions=True)
	return {"status": "sent", "log": log.name}


def mark_log_failed(log, error_message):
	log.status = LOG_STATUS_FAILED
	log.sent_at = now_datetime()
	log.error_message = get_safe_provider_error(error_message)
	log.provider_response = json.dumps(
		normalize_provider_response({"error": log.error_message}), ensure_ascii=False, default=str
	)
	log.save(ignore_permissions=True)
	return {"status": "failed", "log": log.name, "error_message": log.error_message}


def update_live_class_whatsapp_status(live_class, results, retry=False):
	status = LOG_STATUS_RESENT if retry and results and all(result["status"] == "sent" for result in results) else "Enviado"
	if not (results and all(result["status"] == "sent" for result in results)):
		status = "Falhou"
	frappe.db.set_value("Bruce Live Class", live_class.name, "whatsapp_status", status, update_modified=True)


def summarize_results(results):
	sent_count = len([result for result in results if result["status"] == "sent"])
	failed_count = len([result for result in results if result["status"] == "failed"])
	status = "sent" if sent_count and not failed_count else "failed"

	if sent_count and failed_count:
		message = _("Alguns links foram enviados. Verifique os logs de WhatsApp para os envios com falha.")
	elif sent_count:
		message = _("Link da aula enviado por WhatsApp.")
	else:
		message = results[0].get("error_message") if results else _("Não foi possível enviar o link pelo WhatsApp.")

	return {
		"status": status,
		"sent_count": sent_count,
		"failed_count": failed_count,
		"logs": [result["log"] for result in results],
		"message": message,
	}


def summarize_single_test_result(result):
	if result["status"] == "sent":
		message = _("Mensagem de teste enviada pela Evolution API.")
	else:
		message = result.get("error_message") or _("Não foi possível enviar a mensagem de teste.")

	return {
		"status": result["status"],
		"sent": result["status"] == "sent",
		"log": result["log"],
		"message": message,
	}


def normalize_phone(phone):
	phone = re.sub(r"\D+", "", phone or "")

	if len(phone) in (10, 11) and not phone.startswith("55"):
		return f"55{phone}"

	return phone


def redact_provider_payload(payload):
	return redact_sensitive_values(payload)


def normalize_provider_response(response):
	return redact_provider_payload(response)


def get_safe_provider_error(error):
	if isinstance(error, str):
		message = error
	else:
		message = error.__class__.__name__

	return strip_sensitive_text(message)[:500]


def log_safe_provider_error(error, title):
	frappe.log_error(get_safe_provider_error(error), title)


def strip_sensitive_text(message):
	message = str(message or "")
	message = re.sub(r"(?i)(authorization\s*[=:]\s*)(bearer\s+)?\S+", r"\1***", message)
	message = re.sub(r"(?i)(apikey|api_key|token|password|secret)(\s*[=:]\s*)\S+", r"\1\2***", message)
	message = re.sub(r"(?i)bearer\s+\S+", "Bearer ***", message)
	return message


def redact_sensitive_values(value):
	if isinstance(value, dict):
		return {
			key: "***" if is_sensitive_key(key) else redact_sensitive_values(item)
			for key, item in value.items()
		}

	if isinstance(value, list):
		return [redact_sensitive_values(item) for item in value]

	return value


def is_sensitive_key(key):
	key = str(key).lower()
	return any(part in key for part in ("apikey", "api_key", "authorization", "token", "password", "secret"))
