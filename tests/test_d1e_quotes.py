"""Stage D.1e: the quote script must be incapable of issuing a billable request.

These tests never touch the network and never need DATABENTO_API_KEY: the
client is a stub. They check two things the money depends on:

(a) the script's source has no billable call site at all, and
(b) the guard that replaces the billable namespaces really raises.
"""

from __future__ import annotations

import ast
from datetime import date
from types import SimpleNamespace

import pytest

from strategy.research import _d1e_quotes as q

SOURCE_PATH = q.__file__
GUARD_MARKER = "# D1E-GUARD"
BILLABLE_CALL_SITES = (".timeseries", ".batch")
# Nothing in the script may reach a path that moves money.
MONEY_MOVING_NAMES = (
    "fetch_range", "authorize", "commit", "settle", "get_range", "submit_job",
)


@pytest.fixture
def source() -> str:
    with open(SOURCE_PATH) as fh:
        return fh.read()


class TestSourceHasNoBillableCallSite:
    def test_no_dotted_billable_namespace_outside_the_guard_installation(
        self, source: str
    ) -> None:
        # Arrange
        offenders = [
            (n, line)
            for n, line in enumerate(source.splitlines(), start=1)
            if any(tok in line for tok in BILLABLE_CALL_SITES) and GUARD_MARKER not in line
        ]

        # Act / Assert
        assert offenders == [], (
            "billable call site outside the guard installation: "
            + "; ".join(f"line {n}: {line.strip()}" for n, line in offenders)
        )

    def test_no_money_moving_call_site_exists(self, source: str) -> None:
        """AST, not text: the names appear in prose, so only real calls count."""
        # Arrange
        tree = ast.parse(source)
        called: set[str] = set()
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            if isinstance(func, ast.Name):
                called.add(func.id)
            elif isinstance(func, ast.Attribute):
                called.add(func.attr)

        # Act
        offenders = sorted(called & set(MONEY_MOVING_NAMES))

        # Assert
        assert offenders == [], f"script calls money-moving helpers: {offenders}"

    def test_no_attribute_access_on_a_billable_namespace_exists(self, source: str) -> None:
        """The strongest form of (a): no AST attribute node names either namespace."""
        tree = ast.parse(source)
        offenders = sorted({
            node.attr for node in ast.walk(tree)
            if isinstance(node, ast.Attribute) and node.attr in q.FORBIDDEN_NAMESPACES
        })
        assert offenders == [], f"script reaches a billable namespace: {offenders}"

    def test_nothing_money_moving_is_imported(self, source: str) -> None:
        tree = ast.parse(source)
        imported: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom | ast.Import):
                imported |= {a.name for a in node.names}
        assert "fetch_range" not in imported
        assert not any(name.startswith("data.adapter.") for name in imported)

    def test_the_guarded_namespaces_are_the_two_billable_ones(self) -> None:
        assert q.FORBIDDEN_NAMESPACES == ("timeseries", "batch")

    def test_the_script_declares_a_zero_budget(self, source: str) -> None:
        assert "Budget for this stage is $0.00" in source


class TestGuardRaises:
    def test_attribute_access_on_the_guard_raises(self) -> None:
        # Arrange
        guard = q.ForbiddenNamespace()

        # Act / Assert
        with pytest.raises(RuntimeError, match="D.1e: timeseries/batch forbidden"):
            guard.get_range  # noqa: B018

    def test_calling_the_guard_raises(self) -> None:
        guard = q.ForbiddenNamespace()
        with pytest.raises(RuntimeError, match="D.1e: timeseries/batch forbidden"):
            guard()

    def test_every_guarded_namespace_on_a_stub_client_raises(self) -> None:
        # Arrange: a stand-in for databento.Historical, no key needed
        client = SimpleNamespace(
            metadata=SimpleNamespace(get_cost=lambda **_: 1.0),
            symbology=SimpleNamespace(resolve=lambda **_: {}),
            timeseries=SimpleNamespace(get_range=lambda **_: "DOWNLOADED"),
            batch=SimpleNamespace(submit_job=lambda **_: "SUBMITTED"),
        )

        # Act
        guarded = q.install_forbidden_guards(client)

        # Assert
        for name in q.FORBIDDEN_NAMESPACES:
            namespace = getattr(guarded, name)
            with pytest.raises(RuntimeError, match="D.1e: timeseries/batch forbidden"):
                namespace.anything_at_all  # noqa: B018

    def test_the_free_namespaces_survive_the_guard(self) -> None:
        client = SimpleNamespace(
            metadata=SimpleNamespace(get_cost=lambda **_: 1.25),
            symbology=SimpleNamespace(resolve=lambda **_: {"result": {}}),
            timeseries=object(),
            batch=object(),
        )
        guarded = q.install_forbidden_guards(client)
        assert guarded.metadata.get_cost() == 1.25
        assert guarded.symbology.resolve() == {"result": {}}


class TestWindowConversions:
    """CDT and CST differ; the script computes the offset, it does not assume one."""

    def test_rth_window_in_daylight_time_is_1330_to_2010_utc(self) -> None:
        assert q.rth_window_utc(date(2025, 5, 14)) == (
            "2025-05-14T13:30:00Z", "2025-05-14T20:10:00Z"
        )

    def test_rth_window_in_standard_time_is_1430_to_2110_utc(self) -> None:
        assert q.rth_window_utc(date(2026, 2, 11)) == (
            "2026-02-11T14:30:00Z", "2026-02-11T21:10:00Z"
        )

    def test_full_trade_date_in_daylight_time_spans_2200_to_2100_utc(self) -> None:
        assert q.full_trade_date_window_utc(date(2025, 5, 14)) == (
            "2025-05-13T22:00:00Z", "2025-05-14T21:00:00Z"
        )

    def test_full_trade_date_in_standard_time_spans_2300_to_2200_utc(self) -> None:
        assert q.full_trade_date_window_utc(date(2026, 2, 11)) == (
            "2026-02-10T23:00:00Z", "2026-02-11T22:00:00Z"
        )


class TestScaling:
    def test_total_for_days_is_linear_and_labelled_a_scaling(self) -> None:
        out = q.total_for_days(40, 2.5, 1_000.0)
        assert out == {"days": 40, "usd": 100.0, "billable_bytes": 40_000.0}
        assert "NOT a quote" in q.total_for_days.__doc__


class TestExtensionBoundary:
    def test_the_extension_ends_where_the_owned_raw_data_begins(self) -> None:
        assert date(2025, 4, 1) == q.EXTENSION_END

    def test_the_last_extension_chunk_abuts_the_first_owned_chunk(self) -> None:
        from data.pull_mes import monthly_chunks

        chunks = monthly_chunks(date(2019, 5, 1), q.EXTENSION_END)
        assert chunks[-1] == ("2025-03-01", "2025-04-01")
        assert chunks[0][0] == "2019-05-01"
