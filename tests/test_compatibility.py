"""Tests for the version-controlled Azure Functions compatibility catalog."""

from __future__ import annotations

from datetime import date

import pytest

import azure_functions_doctor.compatibility as compatibility_module
from azure_functions_doctor.compatibility import (
    CATALOG_STALENESS_THRESHOLD_DAYS,
    Catalog,
    Fact,
    SupportEnd,
    _build_catalog,
    _parse_fact,
    _parse_major_minor,
    _parse_support_end,
    load_catalog,
)


def test_load_catalog_is_cached() -> None:
    """The catalog is parsed once and the same instance is returned."""
    first = load_catalog()
    second = load_catalog()
    assert first is second
    assert first.catalog_version == "1.0.0"
    assert first.last_verified == "2026-09-06"
    assert "supported_languages" in first.sources


def test_python_versions_sorted_ascending() -> None:
    catalog = load_catalog()
    assert catalog.python_versions() == ("3.10", "3.11", "3.12", "3.13", "3.14")


def test_hosting_plan_matrix_matches_published_caps() -> None:
    catalog = load_catalog()
    matrix = catalog.hosting_plan_matrix()
    assert matrix["linux-consumption"] == ("3.10", "3.11", "3.12")
    assert matrix["flex-consumption"] == ("3.10", "3.11", "3.12", "3.13", "3.14")
    assert matrix["premium"] == ("3.10", "3.11", "3.12", "3.13", "3.14")
    assert matrix["dedicated"] == ("3.10", "3.11", "3.12", "3.13", "3.14")


def test_python_eos_renders_month_precision() -> None:
    catalog = load_catalog()
    support_end = catalog.python_eos("3.10")
    assert support_end is not None
    assert support_end.precision == "month"
    assert support_end.render() == "October 2026"


def test_python_eos_accepts_patch_versions() -> None:
    catalog = load_catalog()
    assert catalog.python_eos("3.12.4") is not None


def test_python_eos_unknown_returns_none() -> None:
    catalog = load_catalog()
    assert catalog.python_eos("3.99") is None


def test_python_eos_unparseable_returns_none() -> None:
    catalog = load_catalog()
    assert catalog.python_eos("not-a-version") is None


def test_get_fact_found_and_missing() -> None:
    catalog = load_catalog()
    assert catalog.get_fact("python-3.10-eos") is not None
    assert catalog.get_fact("does-not-exist") is None


def test_facts_by_category() -> None:
    catalog = load_catalog()
    lifecycle = catalog.facts_by_category("python_runtime_lifecycle")
    assert len(lifecycle) == 5
    assert catalog.facts_by_category("no-such-category") == ()


def test_runtime_lifecycle_day_precision_facts() -> None:
    catalog = load_catalog()
    v1 = catalog.get_fact("functions-runtime-v1-eos")
    assert v1 is not None
    assert v1.support_end is not None
    assert v1.support_end.precision == "day"
    assert v1.support_end.render() == "September 14, 2026"


def test_linux_consumption_retirement_day_precision() -> None:
    catalog = load_catalog()
    fact = catalog.get_fact("linux-consumption-retirement")
    assert fact is not None
    assert fact.status == "retiring"
    assert fact.support_end is not None
    assert fact.support_end.render() == "September 30, 2028"


def test_parse_major_minor_edge_cases() -> None:
    assert _parse_major_minor("3.12") == (3, 12)
    assert _parse_major_minor("3") is None
    assert _parse_major_minor("x.y") is None


def test_support_end_render_year_precision() -> None:
    assert SupportEnd(value="2030", precision="year").render() == "2030"


def test_support_end_render_malformed_returns_raw() -> None:
    # Precision claims a day but the value is malformed: render falls back to raw.
    assert SupportEnd(value="nope", precision="day").render() == "nope"


