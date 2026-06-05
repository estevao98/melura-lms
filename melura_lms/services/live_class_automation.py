# Copyright (c) 2026, Estevão Oliveira Portes and contributors
# For license information, please see LICENSE

from datetime import date, datetime, time, timedelta
from urllib.parse import urlparse

import frappe
from frappe import _
from frappe.utils import add_to_date, cint, get_datetime, get_url, now_datetime, today

from melura_lms.melura_lms.doctype.melura_live_class_notice_log.melura_live_class_notice_log import (
	EVENT_INTEGRATION_DISABLED,
	STATUS_WARNING,
	create_notice_log,
)
from melura_lms.services.routes import get_live_room_route
from melura_lms.services import whatsapp


WEEKDAY_INDEX = {
	"Segunda": 0,
	"Terça": 1,
	"Quarta": 2,
	"Quinta": 3,
	"Sexta": 4,
	"Sábado": 5,
	"Domingo": 6,
}

LIVE_CLASS_DOCTYPE = "Melura Live Class"
LIVE_CLASS_SCHEDULE_DOCTYPE = "Melura Live Class Schedule"
STUDENT_ACCESS_DOCTYPE = "Melura Student Access"


def validate_google_meet_url(url):
	value = (url or "").strip()
	parsed = urlparse(value)

	if not value:
		frappe.throw(_("Informe o link do Google Meet."), frappe.ValidationError)

	if parsed.scheme != "https":
		frappe.throw(_("O link do Google Meet deve começar com https://."), frappe.ValidationError)

	if parsed.netloc.lower() != "meet.google.com":
		frappe.throw(_("Use um link válido do Google Meet em meet.google.com."), frappe.ValidationError)

	if not parsed.path or parsed.path == "/":
		frappe.throw(_("Informe um link completo do Google Meet."), frappe.ValidationError)

	return value


def generate_live_classes_from_schedules(today=None):
	base_date = _coerce_date(today) if today else _coerce_date(frappe.utils.today())
	schedules = frappe.get_all(
		LIVE_CLASS_SCHEDULE_DOCTYPE,
		filters={"enabled": 1},
		fields=[
			"name",
			"title",
			"enabled",
			"course",
			"batch",
			"instructor",
			"google_meet_url",
			"weekday",
			"starts_at_time",
			"duration_minutes",
			"generate_days_ahead",
			"notify_minutes_before",
			"professor_notify_minutes_before",
			"auto_send_student_reminder",
			"auto_send_professor_reminder",
		],
	)

	created = []
	for schedule in schedules:
		created.extend(generate_live_classes_for_schedule(schedule, today=base_date))

	return created


def generate_live_classes_for_schedule(schedule, today=None):
	if not _get(schedule, "enabled"):
		return []

	validate_google_meet_url(_get(schedule, "google_meet_url"))
	base_date = _coerce_date(today) if today else _coerce_date(frappe.utils.today())
	days_ahead = _normalize_days_ahead(_get(schedule, "generate_days_ahead"))
	duration_minutes = _normalize_duration(_get(schedule, "duration_minutes"))
	start_time = _coerce_time(_get(schedule, "starts_at_time"))
	target_weekday = WEEKDAY_INDEX.get(_get(schedule, "weekday"))

	if target_weekday is None:
		frappe.throw(_("Informe um dia da semana válido."), frappe.ValidationError)

	created = []
	for offset in range(days_ahead + 1):
		current_date = base_date + timedelta(days=offset)
		if current_date.weekday() != target_weekday:
			continue

		starts_at = datetime.combine(current_date, start_time)
		if find_existing_generated_class(schedule, starts_at):
			continue

		doc = frappe.get_doc(
			{
				"doctype": LIVE_CLASS_DOCTYPE,
				"title": _build_generated_title(schedule, starts_at),
				"status": "Agendada",
				"whatsapp_status": "Não enviado",
				"course": _get(schedule, "course"),
				"batch": _get(schedule, "batch"),
				"instructor": _get(schedule, "instructor"),
				"starts_at": starts_at,
				"ends_at": starts_at + timedelta(minutes=duration_minutes),
				"meeting_url": _get(schedule, "google_meet_url"),
				"auto_generated": 1,
				"generated_from_schedule": _get(schedule, "name"),
				"auto_start_at": starts_at,
			}
		)
		doc.insert(ignore_permissions=True)
		created.append(doc.name)

	_mark_schedule_generated(schedule)
	return created


