# geolintr

Stop silently joining datasets with mismatched ONS geography boundaries.

```bash
pip install geolintr
```

> **Requires Python 3.9+** · Zero dependencies · Built for UK government and NHS data work

---

## The problem

Every UK government dataset uses ONS geography codes. But those codes change — sometimes quietly and sometimes dramatically:

- CCGs became ICBs in July 2022 (106 areas became 42)
- LSOA and MSOA boundaries were redesigned after Census 2021
- Local authority districts merge and split regularly
- Terminated postcodes still appear in older datasets

When you join two datasets with codes from different years, the join silently succeeds but the results are wrong. **geolintr catches this before it causes problems.**

---

## Quick start

```python
from geolintr import detect_vintages, format_report

# Check a list of codes from your dataset
codes = ["E38000240", "E38000244", "E54000028", "E54000029"]

warnings = detect_vintages(codes)
print(format_report(warnings))
```

Output:
```
============================================================
  geolintr report
============================================================
  2 error(s)  0 warning(s)  1 info(s)
============================================================

[ERROR] 2 CCG code(s) found (E38 prefix). CCGs were abolished on 1 July 2022 and replaced by ICBs (E54).
       Codes: E38000240, E38000244
       Tip:   Use geolintr.map_ccg_to_icb() to convert CCG codes to their ICB successors.

[ERROR] Both CCG (pre-2022) and ICB (post-2022) codes found. These represent different organisational boundaries.
       Codes: E38000240, E38000244, E54000028, E54000029
       Tip:   Standardise to ICB using geolintr.map_ccg_to_icb().
```

---

## Detect geography type

```python
from geolintr import detect_geo_type

info = detect_geo_type("E38000240")
info.geo_type     # "CCG"
info.description  # "CCG (England) - deprecated 2022"
info.warnings     # ["E38000240 appears to be a CCG code. CCGs were replaced by ICBs in July 2022."]

info = detect_geo_type("E54000028")
info.geo_type     # "ICB"
info.is_known     # True
```

---

## Map CCG codes to ICB

```python
from geolintr import map_ccg_to_icb

result = map_ccg_to_icb("E38000240")
result.found        # True
result.target_code  # "E54000029"
result.message      # "Mapped CCG E38000240 to ICB E54000029."
```

---

## Map any codes using a custom lookup

```python
from geolintr import map_codes

# e.g. after a LAD merger
old_to_new = {
    "E07000187": "E06000066",  # Kettering -> North Northamptonshire
    "E07000188": "E06000066",  # Corby -> North Northamptonshire
}

results = map_codes(my_lad_codes, old_to_new, on_missing="warn")
for r in results:
    if not r.found:
        print(f"No mapping for {r.source_code}")
```

---

## Validate codes against a known set

```python
from geolintr import validate_codes

valid_icbs = {"E54000028", "E54000029", "E54000030"}
result = validate_codes(my_codes, valid_icbs)

result["coverage"]      # 0.94 — 94% of codes matched
result["invalid"]       # list of unrecognised codes
result["invalid_count"] # how many failed
```

---

## What changed and when

```python
from geolintr import boundary_changes_between

changes = boundary_changes_between(2021, 2023)
for c in changes:
    print(f"{c['year']}: {c['description']}")

# 2021: LAD restructure - several mergers in England
# 2022: CCGs abolished, replaced by ICBs
# 2023: LSOA/MSOA boundaries updated for Census 2021
# 2023: Further LAD restructure
```

---

## Supported geography types

| Prefix | Type | Notes |
|--------|------|-------|
| E01/W01/N01 | LSOA | Redesigned after Census 2021 |
| E02/W02 | MSOA | Redesigned after Census 2021 |
| E06-E09/W06/S12/N09 | LAD | Changes annually |
| E38 | CCG | Abolished July 2022 |
| E54 | ICB | Replaced CCGs July 2022 |
| E40 | NHS England Region | Stable |
| E12 | Region | Stable |
| E92/W92/S92/N92 | Country | Stable |

---

## Why geolintr

If you work with UK open data, you have almost certainly joined datasets with mismatched boundaries without realising. The results look plausible, but the numbers are wrong. geolintr makes this class of error visible and fixable.

Built by someone who hits this issue everyday.

---

## License

MIT
