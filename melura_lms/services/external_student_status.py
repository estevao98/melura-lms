# Copyright (c) 2026, Estevão Oliveira Portes and contributors
# For license information, please see LICENSE

import hashlib
import hmac
import json
import os

import frappe
from frappe import _

from melura_lms.services.student_access import (
	ACCESS_ACTIVE,
	ACCESS_BLOCKED,
	ACCESS_EXPIRED,
	ACCESS_PENDING,
)


SECRET_CONFIG_KEYS = (
	"external_student_status_webhook_secret",
	"EXTERNAL_STUDENT_STATUS_WEBHOOK_SECRET",
	"MELURA_EXTERNAL_STUDENT_STATUS_WEBHOOK_SECRET",
)
SECRET_ENV_KEYS = (
	"EXTERNAL_STUDENT_STATUS_WEBHOOK_SECRET",
	"MELURA_EXTERNAL_STUDENT_STATUS_WEBHOOK_SECRET",
)
SIGNATURE_HEADER_NAMES = (
	"X-Melura-Signature",
	"x-melura-signature",
	"X-External-Student-Status-Signature",
	"x-external-student-status-signature",
)
ALLOWED_UPDATE_FIELDS = {"access_status", "source", "external_reference"}
FINANCIAL_PAYLOAD_KEYS = {
	"amount",
	"authorization",
	"bank_account",
	"billing",
	"card",
	"card_data",
	"card_number",
	"checkout",
	"credit_card",
	"currency",
	"customer",
	"customer_data",
	"cvv",
	"invoice",
	"invoice_payload",
	"payment",
	"payment_payload",
	"payments",
	"price",
	"provider_payload",
	"subscription",
	"subscription_payload",
	"token",
	"transaction",
	"transaction_payload",
}
STATUS_MAP = {
	"active": ACCESS_ACTIVE,
	"paid": ACCESS_ACTIVE,
	"approved": ACCESS_ACTIVE,
	"ativo": ACCESS_ACTIVE,
	"pending": ACCESS_PENDING,
	"waiting": ACCESS_PENDING,
	"pendente": ACCESS_PENDING,
	"blocked": ACCESS_BLOCKED,
	"cancelled": ACCESS_BLOCKED,
	"canceled": ACCESS_BLOCKED,
	"suspended": ACCESS_BLOCKED,
	"bloqueado": ACCESS_BLOCKED,
	"expired": ACCESS_EXPIRED,
	"overdue": ACCESS_EXPIRED,
	"ended": ACCESS_EXPIRED,
	"expirado": ACCESS_EXPIRED,
}


@frappe.whitelist(allow_guest=True)
def handle_external_student_status():
	"""Signed webhook endpoint for external pedagogical access status updates."""
	raw_body = _get_request_body()
	signature = _get_request_signature()
	result = process_external_student_status(raw_body=raw_body, signature=signature)

	return {
		"ok": True,
		"status": result["status"],
		"updated": result["updated"],
	}


def process_external_student_status(payload=None, signature=None, raw_body=None):
	"""Verify and process one external student status event."""
	body = raw_body if raw_body is not None else _canonical_payload(payload)
	verify_webhook_signature(body, signature)

	payload = parse_payload(body if raw_body is not None else payload)
	reject_overbroad_financial_payload(payload)

	status = normalize_external_status(payload.get("status") or payload.get("access_status"))
	access = locate_student_access_record(payload)
	updated = update_student_access_record(
		access,
		status,
		external_reference=_get_external_reference(payload),
	)

	return {
		"ok": True,
		"status": status,
		"updated": updated,
	}


def verify_webhook_signature(raw_body, signature, secret=None):
	"""Fail closed unless the configured secret signs the exact request body."""
	secret = secret if secret is not None else get_webhook_secret()

	if not secret:
		frappe.throw(_("Webhook de status externo não configurado."), frappe.PermissionError)

	if not signature:
		frappe.throw(_("Assinatura do webhook ausente."), frappe.PermissionError)

	expected = build_signature(raw_body, secret)
	received = _normalize_signature(signature)

	if not hmac.compare_digest(expected, received):
		frappe.throw(_("Assinatura do webhook inválida."), frappe.PermissionError)

	return True


