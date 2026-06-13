from bank_etl.infrastructure.config import RetrySettings
from bank_etl.infrastructure.retry import RetryPolicy


def test_retry_policy_retries_with_backoff(monkeypatch) -> None:
    calls = 0
    delays: list[float] = []

    def flaky_operation() -> str:
        nonlocal calls
        calls += 1
        if calls < 3:
            raise ConnectionError("database unavailable")
        return "ok"

    monkeypatch.setattr("bank_etl.infrastructure.retry.sleep", delays.append)
    policy = RetryPolicy(RetrySettings(3, 0.5, 10))

    assert policy.execute(flaky_operation, "test operation") == "ok"
    assert calls == 3
    assert delays == [0.5, 1.0]
