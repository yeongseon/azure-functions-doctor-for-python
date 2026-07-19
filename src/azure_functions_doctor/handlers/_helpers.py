import ast
from pathlib import Path
import re
import sys
from typing import (
    Callable,
    Dict,
    Iterator,
    List,
    Literal,
    NamedTuple,
    Optional,
    TypedDict,
    TypeVar,
    Union,
)

from packaging.requirements import InvalidRequirement, Requirement
from packaging.utils import canonicalize_name

from azure_functions_doctor.logging_config import get_logger

logger = get_logger(__name__)

EXCLUDED_PROJECT_DIRS = {".venv", "node_modules", "build", "dist", ".pytest_cache", "__pycache__"}


class HandlerResult(TypedDict, total=False):
    status: str
    detail: str
    internal_error: str


class RuleContext(TypedDict, total=False):
    target_python: Optional[str]


# Platform-aware candidates for executables (for symmetric fallback)
_PYTHON_CANDIDATES: dict[str, list[str]] = {
    "python": ["python", "python3"] + (["py"] if sys.platform == "win32" else []),
    "python3": ["python3", "python"] + (["py"] if sys.platform == "win32" else []),
}

NATIVE_DEPENDENCY_PACKAGES: dict[str, str] = {
    "pyodbc": "requires unixODBC and a matching wheel",
    "cryptography": "verify OpenSSL-compatible wheels for the target runtime",
    "lxml": "ensure libxml2/libxslt-compatible wheels for Linux deployment",
    "pillow": "ensure libjpeg/zlib-compatible wheels for Linux deployment",
    "numpy": "ensure compiled wheels match the Azure Functions Linux runtime",
    "pandas": "ensure compiled wheels match the Azure Functions Linux runtime",
    "scipy": "ensure compiled wheels match the Azure Functions Linux runtime",
    "opencv-python": "ensure system-level native libraries match the target runtime",
    "psycopg2": "consider psycopg2-binary on Azure Functions Consumption plans",
    "grpcio": "ensure compiled wheels match the Azure Functions Linux runtime",
    "ujson": "ensure compiled wheels match the Azure Functions Linux runtime",
    "orjson": "ensure compiled wheels match the Azure Functions Linux runtime",
}


def _discover_functionapp_aliases(source: str) -> set[str]:
    """Extract variable names assigned a ``FunctionApp()`` or ``Blueprint()`` call.

    Scans AST assignments like ``app = func.FunctionApp()`` and
    ``bp = Blueprint()`` to discover alias names used for decorators.
    Returns the set of discovered names, or ``{"app"}`` when none are found.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return {"app"}

    names: set[str] = set()
    target_attrs = {"FunctionApp", "Blueprint"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
            func_node = node.value.func
            attr_name: str | None = None
            if isinstance(func_node, ast.Attribute):
                attr_name = func_node.attr
            elif isinstance(func_node, ast.Name):
                attr_name = func_node.id
            if attr_name in target_attrs:
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        names.add(target.id)
    return names or {"app"}


def _collect_blueprint_aliases(source: str) -> set[str]:
    """Extract variable names assigned a ``Blueprint()`` call."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return set()

    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
            func_node = node.value.func
            attr_name: str | None = None
            if isinstance(func_node, ast.Attribute):
                attr_name = func_node.attr
            elif isinstance(func_node, ast.Name):
                attr_name = func_node.id
            if attr_name != "Blueprint":
                continue
            for target in node.targets:
                if isinstance(target, ast.Name):
                    names.add(target.id)
    return names


