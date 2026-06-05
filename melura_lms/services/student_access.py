# Copyright (c) 2026, Estevão Oliveira Portes and contributors
# For license information, please see LICENSE

import frappe
from frappe import _
from frappe.utils import add_to_date, get_datetime, getdate, now_datetime, today


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
EDUCATIONAL_MATERIAL_FIELDS = [
	"name",
	"title",
	"material_type",
	"course",
	"batch",
	"related_live_class",
	"topic",
	"pdf_file",
	"published_at",
	"description",
]
ENEM_QUESTION_FIELDS = [
	"name",
	"title",
	"statement",
	"discipline",
	"topic",
	"competence",
	"skill",
	"year",
	"difficulty",
	"source",
	"related_course",
	"related_batch",
	"related_live_class",
	"related_material",
	"published_at",
]
ENEM_QUESTION_ALTERNATIVE_FIELDS = [
	"name",
	"parent",
	"option_label",
	"option_text",
]
EXERCISE_LIST_FIELDS = [
	"name",
	"title",
	"course",
	"batch",
	"related_live_class",
	"related_material",
	"published_at",
	"due_date",
	"description",
]
EXERCISE_LIST_ITEM_FIELDS = [
	"name",
	"parent",
	"question",
	"order",
	"points",
]
UNRESTRICTED_LIVE_CLASS_ROLES = {"System Manager", "Moderator", "Batch Evaluator", "Course Creator"}
PROGRESS_MANAGER_ROLES = {
	"System Manager",
	"Moderator",
	"Batch Evaluator",
	"Course Creator",
	"Professor",
	"Administrador LMS",
	"LMS Admin",
}
RECENT_ACTIVITY_DAYS = 14


def is_current_student_active():
	"""Return whether the logged user has at least one active pedagogical access scope."""
	return bool(get_active_student_access_records())


def get_current_student_access_status():
	"""Return the highest-priority access status for the logged user."""
	return _get_student_access_status(frappe.session.user)


def can_current_student_access_live_class(live_class):
	"""Return whether the logged student may access the given live class."""
	if isinstance(live_class, str):
		live_class = frappe.get_doc("Melura Live Class", live_class)

	if not live_class or _get_value(live_class, "status") not in LIVE_CLASS_VISIBLE_STATUSES:
		return False

	return _live_class_matches_any_access(live_class, get_active_student_access_records())


def get_permitted_live_classes_for_current_student(statuses=None, starts_from=None, limit=20):
	"""Return only live class rows allowed for the logged student."""
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
			"Melura Live Class",
			filters=filters,
			fields=LIVE_CLASS_FIELDS,
			order_by="starts_at asc",
			limit_page_length=limit,
		):
			classes_by_name[_get_value(live_class, "name")] = dict(live_class)

	return sorted(classes_by_name.values(), key=lambda live_class: live_class.get("starts_at") or "")[:limit]


def get_permitted_educational_materials_for_current_student(limit=10):
	"""Return only published materials allowed for the logged student."""
	materials_by_name = {}

	for access in get_active_student_access_records():
		scope_filters = _get_material_scope_filters(access)

		if not scope_filters:
			continue

		for scope_filter in scope_filters:
			filters = {
				"published": 1,
				"visibility": "Aluno",
			}
			filters.update(scope_filter)

			for material in frappe.get_all(
				"Melura Educational Material",
				filters=filters,
				fields=EDUCATIONAL_MATERIAL_FIELDS,
				order_by="published_at desc, modified desc",
				limit_page_length=limit,
			):
				materials_by_name[_get_value(material, "name")] = dict(material)

	return sorted(
		materials_by_name.values(),
		key=lambda material: material.get("published_at") or "",
		reverse=True,
	)[:limit]


def get_permitted_exercise_lists_for_current_student(limit=10):
	"""Return only published exercise lists allowed for the logged student."""
	limit = _normalize_list_limit(limit, default=10, maximum=50)
	return _get_permitted_exercise_lists(get_active_student_access_records(), limit=limit)


