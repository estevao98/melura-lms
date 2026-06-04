# Copyright (c) 2026, Estevão Oliveira Portes and contributors
# For license information, please see LICENSE

import unittest
from unittest.mock import Mock, patch

import frappe

from melura_lms.melura_lms.doctype.bruce_student_answer.bruce_student_answer import BruceStudentAnswer


class TestBruceStudentAnswer(unittest.TestCase):
	def make_answer(self, **values):
		answer = object.__new__(BruceStudentAnswer)
		answer.exercise_list = "BEL-2026-00001"
		answer.question = "BEQ-2026-00001"
		answer.student_user = "aluno@example.com"
		answer.selected_option = "A"
		answer.is_correct = 0
		answer.answered_at = None

		for fieldname, value in values.items():
			setattr(answer, fieldname, value)

		return answer

	def test_correctness_is_computed_from_question_key(self):
		answer = self.make_answer(selected_option="b", is_correct=1)

		with (
			patch(
				"melura_lms.melura_lms.doctype.bruce_student_answer.bruce_student_answer.frappe.db",
				Mock(get_value=Mock(return_value="A")),
			),
			patch(
				"melura_lms.melura_lms.doctype.bruce_student_answer.bruce_student_answer.now_datetime",
				return_value="2026-06-01 20:00:00",
			),
		):
			answer.validate()

		self.assertEqual(answer.selected_option, "B")
		self.assertFalse(answer.is_correct)
		self.assertEqual(answer.answered_at, "2026-06-01 20:00:00")

	def test_missing_question_key_rejects_answer(self):
		answer = self.make_answer()

		with (
			patch(
				"melura_lms.melura_lms.doctype.bruce_student_answer.bruce_student_answer.frappe.db",
				Mock(get_value=Mock(return_value="")),
			),
			patch(
				"melura_lms.melura_lms.doctype.bruce_student_answer.bruce_student_answer.frappe.throw",
				side_effect=frappe.ValidationError,
			),
			patch(
				"melura_lms.melura_lms.doctype.bruce_student_answer.bruce_student_answer._",
				side_effect=lambda value: value,
			),
		):
			with self.assertRaises(frappe.ValidationError):
				answer.validate()


if __name__ == "__main__":
	unittest.main()