def test_freshness_fresh_catalog() -> None:
    catalog = load_catalog()
    freshness = catalog.freshness(today=date(2026, 9, 6))
    assert freshness.age_days == 0
    assert freshness.is_stale is False
    assert freshness.threshold_days == CATALOG_STALENESS_THRESHOLD_DAYS


def test_freshness_stale_catalog() -> None:
    catalog = load_catalog()
    beyond = date(2026, 9, 6)
    freshness = catalog.freshness(today=beyond.replace(year=beyond.year + 2))
    assert freshness.is_stale is True


def test_freshness_default_today_uses_current_date() -> None:
    catalog = load_catalog()
    freshness = catalog.freshness()
    assert freshness.age_days >= 0


def test_freshness_malformed_last_verified() -> None:
    catalog = Catalog(
        catalog_version="1.0.0",
        last_verified="not-a-date",
        sources={},
        facts=(),
    )
    freshness = catalog.freshness(today=date(2026, 9, 6))
    assert freshness.age_days == 0
    assert freshness.is_stale is False


def test_parse_support_end_none_and_invalid() -> None:
    assert _parse_support_end(None) is None
    assert _parse_support_end({"precision": "day"}) is None
    assert _parse_support_end({"value": "2026", "precision": "decade"}) is None
    parsed = _parse_support_end({"value": "2026-10", "precision": "month"})
    assert parsed == SupportEnd(value="2026-10", precision="month")


def test_parse_fact_tolerates_missing_and_wrong_types() -> None:
    fact = _parse_fact(
        {
            "fact_id": "x",
            "category": "python_runtime_lifecycle",
            "applies_to": "not-a-dict",
            "support_end": "not-a-dict",
            "max_python": 3,
            "supersedes": None,
            "status": 42,
        }
    )
    assert isinstance(fact, Fact)
    assert fact.applies_to == {}
    assert fact.support_end is None
    assert fact.max_python is None
    assert fact.supersedes is None
    assert fact.status is None


def test_build_catalog_tolerates_missing_sections() -> None:
    catalog = _build_catalog({})
    assert catalog.catalog_version == ""
    assert catalog.sources == {}
    assert catalog.facts == ()


def test_build_catalog_skips_non_dict_facts() -> None:
    catalog = _build_catalog(
        {
            "sources": {"a": "b"},
            "facts": ["not-a-dict", {"fact_id": "ok", "category": "c"}],
        }
    )
    assert len(catalog.facts) == 1
    assert catalog.facts[0].fact_id == "ok"


def test_python_versions_ignores_facts_without_python_key() -> None:
    catalog = Catalog(
        catalog_version="1.0.0",
        last_verified="2026-09-06",
        sources={},
        facts=(
            Fact(
                fact_id="no-python",
                category="python_runtime_lifecycle",
                applies_to={},
                source_url="",
                last_verified="",
                verification_notes="",
            ),
        ),
    )
    assert catalog.python_versions() == ()


def test_reload_after_cache_reset(monkeypatch: pytest.MonkeyPatch) -> None:
    """Resetting the module cache forces a fresh parse from disk."""
    monkeypatch.setattr(compatibility_module, "_CATALOG_CACHE", None)
    catalog = load_catalog()
    assert catalog.catalog_version == "1.0.0"


def test_support_end_render_out_of_range_month_falls_back() -> None:
    # Month 13 triggers an IndexError inside render, which is logged and the
    # raw value returned unchanged.
    assert SupportEnd(value="2026-13-40", precision="day").render() == "2026-13-40"


def test_hosting_plan_matrix_skips_fact_without_plan() -> None:
    catalog = Catalog(
        catalog_version="1.0.0",
        last_verified="2026-09-06",
        sources={},
        facts=(
            Fact(
                fact_id="cap-no-plan",
                category="hosting_plan_python_cap",
                applies_to={},
                source_url="",
                last_verified="",
                verification_notes="",
                max_python="3.12",
            ),
        ),
    )
    assert catalog.hosting_plan_matrix() == {}
