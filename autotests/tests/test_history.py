"""
  - transaction history structure and content (per user)
  - ML task history structure and content (per user)
  - users cannot see each other's history
  - new actions appear in the correct user's history only
"""
from conftest import UserClient

ACTIVE_MODEL_ID = 1
VALID_INPUT = {"text": "I love this product!"}


class TestTransactionHistory:
    def test_alice_has_transactions(self, alice: UserClient) -> None:
        resp = alice.get_transactions()
        assert resp.status_code == 200
        assert len(resp.json()) > 0

    def test_transactions_have_expected_fields(self, alice: UserClient) -> None:
        for tx in alice.get_transactions().json():
            assert "id" in tx
            assert "type" in tx
            assert "amount" in tx
            assert "created_at" in tx
            assert "is_applied" in tx

    def test_alice_has_deposit_transactions(self, alice: UserClient) -> None:
        types = {tx["type"] for tx in alice.get_transactions().json()}
        assert "deposit" in types

    def test_alice_has_debit_transactions(self, alice: UserClient) -> None:
        """Alice has completed ML tasks in fixture data - debit transactions must exist."""
        types = {tx["type"] for tx in alice.get_transactions().json()}
        assert "debit" in types

    def test_debit_transactions_reference_ml_task(self, alice: UserClient) -> None:
        debits = [tx for tx in alice.get_transactions().json() if tx["type"] == "debit"]
        assert len(debits) > 0
        for debit in debits:
            assert debit["ml_task_id"] is not None

    def test_deposit_appears_in_own_history(self, fresh_user: UserClient) -> None:
        count_before = len(fresh_user.get_transactions().json())
        fresh_user.deposit(10.0)
        count_after = len(fresh_user.get_transactions().json())
        assert count_after == count_before + 1

    def test_deposit_is_marked_applied(self, fresh_user: UserClient) -> None:
        fresh_user.deposit(25.0)
        transactions = fresh_user.get_transactions().json()
        assert transactions[0]["type"] == "deposit"
        assert transactions[0]["amount"] == 25.0
        assert transactions[0]["is_applied"] is True

    def test_anon_cannot_get_transactions(self, anon: UserClient) -> None:
        assert anon.get_transactions().status_code == 401

    def test_fresh_user_starts_with_empty_history(self, fresh_user: UserClient) -> None:
        assert fresh_user.get_transactions().json() == []

    def test_alices_deposit_does_not_appear_in_bobs_history(
        self, alice: UserClient, bob: UserClient
    ) -> None:
        count_before = len(bob.get_transactions().json())
        alice.deposit(5.0)
        count_after = len(bob.get_transactions().json())
        assert count_after == count_before

    def test_bobs_deposit_does_not_appear_in_alices_history(
        self, alice: UserClient, bob: UserClient
    ) -> None:
        count_before = len(alice.get_transactions().json())
        bob.deposit(5.0)
        count_after = len(alice.get_transactions().json())
        assert count_after == count_before


class TestMLTaskHistory:
    def test_alice_has_tasks(self, alice: UserClient) -> None:
        resp = alice.list_tasks()
        assert resp.status_code == 200
        assert len(resp.json()) > 0

    def test_tasks_have_expected_fields(self, alice: UserClient) -> None:
        for task in alice.list_tasks().json():
            assert "id" in task
            assert "status" in task
            assert "model_id" in task
            assert "created_at" in task

    def test_alice_has_completed_tasks(self, alice: UserClient) -> None:
        statuses = {t["status"] for t in alice.list_tasks().json()}
        assert "completed" in statuses

    def test_completed_task_has_result(self, alice: UserClient) -> None:
        completed = [t for t in alice.list_tasks().json() if t["status"] == "completed"]
        assert len(completed) > 0
        for task in completed:
            assert task["result"] is not None
            assert "output_data" in task["result"]
            assert "credits_charged" in task["result"]

    def test_new_task_appears_in_own_history(self, alice: UserClient) -> None:
        count_before = len(alice.list_tasks().json())
        alice.submit_task(ACTIVE_MODEL_ID, VALID_INPUT)
        count_after = len(alice.list_tasks().json())
        assert count_after == count_before + 1

    def test_task_history_ordered_newest_first(self, alice: UserClient) -> None:
        tasks = alice.list_tasks().json()
        assert len(tasks) >= 2
        dates = [t["created_at"] for t in tasks]
        assert dates == sorted(dates, reverse=True)

    def test_anon_cannot_list_tasks(self, anon: UserClient) -> None:
        assert anon.list_tasks().status_code == 401

    def test_fresh_user_starts_with_empty_task_list(self, fresh_user: UserClient) -> None:
        assert fresh_user.list_tasks().json() == []

    def test_alices_task_does_not_appear_in_bobs_history(
        self, alice: UserClient, bob: UserClient
    ) -> None:
        alice_task_id = alice.submit_task(ACTIVE_MODEL_ID, VALID_INPUT).json()["id"]
        bob_task_ids = {t["id"] for t in bob.list_tasks().json()}
        assert alice_task_id not in bob_task_ids

    def test_bobs_task_does_not_appear_in_alices_history(
        self, alice: UserClient, bob: UserClient
    ) -> None:
        bob_task_id = bob.submit_task(ACTIVE_MODEL_ID, VALID_INPUT).json()["id"]
        alice_task_ids = {t["id"] for t in alice.list_tasks().json()}
        assert bob_task_id not in alice_task_ids
