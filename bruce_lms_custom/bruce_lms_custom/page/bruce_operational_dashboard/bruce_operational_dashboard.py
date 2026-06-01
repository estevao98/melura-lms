# Copyright (c) 2026, Estevão Oliveira Portes and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import add_to_date, get_datetime, now_datetime


OPERATIONAL_DASHBOARD_ROLES = {
	"System Manager",
	"Administrador LMS",
	"Admin operacional",
	"LMS Admin",
}
STUDENT_ACCESS_STATUSES = ("Pendente", "Ativo", "Bloqueado", "Expirado")
RECENT_ACTIVITY_DAYS = 14
LIVE_CLASS_FIELDS = ["name", "title", "course", "batch", "starts_at", "status", "room_name", "meeting_url"]


@frappe.whitelist()
def get_dashboard_data():
	"""Return aggregated operational data for the admin dashboard."""
	_assert_can_access_operational_dashboard()
	student_access = _get_student_access_summary()
	classes = _get_classes_summary()
	content = _get_content_summary()
	exercises_progress = _get_exercises_progress_summary()

	return {
		"overview": _get_overview(student_access, classes, content, exercises_progress),
		"classes": classes,
		"content": content,
		"exercises_progress": exercises_progress,
		"alerts": _get_operational_alerts(classes, exercises_progress),
	}


def _assert_can_access_operational_dashboard(user=None):
	user = user or frappe.session.user
	if _can_access_operational_dashboard(user):
		return

	frappe.throw(_("Você não tem permissão para acessar o Painel Operacional."), frappe.PermissionError)


def _can_access_operational_dashboard(user=None):
	user = user or frappe.session.user
	if user == "Administrator":
		return True

	if not user or user == "Guest":
		return False

	return bool(set(frappe.get_roles(user)) & OPERATIONAL_DASHBOARD_ROLES)


def _get_overview(student_access, classes, content, exercises_progress):
	return {
		"total_students_with_access": student_access["total_students_with_access"],
		"active_students": student_access["status_counts"]["Ativo"],
		"pending_students": student_access["status_counts"]["Pendente"],
		"blocked_students": student_access["status_counts"]["Bloqueado"],
		"expired_students": student_access["status_counts"]["Expirado"],
		"week_live_classes": classes["week_live_classes"],
		"published_materials": content["published_materials"],
		"published_questions": content["published_questions"],
		"published_exercise_lists": content["published_exercise_lists"],
		"registered_answers": exercises_progress["registered_answers"],
		"average_accuracy": exercises_progress["average_accuracy"],
		"inactive_students": len(exercises_progress["inactive_students"]),
	}


def _get_student_access_summary():
	records = frappe.get_all(
		"Bruce Student Access",
		fields=["student", "access_status"],
		limit_page_length=5000,
	)
	status_counts = {status: 0 for status in STUDENT_ACCESS_STATUSES}
	students = set()

	for record in records:
		student = record.get("student")
		status = record.get("access_status")
		if student:
			students.add(student)
		if status in status_counts:
			status_counts[status] += 1

	return {
		"total_students_with_access": len(students),
		"status_counts": status_counts,
	}


def _get_classes_summary():
	start = now_datetime()
	end = add_to_date(start, days=7)
	week_classes = frappe.get_all(
		"Bruce Live Class",
		filters={
			"status": ["in", ["Agendada", "Ao vivo"]],
			"starts_at": ["between", [start, end]],
		},
		fields=LIVE_CLASS_FIELDS,
		order_by="starts_at asc",
		limit_page_length=100,
	)
	classes_without_room = [
		_with_class_display_values(dict(live_class))
		for live_class in week_classes
		if not live_class.get("room_name") or not live_class.get("meeting_url")
	]

	return {
		"week_live_classes": len(week_classes),
		"upcoming_classes_without_room": classes_without_room,
	}


def _get_content_summary():
	return {
		"published_materials": frappe.db.count("Bruce Educational Material", {"published": 1}),
		"published_questions": frappe.db.count("Bruce ENEM Question", {"published": 1}),
		"published_exercise_lists": frappe.db.count("Bruce Exercise List", {"published": 1}),
	}


def _get_exercises_progress_summary():
	answers = frappe.get_all(
		"Bruce Student Answer",
		fields=["student_user", "is_correct", "answered_at"],
		order_by="answered_at desc",
		limit_page_length=5000,
	)
	registered_answers = len(answers)
	correct_answers = sum(1 for answer in answers if answer.get("is_correct"))
	average_accuracy = round((correct_answers / registered_answers) * 100, 1) if registered_answers else 0

	return {
		"registered_answers": registered_answers,
		"correct_answers": correct_answers,
		"average_accuracy": average_accuracy,
		"inactive_students": _get_inactive_students(answers),
	}


def _get_inactive_students(answers=None):
	active_access_records = frappe.get_all(
		"Bruce Student Access",
		filters={"access_status": "Ativo"},
		fields=["student"],
		limit_page_length=5000,
	)
	active_students = sorted({record.get("student") for record in active_access_records if record.get("student")})
	if not active_students:
		return []

	answers = answers if answers is not None else frappe.get_all(
		"Bruce Student Answer",
		filters={"student_user": ["in", active_students]},
		fields=["student_user", "answered_at"],
		order_by="answered_at desc",
		limit_page_length=5000,
	)
	last_activity_by_student = {}
	for answer in answers:
		student = answer.get("student_user")
		answered_at = answer.get("answered_at")
		if student not in active_students or not answered_at:
			continue

		if student not in last_activity_by_student or get_datetime(answered_at) > get_datetime(last_activity_by_student[student]):
			last_activity_by_student[student] = answered_at

	threshold = get_datetime(add_to_date(now_datetime(), days=-RECENT_ACTIVITY_DAYS))
	inactive_students = []
	for student in active_students:
		last_activity = last_activity_by_student.get(student)
		if last_activity and get_datetime(last_activity) >= threshold:
			continue

		inactive_students.append(
			{
				"student": student,
				"student_name": _get_user_display_name(student),
				"last_activity": last_activity,
			}
		)

	return inactive_students[:20]


def _get_operational_alerts(classes, exercises_progress):
	alerts = []

	if classes["upcoming_classes_without_room"]:
		alerts.append(
			{
				"type": "Aulas",
				"title": "Aulas da semana sem link ou sala",
				"message": f"{len(classes['upcoming_classes_without_room'])} aula(s) precisam de link/sala antes do horário.",
				"severity": "warning",
			}
		)

	if exercises_progress["inactive_students"]:
		alerts.append(
			{
				"type": "Progresso",
				"title": "Alunos ativos sem atividade recente",
				"message": f"{len(exercises_progress['inactive_students'])} aluno(s) ativos não responderam exercícios nos últimos {RECENT_ACTIVITY_DAYS} dias.",
				"severity": "warning",
			}
		)

	if not alerts:
		alerts.append(
			{
				"type": "Operação",
				"title": "Sem alertas operacionais",
				"message": "Nenhuma pendência operacional simples foi identificada agora.",
				"severity": "success",
			}
		)

	return alerts


def _with_class_display_values(live_class):
	live_class["course_title"] = _get_link_title("LMS Course", live_class.get("course"))
	live_class["batch_title"] = _get_link_title("LMS Batch", live_class.get("batch"))
	return live_class


def _get_link_title(doctype, name):
	if not name:
		return None

	try:
		return frappe.db.get_value(doctype, name, "title") or name
	except Exception:
		return name


def _get_user_display_name(user):
	if not user:
		return None

	try:
		return frappe.db.get_value("User", user, "full_name") or user
	except Exception:
		return user
