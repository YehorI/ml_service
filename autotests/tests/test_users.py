"""
  - register new user
  - login / re-login
  - error: wrong password - 401
  - error: unknown user - 404
  - error: duplicate username / email - 409
  - protected endpoints reject unauthenticated and wrong-user requests
"""
import uuid

from conftest import UserClient


class TestRegister:
    def test_register_new_user_returns_201(self, anon: UserClient) -> None:
        suffix = uuid.uuid4().hex[:8]
        resp = anon.register(f"newuser_{suffix}", f"newuser_{suffix}@example.com", "secret123")
        assert resp.status_code == 201
        body = resp.json()
        assert f"newuser_{suffix}" == body["username"]
        assert f"newuser_{suffix}@example.com" == body["email"]
        assert "id" in body

    def test_register_duplicate_username_returns_409(self, anon: UserClient) -> None:
        resp = anon.register("alice", "other@example.com", "any")
        assert resp.status_code == 409

    def test_register_duplicate_email_returns_409(self, anon: UserClient) -> None:
        resp = anon.register("completely_new", "alice@example.com", "any")
        assert resp.status_code == 409


class TestLogin:
    def test_login_success_returns_200(self, anon: UserClient) -> None:
        resp = anon.login("alice", "alice123")
        assert resp.status_code == 200
        assert resp.json()["user"]["username"] == "alice"

    def test_login_again_succeeds(self, anon: UserClient) -> None:
        """Re-authentication with the same credentials must succeed every time."""
        for _ in range(2):
            resp = anon.login("alice", "alice123")
            assert resp.status_code == 200

    def test_login_wrong_password_returns_401(self, anon: UserClient) -> None:
        resp = anon.login("alice", "wrongpassword")
        assert resp.status_code == 401

    def test_login_unknown_user_returns_404(self, anon: UserClient) -> None:
        resp = anon.login("nobody", "anything")
        assert resp.status_code == 404


class TestAuthGuards:
    def test_get_user_without_auth_returns_401(self, anon: UserClient) -> None:
        resp = anon.get_user(2)
        assert resp.status_code == 401

    def test_alice_cannot_access_bobs_profile(self, alice: UserClient, bob: UserClient) -> None:
        """Alice's client is authenticated as Alice; fetching Bob's profile should be 403."""
        bob_id = bob.login("bob", "bob123").json()["user"]["id"]
        resp = alice.get_user(bob_id)
        assert resp.status_code == 403

    def test_bob_cannot_access_alices_profile(self, alice: UserClient, bob: UserClient) -> None:
        alice_id = alice.login("alice", "alice123").json()["user"]["id"]
        resp = bob.get_user(alice_id)
        assert resp.status_code == 403