@frappe.whitelist()
def get_progress_for_current_student():
	"""Return progress metrics for the logged student only."""
	student = frappe.session.user
	progress = _get_student_progress(student)

	if progress.get("access_status") != ACCESS_ACTIVE:
		return _locked_student_progress(progress.get("access_status"))

	return progress


@frappe.whitelist()
def get_class_progress_summary(batch=None, course=None, limit=50):
	"""Return a simple progress summary for a permitted class/course scope."""
	_assert_can_manage_progress()

	if not batch and not course:
		frappe.throw(_("Informe uma turma ou curso para consultar o progresso."), frappe.ValidationError)

	limit = _normalize_list_limit(limit, default=50, maximum=100)
	access_filters = {}
	if batch:
		access_filters["batch"] = batch
	elif course:
		access_filters["course"] = course

	access_records = frappe.get_all(
		"Melura Student Access",
		filters=access_filters,
		fields=STUDENT_ACCESS_FIELDS,
		order_by="student asc, modified desc",
		limit_page_length=limit * 4,
	)
	students = []
	access_by_student = {}

	for record in access_records:
		student = _get_value(record, "student")
		if not student:
			continue

		if student not in access_by_student:
			students.append(student)
			access_by_student[student] = []

		access_by_student[student].append(dict(record))

	rows = []
	for student in students[:limit]:
		progress = _get_student_progress(student, access_records=access_by_student.get(student))
		progress["student"] = student
		progress["student_name"] = _get_user_display_name(student)
		rows.append(progress)

	return {
		"batch": batch,
		"course": course,
		"total_students": len(rows),
		"students": rows,
	}


def get_progress_summary_for_scope(batch=None, course=None, limit=50):
	"""Internal helper used by trusted backend pages after role validation."""
	if not _can_manage_progress() or (not batch and not course):
		return {
			"batch": batch,
			"course": course,
			"total_students": 0,
			"students": [],
		}

	return get_class_progress_summary(batch=batch, course=course, limit=limit)


def _get_permitted_exercise_lists(access_records, limit=10):
	exercise_lists_by_name = {}

	for access in access_records:
		scope_filters = _get_exercise_list_scope_filters(access)

		if not scope_filters:
			continue

		for scope_filter in scope_filters:
			filters = {"published": 1}
			filters.update(scope_filter)

			for exercise_list in frappe.get_all(
				"Melura Exercise List",
				filters=filters,
				fields=EXERCISE_LIST_FIELDS,
				order_by="published_at desc, modified desc",
				limit_page_length=limit,
			):
				exercise_lists_by_name[_get_value(exercise_list, "name")] = dict(exercise_list)

	exercise_lists = sorted(
		exercise_lists_by_name.values(),
		key=lambda exercise_list: exercise_list.get("published_at") or "",
		reverse=True,
	)[:limit]

	_add_exercise_list_question_counts(exercise_lists)
	return exercise_lists


def _get_student_progress(student, access_records=None):
	access_status = _get_student_access_status(student)
	active_access_records = (
		_get_active_records_from_access_records(access_records)
		if access_records is not None
		else get_active_student_access_records(student)
	)

	if access_status != ACCESS_ACTIVE or not active_access_records:
		return _locked_student_progress(access_status)

	available_lists = _get_permitted_exercise_lists(active_access_records, limit=100)
	available_list_names = [exercise_list.get("name") for exercise_list in available_lists if exercise_list.get("name")]
	answers = _get_student_answers_for_lists(student, available_list_names)

	total_answered = len(answers)
	total_correct = sum(1 for answer in answers if bool(_get_value(answer, "is_correct")))
	total_errors = total_answered - total_correct
	accuracy_percentage = round((total_correct / total_answered) * 100, 2) if total_answered else 0
	last_activity = _get_last_activity(answers)

	return {
		"student": student,
		"access_status": access_status,
		"total_available_lists": len(available_list_names),
		"answered_lists": len({_get_value(answer, "exercise_list") for answer in answers if _get_value(answer, "exercise_list")}),
		"total_answered_questions": total_answered,
		"total_correct": total_correct,
		"total_errors": total_errors,
		"accuracy_percentage": accuracy_percentage,
		"last_activity": last_activity,
		"is_recently_active": _is_recently_active(last_activity),
		"recent_activity_days": RECENT_ACTIVITY_DAYS,
		"locked": False,
	}


