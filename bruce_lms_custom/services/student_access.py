# Copyright (c) 2026, Estevão Oliveira Portes and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate, today


ACCESS_PENDING = "Pendente"
ACCESS_ACTIVE = "Ativo"
ACCESS_BLOCKED = "Bloqueado"
ACCESS_EXPIRED = "Expirado"

LIVE_CLASS_VISIBLE_STATUSES = ("Agendada", "Ao vivo")
STUDENT_ACCESS_FIELDS = [
	"name",
	"student",
	"access_status",
	"course",
	"batch",
	"starts_on",
	"expires_on",
]
LIVE_CLASS_FIELDS = [
	"name",
	"title",
	"course",
	"batch",
	"starts_at",
	"status",
	"meeting_url",
]
UNRESTRICTED_LIVE_CLASS_ROLES = {"System Manager", "Moderator", "Batch Evaluator", "Course Creator"}


def is_current_student_active():
	"""Return whether the logged user has at least one active pedagogical access scope."""
	return bool(get_active_student_access_records())


def get_current_student_access_status():
	"""Return the highest-priority access status for the logged user."""
	return _get_student_access_status(frappe.session.user)


def can_current_student_access_live_class(live_class):
	"""Return whether the logged student may access the given Bruce Live Class."""
	if isinstance(live_class, str):
		live_class = frappe.get_doc("Bruce Live Class", live_class)

	if not live_class or _get_value(live_class, "status") not in LIVE_CLASS_VISIBLE_STATUSES:
		return False

	return _live_class_matches_any_access(live_class, get_active_student_access_records())


def get_permitted_live_classes_for_current_student(statuses=None, starts_from=None, limit=20):
	"""Return only Bruce Live Class rows allowed for the logged student."""
	statuses = tuple(statuses or LIVE_CLASS_VISIBLE_STATUSES)
	classes_by_name = {}

	for access in get_active_student_access_records():
		filters = {"status": ["in", statuses]}
		if starts_from is not None:
			filters["starts_at"] = [">=", starts_from]

		scope_filter = _get_live_class_scope_filter(access)

		if not scope_filter:
			continue

		filters.update(scope_filter)

		for live_class in frappe.get_all(
			"Bruce Live Class",
			filters=filters,
			fields=LIVE_CLASS_FIELDS,
			order_by="starts_at asc",
			limit_page_length=limit,
		):
			classes_by_name[_get_value(live_class, "name")] = dict(live_class)

	return sorted(classes_by_name.values(), key=lambda live_class: live_class.get("starts_at") or "")[:limit]


def get_active_student_access_records(user=None):
	user = user or frappe.session.user

	if not user or user == "Guest":
		return []

	records = frappe.get_all(
		"Bruce Student Access",
		filters={"student": user},
		fields=STUDENT_ACCESS_FIELDS,
		order_by="modified desc",
	)

	if any(_get_value(record, "access_status") == ACCESS_BLOCKED for record in records):
		return []

	return [
		dict(record)
		for record in records
		if _get_value(record, "access_status") == ACCESS_ACTIVE and _is_access_record_current(record)
	]


def assert_current_student_can_access_live_class(live_class):
	if not is_current_student_active():
		frappe.throw(_("Seu acesso ainda não está ativo. Entre em contato com o suporte."), frappe.PermissionError)

	if not can_current_student_access_live_class(live_class):
		frappe.throw(_("Você não tem acesso a esta aula."), frappe.PermissionError)


def has_live_class_permission(doc, user=None, permission_type=None):
	user = user or frappe.session.user

	if not _should_restrict_student_live_classes(user):
		return True

	if permission_type and permission_type not in {"read", "select"}:
		return False

	return _live_class_matches_any_access(doc, get_active_student_access_records(user))


def get_live_class_permission_query_conditions(user=None):
	user = user or frappe.session.user

	if not _should_restrict_student_live_classes(user):
		return None

	records = get_active_student_access_records(user)
	conditions = [_get_live_class_sql_condition(record) for record in records]
	conditions = [condition for condition in conditions if condition]

	if not conditions:
		return "`tabBruce Live Class`.`name` is null"

	return "(" + " or ".join(conditions) + ")"


def _get_student_access_status(user):
	if not user or user == "Guest":
		return ACCESS_PENDING

	records = frappe.get_all(
		"Bruce Student Access",
		filters={"student": user},
		fields=STUDENT_ACCESS_FIELDS,
		order_by="modified desc",
	)
	statuses = [_get_value(record, "access_status") for record in records]

	if ACCESS_BLOCKED in statuses:
		return ACCESS_BLOCKED

	if any(_get_value(record, "access_status") == ACCESS_ACTIVE and _is_access_record_current(record) for record in records):
		return ACCESS_ACTIVE

	if ACCESS_EXPIRED in statuses or any(_get_value(record, "access_status") == ACCESS_ACTIVE for record in records):
		return ACCESS_EXPIRED

	return ACCESS_PENDING


def _is_access_record_current(record):
	current_date = getdate(today())
	starts_on = record.get("starts_on")
	expires_on = record.get("expires_on")

	if starts_on and getdate(starts_on) > current_date:
		return False

	if expires_on and getdate(expires_on) < current_date:
		return False

	return True


def _live_class_matches_any_access(live_class, access_records):
	return any(_live_class_matches_access(live_class, access) for access in access_records)


def _live_class_matches_access(live_class, access):
	batch = _get_value(live_class, "batch")
	course = _get_value(live_class, "course")

	if access.get("batch"):
		return batch == access.get("batch")

	if access.get("course"):
		return course == access.get("course")

	return False


def _get_live_class_scope_filter(access):
	if access.get("batch"):
		return {"batch": access.get("batch")}

	if access.get("course"):
		return {"course": access.get("course")}

	return None


def _get_live_class_sql_condition(access):
	if access.get("batch"):
		return f"`tabBruce Live Class`.`batch` = {frappe.db.escape(access.get('batch'))}"

	if access.get("course"):
		return f"`tabBruce Live Class`.`course` = {frappe.db.escape(access.get('course'))}"

	return None


def _should_restrict_student_live_classes(user):
	if not user or user == "Guest":
		return True

	roles = set(frappe.get_roles(user))
	if roles & UNRESTRICTED_LIVE_CLASS_ROLES:
		return False

	return "LMS Student" in roles


def _get_value(document_or_dict, fieldname):
	if isinstance(document_or_dict, dict):
		return document_or_dict.get(fieldname)

	return getattr(document_or_dict, fieldname, None)
