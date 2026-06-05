import frappe


RENAME_MAP = (
	("Bruce Live Class", "Melura Live Class"),
	("Bruce Student Access", "Melura Student Access"),
	("Bruce Educational Material", "Melura Educational Material"),
	("Bruce ENEM Question", "Melura ENEM Question"),
	("Bruce ENEM Question Alternative", "Melura ENEM Question Alternative"),
	("Bruce Exercise List", "Melura Exercise List"),
	("Bruce Exercise List Item", "Melura Exercise List Item"),
	("Bruce Student Answer", "Melura Student Answer"),
	("Bruce Evolution Settings", "Melura WhatsApp Settings"),
	("Bruce WhatsApp Message Template", "Melura WhatsApp Message Template"),
	("Bruce WhatsApp Notification Log", "Melura WhatsApp Notification Log"),
	("Bruce Live Class Notice Log", "Melura Live Class Notice Log"),
	("Bruce Jitsi Settings", "Melura Legacy Video Settings"),
)


def execute():
	for old, new in RENAME_MAP:
		if frappe.db.exists("DocType", old) and not frappe.db.exists("DocType", new):
			frappe.rename_doc("DocType", old, new, force=True)
		elif frappe.db.exists("DocType", new):
			continue

	_update_remaining_metadata_references()


def _update_remaining_metadata_references():
	for old, new in RENAME_MAP:
		frappe.db.set_value(
			"DocField",
			{"options": old},
			"options",
			new,
			update_modified=False,
		)
		frappe.db.set_value(
			"Custom Field",
			{"options": old},
			"options",
			new,
			update_modified=False,
		)

	child_parenttype_map = (
		("Melura ENEM Question Alternative", "Bruce ENEM Question", "Melura ENEM Question"),
		("Melura Exercise List Item", "Bruce Exercise List", "Melura Exercise List"),
	)
	for child_doctype, old_parenttype, new_parenttype in child_parenttype_map:
		if frappe.db.table_exists(child_doctype):
			frappe.db.set_value(
				child_doctype,
				{"parenttype": old_parenttype},
				"parenttype",
				new_parenttype,
				update_modified=False,
			)
