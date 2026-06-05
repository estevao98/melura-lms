# Copyright (c) 2026, Estevão Oliveira Portes and contributors
# For license information, please see LICENSE

import unittest
from types import SimpleNamespace
from unittest.mock import patch

from melura_lms.services.external_student_status import (
	build_signature,
	handle_external_student_status,
	normalize_external_status,
	process_external_student_status,
	reject_overbroad_financial_payload,
	update_student_access_record,
	verify_webhook_signature,
)
from melura_lms.services.student_access import (
	ACCESS_ACTIVE,
	ACCESS_BLOCKED,
	ACCESS_EXPIRED,
	ACCESS_PENDING,
)


class FakeAccess:
	def __init__(self):
		self.name = "BSA-2026-00001"
		self.student = "aluno@example.com"
		self.access_status = ACCESS_PENDING
		self.course = "COURSE-001"
		self.batch = "BATCH-001"
		self.starts_on = "2026-01-01"
		self.expires_on = "2026-12-31"
		self.source = "Manual"
		self.external_reference = "ext-access-001"
		self.notes = "Do not change"
		self.save_calls = []

	def save(self, ignore_permissions=False):
		self.save_calls.append({"ignore_permissions": ignore_permissions})
		return self


class TestExternalStudentStatus(unittest.TestCase):
	def signed_payload(self, payload, secret="test-secret"):
		body = '{"access_name":"BSA-2026-00001","external_reference":"ext-access-001","status":"active"}'
		return body, build_signature(body, secret)

	def test_missing_configured_secret_fails_closed(self):
		with (
			patch("melura_lms.services.external_student_status.get_webhook_secret", return_value=None),
		):
			with self.assertRaises(Exception):
				verify_webhook_signature("{}", "signature")

	def test_missing_signature_fails_closed(self):
		with (
			patch("melura_lms.services.external_student_status.get_webhook_secret", return_value="test-secret"),
		):
			with self.assertRaises(Exception):
				verify_webhook_signature("{}", "")

	def test_invalid_signature_fails_closed(self):
		with (
			patch("melura_lms.services.external_student_status.get_webhook_secret", return_value="test-secret"),
		):
			with self.assertRaises(Exception):
				verify_webhook_signature("{}", "wrong")

	def test_valid_payload_maps_status_correctly(self):
		self.assertEqual(normalize_external_status("active"), ACCESS_ACTIVE)
		self.assertEqual(normalize_external_status("paid"), ACCESS_ACTIVE)
		self.assertEqual(normalize_external_status("approved"), ACCESS_ACTIVE)
		self.assertEqual(normalize_external_status("pending"), ACCESS_PENDING)
		self.assertEqual(normalize_external_status("waiting"), ACCESS_PENDING)
		self.assertEqual(normalize_external_status("blocked"), ACCESS_BLOCKED)
		self.assertEqual(normalize_external_status("cancelled"), ACCESS_BLOCKED)
		self.assertEqual(normalize_external_status("suspended"), ACCESS_BLOCKED)
		self.assertEqual(normalize_external_status("expired"), ACCESS_EXPIRED)
		self.assertEqual(normalize_external_status("overdue"), ACCESS_EXPIRED)
		self.assertEqual(normalize_external_status("ended"), ACCESS_EXPIRED)

	def test_unknown_external_status_is_rejected(self):
		with self.assertRaises(Exception):
			normalize_external_status("trialing")

	def test_financial_card_like_payload_fields_are_rejected(self):
		payload = {
			"status": "active",
			"external_reference": "ext-access-001",
			"card": {"last4": "1234"},
		}

		with self.assertRaises(Exception):
			reject_overbroad_financial_payload(payload)

	def test_only_allowed_access_fields_are_updated(self):
		access = FakeAccess()
		original = {
			"student": access.student,
			"course": access.course,
			"batch": access.batch,
			"starts_on": access.starts_on,
			"expires_on": access.expires_on,
			"notes": access.notes,
		}

		updated = update_student_access_record(access, ACCESS_ACTIVE, external_reference="ext-access-002")

		self.assertTrue(updated)
		self.assertEqual(access.access_status, ACCESS_ACTIVE)
		self.assertEqual(access.source, "Integração financeira")
		self.assertEqual(access.external_reference, "ext-access-002")
		self.assertEqual(
			{
				"student": access.student,
				"course": access.course,
				"batch": access.batch,
				"starts_on": access.starts_on,
				"expires_on": access.expires_on,
				"notes": access.notes,
			},
			original,
		)
		self.assertEqual(access.save_calls, [{"ignore_permissions": True}])

	def test_repeated_valid_update_is_idempotent(self):
		access = FakeAccess()
		access.access_status = ACCESS_ACTIVE
		access.source = "Integração financeira"

		updated = update_student_access_record(access, ACCESS_ACTIVE, external_reference="ext-access-001")

		self.assertFalse(updated)
		self.assertEqual(access.save_calls, [])

	def test_process_valid_payload_updates_record_and_returns_minimal_response(self):
		access = FakeAccess()
		body, signature = self.signed_payload({})

		with (
			patch("melura_lms.services.external_student_status.get_webhook_secret", return_value="test-secret"),
			patch("melura_lms.services.external_student_status.frappe.get_doc", return_value=access),
		):
			result = process_external_student_status(raw_body=body, signature=signature)

		self.assertEqual(result, {"ok": True, "status": ACCESS_ACTIVE, "updated": True})
		self.assertEqual(access.access_status, ACCESS_ACTIVE)

	def test_response_does_not_expose_secret(self):
		body, signature = self.signed_payload({})
		access = FakeAccess()
		request = SimpleNamespace(data=body.encode("utf-8"), headers={"X-Melura-Signature": signature})

		with (
			patch("melura_lms.services.external_student_status.get_webhook_secret", return_value="test-secret"),
			patch("melura_lms.services.external_student_status.frappe.request", request),
			patch("melura_lms.services.external_student_status.frappe.get_doc", return_value=access),
		):
			result = handle_external_student_status.__wrapped__()

		self.assertEqual(result, {"ok": True, "status": ACCESS_ACTIVE, "updated": True})
		self.assertNotIn("test-secret", str(result))
		self.assertNotIn(signature, str(result))

	def test_frontend_cannot_directly_decide_status_without_signature(self):
		with (
			patch("melura_lms.services.external_student_status.get_webhook_secret", return_value="test-secret"),
			patch("melura_lms.services.external_student_status.frappe.get_doc") as get_doc,
		):
			with self.assertRaises(Exception):
				process_external_student_status(
					payload={
						"access_name": "BSA-2026-00001",
						"status": "active",
						"external_reference": "ext-access-001",
					}
				)

		get_doc.assert_not_called()

	def test_locates_record_by_external_reference(self):
		access = FakeAccess()
		body = '{"external_reference":"ext-access-001","status":"expired"}'
		signature = build_signature(body, "test-secret")

		with (
			patch("melura_lms.services.external_student_status.get_webhook_secret", return_value="test-secret"),
			patch(
				"melura_lms.services.external_student_status.frappe.get_all",
				return_value=[{"name": "BSA-2026-00001"}],
			) as get_all,
			patch("melura_lms.services.external_student_status.frappe.get_doc", return_value=access) as get_doc,
		):
			result = process_external_student_status(raw_body=body, signature=signature)

		get_all.assert_called_once_with(
			"Melura Student Access",
			filters={"external_reference": "ext-access-001"},
			fields=["name"],
			limit_page_length=2,
		)
		get_doc.assert_called_once_with("Melura Student Access", "BSA-2026-00001")
		self.assertEqual(result["status"], ACCESS_EXPIRED)


if __name__ == "__main__":
	unittest.main()
