# Copyright (c) 2026, Estevão Oliveira Portes and contributors
# For license information, please see LICENSE

import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from bruce_lms_custom.bruce_lms_custom.doctype.bruce_live_class_notice_log.bruce_live_class_notice_log import (
	EVENT_LINK_COPIED,
	STATUS_SUCCESS,
	create_notice_log,
)


class FakeNoticeLog:
	def __init__(self, values):
		self.__dict__.update(values)
		self.name = "BLCN-2026-00001"
		self.insert_called = False

	def insert(self, ignore_permissions=False):
		self.insert_called = True
		self.insert_ignore_permissions = ignore_permissions
		return self


class TestBruceLiveClassNoticeLog(unittest.TestCase):
	def test_create_notice_log_records_live_class_event(self):
		live_class = SimpleNamespace(name="BLC-2026-00001")
		created_logs = []

		def fake_get_doc(values):
			log = FakeNoticeLog(values)
			created_logs.append(log)
			return log

		with (
			patch(
				"bruce_lms_custom.bruce_lms_custom.doctype.bruce_live_class_notice_log.bruce_live_class_notice_log.frappe.get_doc",
				side_effect=fake_get_doc,
			),
			patch(
				"bruce_lms_custom.bruce_lms_custom.doctype.bruce_live_class_notice_log.bruce_live_class_notice_log.frappe.session",
				Mock(user="professor@example.com"),
			),
			patch(
				"bruce_lms_custom.bruce_lms_custom.doctype.bruce_live_class_notice_log.bruce_live_class_notice_log.get_current_datetime",
				return_value="2026-05-31 10:00:00",
			),
		):
			log = create_notice_log(
				live_class,
				EVENT_LINK_COPIED,
				"Link da aula copiado",
				"O link foi copiado pelo usuário.",
				STATUS_SUCCESS,
			)

		self.assertEqual(log.related_live_class, "BLC-2026-00001")
		self.assertEqual(log.event_type, EVENT_LINK_COPIED)
		self.assertEqual(log.status, STATUS_SUCCESS)
		self.assertEqual(log.created_by, "professor@example.com")
		self.assertEqual(log.created_at, "2026-05-31 10:00:00")
		self.assertTrue(created_logs[0].insert_called)
		self.assertTrue(created_logs[0].insert_ignore_permissions)


if __name__ == "__main__":
	unittest.main()
