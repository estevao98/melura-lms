# Copyright (c) 2026, Estevão Oliveira Portes and contributors
# For license information, please see license.txt

import json
import os
import re
from string import Formatter

import frappe
import requests
from frappe import _
from frappe.utils import now_datetime


TEMPLATE_EVENT_TYPE = "Link de aula disponível"
LOG_STATUS_PENDING = "Pendente"
LOG_STATUS_SENT = "Enviado"
LOG_STATUS_FAILED = "Falhou"


class SafeFormatDict(dict):
	def __missing__(self, key):
		return "{" + key + "}"


@frappe.whitelist()
def send_live_class_link(live_class):
	"""Send the Jitsi link for a Bruce Live Class through the configured WhatsApp provider."""
	doc = frappe.get_doc("Bruce Live Class", live_class)
	doc.check_permission("write")
	return send_live_class_link_for_doc(doc)


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

	return summarize_results(results)


def send_logged_message(live_class, recipient, message, log):
	settings = get_settings()
	error_message = validate_send_request(live_class, recipient, settings)

	if error_message:
		return mark_log_failed(log, error_message)

	try:
		provider_response = call_provider(settings, recipient["phone"], message, live_class)
	except Exception:
		frappe.log_error(frappe.get_traceback(), _("Falha ao enviar link de aula por WhatsApp"))
		return mark_log_failed(
			log,
			_("Não foi possível falar com o provedor de WhatsApp. Tente novamente mais tarde."),
		)

	return mark_log_sent(log, provider_response)


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
		return _("A integração de WhatsApp está desativada em Bruce Evolution Settings.")

	if settings.provider_mode == "Evolution API":
		if not settings.api_url or not settings.instance_name:
			return _("Configure URL da API e nome da instância em Bruce Evolution Settings.")

		if not get_evolution_api_key():
			return _("Configure EVOLUTION_API_KEY em variável de ambiente ou site_config.json.")

	if settings.provider_mode == "n8n" and not settings.n8n_webhook_url:
		return _("Configure a URL do webhook n8n em Bruce Evolution Settings.")

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
		return response.json()
	except ValueError:
		return {"status_code": response.status_code, "text": response.text[:500]}


def get_live_class_recipients(live_class):
	members = get_batch_members(live_class.batch)
	if not members:
		members = get_course_members(live_class.course)

	recipients = []
	seen = set()

	for member in members:
		user = member.get("member")
		if not user or user in seen:
			continue

		seen.add(user)
		user_data = get_user_contact(user)
		phone = user_data.get("mobile_no") or user_data.get("phone")

		if not phone:
			continue

		recipients.append(
			{
				"user": user,
				"recipient_name": member.get("member_name") or user_data.get("full_name") or user,
				"phone": phone,
			}
		)

	return recipients


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
	return {
		"nome": recipient.get("recipient_name") or "",
		"aula": live_class.title or "",
		"curso": live_class.course or "",
		"turma": live_class.batch or "",
		"inicio": frappe.format(live_class.starts_at, {"fieldtype": "Datetime"}) if live_class.starts_at else "",
		"link": live_class.meeting_url or "",
		"meeting_url": live_class.meeting_url or "",
	}


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
	log = frappe.get_doc(
		{
			"doctype": "Bruce WhatsApp Notification Log",
			"recipient_name": recipient.get("recipient_name") or _("Destinatário não informado"),
			"phone": recipient.get("phone") or _("Não informado"),
			"message": message,
			"status": LOG_STATUS_PENDING,
			"related_live_class": live_class.name,
		}
	)
	log.insert(ignore_permissions=True)
	return log


def mark_log_sent(log, provider_response):
	log.status = LOG_STATUS_SENT
	log.sent_at = now_datetime()
	log.error_message = ""
	log.provider_response = json.dumps(redact_sensitive_values(provider_response), ensure_ascii=False, default=str)
	log.save(ignore_permissions=True)
	return {"status": "sent", "log": log.name}


def mark_log_failed(log, error_message):
	log.status = LOG_STATUS_FAILED
	log.sent_at = now_datetime()
	log.error_message = error_message
	log.save(ignore_permissions=True)
	return {"status": "failed", "log": log.name, "error_message": error_message}


def update_live_class_whatsapp_status(live_class, results):
	status = "Enviado" if results and all(result["status"] == "sent" for result in results) else "Falhou"
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


def normalize_phone(phone):
	return re.sub(r"\D+", "", phone or "")


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
	return str(key).lower() in {"apikey", "api_key", "authorization", "token", "password", "secret"}
