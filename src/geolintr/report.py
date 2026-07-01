"""
Generate human-readable reports from geolintr analysis.
"""
from __future__ import annotations
from .detector import VintageWarning


SEVERITY_ICONS = {"error": "ERROR", "warning": "WARN", "info": "INFO"}


def format_report(warnings: list[VintageWarning], title: str = "geolintr report") -> str:
    """
    Format a list of VintageWarnings as a human-readable report.

    Args:
        warnings: List of VintageWarning objects from detect_vintages()
        title:    Report title

    Returns:
        Formatted string report
    """
    lines = [
        f"{'=' * 60}",
        f"  {title}",
        f"{'=' * 60}",
    ]

    errors = [w for w in warnings if w.severity == "error"]
    warns = [w for w in warnings if w.severity == "warning"]
    infos = [w for w in warnings if w.severity == "info"]

    lines.append(f"  {len(errors)} error(s)  {len(warns)} warning(s)  {len(infos)} info(s)")
    lines.append(f"{'=' * 60}")

    for w in warnings:
        icon = SEVERITY_ICONS.get(w.severity, "INFO")
        lines.append(f"\n[{icon}] {w.message}")
        if w.codes:
            sample = w.codes[:5]
            suffix = f" ... and {len(w.codes) - 5} more" if len(w.codes) > 5 else ""
            lines.append(f"       Codes: {', '.join(sample)}{suffix}")
        if w.suggestion:
            lines.append(f"       Tip:   {w.suggestion}")

    lines.append(f"\n{'=' * 60}")
    return "\n".join(lines)


def summary(warnings: list[VintageWarning]) -> dict:
    """
    Return a summary dict from a list of warnings.

    Returns:
        Dict with error_count, warning_count, info_count, has_issues
    """
    return {
        "error_count": sum(1 for w in warnings if w.severity == "error"),
        "warning_count": sum(1 for w in warnings if w.severity == "warning"),
        "info_count": sum(1 for w in warnings if w.severity == "info"),
        "has_issues": any(w.severity in ("error", "warning") for w in warnings),
    }
