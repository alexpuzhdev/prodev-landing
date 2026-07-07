"""Ограничение доступа к админке по IP (env ADMIN_ALLOWED_IPS)."""

import os

from fastapi import Request

SAFE_METHODS = ("GET", "HEAD", "OPTIONS")


def allowed_ips() -> list[str]:
    raw = os.environ.get("ADMIN_ALLOWED_IPS", "")
    return [ip.strip() for ip in raw.split(",") if ip.strip()]


def client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else ""


def is_admin_request(request: Request) -> bool:
    path = request.url.path
    if path == "/admin" or path.startswith("/admin/"):
        return True
    if path.startswith("/api/auth"):
        return True
    return path.startswith("/api/") and request.method not in SAFE_METHODS


def ip_allowed(ip: str, allowed: list[str]) -> bool:
    for entry in allowed:
        if ip == entry or (entry.endswith(".") and ip.startswith(entry)):
            return True
    return False