def find_existing_generated_class(schedule, starts_at):
	return frappe.db.exists(
		LIVE_CLASS_DOCTYPE,
		{
			"generated_from_schedule": _get(schedule, "name"),
			"starts_at": get_datetime(starts_at),
		},
	)


def send_due_live_class_reminders(now=None):
	now_value = get_datetime(now) if now else now_datetime()
	classes = frappe.get_all(
		LIVE_CLASS_DOCTYPE,
		filters={
			"status": ["in", ["Agendada", "Ao vivo"]],
			"meeting_url": ["is", "set"],
			"starts_at": ["<=", add_to_date(now_value, minutes=90)],
		},
		fields=[
			"name",
			"title",
			"course",
			"batch",
			"instructor",
			"starts_at",
			"meeting_url",
			"generated_from_schedule",
			"reminder_sent_at",
			"professor_reminder_sent_at",
		],
	)

	results = []
	for live_class in classes:
		try:
			validate_google_meet_url(_get(live_class, "meeting_url"))
		except Exception:
			results.append({"live_class": _get(live_class, "name"), "status": "invalid_url"})
			continue

		schedule = _get_schedule_for_live_class(live_class)
		if _student_reminder_due(live_class, schedule, now_value):
			results.append(send_student_reminders_for_live_class(live_class))

		if _professor_reminder_due(live_class, schedule, now_value):
			results.append(send_professor_reminder_for_live_class(live_class))

	return results


@frappe.whitelist()
def send_student_reminders_for_live_class(live_class):
	doc = _ensure_live_class_doc(live_class)
	validate_google_meet_url(doc.meeting_url)
	recipients = _filter_active_student_recipients(doc, whatsapp.get_live_class_recipients(doc))
	results = []

	for recipient in recipients:
		message = whatsapp.build_live_class_message(doc, recipient)
		log = whatsapp.create_notification_log(doc, recipient, message)
		results.append(whatsapp.send_logged_message(doc, recipient, message, log))

	if not recipients:
		_record_disabled_or_missing_notice(doc, _("Nenhum aluno ativo com telefone foi encontrado para esta aula."))
		return {"live_class": doc.name, "status": "no_recipients", "sent": False}

	whatsapp.update_live_class_whatsapp_status(doc, results)
	if results and all(result["status"] == "sent" for result in results):
		frappe.db.set_value(LIVE_CLASS_DOCTYPE, doc.name, "reminder_sent_at", now_datetime(), update_modified=True)
		return {"live_class": doc.name, "status": "sent", "sent": True}

	return {"live_class": doc.name, "status": "failed", "sent": False}


@frappe.whitelist()
def send_professor_reminder_for_live_class(live_class):
	doc = _ensure_live_class_doc(live_class)
	validate_google_meet_url(doc.meeting_url)
	contact = _get_user_contact(doc.instructor)
	phone = whatsapp.normalize_phone(contact.get("mobile_no") or contact.get("phone"))

	if not phone:
		_record_disabled_or_missing_notice(doc, _("O professor não possui telefone configurado para receber o lembrete."))
		return {"live_class": doc.name, "status": "missing_professor_phone", "sent": False}

	recipient = {
		"user": doc.instructor,
		"recipient_name": contact.get("full_name") or doc.instructor,
		"phone": phone,
	}
	message = _("Sua aula {aula} começa às {horario}. Link: {link}").format(
		aula=doc.title or "",
		horario=frappe.format(doc.starts_at, {"fieldtype": "Datetime"}) if doc.starts_at else "",
		link=_get_live_class_public_link(doc),
	)
	log = whatsapp.create_notification_log(doc, recipient, message)
	result = whatsapp.send_logged_message(doc, recipient, message, log)

	if result["status"] == "sent":
		frappe.db.set_value(
			LIVE_CLASS_DOCTYPE,
			doc.name,
			"professor_reminder_sent_at",
			now_datetime(),
			update_modified=True,
		)
		return {"live_class": doc.name, "status": "sent", "sent": True}

	return {"live_class": doc.name, "status": "failed", "sent": False}


def _filter_active_student_recipients(live_class, recipients):
	return [recipient for recipient in recipients if _student_has_active_access(live_class, recipient.get("user"))]


