# Copyright (c) 2026, Estevão Oliveira Portes and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import now_datetime


LIVE_CLASS_FIELDS = [
	"name",
	"title",
	"course",
	"batch",
	"starts_at",
	"status",
	"whatsapp_status",
	"meeting_url",
]


@frappe.whitelist()
def get_next_live_class():
	"""Return the current live class, or the next scheduled class visible to the user."""
	return _get_next_live_class()


def _get_next_live_class():
	live_class = _get_first_live_class(filters={"status": "Ao vivo"})
	if live_class:
		return live_class

	return _get_first_live_class(
		filters={
			"status": "Agendada",
			"starts_at": [">=", now_datetime()],
		}
	)


def _get_first_live_class(filters):
	classes = frappe.get_list(
		"Bruce Live Class",
		filters=filters,
		fields=LIVE_CLASS_FIELDS,
		order_by="starts_at asc",
		limit_page_length=1,
	)

	if not classes:
		return None

	return dict(classes[0])
