# Copyright (c) 2026, Estevão Oliveira Portes and contributors
# For license information, please see license.txt

import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import frappe

from bruce_lms_custom.www.aluno import (
	_can_access_desk,
	_can_access_professor_dashboard,
	_get_support_url,
	get_context,
	get_student_portal_data,
)


class TestAlunoPortal(unittest.TestCase):
	def setUp(self):
		frappe.local.flags = frappe._dict(in_test=True)
		self.get_roles = patch("bruce_lms_custom.www.aluno.frappe.get_roles", return_value=["LMS Student"])
		self.get_roles.start()
		self.addCleanup(self.get_roles.stop)

	def test_active_student_accesses_portal_content(self):
		dashboard = {
			"access_status": "Ativo",
			"student_is_active": True,
			"next_live_class": {"name": "BLC-2026-00001", "meeting_url": "https://meet.example/aula"},
			"recent_materials": [{"name": "BEM-2026-00001"}],
			"exercise_lists": [{"name": "BEL-2026-00001"}],
			"student_progress": {"total_answered_questions": 3},
		}

		with (
			patch("bruce_lms_custom.www.aluno.frappe.session", Mock(user="aluno@example.com")),
			patch("bruce_lms_custom.www.aluno.get_student_dashboard_data", return_value=dashboard),
		):
			result = get_student_portal_data()

		self.assertEqual(result["access_status"], "Ativo")
		self.assertTrue(result["student_is_active"])
		self.assertEqual(result["next_live_class"]["name"], "BLC-2026-00001")
		self.assertEqual(result["recent_materials"], [{"name": "BEM-2026-00001"}])
		self.assertEqual(result["exercise_lists"], [{"name": "BEL-2026-00001"}])
		self.assertFalse(result["can_access_professor_dashboard"])
		self.assertFalse(result["can_access_operational_dashboard"])
		self.assertFalse(result["can_access_desk"])

	def test_blocked_student_does_not_receive_pedagogical_content(self):
		with (
			patch("bruce_lms_custom.www.aluno.frappe.session", Mock(user="aluno@example.com")),
			patch(
				"bruce_lms_custom.www.aluno.get_student_dashboard_data",
				return_value=_inactive_dashboard("Bloqueado"),
			),
		):
			result = get_student_portal_data()

		self.assertEqual(result["access_status"], "Bloqueado")
		self.assertFalse(result["student_is_active"])
		self.assertIsNone(result["next_live_class"])
		self.assertEqual(result["recent_materials"], [])
		self.assertEqual(result["exercise_lists"], [])
		self.assertTrue(result["student_progress"]["locked"])

	def test_pending_student_does_not_receive_pedagogical_content(self):
		with (
			patch("bruce_lms_custom.www.aluno.frappe.session", Mock(user="aluno@example.com")),
			patch(
				"bruce_lms_custom.www.aluno.get_student_dashboard_data",
				return_value=_inactive_dashboard("Pendente"),
			),
		):
			result = get_student_portal_data()

		self.assertEqual(result["access_status"], "Pendente")
		self.assertFalse(result["student_is_active"])
		self.assertIsNone(result["next_live_class"])
		self.assertEqual(result["recent_materials"], [])
		self.assertEqual(result["exercise_lists"], [])

	def test_expired_student_does_not_receive_pedagogical_content(self):
		with (
			patch("bruce_lms_custom.www.aluno.frappe.session", Mock(user="aluno@example.com")),
			patch(
				"bruce_lms_custom.www.aluno.get_student_dashboard_data",
				return_value=_inactive_dashboard("Expirado"),
			),
		):
			result = get_student_portal_data()

		self.assertEqual(result["access_status"], "Expirado")
		self.assertFalse(result["student_is_active"])
		self.assertIsNone(result["next_live_class"])
		self.assertEqual(result["recent_materials"], [])
		self.assertEqual(result["exercise_lists"], [])

	def test_student_only_receives_backend_permitted_data(self):
		permitted_dashboard = {
			"access_status": "Ativo",
			"student_is_active": True,
			"next_live_class": {"name": "BLC-PERMITIDA"},
			"recent_materials": [{"name": "BEM-PERMITIDO"}],
			"exercise_lists": [{"name": "BEL-PERMITIDA"}],
			"student_progress": {"total_answered_questions": 1},
		}

		with (
			patch("bruce_lms_custom.www.aluno.frappe.session", Mock(user="aluno@example.com")),
			patch("bruce_lms_custom.www.aluno.get_student_dashboard_data", return_value=permitted_dashboard) as get_dashboard,
		):
			result = get_student_portal_data()

		self.assertEqual(result["next_live_class"]["name"], "BLC-PERMITIDA")
		self.assertEqual(result["recent_materials"][0]["name"], "BEM-PERMITIDO")
		self.assertEqual(result["exercise_lists"][0]["name"], "BEL-PERMITIDA")
		get_dashboard.assert_called_once_with()

	def test_guest_cannot_access_portal_data(self):
		with (
			patch("bruce_lms_custom.www.aluno.frappe.session", Mock(user="Guest")),
			patch("bruce_lms_custom.www.aluno._", side_effect=lambda value: value),
			patch("bruce_lms_custom.www.aluno.frappe.throw", side_effect=frappe.PermissionError),
		):
			with self.assertRaises(frappe.PermissionError):
				get_student_portal_data()

	def test_guest_page_redirects_to_login(self):
		frappe.local.flags = frappe._dict()

		with patch("bruce_lms_custom.www.aluno.frappe.session", Mock(user="Guest")):
			with self.assertRaises(frappe.Redirect):
				get_context(frappe._dict())

		self.assertEqual(frappe.local.flags.redirect_location, "/login?redirect-to=/aluno")

	def test_professor_or_admin_does_not_break_student_portal_flow(self):
		with (
			patch("bruce_lms_custom.www.aluno.frappe.session", Mock(user="professor@example.com")),
			patch("bruce_lms_custom.www.aluno.frappe.get_roles", return_value=["Professor"]),
			patch(
				"bruce_lms_custom.www.aluno.get_student_dashboard_data",
				return_value=_inactive_dashboard("Pendente"),
			),
		):
			result = get_student_portal_data()

		self.assertEqual(result["access_status"], "Pendente")
		self.assertFalse(result["student_is_active"])
		self.assertTrue(result["can_access_professor_dashboard"])
		self.assertFalse(result["can_access_operational_dashboard"])
		self.assertTrue(result["can_access_desk"])

	def test_operational_admin_gets_operational_menu_link(self):
		with (
			patch("bruce_lms_custom.www.aluno.frappe.session", Mock(user="admin@example.com")),
			patch("bruce_lms_custom.www.aluno.frappe.get_roles", return_value=["Administrador LMS"]),
			patch(
				"bruce_lms_custom.www.aluno.get_student_dashboard_data",
				return_value=_inactive_dashboard("Pendente"),
			),
		):
			result = get_student_portal_data()

		self.assertTrue(result["can_access_professor_dashboard"])
		self.assertTrue(result["can_access_operational_dashboard"])

	def test_student_role_does_not_get_professor_menu_link(self):
		with patch("bruce_lms_custom.www.aluno.frappe.get_roles", return_value=["LMS Student"]):
			self.assertFalse(_can_access_professor_dashboard("aluno@example.com"))
			self.assertFalse(_can_access_desk("aluno@example.com"))

	def test_page_context_uses_student_portal_body_class(self):
		context = frappe._dict()

		with (
			patch("bruce_lms_custom.www.aluno.frappe.session", Mock(user="aluno@example.com")),
			patch("bruce_lms_custom.www.aluno._", side_effect=lambda value: value),
			patch(
				"bruce_lms_custom.www.aluno.get_student_dashboard_data",
				return_value=_inactive_dashboard("Pendente"),
			),
		):
			get_context(context)

		self.assertEqual(context.body_class, "bruce-student-portal-page")
		self.assertEqual(context.title, "Portal do aluno")

	def test_student_portal_template_does_not_render_standard_frappe_chrome(self):
		template = _app_file("www/aluno.html").read_text()

		self.assertIn('{% extends "templates/base.html" %}', template)
		self.assertNotIn("templates/web.html", template)
		self.assertIn("{% block navbar %}{% endblock %}", template)
		self.assertIn("{% block footer %}{% endblock %}", template)
		self.assertIn("data-student-theme-toggle", template)
		self.assertIn("data-student-menu-toggle", template)
		self.assertIn('data-student-theme-option="light"', template)
		self.assertIn('data-student-theme-option="dark"', template)
		self.assertIn('href="/app"', template)

	def test_student_portal_assets_define_isolated_theme_controls(self):
		css = _app_file("public/css/student_portal.css").read_text()
		js = _app_file("public/js/student_portal.js").read_text()

		self.assertIn("--bruce-bg", css)
		self.assertIn("--bruce-success-text", css)
		self.assertIn('--bruce-primary-hover', css)
		self.assertIn(':root[data-bruce-theme="dark"]', css)
		self.assertIn("body.bruce-student-portal-page .navbar", css)
		self.assertIn('font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif', css)
		self.assertIn("bruceStudentPortalTheme", js)
		self.assertIn("data-student-theme-toggle", js)
		self.assertIn("prefers-color-scheme: dark", js)
		self.assertIn("window.localStorage.setItem", js)

	def test_support_url_ignores_unsafe_scheme(self):
		with patch("bruce_lms_custom.www.aluno.frappe.conf", {"bruce_student_support_url": "javascript:alert(1)"}):
			self.assertIsNone(_get_support_url())

	def test_support_url_accepts_configured_https_link(self):
		with patch("bruce_lms_custom.www.aluno.frappe.conf", {"bruce_student_support_url": "https://suporte.example"}):
			self.assertEqual(_get_support_url(), "https://suporte.example")


def _inactive_dashboard(status):
	return {
		"access_status": status,
		"student_is_active": False,
		"next_live_class": None,
		"recent_materials": [],
		"exercise_lists": [],
		"student_progress": {"access_status": status, "locked": True},
		"student_filter_note": "Acesso não liberado.",
	}


def _app_file(relative_path):
	return Path(__file__).resolve().parents[1] / relative_path
