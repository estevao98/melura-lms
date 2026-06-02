# Copyright (c) 2026, Estevão Oliveira Portes and contributors
# For license information, please see LICENSE

import unittest
from unittest.mock import patch

import frappe

from zuno_lms.zuno_lms.doctype.bruce_exercise_list.bruce_exercise_list import (
	BruceExerciseList,
)


class TestBruceExerciseList(unittest.TestCase):
	def make_doc(self, **values):
		doc = object.__new__(BruceExerciseList)
		doc.title = "Lista de Humanas"
		doc.published = 0
		doc.published_at = None
		doc.items = []

		for fieldname, value in values.items():
			setattr(doc, fieldname, value)

		return doc

	def test_validate_requires_title(self):
		doc = self.make_doc(title=" ")

		with (
			patch(
				"zuno_lms.zuno_lms.doctype.bruce_exercise_list.bruce_exercise_list.frappe.throw",
				side_effect=Exception("sem título"),
			),
			patch(
				"zuno_lms.zuno_lms.doctype.bruce_exercise_list.bruce_exercise_list._",
				side_effect=lambda message, *args, **kwargs: message,
			),
		):
			with self.assertRaisesRegex(Exception, "sem título"):
				doc.validate()

	def test_published_list_requires_at_least_one_question(self):
		doc = self.make_doc(published=1, items=[])

		with (
			patch(
				"zuno_lms.zuno_lms.doctype.bruce_exercise_list.bruce_exercise_list.frappe.throw",
				side_effect=Exception("sem questão"),
			),
			patch(
				"zuno_lms.zuno_lms.doctype.bruce_exercise_list.bruce_exercise_list._",
				side_effect=lambda message, *args, **kwargs: message,
			),
		):
			with self.assertRaisesRegex(Exception, "sem questão"):
				doc.validate()

	def test_validate_sets_published_at_when_published(self):
		doc = self.make_doc(published=1, items=[frappe._dict(question="BEQ-2026-00001")])

		with patch(
			"zuno_lms.zuno_lms.doctype.bruce_exercise_list.bruce_exercise_list.now_datetime",
			return_value="2026-06-01 19:00:00",
		):
			doc.validate()

		self.assertEqual(doc.published_at, "2026-06-01 19:00:00")
