# Copyright (c) 2026, Estevão Oliveira Portes and contributors
# For license information, please see LICENSE

import unittest
from unittest.mock import Mock, patch

import frappe

from melura_lms.services.cache import (
	CACHE_NAMESPACE,
	build_cache_key,
	build_user_cache_key,
	delete_cached_value,
	get_cached_value,
	get_or_set_cached_value,
	set_cached_value,
)


class FakeCacheBackend:
	def __init__(self):
		self.values = {}
		self.expires = {}
		self.deleted_keys = []

	def get_value(self, key):
		return self.values.get(key)

	def set_value(self, key, value, expires_in_sec=None):
		self.values[key] = value
		self.expires[key] = expires_in_sec

	def delete_value(self, key):
		self.deleted_keys.append(key)
		self.values.pop(key, None)


class TestCacheService(unittest.TestCase):
	def test_cache_key_uses_melura_namespace(self):
		key = build_cache_key("jitsi-settings", "public")

		self.assertEqual(key, f"{CACHE_NAMESPACE}:v1:jitsi-settings:public")

	def test_user_scoped_cache_key_uses_frappe_session_user(self):
		with patch("melura_lms.services.cache.frappe.session", Mock(user="aluno@example.com")):
			key = build_user_cache_key("course", "COURSE-001", "batch", "BATCH-001")

		self.assertEqual(
			key,
			f"{CACHE_NAMESPACE}:v1:user:aluno@example.com:course:COURSE-001:batch:BATCH-001",
		)

	def test_user_scoped_cache_keys_are_different_for_different_users(self):
		with patch("melura_lms.services.cache.frappe.session", Mock(user="aluno-a@example.com")):
			first_key = build_user_cache_key("scope", "COURSE-001")
		with patch("melura_lms.services.cache.frappe.session", Mock(user="aluno-b@example.com")):
			second_key = build_user_cache_key("scope", "COURSE-001")

		self.assertNotEqual(first_key, second_key)
		self.assertIn("aluno-a@example.com", first_key)
		self.assertIn("aluno-b@example.com", second_key)

	def test_user_scoped_cache_key_rejects_guest(self):
		with (
			patch("melura_lms.services.cache.frappe.session", Mock(user="Guest")),
			patch("melura_lms.services.cache.frappe.throw", side_effect=frappe.PermissionError),
			patch("melura_lms.services.cache._", side_effect=lambda value: value),
		):
			with self.assertRaises(frappe.PermissionError):
				build_user_cache_key("dashboard")

	def test_cache_key_rejects_sensitive_token_names(self):
		with (
			patch("melura_lms.services.cache.frappe.throw", side_effect=frappe.ValidationError),
			patch("melura_lms.services.cache._", side_effect=lambda value: value),
		):
			with self.assertRaises(frappe.ValidationError):
				build_cache_key("whatsapp", "api_key")

	def test_cache_wrappers_use_backend_without_requiring_redis(self):
		cache_backend = FakeCacheBackend()
		key = build_cache_key("jitsi-settings", "public")

		self.assertTrue(set_cached_value(key, {"domain": "meet.jit.si"}, expires_in_sec=60, cache_backend=cache_backend))
		self.assertEqual(get_cached_value(key, cache_backend=cache_backend), {"domain": "meet.jit.si"})
		self.assertEqual(cache_backend.expires[key], 60)
		self.assertTrue(delete_cached_value(key, cache_backend=cache_backend))
		self.assertIsNone(get_cached_value(key, cache_backend=cache_backend))

	def test_get_or_set_uses_factory_only_on_cache_miss(self):
		cache_backend = FakeCacheBackend()
		key = build_cache_key("jitsi-settings", "public")
		factory = Mock(return_value={"domain": "meet.jit.si", "room_prefix": "bruce"})

		first_value = get_or_set_cached_value(key, factory, expires_in_sec=60, cache_backend=cache_backend)
		second_value = get_or_set_cached_value(key, factory, expires_in_sec=60, cache_backend=cache_backend)

		self.assertEqual(first_value, {"domain": "meet.jit.si", "room_prefix": "bruce"})
		self.assertEqual(second_value, {"domain": "meet.jit.si", "room_prefix": "bruce"})
		factory.assert_called_once_with()


if __name__ == "__main__":
	unittest.main()
