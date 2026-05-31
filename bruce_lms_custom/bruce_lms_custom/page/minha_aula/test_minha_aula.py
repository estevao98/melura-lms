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
			result = get_student_dashboard_data()

		self.assertEqual(result["next_live_class"], {"name": "BLC-2026-00001"})
		self.assertFalse(result["student_filter_enabled"])
		self.assertIn("filtro por matrícula/turma", result["student_filter_note"])
		get_next_visible_live_class.assert_called_once_with()

	def test_get_next_visible_live_class_prefers_live_class(self):
		live_class = {
			"name": "BLC-2026-00001",
			"title": "Aula ao vivo",
			"status": "Ao vivo",
		}

		with (
			patch(
				"bruce_lms_custom.bruce_lms_custom.page.minha_aula.minha_aula.frappe.get_list",
				return_value=[live_class],
			) as get_list,
			patch(
				"bruce_lms_custom.bruce_lms_custom.page.minha_aula.minha_aula.frappe.db",
				Mock(get_value=Mock(return_value=None)),
			),
		):
			result = _get_next_visible_live_class()

		self.assertEqual(result["name"], live_class["name"])
		self.assertEqual(result["class_status_label"], "Aula ao vivo")
		get_list.assert_called_once_with(
			"Bruce Live Class",
			filters={"status": "Ao vivo"},
			fields=[
				"name",
				"title",
				"course",
				"batch",
				"starts_at",
				"status",
				"meeting_url",
			],
			order_by="starts_at asc",
			limit_page_length=1,
		)

	def test_get_next_visible_live_class_returns_next_scheduled_when_no_live_class_exists(self):
		scheduled_class = {
			"name": "BLC-2026-00002",
			"title": "Aula agendada",
			"status": "Agendada",
		}

		with (
			patch(
				"bruce_lms_custom.bruce_lms_custom.page.minha_aula.minha_aula.frappe.get_list",
				side_effect=[[], [scheduled_class]],
			) as get_list,
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
		self.assertEqual(get_list.call_count, 2)
		get_list.assert_any_call(
			"Bruce Live Class",
			filters={
				"status": "Agendada",
				"starts_at": [">=", "2026-05-31 10:00:00"],
			},
			fields=[
				"name",
				"title",
				"course",
				"batch",
				"starts_at",
				"status",
				"meeting_url",
			],
			order_by="starts_at asc",
			limit_page_length=1,
		)

	def test_get_next_visible_live_class_returns_none_when_no_class_exists(self):
		with (
			patch(
				"bruce_lms_custom.bruce_lms_custom.page.minha_aula.minha_aula.frappe.get_list",
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
