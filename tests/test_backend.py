import os
import unittest
from types import SimpleNamespace

from fastapi import HTTPException
from fastapi.testclient import TestClient
from psycopg.errors import UniqueViolation

from controller.user import atomic_user_create
from dependencies import (
    get_protected_master_key_repository,
    get_protected_vault_repository,
    get_user_repository,
)
from main import app
from model.user import UserCreate
from repository.base import RepositoryBase


USER_ID = "80c7ab70-e3cb-4e10-8e2a-2cd18e7e4d9e"
AUTHENTICATION_KEY = "derived-authentication-key"
JWT_SECRET = "test-secret-key-that-is-at-least-32-bytes-long"

CREATE_USER_PAYLOAD = {
    "username": "alice",
    "authentication_key": AUTHENTICATION_KEY,
    "salt": "c2FsdA==",
    "protected_master_key": {
        "encrypted_master_key": "ZW5jcnlwdGVkLW1hc3Rlcg==",
        "iv": "aXY=",
        "salt": "c2FsdA==",
    },
    "protected_vault": {
        "encrypted_vault": "ZW5jcnlwdGVkLXZhdWx0",
        "iv": "aXY=",
    },
}


class FakeUserRepository:
    def __init__(self):
        self.users = {}
        self.deleted_usernames = []

    def create_user(self, user_data):
        if user_data.username in self.users:
            raise HTTPException(status_code=409, detail="Already exists")

        user = {
            "id": USER_ID,
            "username": user_data.username,
            "authentication_key": user_data.authentication_key,
            "salt": user_data.salt,
        }
        self.users[user_data.username] = user
        return SimpleNamespace(**user)

    def get_one_user(self, username):
        user = self.users.get(username)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return SimpleNamespace(**user)

    def get_one_user_by_id(self, user_id):
        for user in self.users.values():
            if user["id"] == user_id:
                return user
        raise HTTPException(status_code=404, detail="User not found")

    def get_user_salt(self, username):
        user = self.users.get(username)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return {"salt": user["salt"]}

    def delete_user_cascade(self, username):
        self.deleted_usernames.append(username)
        self.users.pop(username, None)


class FakeMasterKeyRepository:
    def __init__(self):
        self.records = {}

    def create_master_key(self, user_id, key_data):
        record = key_data.model_dump()
        self.records[user_id] = record
        return record

    def get_one_master_key(self, user_id):
        if user_id not in self.records:
            raise HTTPException(status_code=404, detail="Master key not found")
        return self.records[user_id]

    def change_master_key(self, user_id, key_data):
        if user_id not in self.records:
            raise HTTPException(status_code=404, detail="Master key not found")
        self.records[user_id] = key_data.model_dump()
        return self.records[user_id]


class FakeVaultRepository:
    def __init__(self, fail_create=False):
        self.records = {}
        self.fail_create = fail_create

    def create_protected_vault(self, user_id, vault_data):
        if self.fail_create:
            raise RuntimeError("vault write failed")
        record = vault_data.model_dump()
        self.records[user_id] = record
        return record

    def get_one_protected_vault(self, user_id):
        if user_id not in self.records:
            raise HTTPException(status_code=404, detail="Protected vault not found")
        return self.records[user_id]

    def update_protected_vault_contents(self, user_id, vault_data):
        if user_id not in self.records:
            raise HTTPException(status_code=404, detail="Protected vault not found")
        self.records[user_id] = vault_data.model_dump()
        return self.records[user_id]


