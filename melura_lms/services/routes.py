# Copyright (c) 2026, Estevão Oliveira Portes and contributors
# For license information, please see LICENSE

"""Preferred Melura Desk routes for user-facing links."""


MELURA_LIVE_ROOM_ROUTE = "melura-live-room"
MELURA_PROFESSOR_DASHBOARD_ROUTE = "melura-professor-dashboard"
MELURA_OPERATIONAL_DASHBOARD_ROUTE = "melura-operational-dashboard"


def get_live_room_route(live_class_name):
	if not live_class_name:
		return ""

	return f"/app/{MELURA_LIVE_ROOM_ROUTE}/{live_class_name}"


def get_desk_route_url(route_name):
	if not route_name:
		return ""

	return f"/app/{route_name}"