def build_signature(raw_body, secret):
	body = _body_to_bytes(raw_body)
	return hmac.new(str(secret).encode("utf-8"), body, hashlib.sha256).hexdigest()


def get_webhook_secret():
	for key in SECRET_CONFIG_KEYS:
		value = frappe.conf.get(key)
		if value:
			return value

	for key in SECRET_ENV_KEYS:
		value = os.environ.get(key)
		if value:
			return value

	return None


def normalize_external_status(status):
	value = str(status or "").strip().lower()
	melura_status = STATUS_MAP.get(value)

	if not melura_status:
		frappe.throw(_("Status externo de acesso inválido."), frappe.ValidationError)

	return melura_status


def parse_payload(payload):
	if isinstance(payload, dict):
		return dict(payload)

	if isinstance(payload, bytes):
		payload = payload.decode("utf-8")

	try:
		parsed = json.loads(payload or "{}")
	except Exception:
		frappe.throw(_("Payload de status externo inválido."), frappe.ValidationError)

	if not isinstance(parsed, dict):
		frappe.throw(_("Payload de status externo deve ser um objeto JSON."), frappe.ValidationError)

	return parsed


def reject_overbroad_financial_payload(payload):
	for key in _iter_payload_keys(payload):
		if _normalize_payload_key(key) in FINANCIAL_PAYLOAD_KEYS:
			frappe.throw(_("Payload financeiro não é aceito no Melura LMS."), frappe.ValidationError)

	return True


def locate_student_access_record(payload):
	access_name = _clean_identifier(
		payload.get("bruce_student_access") or payload.get("access_name") or payload.get("student_access")
	)
	external_reference = _get_external_reference(payload)

	if access_name:
		return frappe.get_doc("Bruce Student Access", access_name)

	if external_reference:
		matches = frappe.get_all(
			"Bruce Student Access",
			filters={"external_reference": external_reference},
			fields=["name"],
			limit_page_length=2,
		)

		if len(matches) == 1:
			return frappe.get_doc("Bruce Student Access", matches[0].get("name"))

		if len(matches) > 1:
			frappe.throw(_("Referência externa duplicada para Bruce Student Access."), frappe.ValidationError)

	frappe.throw(_("Informe uma referência segura de Bruce Student Access."), frappe.ValidationError)


def update_student_access_record(access, status, external_reference=None):
	"""Update only the existing access status and opaque integration metadata."""
	before = _snapshot_allowed_fields(access)

	access.access_status = status
	if hasattr(access, "source"):
		access.source = "Integração financeira"
	if external_reference and hasattr(access, "external_reference"):
		access.external_reference = external_reference

	after = _snapshot_allowed_fields(access)
	if before == after:
		return False

	access.save(ignore_permissions=True)
	return True


def _snapshot_allowed_fields(doc):
	return {field: getattr(doc, field, None) for field in ALLOWED_UPDATE_FIELDS}


def _canonical_payload(payload):
	return json.dumps(payload or {}, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _body_to_bytes(raw_body):
	if isinstance(raw_body, bytes):
		return raw_body

	return str(raw_body or "").encode("utf-8")


def _normalize_signature(signature):
	signature = str(signature or "").strip()
	if signature.startswith("sha256="):
		signature = signature.split("=", 1)[1]

	return signature


def _get_request_body():
	request = getattr(frappe, "request", None)
	if not request:
		return b""

	return getattr(request, "data", None) or b""


def _get_request_signature():
	request = getattr(frappe, "request", None)
	headers = getattr(request, "headers", {}) if request else {}

	for name in SIGNATURE_HEADER_NAMES:
		value = headers.get(name) if headers else None
		if value:
			return value

	return None


def _get_external_reference(payload):
	return _clean_identifier(payload.get("external_reference") or payload.get("external_ref"))


def _clean_identifier(value):
	value = str(value or "").strip()
	return value or None


def _iter_payload_keys(value):
	if isinstance(value, dict):
		for key, nested_value in value.items():
			yield key
			yield from _iter_payload_keys(nested_value)
	elif isinstance(value, list):
		for item in value:
			yield from _iter_payload_keys(item)


def _normalize_payload_key(key):
	return str(key or "").strip().lower().replace("-", "_")
