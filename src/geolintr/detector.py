"""
Detect the geography type and likely vintage of ONS codes.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from .codes import GEO_PREFIXES, KNOWN_VINTAGES, BOUNDARY_CHANGES


@dataclass
class CodeInfo:
    """Information about a single ONS geography code."""
    code: str
    geo_type: str | None
    description: str | None
    is_known: bool
    warnings: list[str] = field(default_factory=list)


@dataclass 
class VintageWarning:
    """Warning about a potential vintage mismatch."""
    message: str
    severity: str  # "error", "warning", "info"
    codes: list[str] = field(default_factory=list)
    suggestion: str | None = None


def detect_geo_type(code: str) -> CodeInfo:
    """
    Detect the ONS geography type from a code.

    Args:
        code: An ONS geography code e.g. 'E01000001', 'E38000240'

    Returns:
        CodeInfo with detected type and any warnings
    """
    if not isinstance(code, str):
        return CodeInfo(code=str(code), geo_type=None, description=None, is_known=False,
                       warnings=["Code is not a string"])

    code = code.strip().upper()
    warnings = []

    # Check prefix
    prefix = code[:3] if len(code) >= 3 else ""
    description = GEO_PREFIXES.get(prefix)
    geo_type = _prefix_to_type(prefix)

    if not description:
        return CodeInfo(code=code, geo_type=None, description=None, is_known=False,
                       warnings=[f"Unknown geography prefix: {prefix!r}"])

    # Warn about deprecated types
    if "deprecated" in (description or "").lower():
        warnings.append(f"{code} appears to be a CCG code (E38). CCGs were replaced by ICBs in July 2022.")

    return CodeInfo(code=code, geo_type=geo_type, description=description,
                   is_known=True, warnings=warnings)


def _prefix_to_type(prefix: str) -> str | None:
    type_map = {
        "E01": "LSOA", "W01": "LSOA", "N01": "LSOA",
        "E02": "MSOA", "W02": "MSOA",
        "E06": "LAD", "E07": "LAD", "E08": "LAD", "E09": "LAD",
        "W06": "LAD", "S12": "LAD", "N09": "LAD",
        "E10": "LAD", "E11": "LAD",
        "E12": "RGN",
        "E38": "CCG",
        "E54": "ICB",
        "E40": "NHSER",
        "E92": "CTRY", "W92": "CTRY", "S92": "CTRY", "N92": "CTRY",
    }
    return type_map.get(prefix)


def detect_vintages(codes: list[str]) -> list[VintageWarning]:
    """
    Analyse a list of ONS codes and detect potential vintage mismatches.

    Args:
        codes: List of ONS geography codes

    Returns:
        List of VintageWarning objects describing any issues found
    """
    warnings = []
    
    # Group by type
    by_type: dict[str, list[str]] = {}
    unknown = []
    deprecated = []

    for code in codes:
        info = detect_geo_type(code)
        if not info.is_known:
            unknown.append(code)
        else:
            geo_type = info.geo_type or "UNKNOWN"
            by_type.setdefault(geo_type, []).append(code)
            if any("deprecated" in w.lower() or "ccg" in w.lower() for w in info.warnings):
                deprecated.append(code)

    # Warn about unknown codes
    if unknown:
        warnings.append(VintageWarning(
            message=f"{len(unknown)} unrecognised ONS code(s) found.",
            severity="warning",
            codes=unknown,
            suggestion="Check these are valid ONS codes from the ONS Open Geography Portal."
        ))

    # Warn about deprecated CCG codes
    if deprecated:
        warnings.append(VintageWarning(
            message=f"{len(deprecated)} CCG code(s) found (E38 prefix). CCGs were abolished on 1 July 2022 and replaced by ICBs (E54).",
            severity="error",
            codes=deprecated,
            suggestion="Use geolintr.map_ccg_to_icb() to convert CCG codes to their ICB successors."
        ))

    # Warn about mixing LSOA 2011 and 2021 codes
    lsoa_codes = by_type.get("LSOA", [])
    if lsoa_codes:
        mixed = _check_lsoa_vintage_mix(lsoa_codes)
        if mixed:
            warnings.append(VintageWarning(
                message="Possible mix of LSOA 2011 and LSOA 2021 codes detected. Boundaries changed significantly after Census 2021.",
                severity="warning",
                codes=lsoa_codes,
                suggestion="Ensure all LSOA codes are from the same census vintage. Use ONS LSOA best-fit lookup to harmonise."
            ))

    # Warn about mixing LAD and ICB (common mistake — different geographies)
    if "LAD" in by_type and "ICB" in by_type:
        warnings.append(VintageWarning(
            message="Both LAD and ICB codes detected in the same dataset. These are different geography types and cannot be directly joined.",
            severity="info",
            codes=by_type.get("LAD", [])[:3] + by_type.get("ICB", [])[:3],
            suggestion="Use a postcode lookup to bridge between LAD and ICB geographies."
        ))

    # Warn about mixing CCG and ICB
    if "CCG" in by_type and "ICB" in by_type:
        warnings.append(VintageWarning(
            message="Both CCG (pre-2022) and ICB (post-2022) codes found. These represent different organisational boundaries.",
            severity="error",
            codes=by_type.get("CCG", [])[:3] + by_type.get("ICB", [])[:3],
            suggestion="Standardise to ICB using geolintr.map_ccg_to_icb()."
        ))

    if not warnings:
        warnings.append(VintageWarning(
            message="No vintage issues detected.",
            severity="info",
            codes=[],
            suggestion=None
        ))

    return warnings


def _check_lsoa_vintage_mix(codes: list[str]) -> bool:
    """
    Heuristic check for mixed LSOA vintages.
    LSOA 2021 codes are generally higher numbered than 2011 codes for the same area.
    This is a best-effort detection only.
    """
    # In practice, detecting mixed vintages requires comparing against
    # the full ONS lookup tables. This is a placeholder heuristic.
    # Real implementation would compare against ONSPD vintage data.
    return False


def boundary_changes_between(year_from: int, year_to: int) -> list[dict]:
    """
    Return all known boundary changes between two years.

    Args:
        year_from: Start year (inclusive)
        year_to: End year (inclusive)

    Returns:
        List of boundary change events
    """
    return [
        change for change in BOUNDARY_CHANGES
        if year_from <= change["year"] <= year_to
    ]
