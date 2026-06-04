# Copyright (c) 2026, Estevão Oliveira Portes and contributors
# For license information, please see LICENSE

from urllib.parse import urlparse

import frappe
from frappe import _

from melura_lms.melura_lms.doctype.bruce_live_class.bruce_live_class import BruceLiveClass
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
	"""Return the Jitsi iframe context after backend authorization."""
	if not live_class:
		frappe.throw(_("Informe a aula ao vivo."), frappe.ValidationError)

	_assert_logged_user()
	doc = frappe.get_doc("Bruce Live Class", live_class)
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
		"domain": _get_jitsi_domain(),
		"room_name": doc.room_name,
		"external_url": doc.meeting_url,
	}


def _assert_logged_user():
	if not frappe.session.user or frappe.session.user == "Guest":
		frappe.throw(_("Faça login para acessar a aula ao vivo."), frappe.PermissionError)


def _validate_live_class_can_be_opened(doc):
	if doc.status not in LIVE_CLASS_VISIBLE_STATUSES:
		frappe.throw(_("Esta aula não está disponível para entrada."), frappe.PermissionError)

	if not doc.room_name or not doc.meeting_url:
		frappe.throw(_("Esta aula ainda não tem sala Jitsi configurada."), frappe.ValidationError)

	_validate_external_url(doc.meeting_url)


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


def _get_jitsi_domain():
	settings = BruceLiveClass.get_jitsi_settings()
	return _normalize_jitsi_domain(getattr(settings, "domain", None))


def _normalize_jitsi_domain(domain):
	value = (domain or "meet.jit.si").strip().rstrip("/")
	parsed = urlparse(value if "://" in value else f"https://{value}")

	if not parsed.netloc:
		frappe.throw(_("Informe um domínio Jitsi válido."), frappe.ValidationError)

	return parsed.netloc.rstrip("/")


def _validate_external_url(url):
	parsed = urlparse((url or "").strip())
	if parsed.scheme not in {"http", "https"} or not parsed.netloc:
		frappe.throw(_("O link externo da aula está inválido."), frappe.ValidationError)


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
