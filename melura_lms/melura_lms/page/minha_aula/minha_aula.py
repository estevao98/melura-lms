# Copyright (c) 2026, Estevão Oliveira Portes and contributors
# For license information, please see LICENSE

import frappe
from frappe.utils import now_datetime

from melura_lms.services.routes import get_live_room_route
from melura_lms.services.student_access import (
	ACCESS_ACTIVE,
	LIVE_CLASS_VISIBLE_STATUSES,
	get_current_student_access_status,
	get_permitted_educational_materials_for_current_student,
	get_permitted_exercise_lists_for_current_student,
	get_permitted_live_classes_for_current_student,
	get_progress_for_current_student,
	is_current_student_active,
)


@frappe.whitelist()
def get_student_dashboard_data():
	"""Return the first live or scheduled class allowed for the current student."""
	access_status = get_current_student_access_status()
	student_is_active = is_current_student_active()

	return {
		"access_status": access_status,
		"student_is_active": student_is_active,
		"next_live_class": _get_next_visible_live_class() if student_is_active else None,
		"recent_materials": _get_recent_materials() if student_is_active else [],
		"exercise_lists": _get_exercise_lists() if student_is_active else [],
		"student_progress": get_progress_for_current_student(),
		"student_filter_enabled": True,
		"student_filter_note": _get_student_filter_note(access_status),
	}


@frappe.whitelist()
def get_student_materials():
	"""Return recent materials allowed for the current logged student."""
	if not is_current_student_active():
		return []

	return _get_recent_materials()


@frappe.whitelist()
def get_student_exercise_lists():
	"""Return exercise lists allowed for the current logged student."""
	if not is_current_student_active():
		return []

	return _get_exercise_lists()


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
	status = filters.get("status")
	starts_from = filters.get("starts_at", [None, None])[1] if isinstance(filters.get("starts_at"), list) else None
	classes = get_permitted_live_classes_for_current_student(
		statuses=(status,) if status else LIVE_CLASS_VISIBLE_STATUSES,
		starts_from=starts_from,
		limit=1,
	)

	if not classes:
		return None

	return _with_display_values(dict(classes[0]))


def _with_display_values(live_class):
	live_class["course_title"] = _get_link_title("LMS Course", live_class.get("course"))
	live_class["batch_title"] = _get_link_title("LMS Batch", live_class.get("batch"))
	live_class["class_status_label"] = _get_class_status_label(live_class.get("status"))
	live_class["live_room_route"] = get_live_room_route(live_class.get("name"))
	return live_class


def _get_recent_materials(limit=6):
	return [_with_material_display_values(dict(material)) for material in get_permitted_educational_materials_for_current_student(limit=limit)]


def _get_exercise_lists(limit=6):
	return [_with_exercise_list_display_values(dict(exercise_list)) for exercise_list in get_permitted_exercise_lists_for_current_student(limit=limit)]


def _with_material_display_values(material):
	material["course_title"] = _get_link_title("LMS Course", material.get("course"))
	material["batch_title"] = _get_link_title("LMS Batch", material.get("batch"))
	material["related_live_class_title"] = _get_link_title("Bruce Live Class", material.get("related_live_class"))
	return material


def _with_exercise_list_display_values(exercise_list):
	exercise_list["course_title"] = _get_link_title("LMS Course", exercise_list.get("course"))
	exercise_list["batch_title"] = _get_link_title("LMS Batch", exercise_list.get("batch"))
	exercise_list["related_live_class_title"] = _get_link_title("Bruce Live Class", exercise_list.get("related_live_class"))
	return exercise_list


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


def _get_student_filter_note(access_status):
	if access_status == ACCESS_ACTIVE:
		return "Seu acesso está ativo. Mostramos apenas aulas vinculadas ao seu curso ou turma."

	if access_status == "Bloqueado":
		return "Seu acesso está bloqueado. Entre em contato com o suporte."

	if access_status == "Expirado":
		return "Seu acesso expirou. Entre em contato com o suporte."

	return "Seu acesso ainda está pendente. As aulas serão liberadas quando seu cadastro estiver ativo."
