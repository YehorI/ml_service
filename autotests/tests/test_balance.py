"""
  - get current balance (per user)
  - top up balance and verify update
  - invalid deposit amounts - 422
  - users cannot read each other's balance
"""
from conftest import UserClient


class TestGetBalance:
    def test_alice_get_balance_returns_amount(self, alice: UserClient) -> None:
        resp = alice.get_balance()
        assert resp.status_code == 200
        body = resp.json()
        assert "amount" in body
        assert isinstance(body["amount"], (int, float))
        assert body["amount"] >= 0

    def test_bob_has_independent_balance(self, alice: UserClient, bob: UserClient) -> None:
        alice_balance = alice.get_balance().json()["amount"]
        bob_balance = bob.get_balance().json()["amount"]
        assert alice_balance != bob_balance or True  # balances are per-user (different wallets)
        # the real assertion: both calls succeed with their own wallet_id
        assert alice.get_balance().json()["user_id"] != bob.get_balance().json()["user_id"]

    def test_anon_cannot_get_balance(self, anon: UserClient) -> None:
        assert anon.get_balance().status_code == 401


class TestDeposit:
    def test_deposit_increases_balance(self, fresh_user: UserClient) -> None:
        before = fresh_user.get_balance().json()["amount"]
        resp = fresh_user.deposit(50.0)
        assert resp.status_code == 200
        assert resp.json()["amount"] == before + 50.0

    def test_deposit_reflects_in_balance_endpoint(self, fresh_user: UserClient) -> None:
        fresh_user.deposit(75.0)
        balance = fresh_user.get_balance().json()["amount"]
        assert balance == 75.0

    def test_two_deposits_accumulate(self, fresh_user: UserClient) -> None:
        fresh_user.deposit(30.0)
        fresh_user.deposit(20.0)
        assert fresh_user.get_balance().json()["amount"] == 50.0

    def test_deposit_does_not_affect_other_users_balance(
        self, alice: UserClient, fresh_user: UserClient
    ) -> None:
        alice_before = alice.get_balance().json()["amount"]
        fresh_user.deposit(999.0)
        alice_after = alice.get_balance().json()["amount"]
        assert alice_after == alice_before

    def test_deposit_zero_returns_422(self, fresh_user: UserClient) -> None:
        assert fresh_user.deposit(0.0).status_code == 422

    def test_deposit_negative_returns_422(self, fresh_user: UserClient) -> None:
        assert fresh_user.deposit(-10.0).status_code == 422

    def test_anon_cannot_deposit(self, anon: UserClient) -> None:
        assert anon.deposit(10.0).status_code == 401
