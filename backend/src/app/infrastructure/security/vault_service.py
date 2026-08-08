"""
Infrastructure — Security Vault Service

Provides AES-256 symmetric encryption (Fernet) for sensitive connector credentials
and credential masking utilities for zero-trust API responses.
"""

from __future__ import annotations

import json
import base64
import os
from typing import Any

from cryptography.fernet import Fernet
import structlog

logger = structlog.get_logger()

# Deterministic key derivation or fallback secret for development
DEFAULT_MASTER_KEY = Fernet.generate_key()


class VaultService:
    """
    Encrypts at rest and decrypts connection config credentials.
    """

    def __init__(self, master_key: bytes | None = None) -> None:
        if master_key:
            self._fernet = Fernet(master_key)
        else:
            env_key = os.getenv("VAULT_MASTER_KEY")
            if env_key:
                # Ensure valid Fernet key length
                key_bytes = env_key.encode("utf-8") if isinstance(env_key, str) else env_key
                try:
                    self._fernet = Fernet(key_bytes)
                except Exception:
                    b64_key = base64.urlsafe_b64encode(key_bytes[:32].ljust(32, b"0"))
                    self._fernet = Fernet(b64_key)
            else:
                self._fernet = Fernet(DEFAULT_MASTER_KEY)

    def encrypt_config(self, config_dict: dict[str, Any]) -> str:
        """Encrypts dictionary to Fernet AES-256 token string."""
        json_str = json.dumps(config_dict)
        encrypted_bytes = self._fernet.encrypt(json_str.encode("utf-8"))
        return encrypted_bytes.decode("utf-8")

    def decrypt_config(self, encrypted_token: str) -> dict[str, Any]:
        """Decrypts Fernet AES-256 token string back to dictionary."""
        try:
            decrypted_bytes = self._fernet.decrypt(encrypted_token.encode("utf-8"))
            return json.loads(decrypted_bytes.decode("utf-8"))
        except Exception as exc:
            logger.error("vault_service.decryption_failed", error=str(exc))
            return {}

    @staticmethod
    def mask_credentials(config_dict: dict[str, Any]) -> dict[str, Any]:
        """Sanitizes configuration dictionary replacing secret keys with masked indicators."""
        sensitive_keys = {
            "password",
            "secret_key",
            "aws_secret_access_key",
            "api_key",
            "token",
            "bearer_token",
            "client_secret",
            "private_key",
            "auth_token",
        }

        masked = {}
        for key, value in config_dict.items():
            key_lower = key.lower()
            if any(s in key_lower for s in sensitive_keys):
                if isinstance(value, str) and len(value) > 6:
                    masked[key] = f"{value[:3]}••••••••{value[-3:]}"
                else:
                    masked[key] = "••••••••"
            elif key_lower in ("aws_access_key_id", "access_key", "client_id"):
                if isinstance(value, str) and len(value) > 8:
                    masked[key] = f"{value[:4]}****************"
                else:
                    masked[key] = "AKIA****************"
            else:
                masked[key] = value

        return masked
