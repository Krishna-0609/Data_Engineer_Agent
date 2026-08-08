"""
Tests — Connections & Security Vault Unit and Integration Tests
"""

import pytest
from httpx import AsyncClient

from app.infrastructure.security.vault_service import VaultService


class TestVaultServiceUnit:
    def test_vault_encryption_decryption_roundtrip(self):
        vault = VaultService()
        raw_config = {
            "bucket_name": "my-prod-s3",
            "aws_access_key_id": "AKIA1234567890EXAMPLE",
            "aws_secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
        }

        encrypted_token = vault.encrypt_config(raw_config)
        assert isinstance(encrypted_token, str)
        assert "AKIA" not in encrypted_token

        decrypted = vault.decrypt_config(encrypted_token)
        assert decrypted == raw_config

    def test_vault_credential_masking(self):
        vault = VaultService()
        raw_config = {
            "host": "rds.us-east-1.amazonaws.com",
            "port": 5432,
            "aws_access_key_id": "AKIA1234567890EXAMPLE",
            "password": "SuperSecretPassword123!",
        }

        masked = vault.mask_credentials(raw_config)
        assert masked["host"] == "rds.us-east-1.amazonaws.com"
        assert masked["port"] == 5432
        assert "AKIA" in masked["aws_access_key_id"]
        assert "****************" in masked["aws_access_key_id"]
        assert "SuperSecretPassword123!" not in masked["password"]
        assert "••••••••" in masked["password"]


class TestConnectionEndpoints:
    async def test_connection_lifecycle_and_health_test(
        self, client: AsyncClient, auth_headers: dict
    ):
        # 1. Create a project
        proj_resp = await client.post(
            "/api/v1/projects/",
            json={"name": "Vault Connection Proj"},
            headers=auth_headers,
        )
        assert proj_resp.status_code == 201
        proj_id = proj_resp.json()["id"]

        # 2. Create an AWS S3 source connection
        create_resp = await client.post(
            "/api/v1/connections/",
            json={
                "project_id": proj_id,
                "name": "Production S3 Bucket",
                "category": "source",
                "connection_type": "aws_s3",
                "description": "Main customer transaction bucket",
                "config": {
                    "bucket_name": "prod-customer-tx",
                    "region": "us-east-1",
                    "aws_access_key_id": "AKIA9876543210SECURE",
                    "aws_secret_access_key": "SecretAccessKeyVal123!",
                },
            },
            headers=auth_headers,
        )
        assert create_resp.status_code == 201
        conn_data = create_resp.json()
        assert conn_data["name"] == "Production S3 Bucket"
        assert "AKIA" in conn_data["config"]["aws_access_key_id"]
        assert "SecretAccessKeyVal123!" not in conn_data["config"]["aws_secret_access_key"]
        conn_id = conn_data["id"]

        # 3. List connections
        list_resp = await client.get(
            f"/api/v1/connections/?project_id={proj_id}",
            headers=auth_headers,
        )
        assert list_resp.status_code == 200
        assert list_resp.json()["total"] == 1

        # 4. Perform live health test
        test_resp = await client.post(
            f"/api/v1/connections/{conn_id}/test",
            headers=auth_headers,
        )
        assert test_resp.status_code == 200
        health_data = test_resp.json()
        assert health_data["healthy"] is True
        assert "Successfully pinged AWS S3" in health_data["message"]
