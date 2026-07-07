"""Ограничение доступа к админке по IP (env ADMIN_ALLOWED_IPS)."""

import os

from fastapi import Request

SAFE_METHODS = ("GET", "HEAD", "OPTIONS")


def allowed_ips() -> list[str]:
    raw = os.environ.get("ADMIN_ALLOWED_IPS", "")
    return [ip.strip() for ip in raw.split(",") if ip.strip()]


def client_ip(request: Request) -> str:
    """IP клиента из X-Real-IP: nginx всегда перезаписывает его на $remote_addr.

    X-Forwarded-For не используем: nginx дополняет присланное клиентом значение,
    и первый элемент списка может подделать сам клиент.
    """
    real_ip = request.headers.get("x-real-ip", "").strip()
    if real_ip:
        return real_ip
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
