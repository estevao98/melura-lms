# Copyright (c) 2026, Estevão Oliveira Portes and contributors
# For license information, please see LICENSE

import unittest
from unittest.mock import patch

import frappe

from melura_lms.melura_lms.doctype.melura_enem_question.melura_enem_question import (
	MeluraENEMQuestion,
)


class TestMeluraENEMQuestion(unittest.TestCase):
	def make_doc(self, **values):
		doc = object.__new__(MeluraENEMQuestion)
		doc.statement = "Enunciado da questão"
		doc.published = 0
		doc.published_at = None
		doc.correct_option = None
		doc.alternatives = []

		for fieldname, value in values.items():
			setattr(doc, fieldname, value)

		return doc

	def test_validate_requires_statement(self):
		doc = self.make_doc(statement=" ")

		with (
			patch(
				"melura_lms.melura_lms.doctype.melura_enem_question.melura_enem_question.frappe.throw",
				side_effect=Exception("sem enunciado"),
			),
			patch(
				"melura_lms.melura_lms.doctype.melura_enem_question.melura_enem_question._",
				side_effect=lambda message, *args, **kwargs: message,
			),
		):
			with self.assertRaisesRegex(Exception, "sem enunciado"):
				doc.validate()

	def test_published_question_requires_correct_option(self):
		doc = self.make_doc(published=1)

		with (
			patch(
				"melura_lms.melura_lms.doctype.melura_enem_question.melura_enem_question.frappe.throw",
				side_effect=Exception("sem gabarito"),
			),
			patch(
				"melura_lms.melura_lms.doctype.melura_enem_question.melura_enem_question._",
				side_effect=lambda message, *args, **kwargs: message,
			),
		):
			with self.assertRaisesRegex(Exception, "sem gabarito"):
				doc.validate()

	def test_validate_sets_published_at_when_published_with_answer(self):
		doc = self.make_doc(published=1, correct_option="A")

		with patch(
			"melura_lms.melura_lms.doctype.melura_enem_question.melura_enem_question.now_datetime",
			return_value="2026-06-01 19:00:00",
		):
			doc.validate()

		self.assertEqual(doc.published_at, "2026-06-01 19:00:00")

	def test_validate_rejects_more_than_one_correct_alternative(self):
		doc = self.make_doc(
			alternatives=[
				frappe._dict(option_label="A", is_correct=1),
				frappe._dict(option_label="B", is_correct=1),
			]
		)

		with (
			patch(
				"melura_lms.melura_lms.doctype.melura_enem_question.melura_enem_question.frappe.throw",
				side_effect=Exception("múltiplas corretas"),
			),
			patch(
				"melura_lms.melura_lms.doctype.melura_enem_question.melura_enem_question._",
				side_effect=lambda message, *args, **kwargs: message,
			),
		):
			with self.assertRaisesRegex(Exception, "múltiplas corretas"):
				doc.validate()

	def test_validate_uses_single_correct_alternative_as_correct_option(self):
		doc = self.make_doc(alternatives=[frappe._dict(option_label="C", is_correct=1)])

		doc.validate()

		self.assertEqual(doc.correct_option, "C")
