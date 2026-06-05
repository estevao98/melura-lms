app_name = "melura_lms"
app_title = "Melura LMS"
app_publisher = "Estevão Oliveira Portes"
app_description = "Customizações do Frappe LMS para Google Meet, WhatsApp, painel do professor e KPIs"
app_email = "estevao.opmg2@gmail.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "melura_lms",
# 		"logo": "/assets/melura_lms/logo.png",
# 		"title": "Melura LMS",
# 		"route": "/melura_lms",
# 		"has_permission": "melura_lms.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/melura_lms/css/melura_lms.css"
# app_include_js = "/assets/melura_lms/js/melura_lms.js"

# include js, css files in header of web template
# web_include_css = "/assets/melura_lms/css/melura_lms.css"
# web_include_js = "/assets/melura_lms/js/melura_lms.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "melura_lms/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "melura_lms/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "melura_lms.utils.jinja_methods",
# 	"filters": "melura_lms.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "melura_lms.install.before_install"
# after_install = "melura_lms.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "melura_lms.uninstall.before_uninstall"
# after_uninstall = "melura_lms.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "melura_lms.utils.before_app_install"
# after_app_install = "melura_lms.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "melura_lms.utils.before_app_uninstall"
# after_app_uninstall = "melura_lms.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "melura_lms.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

permission_query_conditions = {
	"Melura Live Class": "melura_lms.services.student_access.get_live_class_permission_query_conditions",
	"Melura Educational Material": (
		"melura_lms.services.student_access.get_educational_material_permission_query_conditions"
	),
	"Melura ENEM Question": (
		"melura_lms.services.student_access.get_enem_question_permission_query_conditions"
	),
	"Melura Exercise List": (
		"melura_lms.services.student_access.get_exercise_list_permission_query_conditions"
	),
}

has_permission = {
	"Melura Live Class": "melura_lms.services.student_access.has_live_class_permission",
	"Melura Educational Material": "melura_lms.services.student_access.has_educational_material_permission",
	"Melura ENEM Question": "melura_lms.services.student_access.has_enem_question_permission",
	"Melura Exercise List": "melura_lms.services.student_access.has_exercise_list_permission",
}

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

scheduler_events = {
	"daily": [
		"melura_lms.services.live_class_automation.generate_live_classes_from_schedules",
	],
	"cron": {
		"*/30 * * * *": [
			"melura_lms.services.live_class_automation.send_due_live_class_reminders",
		],
	},
}

# Testing
# -------

# before_tests = "melura_lms.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "melura_lms.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "melura_lms.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["melura_lms.utils.before_request"]
# after_request = ["melura_lms.utils.after_request"]

# Job Events
# ----------
# before_job = ["melura_lms.utils.before_job"]
# after_job = ["melura_lms.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"melura_lms.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []
