# Copyright (c) 2026, Estevão Oliveira Portes and contributors
# For license information, please see LICENSE

import unittest
from unittest.mock import patch

import frappe

from melura_lms.melura_lms.doctype.melura_educational_material.melura_educational_material import (
	MeluraEducationalMaterial,
)


class TestMeluraEducationalMaterial(unittest.TestCase):
	def make_doc(self, **values):
		doc = object.__new__(MeluraEducationalMaterial)
		doc.title = "Material de teste"
		doc.published = 0
		doc.published_at = None

		for fieldname, value in values.items():
			setattr(doc, fieldname, value)

		return doc

	def test_validate_requires_title(self):
		doc = self.make_doc(title=" ")

		with (
			patch(
				"melura_lms.melura_lms.doctype.melura_educational_material.melura_educational_material.frappe.throw",
				side_effect=Exception("sem título"),
			),
			patch(
				"melura_lms.melura_lms.doctype.melura_educational_material.melura_educational_material._",
				side_effect=lambda message, *args, **kwargs: message,
			),
		):
			with self.assertRaisesRegex(Exception, "sem título"):
				doc.validate()

	def test_validate_sets_published_at_when_published(self):
		doc = self.make_doc(published=1)

		with patch(
			"melura_lms.melura_lms.doctype.melura_educational_material.melura_educational_material.now_datetime",
			return_value="2026-06-01 19:00:00",
		):
			doc.validate()

		self.assertEqual(doc.published_at, "2026-06-01 19:00:00")

	def test_validate_keeps_existing_published_at(self):
		doc = self.make_doc(published=1, published_at="2026-05-31 19:00:00")

		doc.validate()

		self.assertEqual(doc.published_at, "2026-05-31 19:00:00")