class BackendApiTests(unittest.TestCase):
    def setUp(self):
        self.original_jwt_secret = os.environ.get("JWT_SECRET_KEY")
        self.original_creation_setting = os.environ.get("ENABLE_ACCOUNT_CREATION_DELETION")
        os.environ["JWT_SECRET_KEY"] = JWT_SECRET
        os.environ["ENABLE_ACCOUNT_CREATION_DELETION"] = "true"

        self.user_repository = FakeUserRepository()
        self.master_key_repository = FakeMasterKeyRepository()
        self.vault_repository = FakeVaultRepository()
        app.dependency_overrides[get_user_repository] = lambda: self.user_repository
        app.dependency_overrides[get_protected_master_key_repository] = lambda: self.master_key_repository
        app.dependency_overrides[get_protected_vault_repository] = lambda: self.vault_repository
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()
        self._restore_environment("JWT_SECRET_KEY", self.original_jwt_secret)
        self._restore_environment(
            "ENABLE_ACCOUNT_CREATION_DELETION",
            self.original_creation_setting,
        )

    @staticmethod
    def _restore_environment(name, value):
        if value is None:
            os.environ.pop(name, None)
        else:
            os.environ[name] = value

    def test_account_creation_persists_user_master_key_and_vault(self):
        response = self.client.post("/user/", json=CREATE_USER_PAYLOAD)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["username"], "alice")
        self.assertEqual(self.user_repository.users["alice"]["id"], USER_ID)
        self.assertEqual(
            self.master_key_repository.records[USER_ID]["encrypted_master_key"],
            "ZW5jcnlwdGVkLW1hc3Rlcg==",
        )
        self.assertEqual(
            self.vault_repository.records[USER_ID]["encrypted_vault"],
            "ZW5jcnlwdGVkLXZhdWx0",
        )

    def test_duplicate_account_returns_409_and_detail(self):
        self.client.post("/user/", json=CREATE_USER_PAYLOAD)

        response = self.client.post("/user/", json=CREATE_USER_PAYLOAD)

        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json(), {"detail": "Already exists"})

    def test_creation_failure_cleans_up_created_user(self):
        repository = FakeUserRepository()
        failing_vault_repository = FakeVaultRepository(fail_create=True)
        user_data = UserCreate.model_validate(CREATE_USER_PAYLOAD)

        with self.assertRaisesRegex(RuntimeError, "vault write failed"):
            atomic_user_create(
                user_data,
                repository,
                FakeMasterKeyRepository(),
                failing_vault_repository,
            )

        self.assertEqual(repository.deleted_usernames, ["alice"])
        self.assertNotIn("alice", repository.users)

    def test_login_token_protects_master_key_and_vault_endpoints(self):
        self.user_repository.users["alice"] = {
            "id": USER_ID,
            "username": "alice",
            "authentication_key": AUTHENTICATION_KEY,
            "salt": "c2FsdA==",
        }
        self.master_key_repository.records[USER_ID] = {
            "encrypted_master_key": "ZW5jcnlwdGVkLW1hc3Rlcg==",
            "iv": "aXY=",
            "salt": "c2FsdA==",
        }
        self.vault_repository.records[USER_ID] = {
            "encrypted_vault": "ZW5jcnlwdGVkLXZhdWx0",
            "iv": "aXY=",
        }

        token_response = self.client.post(
            "/user/token",
            data={"username": "alice", "password": AUTHENTICATION_KEY},
        )

        self.assertEqual(token_response.status_code, 200)
        self.assertEqual(token_response.json()["token_type"], "bearer")
        token = token_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        master_response = self.client.get("/master/", headers=headers)
        vault_response = self.client.get("/vault/", headers=headers)
        self.assertEqual(master_response.status_code, 200)
        self.assertEqual(master_response.json()["salt"], "c2FsdA==")
        self.assertEqual(vault_response.status_code, 200)
        self.assertEqual(vault_response.json()["encrypted_vault"], "ZW5jcnlwdGVkLXZhdWx0")

        self.assertEqual(self.client.get("/master/").status_code, 401)
        self.assertEqual(self.client.get("/vault/").status_code, 401)

    def test_authenticated_vault_and_master_key_updates(self):
        self.user_repository.users["alice"] = {
            "id": USER_ID,
            "username": "alice",
            "authentication_key": AUTHENTICATION_KEY,
            "salt": "c2FsdA==",
        }
        self.master_key_repository.records[USER_ID] = {
            "encrypted_master_key": "ZW5jcnlwdGVkLW1hc3Rlcg==",
            "iv": "aXY=",
            "salt": "c2FsdA==",
        }
        self.vault_repository.records[USER_ID] = {
            "encrypted_vault": "ZW5jcnlwdGVkLXZhdWx0",
            "iv": "aXY=",
        }
        token = self.client.post(
            "/user/token",
            data={"username": "alice", "password": AUTHENTICATION_KEY},
        ).json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        vault_response = self.client.post(
            "/vault/",
            headers=headers,
            json={"encrypted_vault": "bmV3LXZhdWx0", "iv": "bmV3LWl2"},
        )
        master_response = self.client.post(
            "/master/",
            headers=headers,
            json={
                "encrypted_master_key": "bmV3LWtleQ==",
                "iv": "bmV3LWl2",
                "salt": "bmV3LXNhbHQ=",
            },
        )

        self.assertEqual(vault_response.status_code, 200)
        self.assertEqual(vault_response.json()["encrypted_vault"], "bmV3LXZhdWx0")
        self.assertEqual(master_response.status_code, 200)
        self.assertEqual(master_response.json()["encrypted_master_key"], "bmV3LWtleQ==")


class RepositoryBaseTests(unittest.TestCase):
    def test_unique_violation_maps_to_conflict_response(self):
        class DuplicateConnection:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def execute(self, *_args, **_kwargs):
                raise UniqueViolation("duplicate")

        repository = RepositoryBase(DuplicateConnection)

        with self.assertRaises(HTTPException) as raised:
            repository.fetch_one("INSERT INTO users ...")

        self.assertEqual(raised.exception.status_code, 409)
        self.assertEqual(raised.exception.detail, "Already exists")


if __name__ == "__main__":
    unittest.main()
