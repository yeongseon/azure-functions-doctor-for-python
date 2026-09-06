"""Version-controlled Azure Functions compatibility catalog.

This module loads a version-controlled snapshot of Azure Functions support-matrix
facts (Python version lifecycle, hosting-plan Python caps, runtime lifecycle) from
``assets/compatibility/catalog.json``. The catalog is the single, auditable source
of truth for every date/compatibility rule: each fact carries a source URL and a
``last_verified`` date, and lifecycle dates are tagged with the *precision* at which
Microsoft publishes them (day / month / year) so the tool never renders a more
precise date than the source provides.

No runtime network calls are made; the catalog ships with the package.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import importlib.resources
import json
from typing import Literal, Optional, cast

from azure_functions_doctor.logging_config import get_logger

logger = get_logger(__name__)

# Number of days after which the shipped catalog is considered stale. Staleness is
# a property of the catalog snapshot itself, reported separately from any finding
# severity: a stale catalog emits its own ``catalog_stale`` warning, never an error
# on the diagnosed project.
CATALOG_STALENESS_THRESHOLD_DAYS = 180

Precision = Literal["day", "month", "year"]

_MONTH_NAMES = (
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
)


def _parse_major_minor(version: str) -> Optional[tuple[int, int]]:
    """Return the ``(major, minor)`` pair for a ``"3.12"``-style string."""
    parts = version.split(".")
    if len(parts) < 2:
        return None
    try:
        return int(parts[0]), int(parts[1])
    except ValueError:
        return None


@dataclass(frozen=True)
class SupportEnd:
    """A lifecycle end date modelled at the precision the source publishes.

    ``value`` is ``YYYY-MM-DD`` for day precision, ``YYYY-MM`` for month precision,
    and ``YYYY`` for year precision. ``render`` formats the value at that precision
    and never synthesizes finer detail than the source provides.
    """

    value: str
    precision: Precision

    def render(self) -> str:
        """Render the date at its stated precision (e.g. ``"October 2026"``)."""
        parts = self.value.split("-")
        try:
            if self.precision == "day" and len(parts) == 3:
                year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
                return f"{_MONTH_NAMES[month - 1]} {day}, {year}"
            if self.precision == "month" and len(parts) >= 2:
                year, month = int(parts[0]), int(parts[1])
                return f"{_MONTH_NAMES[month - 1]} {year}"
            if self.precision == "year":
                return str(int(parts[0]))
        except (ValueError, IndexError):
            logger.warning(
                "Malformed support_end value %r for precision %s", self.value, self.precision
            )
        return self.value


@dataclass(frozen=True)
class Fact:
    """A single catalog fact with source and freshness metadata."""

    fact_id: str
    category: str
    applies_to: dict[str, str]
    source_url: str
    last_verified: str
    verification_notes: str
    status: Optional[str] = None
    support_end: Optional[SupportEnd] = None
    max_python: Optional[str] = None
    supersedes: Optional[str] = None


@dataclass(frozen=True)
class Freshness:
    """Freshness state of the catalog snapshot, independent of any finding."""

    last_verified: str
    age_days: int
    is_stale: bool
    threshold_days: int


@dataclass(frozen=True)
class Catalog:
    """Parsed, in-memory view of the compatibility catalog."""

    catalog_version: str
    last_verified: str
    sources: dict[str, str]
    facts: tuple[Fact, ...]

    def get_fact(self, fact_id: str) -> Optional[Fact]:
        """Return the fact with ``fact_id`` or ``None``."""
        for fact in self.facts:
            if fact.fact_id == fact_id:
                return fact
        return None

    def facts_by_category(self, category: str) -> tuple[Fact, ...]:
        """Return all facts in ``category`` in catalog order."""
        return tuple(fact for fact in self.facts if fact.category == category)

    def python_versions(self) -> tuple[str, ...]:
        """Return supported Python ``major.minor`` versions, sorted ascending."""
        versions = [
            fact.applies_to["python"]
            for fact in self.facts_by_category("python_runtime_lifecycle")
            if "python" in fact.applies_to
        ]
        return tuple(sorted(versions, key=lambda v: _parse_major_minor(v) or (0, 0)))

    def python_eos(self, version: str) -> Optional[SupportEnd]:
        """Return the published end-of-support date for a Python ``version``."""
        target = _parse_major_minor(version)
        if target is None:
            return None
        for fact in self.facts_by_category("python_runtime_lifecycle"):
            applies = fact.applies_to.get("python")
            if applies is not None and _parse_major_minor(applies) == target:
                return fact.support_end
        return None

    def hosting_plan_matrix(self) -> dict[str, tuple[str, ...]]:
        """Reconstruct the per-plan supported-Python matrix from the catalog.

        Each plan's allow-list is the globally supported Python set filtered by that
        plan's ``max_python`` cap (plans without a cap track the full set).
        """
        supported = self.python_versions()
        matrix: dict[str, tuple[str, ...]] = {}
        for fact in self.facts_by_category("hosting_plan_python_cap"):
            plan = fact.applies_to.get("hosting_plan")
            if plan is None:
                continue
            cap = _parse_major_minor(fact.max_python) if fact.max_python else None
            if cap is None:
                matrix[plan] = supported
            else:
                matrix[plan] = tuple(
                    v for v in supported if (_parse_major_minor(v) or (0, 0)) <= cap
                )
        return matrix

    def freshness(self, today: Optional[date] = None) -> Freshness:
        """Return the catalog's freshness state relative to ``today``."""
        current = today if today is not None else date.today()
        try:
            verified = date.fromisoformat(self.last_verified)
            age_days = (current - verified).days
        except ValueError:
            logger.warning("Malformed catalog last_verified %r", self.last_verified)
            age_days = 0
        return Freshness(
            last_verified=self.last_verified,
            age_days=age_days,
            is_stale=age_days > CATALOG_STALENESS_THRESHOLD_DAYS,
            threshold_days=CATALOG_STALENESS_THRESHOLD_DAYS,
        )


