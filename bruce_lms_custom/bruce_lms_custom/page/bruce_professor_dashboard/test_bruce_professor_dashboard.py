# Copyright (c) 2026, Estevão Oliveira Portes and contributors
# For license information, please see license.txt

import unittest
from unittest.mock import patch

from bruce_lms_custom.bruce_lms_custom.page.bruce_professor_dashboard.bruce_professor_dashboard import (
	_get_link_title,
	_get_next_live_class,
)


class TestBruceProfessorDashboard(unittest.TestCase):
	def test_get_next_live_class_prefers_live_class(self):
		live_class = {
			"name": "BLC-2026-00001",
			"title": "Aula ao vivo",
			"status": "Ao vivo",
		}

		with patch(
			"bruce_lms_custom.bruce_lms_custom.page.bruce_professor_dashboard.bruce_professor_dashboard.frappe.get_list",
			return_value=[live_class],
		) as get_list:
			result = _get_next_live_class()

		self.assertEqual(result["name"], live_class["name"])
		self.assertEqual(result["status"], live_class["status"])
		self.assertIsNone(result["course_title"])
		self.assertIsNone(result["batch_title"])
		get_list.assert_called_once()

	def test_get_next_live_class_returns_next_scheduled_when_no_live_class_exists(self):
		scheduled_class = {
			"name": "BLC-2026-00002",
			"title": "Aula agendada",
			"status": "Agendada",
		}

		with (
			patch(
				"bruce_lms_custom.bruce_lms_custom.page.bruce_professor_dashboard.bruce_professor_dashboard.frappe.get_list",
				side_effect=[[], [scheduled_class]],
			) as get_list,
			patch(
				"bruce_lms_custom.bruce_lms_custom.page.bruce_professor_dashboard.bruce_professor_dashboard.now_datetime",
				return_value="2026-05-30 12:00:00",
			),
		):
			result = _get_next_live_class()

		self.assertEqual(result["name"], scheduled_class["name"])
		self.assertEqual(result["status"], scheduled_class["status"])
		self.assertEqual(get_list.call_count, 2)

	def test_get_next_live_class_returns_none_when_no_class_exists(self):
		with (
			patch(
				"bruce_lms_custom.bruce_lms_custom.page.bruce_professor_dashboard.bruce_professor_dashboard.frappe.get_list",
				side_effect=[[], []],
			),
			patch(
				"bruce_lms_custom.bruce_lms_custom.page.bruce_professor_dashboard.bruce_professor_dashboard.now_datetime",
				return_value="2026-05-30 12:00:00",
			),
		):
			result = _get_next_live_class()

		self.assertIsNone(result)

	def test_get_next_live_class_adds_course_and_batch_titles(self):
		scheduled_class = {
			"name": "BLC-2026-00003",
			"title": "Aula agendada",
			"course": "a-guide-to-frappe-learning",
			"batch": "turma-teste-jitsi",
			"status": "Agendada",
		}

		with (
			patch(
				"bruce_lms_custom.bruce_lms_custom.page.bruce_professor_dashboard.bruce_professor_dashboard.frappe.get_list",
				side_effect=[[], [scheduled_class]],
			),
			patch(
				"bruce_lms_custom.bruce_lms_custom.page.bruce_professor_dashboard.bruce_professor_dashboard.frappe.db.get_value",
				side_effect=["Guia do Frappe Learning", "Turma Teste Jitsi"],
			),
			patch(
				"bruce_lms_custom.bruce_lms_custom.page.bruce_professor_dashboard.bruce_professor_dashboard.now_datetime",
				return_value="2026-05-30 12:00:00",
			),
		):
			result = _get_next_live_class()

		self.assertEqual(result["course_title"], "Guia do Frappe Learning")
		self.assertEqual(result["batch_title"], "Turma Teste Jitsi")

	def test_get_link_title_falls_back_to_original_value(self):
		with patch(
			"bruce_lms_custom.bruce_lms_custom.page.bruce_professor_dashboard.bruce_professor_dashboard.frappe.db.get_value",
			return_value=None,
		):
			result = _get_link_title("LMS Course", "a-guide-to-frappe-learning")

		self.assertEqual(result, "a-guide-to-frappe-learning")
