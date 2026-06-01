# Copyright (c) 2026, Estevão Oliveira Portes and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import add_to_date, now_datetime

from bruce_lms_custom.services.student_access import get_progress_summary_for_scope


WHATSAPP_INTEGRATION_DISABLED_LABEL = "Integração desativada"
WHATSAPP_STATUS_LABELS = {
	"Não enviado": "WhatsApp pendente",
	"Pendente": "WhatsApp pendente",
	"Enviado": "WhatsApp enviado",
	"Falhou": "WhatsApp falhou",
	"Reenviado": "WhatsApp enviado",
}

LIVE_CLASS_FIELDS = [
	"name",
	"title",
	"course",
	"batch",
	"starts_at",
	"status",
	"whatsapp_status",
	"meeting_url",
]


@frappe.whitelist()
def get_next_live_class():
	"""Return the current live class, or the next scheduled class visible to the user."""
	return _get_next_live_class()


@frappe.whitelist()
def get_dashboard_data():
	"""Return the data shown in the professor dashboard."""
	next_live_class = _get_next_live_class()
	return {
		"next_live_class": next_live_class,
		"week_classes": _get_week_live_classes(),
		"class_progress": _get_class_progress_summary(next_live_class),
	}


def _get_next_live_class():
	live_class = _get_first_live_class(filters={"status": "Ao vivo"})
	if live_class:
		return live_class

	return _get_first_live_class(
		filters={
			"status": "Agendada",
			"starts_at": [">=", now_datetime()],
		}
	)


def _get_week_live_classes():
	start = now_datetime()
	end = add_to_date(start, days=7)
	classes = frappe.get_list(
		"Bruce Live Class",
		filters={
			"status": ["in", ["Agendada", "Ao vivo"]],
			"starts_at": ["between", [start, end]],
		},
		fields=LIVE_CLASS_FIELDS,
		order_by="starts_at asc",
		limit_page_length=20,
	)

	return [_with_display_values(dict(live_class), include_notice_logs=False) for live_class in classes]


def _get_class_progress_summary(live_class):
	if not live_class:
		return {
			"batch": None,
			"course": None,
			"total_students": 0,
			"students": [],
		}

	return get_progress_summary_for_scope(
		batch=live_class.get("batch"),
		course=live_class.get("course"),
		limit=20,
	)


def _get_first_live_class(filters):
	classes = frappe.get_list(
		"Bruce Live Class",
		filters=filters,
		fields=LIVE_CLASS_FIELDS,
		order_by="starts_at asc",
		limit_page_length=1,
	)

	if not classes:
		return None

	return _with_display_values(dict(classes[0]))


def _with_display_values(live_class, include_notice_logs=True):
	live_class["course_title"] = _get_link_title("LMS Course", live_class.get("course"))
	live_class["batch_title"] = _get_link_title("LMS Batch", live_class.get("batch"))
	live_class["class_status_label"] = _get_class_status_label(live_class.get("status"))
	live_class["whatsapp_status_label"] = _get_whatsapp_status_label(live_class.get("whatsapp_status"))
	live_class["notice_logs"] = _get_notice_logs(live_class.get("name")) if include_notice_logs else []
	return live_class


def _get_notice_logs(live_class):
	if not live_class:
		return []

	return frappe.get_all(
		"Bruce Live Class Notice Log",
		filters={"related_live_class": live_class},
		fields=["event_type", "title", "message", "status", "created_by", "created_at"],
		order_by="created_at desc, creation desc",
		limit_page_length=4,
	)


def _get_link_title(doctype, name):
	if not name:
		return None

	try:
		return frappe.db.get_value(doctype, name, "title") or name
	except Exception:
		return name


def _get_class_status_label(status):
	if status == "Ao vivo":
		return "Aula ao vivo"

	if status == "Agendada":
		return "Aula agendada"

	return status or "Sem status"


def _get_whatsapp_status_label(status):
	if not _is_whatsapp_integration_enabled():
		return WHATSAPP_INTEGRATION_DISABLED_LABEL

	return WHATSAPP_STATUS_LABELS.get(status or "Não enviado", status or "WhatsApp pendente")


def _is_whatsapp_integration_enabled():
	try:
		return bool(frappe.db.get_single_value("Bruce Evolution Settings", "enabled"))
	except Exception:
		return False
