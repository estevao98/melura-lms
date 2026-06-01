# Copyright (c) 2026, Estevão Oliveira Portes and contributors
# For license information, please see license.txt

import frappe
from frappe import _

from bruce_lms_custom.bruce_lms_custom.page.bruce_operational_dashboard.bruce_operational_dashboard import (
	_can_access_operational_dashboard,
)
from bruce_lms_custom.bruce_lms_custom.page.minha_aula.minha_aula import get_student_dashboard_data


no_cache = 1
PROFESSOR_PORTAL_ROLES = {
	"System Manager",
	"Moderator",
	"Batch Evaluator",
	"Course Creator",
	"Professor",
	"Administrador LMS",
	"LMS Admin",
}


def get_context(context):
	"""Render the mobile-first student portal outside Desk."""
	_require_logged_user(redirect=True)

	context.no_cache = 1
	context.body_class = "bruce-student-portal-page"
	context.title = _("Portal do aluno")
	context.portal_data = get_student_portal_data()


@frappe.whitelist()
def get_student_portal_data():
	"""Return the current student's portal data without trusting frontend scope."""
	_require_logged_user()

	portal_data = get_student_dashboard_data()
	portal_data.update(_get_student_portal_menu_context())
	return portal_data


def _get_student_portal_menu_context(user=None):
	user = user or frappe.session.user
	return {
		"support_url": _get_support_url(),
		"can_access_professor_dashboard": _can_access_professor_dashboard(user),
		"can_access_operational_dashboard": _can_access_operational_dashboard(user),
		"can_access_desk": _can_access_desk(user),
	}


def _can_access_professor_dashboard(user=None):
	user = user or frappe.session.user
	if user == "Administrator":
		return True

	if not user or user == "Guest":
		return False

	return bool(set(frappe.get_roles(user)) & PROFESSOR_PORTAL_ROLES)


def _can_access_desk(user=None):
	user = user or frappe.session.user
	if user == "Administrator":
		return True

	if not user or user == "Guest":
		return False

	return bool(set(frappe.get_roles(user)) & PROFESSOR_PORTAL_ROLES)


def _get_support_url():
	support_url = ((getattr(frappe, "conf", {}) or {}).get("bruce_student_support_url") or "").strip()
	if not support_url:
		return None

	if support_url.startswith(("/", "https://", "http://", "mailto:", "tel:")):
		return support_url

	return None


def _require_logged_user(redirect=False):
	if frappe.session.user != "Guest":
		return

	if redirect:
		frappe.local.flags.redirect_location = "/login?redirect-to=/aluno"
		raise frappe.Redirect

	frappe.throw(_("Faça login para acessar o portal do aluno."), frappe.PermissionError)
