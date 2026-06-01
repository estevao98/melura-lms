# Copyright (c) 2026, Estevão Oliveira Portes and contributors
# For license information, please see license.txt

import unittest
from unittest.mock import Mock, patch

import frappe

from bruce_lms_custom.bruce_lms_custom.page.minha_aula.minha_aula import (
	_get_class_status_label,
	_get_next_visible_live_class,
	get_student_dashboard_data,
)


class TestMinhaAula(unittest.TestCase):
	def test_get_student_dashboard_data_returns_visible_class_and_filter_note(self):
		frappe.local.flags = frappe._dict(in_test=True)

		with patch(
			"bruce_lms_custom.bruce_lms_custom.page.minha_aula.minha_aula._get_next_visible_live_class",
			return_value={"name": "BLC-2026-00001"},
		) as get_next_visible_live_class:
			with (
				patch(
					"bruce_lms_custom.bruce_lms_custom.page.minha_aula.minha_aula.get_current_student_access_status",
					return_value="Ativo",
				),
				patch(
					"bruce_lms_custom.bruce_lms_custom.page.minha_aula.minha_aula.is_current_student_active",
					return_value=True,
				),
			):
				result = get_student_dashboard_data()

		self.assertEqual(result["next_live_class"], {"name": "BLC-2026-00001"})
		self.assertTrue(result["student_filter_enabled"])
		self.assertTrue(result["student_is_active"])
		self.assertEqual(result["access_status"], "Ativo")
		self.assertIn("curso ou turma", result["student_filter_note"])
		get_next_visible_live_class.assert_called_once_with()

	def test_get_student_dashboard_data_does_not_query_classes_for_pending_student(self):
		frappe.local.flags = frappe._dict(in_test=True)

		with (
			patch(
				"bruce_lms_custom.bruce_lms_custom.page.minha_aula.minha_aula._get_next_visible_live_class",
				return_value={"name": "BLC-2026-00001"},
			) as get_next_visible_live_class,
			patch(
				"bruce_lms_custom.bruce_lms_custom.page.minha_aula.minha_aula.get_current_student_access_status",
				return_value="Pendente",
			),
			patch(
				"bruce_lms_custom.bruce_lms_custom.page.minha_aula.minha_aula.is_current_student_active",
				return_value=False,
			),
		):
			result = get_student_dashboard_data()

		self.assertIsNone(result["next_live_class"])
		self.assertFalse(result["student_is_active"])
		self.assertEqual(result["access_status"], "Pendente")
		self.assertIn("pendente", result["student_filter_note"])
		get_next_visible_live_class.assert_not_called()

	def test_get_next_visible_live_class_prefers_live_class(self):
		live_class = {
			"name": "BLC-2026-00001",
			"title": "Aula ao vivo",
			"status": "Ao vivo",
		}

		with (
			patch(
				"bruce_lms_custom.bruce_lms_custom.page.minha_aula.minha_aula.get_permitted_live_classes_for_current_student",
				return_value=[live_class],
			) as get_permitted_live_classes,
			patch(
				"bruce_lms_custom.bruce_lms_custom.page.minha_aula.minha_aula.frappe.db",
				Mock(get_value=Mock(return_value=None)),
			),
		):
			result = _get_next_visible_live_class()

		self.assertEqual(result["name"], live_class["name"])
		self.assertEqual(result["class_status_label"], "Aula ao vivo")
		get_permitted_live_classes.assert_called_once_with(statuses=("Ao vivo",), starts_from=None, limit=1)

	def test_get_next_visible_live_class_returns_next_scheduled_when_no_live_class_exists(self):
		scheduled_class = {
			"name": "BLC-2026-00002",
			"title": "Aula agendada",
			"status": "Agendada",
		}

		with (
			patch(
				"bruce_lms_custom.bruce_lms_custom.page.minha_aula.minha_aula.get_permitted_live_classes_for_current_student",
				side_effect=[[], [scheduled_class]],
			) as get_permitted_live_classes,
			patch(
				"bruce_lms_custom.bruce_lms_custom.page.minha_aula.minha_aula.frappe.db",
				Mock(get_value=Mock(return_value=None)),
			),
			patch(
				"bruce_lms_custom.bruce_lms_custom.page.minha_aula.minha_aula.now_datetime",
				return_value="2026-05-31 10:00:00",
			),
		):
			result = _get_next_visible_live_class()

		self.assertEqual(result["name"], scheduled_class["name"])
		self.assertEqual(result["class_status_label"], "Aula agendada")
		self.assertEqual(get_permitted_live_classes.call_count, 2)
		get_permitted_live_classes.assert_any_call(
			statuses=("Agendada",),
			starts_from="2026-05-31 10:00:00",
			limit=1,
		)

	def test_get_next_visible_live_class_returns_none_when_no_class_exists(self):
		with (
			patch(
				"bruce_lms_custom.bruce_lms_custom.page.minha_aula.minha_aula.get_permitted_live_classes_for_current_student",
				side_effect=[[], []],
			),
			patch(
				"bruce_lms_custom.bruce_lms_custom.page.minha_aula.minha_aula.now_datetime",
				return_value="2026-05-31 10:00:00",
			),
		):
			result = _get_next_visible_live_class()

		self.assertIsNone(result)

	def test_get_class_status_label_adds_student_friendly_copy(self):
		self.assertEqual(_get_class_status_label("Agendada"), "Aula agendada")
		self.assertEqual(_get_class_status_label("Ao vivo"), "Aula ao vivo")
		self.assertEqual(_get_class_status_label("Cancelada"), "Cancelada")
