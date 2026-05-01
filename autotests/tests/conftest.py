"""
  admin   / admin123   (wallet: 10000.0)
  alice   / alice123   (wallet: 150.5, has completed tasks and transactions)
  bob     / bob123     (wallet: 42.0)
  charlie / charlie123 (wallet: 0.0 — used for insufficient-funds tests)
"""
import os
import time
import uuid
from dataclasses import dataclass

import httpx
import pytest

USERS_URL = os.getenv("USERS_API_URL", "http://localhost:8000")
WALLET_URL = os.getenv("WALLET_API_URL", "http://localhost:8001")
MODEL_URL = os.getenv("MODEL_API_URL", "http://localhost:8002")


@dataclass
class UserClient:
    """A single user's authenticated view of all three services."""
    username: str
    _client: httpx.Client

    # users service

    def register(self, username: str, email: str, password: str) -> httpx.Response:
        return self._client.post(f"{USERS_URL}/users/register", json={
            "username": username, "email": email, "password": password,
        })

    def login(self, username: str, password: str) -> httpx.Response:
        return self._client.post(f"{USERS_URL}/users/login", json={
            "username": username, "password": password,
        })

    def get_user(self, user_id: int) -> httpx.Response:
        return self._client.get(f"{USERS_URL}/users/{user_id}")

    # wallet service

    def get_balance(self) -> httpx.Response:
        return self._client.get(f"{WALLET_URL}/wallet/balance")

    def deposit(self, amount: float) -> httpx.Response:
        return self._client.post(f"{WALLET_URL}/wallet/deposit", json={"amount": amount})

    def get_transactions(self) -> httpx.Response:
        return self._client.get(f"{WALLET_URL}/wallet/transactions")

    # model service

    def submit_task(self, model_id: int, input_data) -> httpx.Response:
        return self._client.post(f"{MODEL_URL}/tasks", json={
            "model_id": model_id, "input_data": input_data,
        })

    def get_task(self, task_id: int) -> httpx.Response:
        return self._client.get(f"{MODEL_URL}/tasks/{task_id}")

    def list_tasks(self) -> httpx.Response:
        return self._client.get(f"{MODEL_URL}/tasks")

    def poll_task(self, task_id: int, *, timeout: int = 120) -> dict:
        """Poll GET /tasks/{id} until COMPLETED or FAILED, or raise TimeoutError."""
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            resp = self.get_task(task_id)
            assert resp.status_code == 200, resp.text
            data = resp.json()
            if data["status"] in ("completed", "failed"):
                return data
            time.sleep(2)
        raise TimeoutError(f"Task {task_id} did not finish within {timeout}s")


def _make_client(username: str, password: str) -> httpx.Client:
    return httpx.Client(auth=httpx.BasicAuth(username, password), timeout=10.0)


@pytest.fixture(scope="session")
def alice() -> UserClient:
    with _make_client("alice", "alice123") as client:
        yield UserClient(username="alice", _client=client)


@pytest.fixture(scope="session")
def bob() -> UserClient:
    with _make_client("bob", "bob123") as client:
        yield UserClient(username="bob", _client=client)


@pytest.fixture(scope="session")
def charlie() -> UserClient:
    with _make_client("charlie", "charlie123") as client:
        yield UserClient(username="charlie", _client=client)


@pytest.fixture(scope="session")
def admin() -> UserClient:
    with _make_client("admin", "admin123") as client:
        yield UserClient(username="admin", _client=client)


@pytest.fixture(scope="session")
def anon() -> UserClient:
    """Unauthenticated client."""
    with httpx.Client(timeout=10.0) as client:
        yield UserClient(username="<anonymous>", _client=client)


@pytest.fixture
def fresh_user() -> UserClient:
    suffix = uuid.uuid4().hex[:8]
    username = f"test_{suffix}"
    password = f"pass_{suffix}"
    email = f"{username}@test.local"

    with _make_client(username, password) as authed_client:
        anon_client = httpx.Client(timeout=10.0)
        try:
            resp = anon_client.post(f"{USERS_URL}/users/register", json={
                "username": username, "email": email, "password": password,
            })
            assert resp.status_code == 201, resp.text
            yield UserClient(username=username, _client=authed_client)
        finally:
            anon_client.close()
