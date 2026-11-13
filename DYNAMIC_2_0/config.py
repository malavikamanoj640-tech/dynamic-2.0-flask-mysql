"""Local configuration for DYNAMIC 2.0.

Set DYNAMIC_SECRET_KEY to a persistent, random value before deployment.
The generated fallback is suitable for local development only and changes on restart.
"""
import os
import secrets

SECRET_KEY = os.environ.get("DYNAMIC_SECRET_KEY") or secrets.token_hex(32)
MYSQL_HOST = os.environ.get("DYNAMIC_MYSQL_HOST", "localhost")
MYSQL_USER = os.environ.get("DYNAMIC_MYSQL_USER", "root")
MYSQL_PASSWORD = os.environ.get("DYNAMIC_MYSQL_PASSWORD", "")
MYSQL_DB = os.environ.get("DYNAMIC_MYSQL_DB", "dynamic2_db")
MYSQL_PORT = int(os.environ.get("DYNAMIC_MYSQL_PORT", "3306"))

DEBUG = os.environ.get("DYNAMIC_DEBUG", "false").strip().lower() in {"1", "true", "yes"}
SESSION_COOKIE_SECURE = os.environ.get("DYNAMIC_HTTPS", "false").strip().lower() in {"1", "true", "yes"}
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
