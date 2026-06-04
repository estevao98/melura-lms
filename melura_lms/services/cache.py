# Copyright (c) 2026, Estevão Oliveira Portes and contributors
# For license information, please see LICENSE

import hashlib
import re

import frappe
from frappe import _


CACHE_NAMESPACE = "melura_lms"
CACHE_VERSION = "v1"
DEFAULT_EXPIRES_IN_SEC = 300
SENSITIVE_KEY_TOKENS = {
	"api_key",
	"apikey",
	"authorization",
	"password",
	"secret",
	"token",
}


def build_cache_key(*parts):
	"""Build a namespaced Melura cache key from non-sensitive components."""
	key_parts = [CACHE_NAMESPACE, CACHE_VERSION]
	key_parts.extend(_normalize_key_part(part) for part in parts)
	return ":".join(key_parts)


def build_user_cache_key(*parts):
	"""Build a user-scoped cache key using the authenticated Frappe session user."""
	user = getattr(frappe.session, "user", None)
	if not user or user == "Guest":
		frappe.throw(_("Faça login antes de usar cache escopado por usuário."), frappe.PermissionError)

	return build_cache_key("user", user, *parts)


def get_cached_value(key, cache_backend=None):
	"""Return a cached value, or None when cache is unavailable."""
	try:
		return _get_cache(cache_backend).get_value(key)
	except Exception:
		return None


def set_cached_value(key, value, expires_in_sec=DEFAULT_EXPIRES_IN_SEC, cache_backend=None):
	"""Set a cached value through Frappe cache APIs when available."""
	try:
		_get_cache(cache_backend).set_value(key, value, expires_in_sec=expires_in_sec)
		return True
	except Exception:
		return False


def delete_cached_value(key, cache_backend=None):
	"""Delete a cached value through Frappe cache APIs when available."""
	try:
		_get_cache(cache_backend).delete_value(key)
		return True
	except Exception:
		return False


def get_or_set_cached_value(key, factory, expires_in_sec=DEFAULT_EXPIRES_IN_SEC, cache_backend=None):
	"""Return a cached value or compute and store it with a short TTL."""
	cached_value = get_cached_value(key, cache_backend=cache_backend)
	if cached_value is not None:
		return cached_value

	value = factory()
	set_cached_value(key, value, expires_in_sec=expires_in_sec, cache_backend=cache_backend)
	return value


def _get_cache(cache_backend=None):
	return cache_backend or frappe.cache()


def _normalize_key_part(part):
	value = str(part or "").strip()
	lower_value = value.lower()
	if lower_value in SENSITIVE_KEY_TOKENS:
		frappe.throw(_("Não use segredo ou identificador sensível em chave de cache."), frappe.ValidationError)

	value = re.sub(r"[^A-Za-z0-9_.@-]+", "-", value).strip("-")
	value = value or "empty"

	if len(value) > 120:
		digest = hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]
		value = f"{value[:80]}-{digest}"

	return value
