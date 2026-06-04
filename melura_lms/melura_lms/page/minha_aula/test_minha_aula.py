# Copyright (c) 2026, Estevão Oliveira Portes and contributors
# For license information, please see LICENSE

import unittest
from unittest.mock import Mock, patch

import frappe

from melura_lms.melura_lms.page.minha_aula.minha_aula import (
	_get_class_status_label,
	_get_exercise_lists,
	_get_next_visible_live_class,
	_get_recent_materials,
	get_student_exercise_lists,
	get_student_materials,
	get_student_dashboard_data,
)


class TestMinhaAula(unittest.TestCase):
	def test_get_student_dashboard_data_returns_visible_class_and_filter_note(self):
		frappe.local.flags = frappe._dict(in_test=True)

		with patch(
			"melura_lms.melura_lms.page.minha_aula.minha_aula._get_next_visible_live_class",
			return_value={"name": "BLC-2026-00001"},
		) as get_next_visible_live_class:
			with (
				patch(
					"melura_lms.melura_lms.page.minha_aula.minha_aula.get_current_student_access_status",
					return_value="Ativo",
				),
				patch(
					"melura_lms.melura_lms.page.minha_aula.minha_aula.is_current_student_active",
					return_value=True,
				),
				patch(
					"melura_lms.melura_lms.page.minha_aula.minha_aula._get_recent_materials",
					return_value=[{"name": "BEM-2026-00001"}],
				),
				patch(
					"melura_lms.melura_lms.page.minha_aula.minha_aula._get_exercise_lists",
					return_value=[{"name": "BEL-2026-00001"}],
				),
				patch(
					"melura_lms.melura_lms.page.minha_aula.minha_aula.get_progress_for_current_student",
					return_value={"total_answered_questions": 2},
				),
			):
				result = get_student_dashboard_data()

		self.assertEqual(result["next_live_class"], {"name": "BLC-2026-00001"})
		self.assertEqual(result["recent_materials"], [{"name": "BEM-2026-00001"}])
		self.assertEqual(result["exercise_lists"], [{"name": "BEL-2026-00001"}])
		self.assertEqual(result["student_progress"], {"total_answered_questions": 2})
		self.assertTrue(result["student_filter_enabled"])
		self.assertTrue(result["student_is_active"])
		self.assertEqual(result["access_status"], "Ativo")
		self.assertIn("curso ou turma", result["student_filter_note"])
		get_next_visible_live_class.assert_called_once_with()

	def test_get_student_dashboard_data_does_not_query_classes_for_pending_student(self):
		frappe.local.flags = frappe._dict(in_test=True)

		with (
			patch(
				"melura_lms.melura_lms.page.minha_aula.minha_aula._get_next_visible_live_class",
				return_value={"name": "BLC-2026-00001"},
			) as get_next_visible_live_class,
			patch(
				"melura_lms.melura_lms.page.minha_aula.minha_aula._get_recent_materials",
				return_value=[{"name": "BEM-2026-00001"}],
			) as get_recent_materials,
			patch(
				"melura_lms.melura_lms.page.minha_aula.minha_aula._get_exercise_lists",
				return_value=[{"name": "BEL-2026-00001"}],
			) as get_exercise_lists,
			patch(
				"melura_lms.melura_lms.page.minha_aula.minha_aula.get_current_student_access_status",
				return_value="Pendente",
			),
			patch(
				"melura_lms.melura_lms.page.minha_aula.minha_aula.get_progress_for_current_student",
				return_value={"access_status": "Pendente", "locked": True},
			),
			patch(
				"melura_lms.melura_lms.page.minha_aula.minha_aula.is_current_student_active",
				return_value=False,
			),
		):
			result = get_student_dashboard_data()

		self.assertIsNone(result["next_live_class"])
		self.assertEqual(result["recent_materials"], [])
		self.assertEqual(result["exercise_lists"], [])
		self.assertEqual(result["student_progress"], {"access_status": "Pendente", "locked": True})
		self.assertFalse(result["student_is_active"])
		self.assertEqual(result["access_status"], "Pendente")
		self.assertIn("pendente", result["student_filter_note"])
		get_next_visible_live_class.assert_not_called()
		get_recent_materials.assert_not_called()
		get_exercise_lists.assert_not_called()

	def test_get_next_visible_live_class_prefers_live_class(self):
		live_class = {
			"name": "BLC-2026-00001",
			"title": "Aula ao vivo",
			"status": "Ao vivo",
		}

		with (
			patch(
				"melura_lms.melura_lms.page.minha_aula.minha_aula.get_permitted_live_classes_for_current_student",
				return_value=[live_class],
			) as get_permitted_live_classes,
			patch(
				"melura_lms.melura_lms.page.minha_aula.minha_aula.frappe.db",
				Mock(get_value=Mock(return_value=None)),
			),
		):
			result = _get_next_visible_live_class()

		self.assertEqual(result["name"], live_class["name"])
		self.assertEqual(result["class_status_label"], "Aula ao vivo")
		self.assertEqual(result["live_room_route"], "/app/bruce-live-room/BLC-2026-00001")
		get_permitted_live_classes.assert_called_once_with(statuses=("Ao vivo",), starts_from=None, limit=1)

	def test_get_next_visible_live_class_returns_next_scheduled_when_no_live_class_exists(self):
		scheduled_class = {
			"name": "BLC-2026-00002",
			"title": "Aula agendada",
			"status": "Agendada",
		}

		with (
			patch(
				"melura_lms.melura_lms.page.minha_aula.minha_aula.get_permitted_live_classes_for_current_student",
				side_effect=[[], [scheduled_class]],
			) as get_permitted_live_classes,
			patch(
				"melura_lms.melura_lms.page.minha_aula.minha_aula.frappe.db",
				Mock(get_value=Mock(return_value=None)),
			),
			patch(
				"melura_lms.melura_lms.page.minha_aula.minha_aula.now_datetime",
				return_value="2026-05-31 10:00:00",
			),
		):
			result = _get_next_visible_live_class()

		self.assertEqual(result["name"], scheduled_class["name"])
		self.assertEqual(result["class_status_label"], "Aula agendada")
		self.assertEqual(result["live_room_route"], "/app/bruce-live-room/BLC-2026-00002")
		self.assertEqual(get_permitted_live_classes.call_count, 2)
		get_permitted_live_classes.assert_any_call(
			statuses=("Agendada",),
			starts_from="2026-05-31 10:00:00",
			limit=1,
		)

	def test_get_next_visible_live_class_returns_none_when_no_class_exists(self):
		with (
			patch(
				"melura_lms.melura_lms.page.minha_aula.minha_aula.get_permitted_live_classes_for_current_student",
				side_effect=[[], []],
			),
			patch(
				"melura_lms.melura_lms.page.minha_aula.minha_aula.now_datetime",
				return_value="2026-05-31 10:00:00",
			),
		):
			result = _get_next_visible_live_class()

		self.assertIsNone(result)

	def test_get_class_status_label_adds_student_friendly_copy(self):
		self.assertEqual(_get_class_status_label("Agendada"), "Aula agendada")
		self.assertEqual(_get_class_status_label("Ao vivo"), "Aula ao vivo")
		self.assertEqual(_get_class_status_label("Cancelada"), "Cancelada")

	def test_get_recent_materials_adds_display_values(self):
		material = {
			"name": "BEM-2026-00001",
			"title": "Apostila",
			"course": "COURSE-001",
			"batch": "BATCH-001",
			"related_live_class": "BLC-2026-00001",
		}

		with (
			patch(
				"melura_lms.melura_lms.page.minha_aula.minha_aula.get_permitted_educational_materials_for_current_student",
				return_value=[material],
			),
			patch(
				"melura_lms.melura_lms.page.minha_aula.minha_aula.frappe.db",
				Mock(get_value=Mock(side_effect=["Curso ENEM", "Turma Maio", "Aula 1"])),
			),
		):
			result = _get_recent_materials()

		self.assertEqual(result[0]["course_title"], "Curso ENEM")
		self.assertEqual(result[0]["batch_title"], "Turma Maio")
		self.assertEqual(result[0]["related_live_class_title"], "Aula 1")

	def test_get_student_materials_returns_only_when_student_is_active(self):
		with (
			patch(
				"melura_lms.melura_lms.page.minha_aula.minha_aula.is_current_student_active",
				return_value=True,
			),
			patch(
				"melura_lms.melura_lms.page.minha_aula.minha_aula._get_recent_materials",
				return_value=[{"name": "BEM-2026-00001"}],
			) as get_recent_materials,
		):
			result = get_student_materials()

		self.assertEqual(result, [{"name": "BEM-2026-00001"}])
		get_recent_materials.assert_called_once_with()

	def test_get_student_materials_returns_empty_for_inactive_student(self):
		with (
			patch(
				"melura_lms.melura_lms.page.minha_aula.minha_aula.is_current_student_active",
				return_value=False,
			),
			patch(
				"melura_lms.melura_lms.page.minha_aula.minha_aula._get_recent_materials",
				return_value=[{"name": "BEM-2026-00001"}],
			) as get_recent_materials,
		):
			result = get_student_materials()

		self.assertEqual(result, [])
		get_recent_materials.assert_not_called()

	def test_get_exercise_lists_adds_display_values(self):
		exercise_list = {
			"name": "BEL-2026-00001",
			"title": "Lista de Humanas",
			"course": "COURSE-001",
			"batch": "BATCH-001",
			"related_live_class": "BLC-2026-00001",
		}

		with (
			patch(
				"melura_lms.melura_lms.page.minha_aula.minha_aula.get_permitted_exercise_lists_for_current_student",
				return_value=[exercise_list],
			),
			patch(
				"melura_lms.melura_lms.page.minha_aula.minha_aula.frappe.db",
				Mock(get_value=Mock(side_effect=["Curso ENEM", "Turma Maio", "Aula 1"])),
			),
		):
			result = _get_exercise_lists()

		self.assertEqual(result[0]["course_title"], "Curso ENEM")
		self.assertEqual(result[0]["batch_title"], "Turma Maio")
		self.assertEqual(result[0]["related_live_class_title"], "Aula 1")

	def test_get_student_exercise_lists_returns_only_when_student_is_active(self):
		with (
			patch(
				"melura_lms.melura_lms.page.minha_aula.minha_aula.is_current_student_active",
				return_value=True,
			),
			patch(
				"melura_lms.melura_lms.page.minha_aula.minha_aula._get_exercise_lists",
				return_value=[{"name": "BEL-2026-00001"}],
			) as get_exercise_lists,
		):
			result = get_student_exercise_lists()

		self.assertEqual(result, [{"name": "BEL-2026-00001"}])
		get_exercise_lists.assert_called_once_with()

	def test_get_student_exercise_lists_returns_empty_for_inactive_student(self):
		with (
			patch(
				"melura_lms.melura_lms.page.minha_aula.minha_aula.is_current_student_active",
				return_value=False,
			),
			patch(
				"melura_lms.melura_lms.page.minha_aula.minha_aula._get_exercise_lists",
				return_value=[{"name": "BEL-2026-00001"}],
			) as get_exercise_lists,
		):
			result = get_student_exercise_lists()

		self.assertEqual(result, [])
		get_exercise_lists.assert_not_called()