def _student_has_active_access(live_class, student):
	if not student:
		return False

	filters = {"student": student, "access_status": "Ativo"}
	scope_filters = []
	if live_class.batch:
		scope_filters.append({**filters, "batch": live_class.batch})
	if live_class.course:
		scope_filters.append({**filters, "course": live_class.course})

	for scope_filter in scope_filters:
		if frappe.db.exists(STUDENT_ACCESS_DOCTYPE, scope_filter):
			return True

	return False


def _get_schedule_for_live_class(live_class):
	schedule_name = _get(live_class, "generated_from_schedule")
	if not schedule_name:
		return None

	try:
		return frappe.get_doc(LIVE_CLASS_SCHEDULE_DOCTYPE, schedule_name)
	except Exception:
		return None


def _student_reminder_due(live_class, schedule, now_value):
	if _get(live_class, "reminder_sent_at"):
		return False
	if schedule and not cint(_get(schedule, "auto_send_student_reminder")):
		return False

	minutes_before = cint(_get(schedule, "notify_minutes_before")) if schedule else 30
	return _is_within_due_window(_get(live_class, "starts_at"), minutes_before, now_value)


def _professor_reminder_due(live_class, schedule, now_value):
	if _get(live_class, "professor_reminder_sent_at"):
		return False
	if schedule and not cint(_get(schedule, "auto_send_professor_reminder")):
		return False

	minutes_before = cint(_get(schedule, "professor_notify_minutes_before")) if schedule else 30
	return _is_within_due_window(_get(live_class, "starts_at"), minutes_before, now_value)


def _is_within_due_window(starts_at, minutes_before, now_value):
	if not starts_at:
		return False

	send_at = get_datetime(starts_at) - timedelta(minutes=max(0, cint(minutes_before)))
	return send_at <= now_value <= get_datetime(starts_at) + timedelta(minutes=15)


def _ensure_live_class_doc(live_class):
	if isinstance(live_class, str):
		return frappe.get_doc(LIVE_CLASS_DOCTYPE, live_class)

	if getattr(live_class, "doctype", None) == LIVE_CLASS_DOCTYPE:
		return live_class

	return frappe.get_doc(LIVE_CLASS_DOCTYPE, _get(live_class, "name"))


def _get_live_class_public_link(live_class):
	try:
		base_url = get_url()
	except Exception:
		base_url = ""

	if base_url:
		return f"{base_url.rstrip('/')}{get_live_room_route(live_class.name)}"

	return live_class.meeting_url


def _get_user_contact(user):
	if not user:
		return {}

	return frappe.db.get_value("User", user, ["full_name", "mobile_no", "phone"], as_dict=True) or {}


def _record_disabled_or_missing_notice(live_class, message):
	create_notice_log(
		live_class,
		EVENT_INTEGRATION_DISABLED,
		_("Lembrete não enviado"),
		message,
		STATUS_WARNING,
	)


def _mark_schedule_generated(schedule):
	name = _get(schedule, "name")
	if name:
		frappe.db.set_value(LIVE_CLASS_SCHEDULE_DOCTYPE, name, "last_generated_at", now_datetime(), update_modified=True)


def _build_generated_title(schedule, starts_at):
	return f"{_get(schedule, 'title') or 'Aula ao vivo'} - {starts_at.strftime('%d/%m/%Y')}"


def _normalize_duration(value):
	duration = cint(value)
	if duration <= 0:
		frappe.throw(_("A duração da aula deve ser maior que zero."), frappe.ValidationError)
	return duration


def _normalize_days_ahead(value):
	days = cint(value) or 14
	if days < 1 or days > 90:
		frappe.throw(_("O período de geração deve ficar entre 1 e 90 dias."), frappe.ValidationError)
	return days


def _coerce_time(value):
	if isinstance(value, time):
		return value
	if isinstance(value, timedelta):
		return (datetime.min + value).time()
	if isinstance(value, str):
		return datetime.strptime(value.split(".")[0], "%H:%M:%S").time()

	frappe.throw(_("Informe um horário de início válido."), frappe.ValidationError)


def _coerce_date(value):
	if isinstance(value, datetime):
		return value.date()
	if isinstance(value, date):
		return value
	return datetime.strptime(str(value), "%Y-%m-%d").date()


def _get(source, fieldname, default=None):
	if isinstance(source, dict):
		return source.get(fieldname, default)
	return getattr(source, fieldname, default)
