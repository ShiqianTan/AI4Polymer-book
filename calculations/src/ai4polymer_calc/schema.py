"""Small explicit accounting records shared by all polymer representation adapters."""
from dataclasses import dataclass, asdict
import json
import math

from .units import positive_int, fraction

SCHEMA_VERSION = 1
REQUIRED_KEYS = ("schema_version", "calculation", "model", "scenario", "sources", "summary", "assumptions")
OPTIONAL_KEYS = ("selected_peak",)
ARCHITECTURES = ("homopolymer", "random", "block", "alternating")


@dataclass(frozen=True)
class Polymer:
    name: str
    monomers: int
    chain_length: int
    architecture: str = "homopolymer"

    def __post_init__(self):
        positive_int(self.monomers, "monomers")
        positive_int(self.chain_length, "chain_length")
        if self.architecture not in ARCHITECTURES:
            raise ValueError("architecture must be one of " + ", ".join(ARCHITECTURES))

    @property
    def distinct_sequences(self) -> int:
        return sequence_count(self.monomers, self.chain_length, self.architecture)

    def record(self) -> dict:
        return {**asdict(self), "distinct_sequences": self.distinct_sequences}


@dataclass(frozen=True)
class Descriptor:
    name: str
    kind: str
    dimension: int
    element_bytes: int
    note: str = ""

    def __post_init__(self):
        if not self.name:
            raise ValueError("descriptor name is required")
        positive_int(self.dimension, "descriptor dimension")
        positive_int(self.element_bytes, "descriptor element_bytes")

    @property
    def bytes_per_molecule(self) -> int:
        return self.dimension * self.element_bytes

    @property
    def bits_per_molecule(self) -> int:
        return self.bytes_per_molecule * 8

    def record(self) -> dict:
        return {**asdict(self), "bytes_per_molecule": self.bytes_per_molecule,
                "bits_per_molecule": self.bits_per_molecule}


@dataclass(frozen=True)
class Graph:
    atoms: int
    bonds: int
    atom_feature_dim: int = 64
    bond_feature_dim: int = 16
    element_bytes: int = 1

    def __post_init__(self):
        positive_int(self.atoms, "atoms")
        positive_int(self.bonds, "bonds", allow_zero=True)
        positive_int(self.atom_feature_dim, "atom_feature_dim")
        positive_int(self.bond_feature_dim, "bond_feature_dim")
        positive_int(self.element_bytes, "element_bytes")

    @property
    def feature_dim(self) -> int:
        return self.atoms * self.atom_feature_dim + self.bonds * self.bond_feature_dim

    @property
    def bytes_per_molecule(self) -> int:
        return self.feature_dim * self.element_bytes

    def record(self) -> dict:
        return {**asdict(self), "feature_dim": self.feature_dim,
                "bytes_per_molecule": self.bytes_per_molecule}


def sequence_count(monomers: int, chain_length: int, architecture: str) -> int:
    """Exact big-integer sequence count for one declared copolymer architecture."""
    positive_int(monomers, "monomers")
    positive_int(chain_length, "chain_length")
    if architecture == "homopolymer":
        return monomers
    if architecture == "random":
        return monomers ** chain_length
    if architecture == "alternating":
        if chain_length < 2:
            return 0
        return monomers * (monomers - 1)
    if architecture == "block":
        if chain_length < 2:
            return 0
        return monomers * (monomers - 1) * (chain_length - 1)
    raise ValueError("architecture must be one of " + ", ".join(ARCHITECTURES))


def sequences_at_most_k_types(monomers: int, chain_length: int, max_distinct: int) -> int:
    """Sequences over a pool of `monomers` types that use at most `max_distinct` distinct types."""
    positive_int(monomers, "monomers")
    positive_int(chain_length, "chain_length")
    positive_int(max_distinct, "max_distinct")
    total = 0
    stirling = [0] * (chain_length + 1)
    stirling[0] = 1
    for length in range(1, chain_length + 1):
        updated = [0] * (chain_length + 1)
        for parts in range(1, length + 1):
            updated[parts] = stirling[parts - 1] + parts * stirling[parts]
        stirling = updated
    from math import comb, factorial
    for parts in range(1, min(max_distinct, monomers, chain_length) + 1):
        total += comb(monomers, parts) * factorial(parts) * stirling[parts]
    return total


def parse_stoichiometry(text: str, monomers: int) -> tuple[float, ...]:
    parts = [piece.strip() for piece in str(text).split(",") if piece.strip()]
    if not parts:
        raise ValueError("stoichiometry must list at least one positive number")
    values = []
    for piece in parts:
        try:
            value = float(piece)
        except ValueError as error:
            raise ValueError(f"stoichiometry entry {piece!r} is not a number") from error
        values.append(fraction(value, "stoichiometry entry"))
    if len(values) > monomers:
        raise ValueError("stoichiometry lists more monomers than the declared pool")
    total = sum(values)
    return tuple(value / total for value in values)


def result(*, calculation: str, model: str, scenario: dict, sources: list,
           summary: dict, assumptions: list, selected_peak: dict | None = None) -> dict:
    """Assemble the fixed result contract and reject any non-finite number."""
    payload = {
        "schema_version": SCHEMA_VERSION,
        "calculation": calculation,
        "model": model,
        "scenario": scenario,
        "sources": sources,
        "summary": summary,
        "assumptions": assumptions,
    }
    if selected_peak is not None:
        payload["selected_peak"] = selected_peak
    validate_result(payload)
    return payload


def validate_result(payload: dict) -> None:
    if not isinstance(payload, dict):
        raise ValueError("result must be a JSON object")
    keys = set(payload)
    missing = set(REQUIRED_KEYS) - keys
    extra = keys - set(REQUIRED_KEYS) - set(OPTIONAL_KEYS)
    if missing:
        raise ValueError("result lacks required keys: " + ", ".join(sorted(missing)))
    if extra:
        raise ValueError("result has unexpected top-level keys: " + ", ".join(sorted(extra)))
    if payload["schema_version"] != SCHEMA_VERSION:
        raise ValueError("schema_version must be 1")
    for name in ("calculation", "model"):
        if not isinstance(payload[name], str) or not payload[name]:
            raise ValueError(f"{name} must be a nonempty string")
    for name in ("scenario", "summary"):
        if not isinstance(payload[name], dict):
            raise ValueError(f"{name} must be a JSON object")
    if not isinstance(payload["sources"], list) or not payload["sources"]:
        raise ValueError("sources must be a nonempty list")
    if not isinstance(payload["assumptions"], list) or not payload["assumptions"]:
        raise ValueError("assumptions must be a nonempty list")
    for statement in payload["assumptions"]:
        if not isinstance(statement, str) or not statement.strip():
            raise ValueError("assumptions must be nonempty strings")
    _reject_non_finite(payload)
    json.dumps(payload, ensure_ascii=False, allow_nan=False)


def _reject_non_finite(value) -> None:
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("result contains a non-finite number")
    elif isinstance(value, dict):
        for item in value.values():
            _reject_non_finite(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            _reject_non_finite(item)


def to_json(payload: dict) -> str:
    validate_result(payload)
    return json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n"


def read_json_object(path) -> dict:
    """Load a JSON object while rejecting NaN/Infinity and non-object roots."""
    text = path.read_text(encoding="utf-8")
    payload = json.loads(text, parse_constant=_reject_constant)
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return payload


def _reject_constant(token: str):
    raise ValueError(f"JSON constant {token} is not permitted")
