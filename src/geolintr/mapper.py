"""
Map between different ONS geography vintages.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from .codes import CCG_TO_ICB


@dataclass
class MappingResult:
    """Result of a geography code mapping operation."""
    source_code: str
    target_code: str | None
    found: bool
    ambiguous: bool = False
    message: str | None = None


def map_ccg_to_icb(ccg_code: str) -> MappingResult:
    """
    Map a CCG code (pre-July 2022) to its successor ICB code.

    Args:
        ccg_code: An E38 CCG code e.g. 'E38000240'

    Returns:
        MappingResult with the ICB code if found
    """
    ccg_code = ccg_code.strip().upper()

    if not ccg_code.startswith("E38"):
        return MappingResult(
            source_code=ccg_code,
            target_code=None,
            found=False,
            message=f"{ccg_code} does not appear to be a CCG code (expected E38 prefix)."
        )

    icb = CCG_TO_ICB.get(ccg_code)
    if icb:
        return MappingResult(
            source_code=ccg_code,
            target_code=icb,
            found=True,
            message=f"Mapped CCG {ccg_code} to ICB {icb}."
        )

    return MappingResult(
        source_code=ccg_code,
        target_code=None,
        found=False,
        message=(
            f"No built-in mapping found for {ccg_code}. "
            "For the full CCG-to-ICB lookup, use the ONS Open Geography Portal: "
            "https://geoportal.statistics.gov.uk"
        )
    )


def map_codes(
    codes: list[str],
    mapping: dict[str, str],
    on_missing: str = "warn",
) -> list[MappingResult]:
    """
    Map a list of codes using a provided lookup dictionary.

    Args:
        codes:      List of source codes to map
        mapping:    Dict of {source_code: target_code}
        on_missing: What to do when a code isn't in the mapping.
                    'warn' (default), 'error', or 'passthrough'

    Returns:
        List of MappingResult objects

    Example:
        # Map old LAD codes to new ones after a merger
        old_to_new = {"E07000187": "E06000066", "E07000188": "E06000066"}
        results = map_codes(my_lad_codes, old_to_new)
    """
    results = []
    for code in codes:
        code = code.strip().upper()
        target = mapping.get(code)
        if target:
            results.append(MappingResult(source_code=code, target_code=target, found=True))
        else:
            if on_missing == "error":
                raise KeyError(f"No mapping found for code: {code}")
            results.append(MappingResult(
                source_code=code,
                target_code=code if on_missing == "passthrough" else None,
                found=False,
                message=f"No mapping found for {code}."
            ))
    return results


def validate_codes(codes: list[str], valid_set: set[str]) -> dict[str, Any]:
    """
    Validate a list of ONS codes against a known valid set.

    Args:
        codes:      List of codes to validate
        valid_set:  Set of valid codes to check against

    Returns:
        Dict with 'valid', 'invalid', and 'coverage' keys

    Example:
        valid_icbs = {"E54000028", "E54000029", "E54000030"}
        result = validate_codes(my_codes, valid_icbs)
        print(result['coverage'])  # 0.95
    """
    codes_upper = [c.strip().upper() for c in codes]
    valid = [c for c in codes_upper if c in valid_set]
    invalid = [c for c in codes_upper if c not in valid_set]
    coverage = len(valid) / len(codes_upper) if codes_upper else 0.0

    return {
        "valid": valid,
        "invalid": invalid,
        "coverage": round(coverage, 4),
        "total": len(codes_upper),
        "valid_count": len(valid),
        "invalid_count": len(invalid),
    }
