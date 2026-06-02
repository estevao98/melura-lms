# Copyright (c) 2026, Estevão Oliveira Portes and contributors
# For license information, please see LICENSE

import unittest
from unittest.mock import Mock, patch

import frappe

from bruce_lms_custom.bruce_lms_custom.page.bruce_live_room.bruce_live_room import (
	get_live_room_context,
)

get_live_room_context_without_frappe_wrapper = getattr(get_live_room_context, "__wrapped__", get_live_room_context)


class TestBruceLiveRoom(unittest.TestCase):
	def make_live_class(self, **values):
		doc = Mock()
		doc.name = "BLC-2026-00001"
		doc.title = "Aula de História"
		doc.course = "COURSE-001"
		doc.batch = "BATCH-001"
		doc.instructor = "professor@example.com"
		doc.starts_at = "2026-06-01 19:00:00"
		doc.status = "Ao vivo"
		doc.room_name = "bruce-token-seguro"
		doc.meeting_url = "https://meet.jit.si/bruce-token-seguro"

		for fieldname, value in values.items():
			setattr(doc, fieldname, value)

		return doc

	def test_active_student_can_access_permitted_room(self):
		doc = self.make_live_class()

		with (
			patch(
				"bruce_lms_custom.bruce_lms_custom.page.bruce_live_room.bruce_live_room.frappe.session",
				Mock(user="aluno@example.com"),
			),
			patch(
				"bruce_lms_custom.bruce_lms_custom.page.bruce_live_room.bruce_live_room.frappe.get_doc",
				return_value=doc,
			),
			patch(
				"bruce_lms_custom.bruce_lms_custom.page.bruce_live_room.bruce_live_room.frappe.get_roles",
				return_value=["LMS Student"],
			),
			patch(
				"bruce_lms_custom.bruce_lms_custom.page.bruce_live_room.bruce_live_room.assert_current_student_can_access_live_class"
			) as assert_student_can_access,
			patch(
				"bruce_lms_custom.bruce_lms_custom.page.bruce_live_room.bruce_live_room.BruceLiveClass.get_jitsi_settings",
				return_value=Mock(domain="meet.jit.si"),
			),
			patch(
				"bruce_lms_custom.bruce_lms_custom.page.bruce_live_room.bruce_live_room.frappe.db",
				Mock(get_value=Mock(side_effect=["Curso ENEM", "Turma Maio"])),
			),
		):
			result = get_live_room_context_without_frappe_wrapper("BLC-2026-00001")

		assert_student_can_access.assert_called_once_with(doc)
		self.assertEqual(result["room_name"], "bruce-token-seguro")
		self.assertEqual(result["domain"], "meet.jit.si")
		self.assertEqual(result["external_url"], "https://meet.jit.si/bruce-token-seguro")
		self.assertEqual(result["course_title"], "Curso ENEM")
		self.assertEqual(result["batch_title"], "Turma Maio")

	def test_blocked_student_cannot_access_room(self):
		doc = self.make_live_class()

		with (
			patch(
				"bruce_lms_custom.bruce_lms_custom.page.bruce_live_room.bruce_live_room.frappe.session",
				Mock(user="aluno@example.com"),
			),
			patch(
				"bruce_lms_custom.bruce_lms_custom.page.bruce_live_room.bruce_live_room.frappe.get_doc",
				return_value=doc,
			),
			patch(
				"bruce_lms_custom.bruce_lms_custom.page.bruce_live_room.bruce_live_room.frappe.get_roles",
				return_value=["LMS Student"],
			),
			patch(
				"bruce_lms_custom.bruce_lms_custom.page.bruce_live_room.bruce_live_room.assert_current_student_can_access_live_class",
				side_effect=frappe.PermissionError("bloqueado"),
			),
		):
			with self.assertRaises(frappe.PermissionError):
				get_live_room_context_without_frappe_wrapper("BLC-2026-00001")

	def test_student_cannot_access_room_from_another_batch(self):
		doc = self.make_live_class(batch="BATCH-002")

		with (
			patch(
				"bruce_lms_custom.bruce_lms_custom.page.bruce_live_room.bruce_live_room.frappe.session",
				Mock(user="aluno@example.com"),
			),
			patch(
				"bruce_lms_custom.bruce_lms_custom.page.bruce_live_room.bruce_live_room.frappe.get_doc",
				return_value=doc,
			),
			patch(
				"bruce_lms_custom.bruce_lms_custom.page.bruce_live_room.bruce_live_room.frappe.get_roles",
				return_value=["LMS Student"],
			),
			patch(
				"bruce_lms_custom.bruce_lms_custom.page.bruce_live_room.bruce_live_room.assert_current_student_can_access_live_class",
				side_effect=frappe.PermissionError("outra turma"),
			),
		):
			with self.assertRaises(frappe.PermissionError):
				get_live_room_context_without_frappe_wrapper("BLC-2026-00001")

	def test_professor_can_open_own_room(self):
		doc = self.make_live_class(instructor="professor@example.com")

		with (
			patch(
				"bruce_lms_custom.bruce_lms_custom.page.bruce_live_room.bruce_live_room.frappe.session",
				Mock(user="professor@example.com"),
			),
			patch(
				"bruce_lms_custom.bruce_lms_custom.page.bruce_live_room.bruce_live_room.frappe.get_doc",
				return_value=doc,
			),
			patch(
				"bruce_lms_custom.bruce_lms_custom.page.bruce_live_room.bruce_live_room.frappe.get_roles",
				return_value=["Professor"],
			),
			patch(
				"bruce_lms_custom.bruce_lms_custom.page.bruce_live_room.bruce_live_room.assert_current_student_can_access_live_class"
			) as assert_student_can_access,
			patch(
				"bruce_lms_custom.bruce_lms_custom.page.bruce_live_room.bruce_live_room.BruceLiveClass.get_jitsi_settings",
				return_value=Mock(domain="https://meet.jit.si/"),
			),
			patch(
				"bruce_lms_custom.bruce_lms_custom.page.bruce_live_room.bruce_live_room.frappe.db",
				Mock(get_value=Mock(return_value=None)),
			),
		):
			result = get_live_room_context_without_frappe_wrapper("BLC-2026-00001")

		assert_student_can_access.assert_not_called()
		self.assertEqual(result["domain"], "meet.jit.si")

	def test_admin_can_open_room(self):
		doc = self.make_live_class()

		with (
			patch(
				"bruce_lms_custom.bruce_lms_custom.page.bruce_live_room.bruce_live_room.frappe.session",
				Mock(user="admin@example.com"),
			),
			patch(
				"bruce_lms_custom.bruce_lms_custom.page.bruce_live_room.bruce_live_room.frappe.get_doc",
				return_value=doc,
			),
			patch(
				"bruce_lms_custom.bruce_lms_custom.page.bruce_live_room.bruce_live_room.frappe.get_roles",
				return_value=["Administrador LMS"],
			),
			patch(
				"bruce_lms_custom.bruce_lms_custom.page.bruce_live_room.bruce_live_room.assert_current_student_can_access_live_class"
			) as assert_student_can_access,
			patch(
				"bruce_lms_custom.bruce_lms_custom.page.bruce_live_room.bruce_live_room.BruceLiveClass.get_jitsi_settings",
				return_value=Mock(domain="meet.jit.si"),
			),
			patch(
				"bruce_lms_custom.bruce_lms_custom.page.bruce_live_room.bruce_live_room.frappe.db",
				Mock(get_value=Mock(return_value=None)),
			),
		):
			result = get_live_room_context_without_frappe_wrapper("BLC-2026-00001")

		assert_student_can_access.assert_not_called()
		self.assertEqual(result["status_label"], "Aula ao vivo")

	def test_fallback_external_url_remains_available(self):
		doc = self.make_live_class(meeting_url="https://meet.jit.si/bruce-token-seguro")

		with (
			patch(
				"bruce_lms_custom.bruce_lms_custom.page.bruce_live_room.bruce_live_room.frappe.session",
				Mock(user="admin@example.com"),
			),
			patch(
				"bruce_lms_custom.bruce_lms_custom.page.bruce_live_room.bruce_live_room.frappe.get_doc",
				return_value=doc,
			),
			patch(
				"bruce_lms_custom.bruce_lms_custom.page.bruce_live_room.bruce_live_room.frappe.get_roles",
				return_value=["System Manager"],
			),
			patch(
				"bruce_lms_custom.bruce_lms_custom.page.bruce_live_room.bruce_live_room.BruceLiveClass.get_jitsi_settings",
				return_value=Mock(domain="meet.jit.si"),
			),
			patch(
				"bruce_lms_custom.bruce_lms_custom.page.bruce_live_room.bruce_live_room.frappe.db",
				Mock(get_value=Mock(return_value=None)),
			),
		):
			result = get_live_room_context_without_frappe_wrapper("BLC-2026-00001")

		self.assertEqual(result["external_url"], "https://meet.jit.si/bruce-token-seguro")