def _parse_support_end(raw: Optional[dict[str, str]]) -> Optional[SupportEnd]:
    if raw is None:
        return None
    value = raw.get("value")
    precision = raw.get("precision")
    if value is None or precision not in ("day", "month", "year"):
        return None
    return SupportEnd(value=value, precision=cast(Precision, precision))


def _parse_fact(raw: dict[str, object]) -> Fact:
    support_end_raw = raw.get("support_end")
    support_end = _parse_support_end(support_end_raw if isinstance(support_end_raw, dict) else None)
    applies_raw = raw.get("applies_to")
    applies_to = (
        {str(k): str(v) for k, v in applies_raw.items()} if isinstance(applies_raw, dict) else {}
    )
    max_python = raw.get("max_python")
    supersedes = raw.get("supersedes")
    status = raw.get("status")
    return Fact(
        fact_id=str(raw.get("fact_id", "")),
        category=str(raw.get("category", "")),
        applies_to=applies_to,
        source_url=str(raw.get("source_url", "")),
        last_verified=str(raw.get("last_verified", "")),
        verification_notes=str(raw.get("verification_notes", "")),
        status=str(status) if isinstance(status, str) else None,
        support_end=support_end,
        max_python=str(max_python) if isinstance(max_python, str) else None,
        supersedes=str(supersedes) if isinstance(supersedes, str) else None,
    )


def _build_catalog(raw: dict[str, object]) -> Catalog:
    sources_raw = raw.get("sources")
    sources = (
        {str(k): str(v) for k, v in sources_raw.items()} if isinstance(sources_raw, dict) else {}
    )
    facts_raw = raw.get("facts")
    facts = (
        tuple(_parse_fact(item) for item in facts_raw if isinstance(item, dict))
        if isinstance(facts_raw, list)
        else ()
    )
    return Catalog(
        catalog_version=str(raw.get("catalog_version", "")),
        last_verified=str(raw.get("last_verified", "")),
        sources=sources,
        facts=facts,
    )


_CATALOG_CACHE: Optional[Catalog] = None


def load_catalog() -> Catalog:
    """Load and cache the version-controlled compatibility catalog.

    The catalog ships with the package under ``assets/compatibility/catalog.json``;
    no network calls are made.
    """
    global _CATALOG_CACHE
    if _CATALOG_CACHE is not None:
        return _CATALOG_CACHE

    catalog_path = importlib.resources.files("azure_functions_doctor.assets").joinpath(
        "compatibility/catalog.json"
    )
    try:
        with catalog_path.open(encoding="utf-8") as handle:
            raw = json.load(handle)
    except FileNotFoundError as exc:  # pragma: no cover - packaging safeguard
        logger.error("compatibility catalog.json not found")
        raise RuntimeError("compatibility catalog.json not found") from exc
    except json.JSONDecodeError as exc:  # pragma: no cover - packaging safeguard
        logger.error("Invalid JSON in catalog.json: %s", exc)
        raise RuntimeError(f"Failed to parse catalog.json: {exc}") from exc

    _CATALOG_CACHE = _build_catalog(raw)
    return _CATALOG_CACHE
