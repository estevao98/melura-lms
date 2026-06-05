# Copyright (c) 2026, Estevão Oliveira Portes and contributors
# For license information, please see LICENSE

import unittest

from melura_lms.services.routes import (
	MELURA_LIVE_ROOM_ROUTE,
	MELURA_OPERATIONAL_DASHBOARD_ROUTE,
	MELURA_PROFESSOR_DASHBOARD_ROUTE,
	get_desk_route_url,
	get_live_room_route,
)


class TestMeluraRoutes(unittest.TestCase):
	def test_live_room_route_uses_preferred_melura_alias(self):
		self.assertEqual(get_live_room_route("BLC-2026-00017"), "/app/melura-live-room/BLC-2026-00017")

	def test_live_room_route_returns_empty_for_missing_class(self):
		self.assertEqual(get_live_room_route(""), "")

	def test_dashboard_alias_route_urls_use_preferred_melura_aliases(self):
		self.assertEqual(MELURA_LIVE_ROOM_ROUTE, "melura-live-room")
		self.assertEqual(get_desk_route_url(MELURA_PROFESSOR_DASHBOARD_ROUTE), "/app/melura-professor-dashboard")
		self.assertEqual(get_desk_route_url(MELURA_OPERATIONAL_DASHBOARD_ROUTE), "/app/melura-operational-dashboard")
