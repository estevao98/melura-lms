# Copyright (c) 2026, Estevão Oliveira Portes and contributors
# For license information, please see LICENSE

from datetime import datetime

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint, now_datetime


EVENT_LINK_COPIED = "Link copiado"
EVENT_WHATSAPP_PREVIEW = "Pré-visualização de WhatsApp gerada"
EVENT_MANUAL_SEND_ATTEMPT = "Tentativa de envio manual"
EVENT_SEND_FAILED = "Falha de envio"
EVENT_INTEGRATION_DISABLED = "Integração desativada"
EVENT_CLASS_OPENED = "Aula aberta"
EVENT_CLASS_STARTED = "Aula iniciada"

STATUS_REGISTERED = "Registrado"
STATUS_SUCCESS = "Sucesso"
STATUS_FAILED = "Falhou"
STATUS_WARNING = "Aviso"

ALLOWED_EVENT_TYPES = {
	EVENT_LINK_COPIED,
	EVENT_WHATSAPP_PREVIEW,
	EVENT_MANUAL_SEND_ATTEMPT,
	EVENT_SEND_FAILED,
	EVENT_INTEGRATION_DISABLED,
	EVENT_CLASS_OPENED,
	EVENT_CLASS_STARTED,
}

ALLOWED_STATUSES = {
	STATUS_REGISTERED,
	STATUS_SUCCESS,
	STATUS_FAILED,
	STATUS_WARNING,
}


class BruceLiveClassNoticeLog(Document):
	def validate(self):
		if self.event_type not in ALLOWED_EVENT_TYPES:
			frappe.throw(_("Tipo de evento inválido para o histórico da aula ao vivo."))

		if self.status not in ALLOWED_STATUSES:
			frappe.throw(_("Status inválido para o histórico da aula ao vivo."))

		if not self.created_by:
			self.created_by = get_current_user()

		if not self.created_at:
			self.created_at = get_current_datetime()


def create_notice_log(live_class, event_type, title, message="", status=STATUS_REGISTERED):
	"""Create an operational audit entry for a Bruce Live Class."""
	if not live_class:
		return None

	live_class_name = live_class if isinstance(live_class, str) else getattr(live_class, "name", None)

	log = frappe.get_doc(
		{
			"doctype": "Bruce Live Class Notice Log",
			"related_live_class": live_class_name,
			"event_type": event_type,
			"title": title,
			"message": message or "",
			"status": status,
			"created_by": get_current_user(),
			"created_at": get_current_datetime(),
		}
	)
	log.insert(ignore_permissions=True)
	return log


def get_current_user():
	try:
		return getattr(frappe.session, "user", None) or "Administrator"
	except RuntimeError:
		return "Administrator"


def get_current_datetime():
	try:
		return now_datetime()
	except Exception:
		return datetime.now()

@frappe.whitelist()
def record_live_class_notice_event(live_class, event_type, title=None, message=None, status=STATUS_REGISTERED):
	doc = frappe.get_doc("Bruce Live Class", live_class)
	doc.check_permission("read")

	title = title or event_type
	log = create_notice_log(doc, event_type, title, message or "", status)

	return {"name": log.name if log else None}


@frappe.whitelist()
def get_live_class_notice_logs(live_class, limit=6):
	doc = frappe.get_doc("Bruce Live Class", live_class)
	doc.check_permission("read")

	limit = max(1, min(cint(limit) or 6, 20))
	return frappe.get_all(
		"Bruce Live Class Notice Log",
		filters={"related_live_class": live_class},
		fields=["name", "event_type", "title", "message", "status", "created_by", "created_at"],
		order_by="created_at desc, creation desc",
		limit_page_length=limit,
	)
