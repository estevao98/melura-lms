# Copyright (c) 2026, Estevão Oliveira Portes and contributors
# For license information, please see LICENSE

import frappe
from frappe import _

from melura_lms.services.live_class_automation import validate_google_meet_url
from melura_lms.services.student_access import (
	LIVE_CLASS_VISIBLE_STATUSES,
	assert_current_student_can_access_live_class,
)


LIVE_ROOM_ADMIN_ROLES = {
	"System Manager",
	"Moderator",
	"Administrador LMS",
	"LMS Admin",
	"Admin operacional",
}
LIVE_ROOM_PROFESSOR_ROLES = {
	"Professor",
	"Batch Evaluator",
	"Course Creator",
}


@frappe.whitelist()
def get_live_room_context(live_class):
	"""Return the Google Meet launch context after backend authorization."""
	if not live_class:
		frappe.throw(_("Informe a aula ao vivo."), frappe.ValidationError)

	_assert_logged_user()
	doc = frappe.get_doc("Melura Live Class", live_class)
	_validate_live_class_can_be_opened(doc)
	_assert_can_open_live_room(doc)

	return {
		"name": doc.name,
		"title": doc.title,
		"course": doc.course,
		"course_title": _get_link_title("LMS Course", doc.course),
		"batch": doc.batch,
		"batch_title": _get_link_title("LMS Batch", doc.batch),
		"starts_at": doc.starts_at,
		"status": doc.status,
		"status_label": _get_class_status_label(doc.status),
		"provider_label": "Google Meet",
		"meeting_url": doc.meeting_url,
		"external_url": doc.meeting_url,
	}


def _assert_logged_user():
	if not frappe.session.user or frappe.session.user == "Guest":
		frappe.throw(_("Faça login para acessar a aula ao vivo."), frappe.PermissionError)


def _validate_live_class_can_be_opened(doc):
	if doc.status not in LIVE_CLASS_VISIBLE_STATUSES:
		frappe.throw(_("Esta aula não está disponível para entrada."), frappe.PermissionError)

	if not doc.meeting_url:
		frappe.throw(_("Esta aula ainda não tem link do Google Meet configurado."), frappe.ValidationError)

	validate_google_meet_url(doc.meeting_url)


def _assert_can_open_live_room(doc):
	if _can_open_as_staff(doc):
		return

	assert_current_student_can_access_live_class(doc)


def _can_open_as_staff(doc, user=None):
	user = user or frappe.session.user
	if user == "Administrator":
		return True

	roles = set(frappe.get_roles(user))
	if roles & LIVE_ROOM_ADMIN_ROLES:
		return True

	if doc.instructor == user and roles & LIVE_ROOM_PROFESSOR_ROLES:
		return True

	return False


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
