# Copyright (c) 2026, Estevão Oliveira Portes and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import now_datetime


LIVE_CLASS_FIELDS = [
	"name",
	"title",
	"course",
	"batch",
	"starts_at",
	"status",
	"meeting_url",
]


@frappe.whitelist()
def get_student_dashboard_data():
	"""Return the first live or scheduled class visible to the current student."""
	return {
		"next_live_class": _get_next_visible_live_class(),
		"student_filter_enabled": False,
		"student_filter_note": (
			"Versão inicial: lista a próxima Bruce Live Class ativa ou agendada "
			"visível para o usuário. O filtro por matrícula/turma será refinado depois."
		),
	}


def _get_next_visible_live_class():
	live_class = _get_first_visible_live_class(filters={"status": "Ao vivo"})
	if live_class:
		return live_class

	return _get_first_visible_live_class(
		filters={
			"status": "Agendada",
			"starts_at": [">=", now_datetime()],
		}
	)


def _get_first_visible_live_class(filters):
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


def _with_display_values(live_class):
	live_class["course_title"] = _get_link_title("LMS Course", live_class.get("course"))
	live_class["batch_title"] = _get_link_title("LMS Batch", live_class.get("batch"))
	live_class["class_status_label"] = _get_class_status_label(live_class.get("status"))
	return live_class


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
