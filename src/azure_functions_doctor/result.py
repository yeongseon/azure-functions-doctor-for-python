from dataclasses import asdict, dataclass
from typing import Any, Dict, Literal


@dataclass
class DiagnosticResult:
    check: str
    result: Literal["pass", "fail", "warn"]
    detail: str
    recommendation: str
    docs_url: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