def _locked_student_progress(access_status):
	return {
		"access_status": access_status or ACCESS_PENDING,
		"total_available_lists": 0,
		"answered_lists": 0,
		"total_answered_questions": 0,
		"total_correct": 0,
		"total_errors": 0,
		"accuracy_percentage": 0,
		"last_activity": None,
		"is_recently_active": False,
		"recent_activity_days": RECENT_ACTIVITY_DAYS,
		"locked": True,
	}


@frappe.whitelist()
def get_permitted_enem_questions_for_current_student(limit=20):
	"""Return only published ENEM questions allowed for the logged student.

	The returned payload intentionally omits the answer key and commented resolution.
	"""
	limit = _normalize_list_limit(limit, default=20, maximum=50)
	questions_by_name = {}

	for access in get_active_student_access_records():
		scope_filters = _get_question_scope_filters(access)

		if not scope_filters:
			continue

		for scope_filter in scope_filters:
			filters = {"published": 1}
			filters.update(scope_filter)

			for question in frappe.get_all(
				"Melura ENEM Question",
				filters=filters,
				fields=ENEM_QUESTION_FIELDS,
				order_by="published_at desc, modified desc",
				limit_page_length=limit,
			):
				questions_by_name[_get_value(question, "name")] = _sanitize_question_for_student(question)

	questions = sorted(
		questions_by_name.values(),
		key=lambda question: question.get("published_at") or "",
		reverse=True,
	)[:limit]

	_add_visible_question_alternatives(questions)
	return questions


@frappe.whitelist()
def get_exercise_list_for_current_student(exercise_list):
	"""Return a published exercise list and its questions for the logged student."""
	if not exercise_list:
		frappe.throw(_("Informe a lista de exercícios."), frappe.ValidationError)

	doc = frappe.get_doc("Melura Exercise List", exercise_list)
	assert_current_student_can_access_exercise_list(doc)

	items = _get_exercise_list_items(doc.name)
	questions = _get_visible_questions_for_exercise_items(items)

	return {
		"name": doc.name,
		"title": doc.title,
		"course": doc.course,
		"batch": doc.batch,
		"related_live_class": doc.related_live_class,
		"related_material": doc.related_material,
		"published_at": doc.published_at,
		"due_date": doc.due_date,
		"description": doc.description,
		"question_count": len(items),
		"questions": questions,
	}


@frappe.whitelist()
def save_student_answer(exercise_list, question, selected_option):
	"""Save or update the current student's answer after backend access validation."""
	if not selected_option:
		frappe.throw(_("Selecione uma alternativa."), frappe.ValidationError)

	selected_option = str(selected_option).strip().upper()
	if selected_option not in {"A", "B", "C", "D", "E"}:
		frappe.throw(_("Alternativa inválida."), frappe.ValidationError)

	if not is_current_student_active():
		frappe.throw(_("Seu acesso ainda não está ativo. Entre em contato com o suporte."), frappe.PermissionError)

	doc = frappe.get_doc("Melura Exercise List", exercise_list)
	assert_current_student_can_access_exercise_list(doc)

	if not _exercise_list_contains_question(doc.name, question):
		frappe.throw(_("Esta questão não pertence à lista informada."), frappe.PermissionError)

	correct_option = frappe.db.get_value("Melura ENEM Question", question, "correct_option")
	if not correct_option:
		frappe.throw(_("A questão ainda não possui gabarito cadastrado."), frappe.ValidationError)

	answer_name = frappe.db.get_value(
		"Melura Student Answer",
		{
			"exercise_list": doc.name,
			"question": question,
			"student_user": frappe.session.user,
		},
		"name",
	)
	answer_doc = frappe.get_doc("Melura Student Answer", answer_name) if answer_name else frappe.new_doc("Melura Student Answer")
	answer_doc.exercise_list = doc.name
	answer_doc.question = question
	answer_doc.student_user = frappe.session.user
	answer_doc.selected_option = selected_option
	answer_doc.is_correct = selected_option == correct_option
	answer_doc.answered_at = now_datetime()

	if answer_name:
		answer_doc.save(ignore_permissions=True)
	else:
		answer_doc.insert(ignore_permissions=True)

	return {
		"name": answer_doc.name,
		"is_correct": bool(answer_doc.is_correct),
		"selected_option": answer_doc.selected_option,
		"answered_at": answer_doc.answered_at,
	}


