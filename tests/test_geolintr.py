import pytest
from geolintr import (
    detect_geo_type, detect_vintages, boundary_changes_between,
    map_ccg_to_icb, map_codes, validate_codes, format_report, summary
)


class TestDetectGeoType:
    def test_lsoa_england(self):
        info = detect_geo_type("E01000001")
        assert info.geo_type == "LSOA"
        assert info.is_known is True
        assert "LSOA" in info.description

    def test_msoa_england(self):
        info = detect_geo_type("E02000576")
        assert info.geo_type == "MSOA"
        assert info.is_known is True

    def test_lad_london_borough(self):
        info = detect_geo_type("E09000019")
        assert info.geo_type == "LAD"
        assert info.is_known is True

    def test_ccg_warns_deprecated(self):
        info = detect_geo_type("E38000240")
        assert info.geo_type == "CCG"
        assert len(info.warnings) > 0
        assert any("CCG" in w or "ICB" in w for w in info.warnings)

    def test_icb(self):
        info = detect_geo_type("E54000028")
        assert info.geo_type == "ICB"
        assert info.is_known is True

    def test_unknown_prefix(self):
        info = detect_geo_type("Z99000001")
        assert info.is_known is False
        assert len(info.warnings) > 0

    def test_lsoa_wales(self):
        info = detect_geo_type("W01000001")
        assert info.geo_type == "LSOA"
        assert info.is_known is True

    def test_strips_whitespace(self):
        info = detect_geo_type("  E01000001  ")
        assert info.is_known is True

    def test_case_insensitive(self):
        info = detect_geo_type("e01000001")
        assert info.is_known is True


class TestDetectVintages:
    def test_clean_codes_returns_info(self):
        codes = ["E54000028", "E54000029", "E54000030"]
        warnings = detect_vintages(codes)
        assert isinstance(warnings, list)
        assert len(warnings) > 0

    def test_ccg_codes_flagged_as_error(self):
        codes = ["E38000240", "E38000244"]
        warnings = detect_vintages(codes)
        errors = [w for w in warnings if w.severity == "error"]
        assert len(errors) > 0
        assert any("CCG" in w.message for w in errors)

    def test_mixed_ccg_and_icb_flagged(self):
        codes = ["E38000240", "E54000028"]
        warnings = detect_vintages(codes)
        errors = [w for w in warnings if w.severity == "error"]
        assert any("CCG" in w.message and "ICB" in w.message for w in errors)

    def test_unknown_codes_flagged(self):
        codes = ["Z99000001", "Z99000002"]
        warnings = detect_vintages(codes)
        warns = [w for w in warnings if w.severity in ("warning", "error")]
        assert len(warns) > 0

    def test_mixed_lad_and_icb_flagged_as_info(self):
        codes = ["E09000019", "E54000028"]
        warnings = detect_vintages(codes)
        infos = [w for w in warnings if w.severity == "info"]
        assert any("LAD" in w.message and "ICB" in w.message for w in infos)


class TestBoundaryChanges:
    def test_returns_changes_in_range(self):
        changes = boundary_changes_between(2021, 2023)
        assert len(changes) > 0
        assert all(2021 <= c["year"] <= 2023 for c in changes)

    def test_ccg_abolition_in_2022(self):
        changes = boundary_changes_between(2022, 2022)
        assert any("CCG" in c["description"] or "ICB" in c["description"] for c in changes)

    def test_no_changes_outside_range(self):
        changes = boundary_changes_between(2000, 2010)
        assert len(changes) == 0

    def test_lsoa_census_2021_change(self):
        changes = boundary_changes_between(2023, 2023)
        assert any("LSOA" in c["description"] or "MSOA" in c["description"] for c in changes)


class TestMapCcgToIcb:
    def test_known_mapping(self):
        result = map_ccg_to_icb("E38000240")
        assert result.found is True
        assert result.target_code == "E54000029"

    def test_unknown_ccg(self):
        result = map_ccg_to_icb("E38000999")
        assert result.found is False
        assert result.target_code is None

    def test_non_ccg_code(self):
        result = map_ccg_to_icb("E54000028")
        assert result.found is False
        assert "E38" in result.message

    def test_case_insensitive(self):
        result = map_ccg_to_icb("e38000240")
        assert result.found is True


class TestMapCodes:
    def test_basic_mapping(self):
        mapping = {"E07000187": "E06000066", "E07000188": "E06000066"}
        results = map_codes(["E07000187", "E07000188"], mapping)
        assert all(r.found for r in results)
        assert all(r.target_code == "E06000066" for r in results)

    def test_missing_code_warn(self):
        results = map_codes(["E07000999"], {}, on_missing="warn")
        assert results[0].found is False
        assert results[0].target_code is None

    def test_missing_code_passthrough(self):
        results = map_codes(["E07000999"], {}, on_missing="passthrough")
        assert results[0].found is False
        assert results[0].target_code == "E07000999"

    def test_missing_code_error(self):
        with pytest.raises(KeyError):
            map_codes(["E07000999"], {}, on_missing="error")


class TestValidateCodes:
    def test_all_valid(self):
        valid_set = {"E54000028", "E54000029"}
        result = validate_codes(["E54000028", "E54000029"], valid_set)
        assert result["coverage"] == 1.0
        assert result["invalid_count"] == 0

    def test_some_invalid(self):
        valid_set = {"E54000028"}
        result = validate_codes(["E54000028", "E54000999"], valid_set)
        assert result["coverage"] == 0.5
        assert result["invalid_count"] == 1
        assert "E54000999" in result["invalid"]

    def test_empty_codes(self):
        result = validate_codes([], {"E54000028"})
        assert result["coverage"] == 0.0
        assert result["total"] == 0


class TestReport:
    def test_format_report_returns_string(self):
        codes = ["E38000240", "E54000028"]
        warnings = detect_vintages(codes)
        report = format_report(warnings)
        assert isinstance(report, str)
        assert "geolintr" in report.lower()

    def test_summary_counts(self):
        codes = ["E38000240", "E54000028"]
        warnings = detect_vintages(codes)
        s = summary(warnings)
        assert "error_count" in s
        assert "warning_count" in s
        assert "has_issues" in s
        assert s["has_issues"] is True
