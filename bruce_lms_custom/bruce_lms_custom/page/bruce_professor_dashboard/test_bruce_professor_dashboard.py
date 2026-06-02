# Copyright (c) 2026, Estevão Oliveira Portes and contributors
# For license information, please see LICENSE

import unittest
from unittest.mock import Mock, patch

import frappe

from bruce_lms_custom.bruce_lms_custom.page.bruce_professor_dashboard.bruce_professor_dashboard import (
	WHATSAPP_INTEGRATION_DISABLED_LABEL,
	_get_class_status_label,
	_get_class_progress_summary,
	_get_link_title,
	_get_next_live_class,
	_get_week_live_classes,
	_get_whatsapp_status_label,
	get_dashboard_data,
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
		) as get_list, patch(
			"bruce_lms_custom.bruce_lms_custom.page.bruce_professor_dashboard.bruce_professor_dashboard.frappe.get_all",
			return_value=[],
		) as get_all, patch(
			"bruce_lms_custom.bruce_lms_custom.page.bruce_professor_dashboard.bruce_professor_dashboard.frappe.db",
			Mock(get_value=Mock(return_value=None), get_single_value=Mock(return_value=1)),
		):
			result = _get_next_live_class()

		self.assertEqual(result["name"], live_class["name"])
		self.assertEqual(result["status"], live_class["status"])
		self.assertIsNone(result["course_title"])
		self.assertIsNone(result["batch_title"])
		self.assertEqual(result["class_status_label"], "Aula ao vivo")
		self.assertEqual(result["live_room_route"], "/app/bruce-live-room/BLC-2026-00001")
		self.assertEqual(result["notice_logs"], [])
		get_list.assert_called_once()
		get_list.assert_called_with(
			"Bruce Live Class",
			filters={"status": "Ao vivo"},
			fields=[
				"name",
				"title",
				"course",
				"batch",
				"starts_at",
				"status",
				"whatsapp_status",
				"meeting_url",
			],
			order_by="starts_at asc",
			limit_page_length=1,
		)
		get_all.assert_called_once_with(
			"Bruce Live Class Notice Log",
			filters={"related_live_class": live_class["name"]},
			fields=["event_type", "title", "message", "status", "created_by", "created_at"],
			order_by="created_at desc, creation desc",
			limit_page_length=4,
		)

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
				"bruce_lms_custom.bruce_lms_custom.page.bruce_professor_dashboard.bruce_professor_dashboard.frappe.get_all",
				return_value=[],
			) as get_all,
			patch(
				"bruce_lms_custom.bruce_lms_custom.page.bruce_professor_dashboard.bruce_professor_dashboard.frappe.db",
				Mock(get_value=Mock(return_value=None), get_single_value=Mock(return_value=1)),
			),
			patch(
				"bruce_lms_custom.bruce_lms_custom.page.bruce_professor_dashboard.bruce_professor_dashboard.now_datetime",
				return_value="2026-05-30 12:00:00",
			),
		):
			result = _get_next_live_class()

		self.assertEqual(result["name"], scheduled_class["name"])
		self.assertEqual(result["status"], scheduled_class["status"])
		self.assertEqual(result["live_room_route"], "/app/bruce-live-room/BLC-2026-00002")
		self.assertEqual(result["notice_logs"], [])
		self.assertEqual(get_list.call_count, 2)
		get_list.assert_any_call(
			"Bruce Live Class",
			filters={"status": "Ao vivo"},
			fields=[
				"name",
				"title",
				"course",
				"batch",
				"starts_at",
				"status",
				"whatsapp_status",
				"meeting_url",
			],
			order_by="starts_at asc",
			limit_page_length=1,
		)
		get_all.assert_called_once_with(
			"Bruce Live Class Notice Log",
			filters={"related_live_class": scheduled_class["name"]},
			fields=["event_type", "title", "message", "status", "created_by", "created_at"],
			order_by="created_at desc, creation desc",
			limit_page_length=4,
		)

	def test_get_next_live_class_returns_none_when_no_class_exists(self):
		with (
			patch(
				"bruce_lms_custom.bruce_lms_custom.page.bruce_professor_dashboard.bruce_professor_dashboard.frappe.get_list",
				side_effect=[[], []],
			),
			patch(
				"bruce_lms_custom.bruce_lms_custom.page.bruce_professor_dashboard.bruce_professor_dashboard.frappe.get_all",
				return_value=[],
			) as get_all,
			patch(
				"bruce_lms_custom.bruce_lms_custom.page.bruce_professor_dashboard.bruce_professor_dashboard.now_datetime",
				return_value="2026-05-30 12:00:00",
			),
		):
			result = _get_next_live_class()

		self.assertIsNone(result)
		get_all.assert_not_called()

	def test_get_dashboard_data_returns_next_class_and_week_classes(self):
		frappe.local.flags = frappe._dict(in_test=True)

		with (
			patch(
				"bruce_lms_custom.bruce_lms_custom.page.bruce_professor_dashboard.bruce_professor_dashboard._get_next_live_class",
				return_value={"name": "BLC-2026-00001"},
			) as get_next_live_class,
			patch(
				"bruce_lms_custom.bruce_lms_custom.page.bruce_professor_dashboard.bruce_professor_dashboard._get_week_live_classes",
				return_value=[{"name": "BLC-2026-00002"}],
			) as get_week_live_classes,
			patch(
				"bruce_lms_custom.bruce_lms_custom.page.bruce_professor_dashboard.bruce_professor_dashboard._get_class_progress_summary",
				return_value={"total_students": 1, "students": [{"student": "aluno@example.com"}]},
			) as get_class_progress_summary,
		):
			result = get_dashboard_data()

		self.assertEqual(result["next_live_class"], {"name": "BLC-2026-00001"})
		self.assertEqual(result["week_classes"], [{"name": "BLC-2026-00002"}])
		self.assertEqual(result["class_progress"], {"total_students": 1, "students": [{"student": "aluno@example.com"}]})
		self.assertNotIn("week_live_classes", result)
		get_next_live_class.assert_called_once_with()
		get_week_live_classes.assert_called_once_with()
		get_class_progress_summary.assert_called_once_with({"name": "BLC-2026-00001"})

	def test_get_class_progress_summary_uses_live_class_batch_and_course(self):
		live_class = {"name": "BLC-2026-00001", "course": "COURSE-001", "batch": "BATCH-001"}

		with patch(
			"bruce_lms_custom.bruce_lms_custom.page.bruce_professor_dashboard.bruce_professor_dashboard.get_progress_summary_for_scope",
			return_value={"batch": "BATCH-001", "total_students": 1},
		) as get_progress_summary_for_scope:
			result = _get_class_progress_summary(live_class)

		self.assertEqual(result["total_students"], 1)
		get_progress_summary_for_scope.assert_called_once_with(batch="BATCH-001", course="COURSE-001", limit=20)

	def test_get_week_live_classes_returns_scheduled_and_live_classes_for_next_7_days(self):
		classes = [
			{
				"name": "BLC-2026-00002",
				"title": "Aula de Geografia",
				"course": "humanas-enem",
				"batch": "turma-maio",
				"status": "Agendada",
				"whatsapp_status": "Pendente",
			}
		]

		with (
			patch(
				"bruce_lms_custom.bruce_lms_custom.page.bruce_professor_dashboard.bruce_professor_dashboard.frappe.get_list",
				return_value=classes,
			) as get_list,
			patch(
				"bruce_lms_custom.bruce_lms_custom.page.bruce_professor_dashboard.bruce_professor_dashboard.frappe.db",
				Mock(
					get_value=Mock(side_effect=["Humanas ENEM", "Turma Maio"]),
					get_single_value=Mock(return_value=1),
				),
			),
			patch(
				"bruce_lms_custom.bruce_lms_custom.page.bruce_professor_dashboard.bruce_professor_dashboard.now_datetime",
				return_value="2026-05-30 12:00:00",
			),
			patch(
				"bruce_lms_custom.bruce_lms_custom.page.bruce_professor_dashboard.bruce_professor_dashboard.add_to_date",
				return_value="2026-06-06 12:00:00",
			) as add_to_date,
		):
			result = _get_week_live_classes()

		self.assertEqual(len(result), 1)
		self.assertEqual(result[0]["name"], "BLC-2026-00002")
		self.assertEqual(result[0]["course_title"], "Humanas ENEM")
		self.assertEqual(result[0]["batch_title"], "Turma Maio")
		self.assertEqual(result[0]["class_status_label"], "Aula agendada")
		self.assertEqual(result[0]["whatsapp_status_label"], "WhatsApp pendente")
		self.assertEqual(result[0]["live_room_route"], "/app/bruce-live-room/BLC-2026-00002")
		self.assertEqual(result[0]["notice_logs"], [])
		add_to_date.assert_called_once_with("2026-05-30 12:00:00", days=7)
		get_list.assert_called_once_with(
			"Bruce Live Class",
			filters={
				"status": ["in", ["Agendada", "Ao vivo"]],
				"starts_at": ["between", ["2026-05-30 12:00:00", "2026-06-06 12:00:00"]],
			},
			fields=[
				"name",
				"title",
				"course",
				"batch",
				"starts_at",
				"status",
				"whatsapp_status",
				"meeting_url",
			],
			order_by="starts_at asc",
			limit_page_length=20,
		)

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
				"bruce_lms_custom.bruce_lms_custom.page.bruce_professor_dashboard.bruce_professor_dashboard.frappe.get_all",
				return_value=[],
			),
			patch(
				"bruce_lms_custom.bruce_lms_custom.page.bruce_professor_dashboard.bruce_professor_dashboard.frappe.db",
				Mock(
					get_value=Mock(side_effect=["Guia do Frappe Learning", "Turma Teste Jitsi"]),
					get_single_value=Mock(return_value=1),
				),
			),
			patch(
				"bruce_lms_custom.bruce_lms_custom.page.bruce_professor_dashboard.bruce_professor_dashboard.now_datetime",
				return_value="2026-05-30 12:00:00",
			),
		):
			result = _get_next_live_class()

		self.assertEqual(result["course_title"], "Guia do Frappe Learning")
		self.assertEqual(result["batch_title"], "Turma Teste Jitsi")
		self.assertEqual(result["notice_logs"], [])

	def test_get_link_title_falls_back_to_original_value(self):
		with patch(
			"bruce_lms_custom.bruce_lms_custom.page.bruce_professor_dashboard.bruce_professor_dashboard.frappe.db",
			Mock(get_value=Mock(return_value=None)),
		):
			result = _get_link_title("LMS Course", "a-guide-to-frappe-learning")

		self.assertEqual(result, "a-guide-to-frappe-learning")

	def test_get_class_status_label_adds_teacher_friendly_copy(self):
		self.assertEqual(_get_class_status_label("Agendada"), "Aula agendada")
		self.assertEqual(_get_class_status_label("Ao vivo"), "Aula ao vivo")
		self.assertEqual(_get_class_status_label("Encerrada"), "Encerrada")

	def test_get_whatsapp_status_label_uses_integration_disabled_when_settings_are_off(self):
		with patch(
			"bruce_lms_custom.bruce_lms_custom.page.bruce_professor_dashboard.bruce_professor_dashboard.frappe.db",
			Mock(get_single_value=Mock(return_value=0)),
		):
			result = _get_whatsapp_status_label("Enviado")

		self.assertEqual(result, WHATSAPP_INTEGRATION_DISABLED_LABEL)

	def test_get_whatsapp_status_label_maps_stored_status_when_integration_is_on(self):
		with patch(
			"bruce_lms_custom.bruce_lms_custom.page.bruce_professor_dashboard.bruce_professor_dashboard.frappe.db",
			Mock(get_single_value=Mock(return_value=1)),
		):
			self.assertEqual(_get_whatsapp_status_label("Não enviado"), "WhatsApp pendente")
			self.assertEqual(_get_whatsapp_status_label("Pendente"), "WhatsApp pendente")
			self.assertEqual(_get_whatsapp_status_label("Enviado"), "WhatsApp enviado")
			self.assertEqual(_get_whatsapp_status_label("Falhou"), "WhatsApp falhou")