def _collect_register_functions_args(source: str) -> set[str]:
    """Collect Blueprint aliases passed to ``register_functions(...)`` calls.

    Only the official Azure Functions Python v2 API (``app.register_functions``)
    is recognized. Flask/FastAPI-style ``register_blueprint`` is intentionally
    not accepted because it is not a valid registration call for the Azure
    Functions runtime.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return set()

    names: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        func_node = node.func
        if not isinstance(func_node, ast.Attribute):
            continue
        if func_node.attr != "register_functions":
            continue

        for arg in node.args:
            if isinstance(arg, ast.Name):
                names.add(arg.id)
    return names


def _source_contains_blueprint_decorator(source: str, blueprint_aliases: set[str]) -> set[str]:
    """Return Blueprint aliases used in decorators like ``@bp.route()``."""
    if not blueprint_aliases:
        return set()

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return set()

    matched_aliases: set[str] = set()

    def decorator_alias(dec: ast.expr) -> str | None:
        node: ast.expr = dec.func if isinstance(dec, ast.Call) else dec
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
            alias = node.value.id
            if alias in blueprint_aliases:
                return alias
        return None

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.decorator_list:
            for dec in node.decorator_list:
                alias = decorator_alias(dec)
                if alias is not None:
                    matched_aliases.add(alias)
    return matched_aliases


def _collect_unregistered_blueprint_aliases(path: Path) -> set[str]:
    """Collect Blueprint aliases that are decorated but never registered."""
    project_contents = list(_iter_project_py_contents(path))
    blueprint_aliases: set[str] = set()

    for _py_file, content in project_contents:
        blueprint_aliases |= _collect_blueprint_aliases(content)

    decorated_blueprint_aliases: set[str] = set()
    registered_blueprint_aliases: set[str] = set()

    for _py_file, content in project_contents:
        decorated_blueprint_aliases |= _source_contains_blueprint_decorator(
            content, blueprint_aliases
        )
        registered_blueprint_aliases |= _collect_register_functions_args(content)

    return decorated_blueprint_aliases - registered_blueprint_aliases


def _source_contains_ast(source: str, identifier: str) -> bool:
    """Return True when the source contains a decorator like ``@identifier.xxx``.

    ``identifier`` may be a pipe-separated list (e.g. ``"app|bp"``) to match
    any of the given names, which covers both ``@app.route()`` and the
    Blueprint-style ``@bp.route()``.

    Additionally, ``FunctionApp()`` and ``Blueprint()`` variable assignments are
    discovered automatically so that custom aliases (e.g. ``fa = func.FunctionApp()``)
    are recognised even when they are not listed in ``identifier``.
    """
    identifiers = set(identifier.split("|"))
    # Merge in dynamically-discovered aliases
    identifiers |= _discover_functionapp_aliases(source)
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return False

    def decorator_matches(dec: ast.expr) -> bool:
        # @app.route() is ast.Call(func=Attribute(...)); @app.route is ast.Attribute
        node: ast.expr = dec.func if isinstance(dec, ast.Call) else dec
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
            return node.value.id in identifiers
        return False

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.decorator_list:
            for dec in node.decorator_list:
                if decorator_matches(dec):
                    return True
    return False


def _iter_project_py_contents(path: Path) -> Iterator[tuple[Path, str]]:
    """Yield (py_file, content) for each .py file under path, skipping excluded dirs."""
    for py_file in path.rglob("*.py"):
        if any(part in EXCLUDED_PROJECT_DIRS for part in py_file.parts):
            continue
        content = _read_project_python_file(py_file)
        if content is None:
            continue
        yield py_file, content


def _read_project_python_file(py_file: Path) -> Optional[str]:
    """Read Python source without failing the whole traversal."""
    try:
        return py_file.read_text(encoding="utf-8")
    except PermissionError:
        logger.warning(f"Permission denied reading {py_file}")
        return None
    except UnicodeDecodeError:
        try:
            return py_file.read_text(encoding="utf-8", errors="ignore")
        except (OSError, PermissionError, ValueError) as exc:
            logger.debug(f"Skip {py_file}: {exc}")
            return None
    except (MemoryError, OSError, ValueError) as exc:
        logger.debug(f"Skip {py_file}: {exc}")
        return None


def _parse_requirements_names(content: str) -> set[str]:
    """Extract normalized package names from requirements.txt content.

    Handles extras (``requests[security]``), environment markers (``;``),
    URL installs (``@``), pip directives (``-r``, ``-e``), and inline comments.
    """
    names: set[str] = set()
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        # Skip -r / -c / --requirement / --constraint includes
        if line.startswith(("-r ", "-c ", "--requirement", "--constraint")):
            continue
        # Handle editable installs: -e git+...#egg=name
        if line.startswith(("-e ", "--editable")):
            egg_match = re.search(r"#egg=([^&\s]+)", line)
            if egg_match:
                names.add(canonicalize_name(egg_match.group(1)))
            continue
        # Skip other pip flags (--find-links, --index-url, etc.)
        if line.startswith("-"):
            continue
        # Strip inline comments
        line = line.split("#")[0].strip()
        if not line:
            continue
        try:
            req = Requirement(line)
            names.add(canonicalize_name(req.name))
        except InvalidRequirement:
            # Fall back to a simple split for unparseable lines
            name = re.split(r"[=<>!~;\[\]@]", line, maxsplit=1)[0].strip()
            if name:
                names.add(canonicalize_name(name))
    return names


def _detect_native_dependency_risks(content: str) -> list[tuple[str, str]]:
    """Return matching native-dependency packages in requirements order."""
    matches: list[tuple[str, str]] = []
    seen: set[str] = set()
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith(("-r ", "-c ", "--requirement", "--constraint")):
            continue
        if line.startswith(("-e ", "--editable")):
            egg_match = re.search(r"#egg=([^&\s]+)", line)
            if egg_match:
                normalized_egg = canonicalize_name(egg_match.group(1))
                if normalized_egg in NATIVE_DEPENDENCY_PACKAGES and normalized_egg not in seen:
                    matches.append((normalized_egg, NATIVE_DEPENDENCY_PACKAGES[normalized_egg]))
                    seen.add(normalized_egg)
            continue
        if line.startswith("-"):
            continue
        line = line.split("#")[0].strip()
        if not line:
            continue

        normalized_name: str | None = None
        try:
            req = Requirement(line)
            normalized_name = canonicalize_name(req.name)
        except InvalidRequirement:
            fallback_name = re.split(r"[=<>!~;\[\]@]", line, maxsplit=1)[0].strip()
            if fallback_name:
                normalized_name = canonicalize_name(fallback_name)

        if normalized_name is None or normalized_name in seen:
            continue
        if normalized_name in NATIVE_DEPENDENCY_PACKAGES:
            matches.append((normalized_name, NATIVE_DEPENDENCY_PACKAGES[normalized_name]))
            seen.add(normalized_name)

    return matches


def _create_result(status: str, detail: str, internal_error: bool = False) -> HandlerResult:
    """Create a standardized result dictionary (status limited to 'pass'/'fail')."""
    res: HandlerResult = {"status": status, "detail": detail}
    if internal_error:
        res["internal_error"] = "true"
    return res


def _handle_exception(operation: str, exc: Exception) -> HandlerResult:
    """Handle exceptions consistently across all handlers (always fail)."""
    error_msg = f"Error during {operation}: {exc}"
    logger.error(error_msg, exc_info=True)
    return _create_result("fail", error_msg, internal_error=True)


def _handle_specific_exceptions(operation: str, exc: Exception) -> HandlerResult:
    """Handle specific exception types with user-friendly messages (fail only)."""
    if isinstance(exc, UnicodeDecodeError):
        return _create_result("fail", f"Encoding error in {operation}: {exc}.", internal_error=True)
    if isinstance(exc, (ValueError, TypeError)):
        return _create_result(
            "fail", f"Configuration error in {operation}: {exc}.", internal_error=True
        )
    if isinstance(exc, (OSError, PermissionError)):
        return _create_result(
            "fail", f"File system error in {operation}: {exc}", internal_error=True
        )
    if isinstance(exc, ImportError):
        return _create_result("fail", f"Import error in {operation}: {exc}", internal_error=True)
    if isinstance(exc, MemoryError):
        return _create_result("fail", "Memory error: file too large", internal_error=True)
    if isinstance(exc, KeyboardInterrupt):
        raise exc
    if isinstance(exc, SystemExit):
        raise exc
    logger.error(f"Unexpected error in {operation}: {exc}", exc_info=True)
    return _create_result("fail", f"Unexpected error in {operation}", internal_error=True)


class Condition(TypedDict, total=False):
    target: str
    operator: str
    value: Union[str, int, float]
    keyword: str
    mode: Literal["string", "ast"]  # for source_code_contains: "string" (default) or "ast"
    jsonpath: str
    targets: list[str]
    patterns: list[str]
    pypi: str
    package: str
    file: str


class Rule(TypedDict, total=False):
    id: str
    type: Literal[
        "compare_version",
        "env_var_exists",
        "path_exists",
        "file_exists",
        "package_installed",
        "source_code_contains",
        "conditional_exists",
        "callable_detection",
        "executable_exists",
        "any_of_exists",
        "file_glob_check",
        "host_json_property",
        "host_json_version",
        "local_settings_security",
        "host_json_extension_bundle_version",
        "package_forbidden",
        "package_declared",
        "blueprint_registration",
        "native_dependency_risk",
    ]
    label: str
    category: str
    section: str
    description: str
    required: bool
    condition: Condition
    hint: str
    fix: str
    fix_command: str
    hint_url: str
    source_type: Literal["ms_learn", "derived", "heuristic"]
    source_title: str
    source_url: str
    why_it_matters: str
    symptoms: str
    check_order: int


class CompareVersionParams(NamedTuple):
    """Validated parameters for the ``compare_version`` rule type."""

    target: str
    operator: str
    value: Union[str, int, float]


class SourceCodeParams(NamedTuple):
    """Validated parameters for the ``source_code_contains`` rule type."""

    keyword: str
    mode: Literal["string", "ast"]


class PackageParams(NamedTuple):
    """Validated parameters for the package declaration rule types."""

    package: str
    file: str


def parse_target(condition: Condition) -> Optional[str]:
    """Return a non-empty ``target`` string from ``condition``, or ``None``."""
    target = condition.get("target")
    return target if isinstance(target, str) and target else None


def parse_compare_version(condition: Condition) -> Optional[CompareVersionParams]:
    """Return validated ``compare_version`` params, or ``None`` if incomplete."""
    target = condition.get("target")
    operator = condition.get("operator")
    value = condition.get("value")
    if (
        isinstance(target, str)
        and target
        and isinstance(operator, str)
        and operator
        and isinstance(value, (str, int, float))
        and not isinstance(value, bool)
    ):
        return CompareVersionParams(target, operator, value)
    return None


def parse_source_code(condition: Condition) -> Optional[SourceCodeParams]:
    """Return validated ``source_code_contains`` params, or ``None``."""
    keyword = condition.get("keyword")
    if not isinstance(keyword, str):
        return None
    if condition.get("mode") == "ast":
        return SourceCodeParams(keyword, "ast")
    return SourceCodeParams(keyword, "string")


def parse_package(condition: Condition) -> Optional[PackageParams]:
    """Return validated package params, falling back from ``package`` to ``target``."""
    package = condition.get("package") or condition.get("target")
    if not isinstance(package, str) or not package:
        return None
    file = condition.get("file", "requirements.txt")
    if not isinstance(file, str) or not file:
        file = "requirements.txt"
    return PackageParams(package, file)


_HOST_JSON_MISSING = object()


def _resolve_host_json_pointer(data: object, parts: List[str]) -> object:
    """Walk a host.json object along dotted ``parts``.

    Returns the resolved node, or ``_HOST_JSON_MISSING`` if any part is absent
    (or an intermediate node is not a dict). An empty ``parts`` list returns
    ``data`` unchanged.
    """
    node: object = data
    for p in parts:
        if isinstance(node, dict) and p in node:
            node = node[p]
        else:
            return _HOST_JSON_MISSING
    return node



_HandlerFn = TypeVar("_HandlerFn", bound=Callable[..., "HandlerResult"])

# Populated at class-definition time by the @_rule_handler decorator:
# maps a rule type -> the HandlerRegistry method name that handles it.
_RULE_DISPATCH: Dict[str, str] = {}


def _rule_handler(func: _HandlerFn) -> _HandlerFn:
    """Register a HandlerRegistry method as the handler for its rule type.

    The rule type is derived from the method name by stripping the
    ``_handle_`` prefix (e.g. ``_handle_compare_version`` -> ``compare_version``).
    """
    _RULE_DISPATCH[func.__name__.removeprefix("_handle_")] = func.__name__
    return func