def get_active_student_access_records(user=None):
	user = user or frappe.session.user

	if not user or user == "Guest":
		return []

	records = frappe.get_all(
		"Melura Student Access",
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


def assert_current_student_can_access_exercise_list(exercise_list):
	if not is_current_student_active():
		frappe.throw(_("Seu acesso ainda não está ativo. Entre em contato com o suporte."), frappe.PermissionError)

	if not _exercise_list_is_student_visible(exercise_list):
		frappe.throw(_("Esta lista de exercícios não está publicada."), frappe.PermissionError)

	if not _exercise_list_matches_any_access(exercise_list, get_active_student_access_records()):
		frappe.throw(_("Você não tem acesso a esta lista de exercícios."), frappe.PermissionError)


def has_live_class_permission(doc, user=None, permission_type=None):
	user = user or frappe.session.user

	if not _should_restrict_student_live_classes(user):
		return True

	if permission_type and permission_type not in {"read", "select"}:
		return False

	return _live_class_matches_any_access(doc, get_active_student_access_records(user))


def has_educational_material_permission(doc, user=None, permission_type=None):
	user = user or frappe.session.user

	if not _should_restrict_student_live_classes(user):
		return True

	if permission_type and permission_type not in {"read", "select"}:
		return False

	if not _material_is_student_visible(doc):
		return False

	return _material_matches_any_access(doc, get_active_student_access_records(user))


def has_enem_question_permission(doc, user=None, permission_type=None):
	user = user or frappe.session.user

	if not _should_restrict_student_live_classes(user):
		return True

	if permission_type and permission_type not in {"read", "select"}:
		return False

	if not _question_is_student_visible(doc):
		return False

	return _question_matches_any_access(doc, get_active_student_access_records(user))


def has_exercise_list_permission(doc, user=None, permission_type=None):
	user = user or frappe.session.user

	if not _should_restrict_student_live_classes(user):
		return True

	if permission_type and permission_type not in {"read", "select"}:
		return False

	if not _exercise_list_is_student_visible(doc):
		return False

	return _exercise_list_matches_any_access(doc, get_active_student_access_records(user))


def get_live_class_permission_query_conditions(user=None):
	user = user or frappe.session.user

	if not _should_restrict_student_live_classes(user):
		return None

	records = get_active_student_access_records(user)
	conditions = [_get_live_class_sql_condition(record) for record in records]
	conditions = [condition for condition in conditions if condition]

	if not conditions:
		return "`tabMelura Live Class`.`name` is null"

	return "(" + " or ".join(conditions) + ")"


def get_educational_material_permission_query_conditions(user=None):
	user = user or frappe.session.user

	if not _should_restrict_student_live_classes(user):
		return None

	records = get_active_student_access_records(user)
	conditions = [_get_material_sql_condition(record) for record in records]
	conditions = [condition for condition in conditions if condition]

	if not conditions:
		return "`tabMelura Educational Material`.`name` is null"

	return (
		"`tabMelura Educational Material`.`published` = 1"
		" and `tabMelura Educational Material`.`visibility` = 'Aluno'"
		" and (" + " or ".join(conditions) + ")"
	)


def get_enem_question_permission_query_conditions(user=None):
	user = user or frappe.session.user

	if not _should_restrict_student_live_classes(user):
		return None

	records = get_active_student_access_records(user)
	conditions = [_get_question_sql_condition(record) for record in records]
	conditions = [condition for condition in conditions if condition]

	if not conditions:
		return "`tabMelura ENEM Question`.`name` is null"

	return "`tabMelura ENEM Question`.`published` = 1 and (" + " or ".join(conditions) + ")"


def get_exercise_list_permission_query_conditions(user=None):
	user = user or frappe.session.user

	if not _should_restrict_student_live_classes(user):
		return None

	records = get_active_student_access_records(user)
	conditions = [_get_exercise_list_sql_condition(record) for record in records]
	conditions = [condition for condition in conditions if condition]

	if not conditions:
		return "`tabMelura Exercise List`.`name` is null"

	return "`tabMelura Exercise List`.`published` = 1 and (" + " or ".join(conditions) + ")"


def _get_student_access_status(user):
	if not user or user == "Guest":
		return ACCESS_PENDING

	records = frappe.get_all(
		"Melura Student Access",
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


def _get_active_records_from_access_records(records):
	if not records:
		return []

	if any(_get_value(record, "access_status") == ACCESS_BLOCKED for record in records):
		return []

	return [
		dict(record)
		for record in records
		if _get_value(record, "access_status") == ACCESS_ACTIVE and _is_access_record_current(record)
	]


def _get_student_answers_for_lists(student, exercise_lists):
	if not student or not exercise_lists:
		return []

	return [
		dict(answer)
		for answer in frappe.get_all(
			"Melura Student Answer",
			filters={
				"student_user": student,
				"exercise_list": ["in", exercise_lists],
			},
			fields=["exercise_list", "question", "is_correct", "answered_at"],
			order_by="answered_at asc",
			limit_page_length=5000,
		)
	]


def _get_last_activity(answers):
	answered_at_values = [_get_value(answer, "answered_at") for answer in answers if _get_value(answer, "answered_at")]

	if not answered_at_values:
		return None

	return max(answered_at_values)


def _is_recently_active(last_activity):
	if not last_activity:
		return False

	try:
		threshold = get_datetime(add_to_date(now_datetime(), days=-RECENT_ACTIVITY_DAYS))
		return get_datetime(last_activity) >= threshold
	except Exception:
		return False


def _get_user_display_name(user):
	if not user:
		return None

	try:
		return frappe.db.get_value("User", user, "full_name") or user
	except Exception:
		return user


def _assert_can_manage_progress():
	if not _can_manage_progress():
		frappe.throw(_("Você não tem permissão para consultar progresso de turma."), frappe.PermissionError)


def _can_manage_progress(user=None):
	user = user or frappe.session.user
	if not user or user == "Guest":
		return False

	return bool(set(frappe.get_roles(user)) & PROGRESS_MANAGER_ROLES)


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


def _material_matches_any_access(material, access_records):
	return any(_material_matches_access(material, access) for access in access_records)


def _question_matches_any_access(question, access_records):
	return any(_question_matches_access(question, access) for access in access_records)


def _exercise_list_matches_any_access(exercise_list, access_records):
	return any(_exercise_list_matches_access(exercise_list, access) for access in access_records)


def _live_class_matches_access(live_class, access):
	batch = _get_value(live_class, "batch")
	course = _get_value(live_class, "course")

	if access.get("batch"):
		return batch == access.get("batch")

	if access.get("course"):
		return course == access.get("course")

	return False


def _material_matches_access(material, access):
	batch = _get_value(material, "batch")
	course = _get_value(material, "course")

	if batch:
		if access.get("batch"):
			return batch == access.get("batch")

		return bool(access.get("course") and course == access.get("course"))

	if course:
		return course == access.get("course")

	return False


def _question_matches_access(question, access):
	batch = _get_value(question, "related_batch")
	course = _get_value(question, "related_course")

	if batch:
		if access.get("batch"):
			return batch == access.get("batch")

		return bool(access.get("course") and course == access.get("course"))

	if course:
		return course == access.get("course")

	return False


def _exercise_list_matches_access(exercise_list, access):
	batch = _get_value(exercise_list, "batch")
	course = _get_value(exercise_list, "course")

	if batch:
		if access.get("batch"):
			return batch == access.get("batch")

		return bool(access.get("course") and course == access.get("course"))

	if course:
		return course == access.get("course")

	return False


def _get_live_class_scope_filter(access):
	if access.get("batch"):
		return {"batch": access.get("batch")}

	if access.get("course"):
		return {"course": access.get("course")}

	return None


def _get_material_scope_filters(access):
	if access.get("batch") and access.get("course"):
		return [
			{"batch": access.get("batch")},
			{
				"course": access.get("course"),
				"batch": ["in", ("", None)],
			},
		]

	if access.get("batch"):
		return [{"batch": access.get("batch")}]

	if access.get("course"):
		return [{"course": access.get("course")}]

	return []


def _get_question_scope_filters(access):
	if access.get("batch") and access.get("course"):
		return [
			{"related_batch": access.get("batch")},
			{
				"related_course": access.get("course"),
				"related_batch": ["in", ("", None)],
			},
		]

	if access.get("batch"):
		return [{"related_batch": access.get("batch")}]

	if access.get("course"):
		return [{"related_course": access.get("course")}]

	return []


def _get_exercise_list_scope_filters(access):
	if access.get("batch") and access.get("course"):
		return [
			{"batch": access.get("batch")},
			{
				"course": access.get("course"),
				"batch": ["in", ("", None)],
			},
		]

	if access.get("batch"):
		return [{"batch": access.get("batch")}]

	if access.get("course"):
		return [{"course": access.get("course")}]

	return []


def _get_live_class_sql_condition(access):
	if access.get("batch"):
		return f"`tabMelura Live Class`.`batch` = {frappe.db.escape(access.get('batch'))}"

	if access.get("course"):
		return f"`tabMelura Live Class`.`course` = {frappe.db.escape(access.get('course'))}"

	return None


def _get_material_sql_condition(access):
	if access.get("batch") and access.get("course"):
		return (
			f"`tabMelura Educational Material`.`batch` = {frappe.db.escape(access.get('batch'))}"
			" or ("
			f"`tabMelura Educational Material`.`course` = {frappe.db.escape(access.get('course'))}"
			" and ifnull(`tabMelura Educational Material`.`batch`, '') = ''"
			")"
		)

	if access.get("batch"):
		return f"`tabMelura Educational Material`.`batch` = {frappe.db.escape(access.get('batch'))}"

	if access.get("course"):
		return f"`tabMelura Educational Material`.`course` = {frappe.db.escape(access.get('course'))}"

	return None


def _get_question_sql_condition(access):
	if access.get("batch") and access.get("course"):
		return (
			f"`tabMelura ENEM Question`.`related_batch` = {frappe.db.escape(access.get('batch'))}"
			" or ("
			f"`tabMelura ENEM Question`.`related_course` = {frappe.db.escape(access.get('course'))}"
			" and ifnull(`tabMelura ENEM Question`.`related_batch`, '') = ''"
			")"
		)

	if access.get("batch"):
		return f"`tabMelura ENEM Question`.`related_batch` = {frappe.db.escape(access.get('batch'))}"

	if access.get("course"):
		return f"`tabMelura ENEM Question`.`related_course` = {frappe.db.escape(access.get('course'))}"

	return None


def _get_exercise_list_sql_condition(access):
	if access.get("batch") and access.get("course"):
		return (
			f"`tabMelura Exercise List`.`batch` = {frappe.db.escape(access.get('batch'))}"
			" or ("
			f"`tabMelura Exercise List`.`course` = {frappe.db.escape(access.get('course'))}"
			" and ifnull(`tabMelura Exercise List`.`batch`, '') = ''"
			")"
		)

	if access.get("batch"):
		return f"`tabMelura Exercise List`.`batch` = {frappe.db.escape(access.get('batch'))}"

	if access.get("course"):
		return f"`tabMelura Exercise List`.`course` = {frappe.db.escape(access.get('course'))}"

	return None


def _material_is_student_visible(material):
	return (
		bool(_get_value(material, "published"))
		and _get_value(material, "visibility") == "Aluno"
	)


def _question_is_student_visible(question):
	return bool(_get_value(question, "published"))


def _exercise_list_is_student_visible(exercise_list):
	return bool(_get_value(exercise_list, "published"))


def _add_visible_question_alternatives(questions):
	if not questions:
		return

	question_names = [question.get("name") for question in questions if question.get("name")]
	alternatives_by_question = {name: [] for name in question_names}

	for alternative in frappe.get_all(
		"Melura ENEM Question Alternative",
		filters={
			"parent": ["in", question_names],
			"parenttype": "Melura ENEM Question",
		},
		fields=ENEM_QUESTION_ALTERNATIVE_FIELDS,
		order_by="parent asc, idx asc",
	):
		alternatives_by_question.setdefault(_get_value(alternative, "parent"), []).append(
			{
				"option_label": _get_value(alternative, "option_label"),
				"option_text": _get_value(alternative, "option_text"),
			}
		)

	for question in questions:
		question["alternatives"] = alternatives_by_question.get(question.get("name"), [])


def _sanitize_question_for_student(question):
	return {fieldname: _get_value(question, fieldname) for fieldname in ENEM_QUESTION_FIELDS}


def _add_exercise_list_question_counts(exercise_lists):
	if not exercise_lists:
		return

	exercise_list_names = [exercise_list.get("name") for exercise_list in exercise_lists if exercise_list.get("name")]
	counts = {name: 0 for name in exercise_list_names}

	for item in frappe.get_all(
		"Melura Exercise List Item",
		filters={
			"parent": ["in", exercise_list_names],
			"parenttype": "Melura Exercise List",
		},
		fields=["parent"],
	):
		counts[_get_value(item, "parent")] = counts.get(_get_value(item, "parent"), 0) + 1

	for exercise_list in exercise_lists:
		exercise_list["question_count"] = counts.get(exercise_list.get("name"), 0)


def _get_exercise_list_items(exercise_list):
	return [
		dict(item)
		for item in frappe.get_all(
			"Melura Exercise List Item",
			filters={
				"parent": exercise_list,
				"parenttype": "Melura Exercise List",
			},
			fields=EXERCISE_LIST_ITEM_FIELDS,
			order_by="`order` asc, idx asc",
		)
	]


def _get_visible_questions_for_exercise_items(items):
	if not items:
		return []

	question_names = [item.get("question") for item in items if item.get("question")]
	questions_by_name = {}

	for question in frappe.get_all(
		"Melura ENEM Question",
		filters={
			"name": ["in", question_names],
			"published": 1,
		},
		fields=ENEM_QUESTION_FIELDS,
	):
		questions_by_name[_get_value(question, "name")] = _sanitize_question_for_student(question)

	questions = []
	for item in items:
		question = questions_by_name.get(item.get("question"))
		if not question:
			continue

		question["order"] = item.get("order")
		question["points"] = item.get("points")
		questions.append(question)

	_add_visible_question_alternatives(questions)
	return questions


def _exercise_list_contains_question(exercise_list, question):
	if not exercise_list or not question:
		return False

	return bool(
		frappe.db.exists(
			"Melura Exercise List Item",
			{
				"parent": exercise_list,
				"parenttype": "Melura Exercise List",
				"question": question,
			},
		)
	)


def _normalize_list_limit(limit, default=20, maximum=50):
	try:
		normalized_limit = int(limit)
	except (TypeError, ValueError):
		return default

	if normalized_limit < 1:
		return default

	return min(normalized_limit, maximum)


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
