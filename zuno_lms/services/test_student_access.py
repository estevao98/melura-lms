# Copyright (c) 2026, Estevão Oliveira Portes and contributors
# For license information, please see LICENSE

import unittest
from unittest.mock import Mock, patch

import frappe

from zuno_lms.services.student_access import (
	ACCESS_ACTIVE,
	ACCESS_BLOCKED,
	ACCESS_EXPIRED,
	ACCESS_PENDING,
	can_current_student_access_live_class,
	get_permitted_educational_materials_for_current_student,
	get_current_student_access_status,
	get_class_progress_summary,
	get_permitted_enem_questions_for_current_student,
	get_permitted_exercise_lists_for_current_student,
	get_permitted_live_classes_for_current_student,
	get_progress_for_current_student,
	has_enem_question_permission,
	has_educational_material_permission,
	save_student_answer,
	has_live_class_permission,
	is_current_student_active,
)


class TestStudentAccess(unittest.TestCase):
	def test_active_student_with_current_access_is_active(self):
		records = [
			frappe._dict(
				name="BSA-2026-00001",
				student="aluno@example.com",
				access_status=ACCESS_ACTIVE,
				course="COURSE-001",
				batch="BATCH-001",
				starts_on="2026-01-01",
				expires_on="2026-12-31",
			)
		]

		with (
			patch("zuno_lms.services.student_access.frappe.session", Mock(user="aluno@example.com")),
			patch("zuno_lms.services.student_access.frappe.get_all", return_value=records),
			patch("zuno_lms.services.student_access.today", return_value="2026-06-01"),
		):
			self.assertTrue(is_current_student_active())
			self.assertEqual(get_current_student_access_status(), ACCESS_ACTIVE)

	def test_pending_student_without_access_is_not_active(self):
		with (
			patch("zuno_lms.services.student_access.frappe.session", Mock(user="aluno@example.com")),
			patch("zuno_lms.services.student_access.frappe.get_all", return_value=[]),
		):
			self.assertFalse(is_current_student_active())
			self.assertEqual(get_current_student_access_status(), ACCESS_PENDING)

	def test_blocked_student_is_not_active_even_with_other_records(self):
		status_records = [
			frappe._dict(
				name="BSA-2026-00001",
				student="aluno@example.com",
				access_status=ACCESS_ACTIVE,
				course="COURSE-001",
				batch="BATCH-001",
			),
			frappe._dict(
				name="BSA-2026-00002",
				student="aluno@example.com",
				access_status=ACCESS_BLOCKED,
				course="COURSE-001",
				batch="BATCH-001",
			),
		]

		with (
			patch("zuno_lms.services.student_access.frappe.session", Mock(user="aluno@example.com")),
			patch("zuno_lms.services.student_access.frappe.get_all", side_effect=[status_records, status_records]),
		):
			self.assertFalse(is_current_student_active())
			self.assertEqual(get_current_student_access_status(), ACCESS_BLOCKED)

	def test_expired_student_access_is_not_active(self):
		records = [
			frappe._dict(
				name="BSA-2026-00001",
				student="aluno@example.com",
				access_status=ACCESS_ACTIVE,
				course="COURSE-001",
				batch="BATCH-001",
				starts_on="2026-01-01",
				expires_on="2026-05-31",
			)
		]

		with (
			patch("zuno_lms.services.student_access.frappe.session", Mock(user="aluno@example.com")),
			patch("zuno_lms.services.student_access.frappe.get_all", return_value=records),
			patch("zuno_lms.services.student_access.today", return_value="2026-06-01"),
		):
			self.assertFalse(is_current_student_active())
			self.assertEqual(get_current_student_access_status(), ACCESS_EXPIRED)

	def test_current_student_can_access_live_class_only_inside_active_batch_scope(self):
		access_records = [
			{
				"name": "BSA-2026-00001",
				"access_status": ACCESS_ACTIVE,
				"course": "COURSE-001",
				"batch": "BATCH-001",
			}
		]

		with patch(
			"zuno_lms.services.student_access.get_active_student_access_records",
			return_value=access_records,
		):
			self.assertTrue(
				can_current_student_access_live_class(
					{
						"name": "BLC-2026-00001",
						"course": "COURSE-001",
						"batch": "BATCH-001",
						"status": "Ao vivo",
					}
				)
			)
			self.assertFalse(
				can_current_student_access_live_class(
					{
						"name": "BLC-2026-00002",
						"course": "COURSE-001",
						"batch": "BATCH-999",
						"status": "Ao vivo",
					}
				)
			)

	def test_permitted_live_classes_are_queried_from_active_access_scope(self):
		access_records = [
			{
				"name": "BSA-2026-00001",
				"access_status": ACCESS_ACTIVE,
				"course": "COURSE-001",
				"batch": "BATCH-001",
			}
		]
		live_class = frappe._dict(
			name="BLC-2026-00001",
			title="Aula permitida",
			course="COURSE-001",
			batch="BATCH-001",
			starts_at="2026-06-01 19:00:00",
			status="Agendada",
			meeting_url="https://meet.jit.si/sala",
		)

		with (
			patch(
				"zuno_lms.services.student_access.get_active_student_access_records",
				return_value=access_records,
			),
			patch("zuno_lms.services.student_access.frappe.get_all", return_value=[live_class]) as get_all,
		):
			result = get_permitted_live_classes_for_current_student(
				statuses=("Agendada",),
				starts_from="2026-06-01 00:00:00",
				limit=5,
			)

		self.assertEqual(result[0]["name"], "BLC-2026-00001")
		get_all.assert_called_once_with(
			"Bruce Live Class",
			filters={
				"status": ["in", ("Agendada",)],
				"starts_at": [">=", "2026-06-01 00:00:00"],
				"batch": "BATCH-001",
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
			limit_page_length=5,
		)

	def test_published_material_is_listed_for_active_student(self):
		access_records = [
			{
				"name": "BSA-2026-00001",
				"access_status": ACCESS_ACTIVE,
				"course": "COURSE-001",
				"batch": "BATCH-001",
			}
		]
		batch_material = frappe._dict(
			name="BEM-2026-00001",
			title="Apostila permitida",
			material_type="Apostila",
			course="COURSE-001",
			batch="BATCH-001",
			related_live_class="BLC-2026-00001",
			topic="Brasil Colônia",
			pdf_file="/private/files/apostila.pdf",
			published_at="2026-06-01 19:00:00",
			description="",
		)
		course_material = frappe._dict(
			name="BEM-2026-00002",
			title="Resumo do curso",
			material_type="Resumo",
			course="COURSE-001",
			batch="",
			related_live_class="",
			topic="Revisão",
			pdf_file="/private/files/resumo.pdf",
			published_at="2026-06-02 19:00:00",
			description="",
		)

		with (
			patch(
				"zuno_lms.services.student_access.get_active_student_access_records",
				return_value=access_records,
			),
			patch(
				"zuno_lms.services.student_access.frappe.get_all",
				side_effect=[[batch_material], [course_material]],
			) as get_all,
		):
			result = get_permitted_educational_materials_for_current_student(limit=5)

		self.assertEqual([material["name"] for material in result], ["BEM-2026-00002", "BEM-2026-00001"])
		self.assertEqual(get_all.call_count, 2)
		get_all.assert_any_call(
			"Bruce Educational Material",
			filters={
				"published": 1,
				"visibility": "Aluno",
				"batch": "BATCH-001",
			},
			fields=[
				"name",
				"title",
				"material_type",
				"course",
				"batch",
				"related_live_class",
				"topic",
				"pdf_file",
				"published_at",
				"description",
			],
			order_by="published_at desc, modified desc",
			limit_page_length=5,
		)
		get_all.assert_any_call(
			"Bruce Educational Material",
			filters={
				"published": 1,
				"visibility": "Aluno",
				"course": "COURSE-001",
				"batch": ["in", ("", None)],
			},
			fields=[
				"name",
				"title",
				"material_type",
				"course",
				"batch",
				"related_live_class",
				"topic",
				"pdf_file",
				"published_at",
				"description",
			],
			order_by="published_at desc, modified desc",
			limit_page_length=5,
		)

	def test_unpublished_material_is_not_allowed_for_student_permission(self):
		doc = Mock(
			course="COURSE-001",
			batch="BATCH-001",
			published=0,
			visibility="Aluno",
		)

		with (
			patch("zuno_lms.services.student_access.frappe.get_roles", return_value=["LMS Student"]),
			patch(
				"zuno_lms.services.student_access.get_active_student_access_records",
				return_value=[{"course": "COURSE-001", "batch": "BATCH-001"}],
			),
		):
			self.assertFalse(has_educational_material_permission(doc, user="aluno@example.com", permission_type="read"))

	def test_blocked_or_pending_student_gets_no_materials(self):
		with (
			patch(
				"zuno_lms.services.student_access.get_active_student_access_records",
				return_value=[],
			),
			patch("zuno_lms.services.student_access.frappe.get_all") as get_all,
		):
			result = get_permitted_educational_materials_for_current_student(limit=5)

		self.assertEqual(result, [])
		get_all.assert_not_called()

	def test_active_student_can_list_published_permitted_enem_question(self):
		access_records = [
			{
				"name": "BSA-2026-00001",
				"access_status": ACCESS_ACTIVE,
				"course": "COURSE-001",
				"batch": "BATCH-001",
			}
		]
		question = frappe._dict(
			name="BEQ-2026-00001",
			title="Brasil Colônia",
			statement="Enunciado permitido",
			discipline="História",
			topic="Brasil Colônia",
			competence="C1",
			skill="H1",
			year=2025,
			difficulty="Média",
			source="ENEM",
			related_course="COURSE-001",
			related_batch="BATCH-001",
			related_live_class="",
			related_material="",
			published_at="2026-06-01 19:00:00",
			correct_option="A",
			commented_resolution="Não deve sair na listagem do aluno",
		)
		alternative = frappe._dict(
			name="BEQA-2026-00001",
			parent="BEQ-2026-00001",
			option_label="A",
			option_text="Alternativa A",
			is_correct=1,
		)

		with (
			patch(
				"zuno_lms.services.student_access.get_active_student_access_records",
				return_value=access_records,
			),
			patch(
				"zuno_lms.services.student_access.frappe.get_all",
				side_effect=[[question], [], [alternative]],
			) as get_all,
		):
			frappe.local.flags = frappe._dict(in_test=True)
			result = get_permitted_enem_questions_for_current_student(limit=5)

		self.assertEqual([item["name"] for item in result], ["BEQ-2026-00001"])
		self.assertNotIn("correct_option", result[0])
		self.assertNotIn("commented_resolution", result[0])
		self.assertEqual(result[0]["alternatives"], [{"option_label": "A", "option_text": "Alternativa A"}])
		get_all.assert_any_call(
			"Bruce ENEM Question",
			filters={
				"published": 1,
				"related_batch": "BATCH-001",
			},
			fields=[
				"name",
				"title",
				"statement",
				"discipline",
				"topic",
				"competence",
				"skill",
				"year",
				"difficulty",
				"source",
				"related_course",
				"related_batch",
				"related_live_class",
				"related_material",
				"published_at",
			],
			order_by="published_at desc, modified desc",
			limit_page_length=5,
		)

	def test_unpublished_enem_question_is_not_allowed_for_student_permission(self):
		doc = Mock(
			related_course="COURSE-001",
			related_batch="BATCH-001",
			published=0,
		)

		with (
			patch("zuno_lms.services.student_access.frappe.get_roles", return_value=["LMS Student"]),
			patch(
				"zuno_lms.services.student_access.get_active_student_access_records",
				return_value=[{"course": "COURSE-001", "batch": "BATCH-001"}],
			),
		):
			self.assertFalse(has_enem_question_permission(doc, user="aluno@example.com", permission_type="read"))

	def test_blocked_or_pending_student_gets_no_enem_questions(self):
		with (
			patch(
				"zuno_lms.services.student_access.get_active_student_access_records",
				return_value=[],
			),
			patch("zuno_lms.services.student_access.frappe.get_all") as get_all,
		):
			frappe.local.flags = frappe._dict(in_test=True)
			result = get_permitted_enem_questions_for_current_student(limit=5)

		self.assertEqual(result, [])
		get_all.assert_not_called()

	def test_published_exercise_list_is_listed_for_active_student(self):
		access_records = [
			{
				"name": "BSA-2026-00001",
				"access_status": ACCESS_ACTIVE,
				"course": "COURSE-001",
				"batch": "BATCH-001",
			}
		]
		exercise_list = frappe._dict(
			name="BEL-2026-00001",
			title="Lista de Humanas",
			course="COURSE-001",
			batch="BATCH-001",
			related_live_class="",
			related_material="",
			published_at="2026-06-01 19:00:00",
			due_date="2026-06-07 23:59:00",
			description="",
		)
		item = frappe._dict(parent="BEL-2026-00001")

		with (
			patch(
				"zuno_lms.services.student_access.get_active_student_access_records",
				return_value=access_records,
			),
			patch(
				"zuno_lms.services.student_access.frappe.get_all",
				side_effect=[[exercise_list], [], [item]],
			) as get_all,
		):
			result = get_permitted_exercise_lists_for_current_student(limit=5)

		self.assertEqual(result[0]["name"], "BEL-2026-00001")
		self.assertEqual(result[0]["question_count"], 1)
		get_all.assert_any_call(
			"Bruce Exercise List",
			filters={
				"published": 1,
				"batch": "BATCH-001",
			},
			fields=[
				"name",
				"title",
				"course",
				"batch",
				"related_live_class",
				"related_material",
				"published_at",
				"due_date",
				"description",
			],
			order_by="published_at desc, modified desc",
			limit_page_length=5,
		)

	def test_unpublished_exercise_list_is_not_listed_for_student(self):
		access_records = [
			{
				"name": "BSA-2026-00001",
				"access_status": ACCESS_ACTIVE,
				"course": "COURSE-001",
				"batch": "BATCH-001",
			}
		]

		with (
			patch(
				"zuno_lms.services.student_access.get_active_student_access_records",
				return_value=access_records,
			),
			patch("zuno_lms.services.student_access.frappe.get_all", side_effect=[[], [], []]) as get_all,
		):
			result = get_permitted_exercise_lists_for_current_student(limit=5)

		self.assertEqual(result, [])
		get_all.assert_any_call(
			"Bruce Exercise List",
			filters={
				"published": 1,
				"batch": "BATCH-001",
			},
			fields=[
				"name",
				"title",
				"course",
				"batch",
				"related_live_class",
				"related_material",
				"published_at",
				"due_date",
				"description",
			],
			order_by="published_at desc, modified desc",
			limit_page_length=5,
		)

	def test_blocked_or_pending_student_gets_no_exercise_lists(self):
		with (
			patch(
				"zuno_lms.services.student_access.get_active_student_access_records",
				return_value=[],
			),
			patch("zuno_lms.services.student_access.frappe.get_all") as get_all,
		):
			result = get_permitted_exercise_lists_for_current_student(limit=5)

		self.assertEqual(result, [])
		get_all.assert_not_called()

	def test_correct_student_answer_is_marked_correct(self):
		answer_doc = Mock(name="BSAW-2026-00001")
		exercise_list = Mock(name="BEL-2026-00001")

		with (
			patch("zuno_lms.services.student_access.frappe.session", Mock(user="aluno@example.com")),
			patch("zuno_lms.services.student_access.is_current_student_active", return_value=True),
			patch("zuno_lms.services.student_access.assert_current_student_can_access_exercise_list"),
			patch("zuno_lms.services.student_access._exercise_list_contains_question", return_value=True),
			patch("zuno_lms.services.student_access.frappe.get_doc", return_value=exercise_list),
			patch("zuno_lms.services.student_access.frappe.new_doc", return_value=answer_doc),
			patch("zuno_lms.services.student_access.now_datetime", return_value="2026-06-01 20:00:00"),
			patch(
				"zuno_lms.services.student_access.frappe.db",
				Mock(get_value=Mock(side_effect=["A", None])),
			),
		):
			result = save_student_answer("BEL-2026-00001", "BEQ-2026-00001", "A")

		self.assertTrue(result["is_correct"])
		self.assertEqual(answer_doc.student_user, "aluno@example.com")
		answer_doc.insert.assert_called_once_with(ignore_permissions=True)

	def test_wrong_student_answer_is_marked_wrong(self):
		answer_doc = Mock(name="BSAW-2026-00001")
		exercise_list = Mock(name="BEL-2026-00001")

		with (
			patch("zuno_lms.services.student_access.frappe.session", Mock(user="aluno@example.com")),
			patch("zuno_lms.services.student_access.is_current_student_active", return_value=True),
			patch("zuno_lms.services.student_access.assert_current_student_can_access_exercise_list"),
			patch("zuno_lms.services.student_access._exercise_list_contains_question", return_value=True),
			patch("zuno_lms.services.student_access.frappe.get_doc", return_value=exercise_list),
			patch("zuno_lms.services.student_access.frappe.new_doc", return_value=answer_doc),
			patch("zuno_lms.services.student_access.now_datetime", return_value="2026-06-01 20:00:00"),
			patch(
				"zuno_lms.services.student_access.frappe.db",
				Mock(get_value=Mock(side_effect=["A", None])),
			),
		):
			result = save_student_answer("BEL-2026-00001", "BEQ-2026-00001", "B")

		self.assertFalse(result["is_correct"])
		answer_doc.insert.assert_called_once_with(ignore_permissions=True)

	def test_student_answer_submission_does_not_accept_frontend_student_user_parameter(self):
		with self.assertRaises(TypeError):
			save_student_answer(
				"BEL-2026-00001",
				"BEQ-2026-00001",
				"A",
				student_user="outro-aluno@example.com",
			)

	def test_inactive_student_cannot_save_answer_before_content_lookup(self):
		with (
			patch("zuno_lms.services.student_access.is_current_student_active", return_value=False),
			patch("zuno_lms.services.student_access.frappe.throw", side_effect=frappe.PermissionError),
			patch("zuno_lms.services.student_access._", side_effect=lambda value: value),
			patch("zuno_lms.services.student_access.frappe.get_doc") as get_doc,
		):
			with self.assertRaises(frappe.PermissionError):
				save_student_answer("BEL-2026-00001", "BEQ-2026-00001", "A")

		get_doc.assert_not_called()

	def test_active_student_progress_uses_only_current_student(self):
		access_records = [
			{
				"name": "BSA-2026-00001",
				"student": "aluno@example.com",
				"access_status": ACCESS_ACTIVE,
				"course": "COURSE-001",
				"batch": "BATCH-001",
			}
		]
		exercise_list = frappe._dict(
			name="BEL-2026-00001",
			title="Lista de Humanas",
			course="COURSE-001",
			batch="BATCH-001",
			published_at="2026-06-01 19:00:00",
		)
		answers = [
			frappe._dict(exercise_list="BEL-2026-00001", question="BEQ-001", is_correct=1, answered_at="2026-06-01 20:00:00"),
			frappe._dict(exercise_list="BEL-2026-00001", question="BEQ-002", is_correct=0, answered_at="2026-06-01 20:05:00"),
		]

		def get_all_side_effect(doctype, filters=None, fields=None, order_by=None, limit_page_length=None):
			if doctype == "Bruce Student Access":
				return access_records
			if doctype == "Bruce Exercise List":
				return [exercise_list]
			if doctype == "Bruce Exercise List Item":
				return [frappe._dict(parent="BEL-2026-00001")]
			if doctype == "Bruce Student Answer":
				self.assertEqual(filters["student_user"], "aluno@example.com")
				return answers
			return []

		with (
			patch("zuno_lms.services.student_access.frappe.session", Mock(user="aluno@example.com")),
			patch("zuno_lms.services.student_access.frappe.get_all", side_effect=get_all_side_effect),
			patch("zuno_lms.services.student_access.today", return_value="2026-06-01"),
			patch("zuno_lms.services.student_access.now_datetime", return_value="2026-06-02 10:00:00"),
		):
			result = get_progress_for_current_student()

		self.assertFalse(result["locked"])
		self.assertEqual(result["total_available_lists"], 1)
		self.assertEqual(result["answered_lists"], 1)
		self.assertEqual(result["total_answered_questions"], 2)
		self.assertEqual(result["total_correct"], 1)
		self.assertEqual(result["total_errors"], 1)
		self.assertEqual(result["accuracy_percentage"], 50)
		self.assertEqual(result["last_activity"], "2026-06-01 20:05:00")
		self.assertTrue(result["is_recently_active"])

	def test_pending_or_blocked_student_progress_is_locked(self):
		with (
			patch("zuno_lms.services.student_access.frappe.session", Mock(user="aluno@example.com")),
			patch(
				"zuno_lms.services.student_access.frappe.get_all",
				return_value=[
					frappe._dict(
						student="aluno@example.com",
						access_status=ACCESS_BLOCKED,
						course="COURSE-001",
						batch="BATCH-001",
					)
				],
			) as get_all,
		):
			result = get_progress_for_current_student()

		self.assertTrue(result["locked"])
		self.assertEqual(result["access_status"], ACCESS_BLOCKED)
		self.assertEqual(result["total_answered_questions"], 0)
		self.assertEqual(result["accuracy_percentage"], 0)
		self.assertEqual(get_all.call_count, 2)

	def test_student_cannot_get_class_progress_summary(self):
		with (
			patch("zuno_lms.services.student_access.frappe.session", Mock(user="aluno@example.com")),
			patch("zuno_lms.services.student_access.frappe.get_roles", return_value=["LMS Student"]),
			patch("zuno_lms.services.student_access._", side_effect=lambda value: value),
			patch("zuno_lms.services.student_access.frappe.throw", side_effect=frappe.PermissionError),
		):
			with self.assertRaises(frappe.PermissionError):
				get_class_progress_summary(batch="BATCH-001")

	def test_professor_can_get_batch_progress_summary(self):
		access_records = [
			frappe._dict(
				name="BSA-2026-00001",
				student="aluno@example.com",
				access_status=ACCESS_ACTIVE,
				course="COURSE-001",
				batch="BATCH-001",
			)
		]
		exercise_list = frappe._dict(name="BEL-2026-00001", course="COURSE-001", batch="BATCH-001", published_at="2026-06-01")
		answers = [
			frappe._dict(exercise_list="BEL-2026-00001", question="BEQ-001", is_correct=1, answered_at="2026-06-01 20:00:00"),
			frappe._dict(exercise_list="BEL-2026-00001", question="BEQ-002", is_correct=1, answered_at="2026-06-01 20:05:00"),
			frappe._dict(exercise_list="BEL-2026-00001", question="BEQ-003", is_correct=0, answered_at="2026-06-01 20:10:00"),
		]

		def get_all_side_effect(doctype, filters=None, fields=None, order_by=None, limit_page_length=None):
			if doctype == "Bruce Student Access":
				return access_records
			if doctype == "Bruce Exercise List":
				return [exercise_list]
			if doctype == "Bruce Exercise List Item":
				return [frappe._dict(parent="BEL-2026-00001")]
			if doctype == "Bruce Student Answer":
				return answers
			return []

		with (
			patch("zuno_lms.services.student_access.frappe.session", Mock(user="professor@example.com")),
			patch("zuno_lms.services.student_access.frappe.get_roles", return_value=["Batch Evaluator"]),
			patch("zuno_lms.services.student_access.frappe.get_all", side_effect=get_all_side_effect),
			patch("zuno_lms.services.student_access.frappe.db", Mock(get_value=Mock(return_value="Aluno Teste"))),
			patch("zuno_lms.services.student_access.today", return_value="2026-06-01"),
			patch("zuno_lms.services.student_access.now_datetime", return_value="2026-06-02 10:00:00"),
		):
			result = get_class_progress_summary(batch="BATCH-001")

		self.assertEqual(result["total_students"], 1)
		self.assertEqual(result["students"][0]["student"], "aluno@example.com")
		self.assertEqual(result["students"][0]["student_name"], "Aluno Teste")
		self.assertEqual(result["students"][0]["total_answered_questions"], 3)
		self.assertEqual(result["students"][0]["total_correct"], 2)
		self.assertEqual(result["students"][0]["total_errors"], 1)
		self.assertEqual(result["students"][0]["accuracy_percentage"], 66.67)

	def test_student_live_class_permission_rejects_class_outside_access_scope(self):
		doc = Mock(course="COURSE-001", batch="BATCH-999")

		with (
			patch("zuno_lms.services.student_access.frappe.session", Mock(user="aluno@example.com")),
			patch("zuno_lms.services.student_access.frappe.get_roles", return_value=["LMS Student"]),
			patch(
				"zuno_lms.services.student_access.get_active_student_access_records",
				return_value=[{"course": "COURSE-001", "batch": "BATCH-001"}],
			),
		):
			self.assertFalse(has_live_class_permission(doc, user="aluno@example.com", permission_type="read"))

	def test_active_student_material_permission_rejects_other_batch(self):
		doc = Mock(
			course="COURSE-001",
			batch="BATCH-999",
			published=1,
			visibility="Aluno",
		)

		with (
			patch("zuno_lms.services.student_access.frappe.get_roles", return_value=["LMS Student"]),
			patch(
				"zuno_lms.services.student_access.get_active_student_access_records",
				return_value=[{"course": "COURSE-001", "batch": "BATCH-001"}],
			),
		):
			self.assertFalse(has_educational_material_permission(doc, user="aluno@example.com", permission_type="read"))
