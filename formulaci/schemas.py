"""Shared record schemas. Owned by the coordinator. See SPEC.md."""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


class Formula(BaseModel):
    formula_id: str
    source: str = "wikipedia"
    lang: str = "en"
    page_title: str
    page_id: int
    revision_id: int
    url: str
    section: str = ""
    index: int
    latex: str
    display: bool = False
    context_before: str = ""
    context_after: str = ""
    page_categories: list[str] = Field(default_factory=list)


class Parsed(BaseModel):
    formula_id: str
    status: Literal["ok", "unparsed", "not_checkable"]
    kind: Literal["equation", "chain", "inequality", "definition_like", "other"] = "other"
    index_in_chain: Optional[int] = None
    relation: Optional[str] = None
    lhs: Optional[str] = None
    rhs: Optional[str] = None
    free_symbols: list[str] = Field(default_factory=list)
    functions: list[str] = Field(default_factory=list)
    has_unsupported: list[str] = Field(default_factory=list)
    error: Optional[str] = None
    translator: str = ""
    notes: Optional[str] = None


class Domain(BaseModel):
    type: Literal[
        "real", "positive", "nonneg", "integer", "nonneg_integer", "positive_integer",
        "complex", "unit_interval", "angle",
    ] = "real"
    lower: Optional[float] = None
    upper: Optional[float] = None
    exclude: list[float] = Field(default_factory=list)


class Semantics(BaseModel):
    formula_id: str
    checkable: bool = True
    skip_reason: Optional[str] = None
    domains: dict[str, Domain] = Field(default_factory=dict)
    constants: dict[str, str] = Field(default_factory=dict)
    constraints: list[str] = Field(default_factory=list)
    assumptions_source: list[str] = Field(default_factory=list)
    backend: str = "rules"


class RegimeResult(BaseModel):
    name: str
    n_points: int
    n_fail: int
    n_error: int


class Counterexample(BaseModel):
    assignments: dict[str, str]
    lhs: str
    rhs: str
    abs_diff: str
    rel_diff: str


class Tolerance(BaseModel):
    abs: float = 1e-20
    rel: float = 1e-8
    dps: int = 50


class Verdict(BaseModel):
    formula_id: str
    verdict: Literal["PASS", "FAIL", "INCONCLUSIVE", "SKIP"]
    symbolic: Literal["equal", "not_equal", "unknown"] = "unknown"
    regimes: list[RegimeResult] = Field(default_factory=list)
    counterexample: Optional[Counterexample] = None
    tolerance: Tolerance = Field(default_factory=Tolerance)
    reason: str = ""


class Review(BaseModel):
    status: Literal["unreviewed", "confirmed_error", "false_positive", "ambiguous"] = "unreviewed"
    reviewer: str = ""
    notes: str = ""


class Finding(BaseModel):
    formula_id: str
    verdict: str
    confidence: float = 0.0
    review: Review = Field(default_factory=Review)
    suggested_fix: Optional[str] = None
    evidence: str = ""


def read_jsonl(path, model):
    """Yield `model` instances from a JSONL file; tolerate blank lines."""
    import json
    from pathlib import Path

    p = Path(path)
    if not p.exists():
        return
    with p.open() as f:
        for line in f:
            line = line.strip()
            if line:
                yield model.model_validate(json.loads(line))


def append_jsonl(path, records):
    """Append pydantic records to a JSONL file, creating parents."""
    from pathlib import Path

    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a") as f:
        for r in records:
            f.write(r.model_dump_json() + "\n")


def existing_ids(path, model):
    return {r.formula_id for r in read_jsonl(path, model)}
