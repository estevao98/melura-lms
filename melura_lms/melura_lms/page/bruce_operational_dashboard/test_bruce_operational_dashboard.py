# Copyright (c) 2026, Estevão Oliveira Portes and contributors
# For license information, please see LICENSE

import unittest
from unittest.mock import Mock, patch

import frappe

from melura_lms.melura_lms.page.bruce_operational_dashboard.bruce_operational_dashboard import (
	_can_access_operational_dashboard,
	_get_content_summary,
	_get_exercises_progress_summary,
	_get_inactive_students,
	_get_student_access_summary,
	get_dashboard_data,
)


class TestBruceOperationalDashboard(unittest.TestCase):
	def setUp(self):
		frappe.local.flags = frappe._dict(in_test=True)
		frappe.local.session = frappe._dict(user="Administrator")

	def test_admin_can_access_aggregated_data(self):
		frappe.local.session.user = "Administrator"

		with (
			patch(
				"melura_lms.melura_lms.page.bruce_operational_dashboard.bruce_operational_dashboard._get_student_access_summary",
				return_value={
					"total_students_with_access": 1,
					"status_counts": {"Ativo": 1, "Pendente": 0, "Bloqueado": 0, "Expirado": 0},
				},
			),
			patch(
				"melura_lms.melura_lms.page.bruce_operational_dashboard.bruce_operational_dashboard._get_classes_summary",
				return_value={"week_live_classes": 0, "upcoming_classes_without_room": []},
			),
			patch(
				"melura_lms.melura_lms.page.bruce_operational_dashboard.bruce_operational_dashboard._get_content_summary",
				return_value={"published_materials": 0, "published_questions": 0, "published_exercise_lists": 0},
			),
			patch(
				"melura_lms.melura_lms.page.bruce_operational_dashboard.bruce_operational_dashboard._get_exercises_progress_summary",
				return_value={"registered_answers": 0, "correct_answers": 0, "average_accuracy": 0, "inactive_students": []},
			),
			patch(
				"melura_lms.melura_lms.page.bruce_operational_dashboard.bruce_operational_dashboard._get_operational_alerts",
				return_value=[],
			),
		):
			result = get_dashboard_data()

		self.assertEqual(result["overview"]["total_students_with_access"], 1)
		self.assertEqual(result["overview"]["active_students"], 1)
		self.assertIn("classes", result)
		self.assertIn("content", result)
		self.assertIn("exercises_progress", result)
		self.assertIn("alerts", result)

	def test_common_student_cannot_access_operational_dashboard(self):
		frappe.local.session.user = "student@example.com"
		with (
			patch(
				"melura_lms.melura_lms.page.bruce_operational_dashboard.bruce_operational_dashboard.frappe.get_roles",
				return_value=["LMS Student"],
			),
			patch(
				"melura_lms.melura_lms.page.bruce_operational_dashboard.bruce_operational_dashboard.frappe.throw",
				side_effect=frappe.PermissionError,
			),
			patch(
				"melura_lms.melura_lms.page.bruce_operational_dashboard.bruce_operational_dashboard._",
				side_effect=lambda message: message,
			),
		):
			self.assertFalse(_can_access_operational_dashboard())
			with self.assertRaises(frappe.PermissionError):
				get_dashboard_data()

	def test_student_access_status_counts_are_correct(self):
		records = [
			{"student": "a@example.com", "access_status": "Ativo"},
			{"student": "b@example.com", "access_status": "Ativo"},
			{"student": "c@example.com", "access_status": "Pendente"},
			{"student": "d@example.com", "access_status": "Bloqueado"},
			{"student": "e@example.com", "access_status": "Expirado"},
		]

		with patch(
			"melura_lms.melura_lms.page.bruce_operational_dashboard.bruce_operational_dashboard.frappe.get_all",
			return_value=records,
		):
			result = _get_student_access_summary()

		self.assertEqual(result["total_students_with_access"], 5)
		self.assertEqual(result["status_counts"]["Ativo"], 2)
		self.assertEqual(result["status_counts"]["Pendente"], 1)
		self.assertEqual(result["status_counts"]["Bloqueado"], 1)
		self.assertEqual(result["status_counts"]["Expirado"], 1)

	def test_published_content_counts_are_correct(self):
		with patch(
			"melura_lms.melura_lms.page.bruce_operational_dashboard.bruce_operational_dashboard.frappe.db",
			Mock(count=Mock(side_effect=[7, 30, 4])),
		):
			result = _get_content_summary()

		self.assertEqual(result["published_materials"], 7)
		self.assertEqual(result["published_questions"], 30)
		self.assertEqual(result["published_exercise_lists"], 4)

	def test_inactive_students_are_identified_from_student_answers(self):
		get_all_results = [
			[
				{"student": "active@example.com"},
				{"student": "inactive@example.com"},
				{"student": "never@example.com"},
			],
		]
		answers = [
			{"student_user": "active@example.com", "answered_at": "2026-05-25 10:00:00"},
			{"student_user": "inactive@example.com", "answered_at": "2026-05-01 10:00:00"},
		]

		with (
			patch(
				"melura_lms.melura_lms.page.bruce_operational_dashboard.bruce_operational_dashboard.frappe.get_all",
				side_effect=get_all_results,
			),
			patch(
				"melura_lms.melura_lms.page.bruce_operational_dashboard.bruce_operational_dashboard.now_datetime",
				return_value="2026-06-01 12:00:00",
			),
			patch(
				"melura_lms.melura_lms.page.bruce_operational_dashboard.bruce_operational_dashboard.add_to_date",
				return_value="2026-05-18 12:00:00",
			),
			patch(
				"melura_lms.melura_lms.page.bruce_operational_dashboard.bruce_operational_dashboard.frappe.db",
				Mock(get_value=Mock(side_effect=lambda doctype, name, fieldname: name.split("@")[0].title())),
			),
		):
			result = _get_inactive_students(answers)

		students = {student["student"] for student in result}
		self.assertNotIn("active@example.com", students)
		self.assertIn("inactive@example.com", students)
		self.assertIn("never@example.com", students)

	def test_exercises_progress_calculates_registered_answers_and_accuracy(self):
		answers = [
			{"student_user": "a@example.com", "is_correct": 1, "answered_at": "2026-05-25 10:00:00"},
			{"student_user": "a@example.com", "is_correct": 0, "answered_at": "2026-05-25 10:10:00"},
			{"student_user": "b@example.com", "is_correct": 1, "answered_at": "2026-05-25 10:20:00"},
		]

		with (
			patch(
				"melura_lms.melura_lms.page.bruce_operational_dashboard.bruce_operational_dashboard.frappe.get_all",
				side_effect=[answers, []],
			),
			patch(
				"melura_lms.melura_lms.page.bruce_operational_dashboard.bruce_operational_dashboard.now_datetime",
				return_value="2026-06-01 12:00:00",
			),
			patch(
				"melura_lms.melura_lms.page.bruce_operational_dashboard.bruce_operational_dashboard.add_to_date",
				return_value="2026-05-18 12:00:00",
			),
		):
			result = _get_exercises_progress_summary()

		self.assertEqual(result["registered_answers"], 3)
		self.assertEqual(result["correct_answers"], 2)
		self.assertEqual(result["average_accuracy"], 66.7)
		self.assertEqual(result["inactive_students"], [])
