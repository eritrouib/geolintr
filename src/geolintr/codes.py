"""
Known ONS geography code prefixes and their boundary change history.
Data sourced from ONS Open Geography Portal and published change notices.
"""

# Geography type prefixes
GEO_PREFIXES = {
    "E01": "LSOA (England)",
    "W01": "LSOA (Wales)",
    "N01": "LSOA (Northern Ireland)",
    "E02": "MSOA (England)",
    "W02": "MSOA (Wales)",
    "E06": "Unitary Authority (England)",
    "E07": "Non-metropolitan District (England)",
    "E08": "Metropolitan District (England)",
    "E09": "London Borough",
    "W06": "Unitary Authority (Wales)",
    "S12": "Council Area (Scotland)",
    "N09": "Local Government District (NI)",
    "E10": "County (England)",
    "E11": "Metropolitan County (England)",
    "E12": "Region (England)",
    "E38": "CCG (England) - deprecated 2022",
    "E54": "ICB (England) - from 2022",
    "E40": "NHS England Region",
    "E92": "Country (England)",
    "W92": "Country (Wales)",
    "S92": "Country (Scotland)",
    "N92": "Country (Northern Ireland)",
}

# Major boundary change events
BOUNDARY_CHANGES = [
    {
        "year": 2021,
        "month": 4,
        "description": "LAD restructure - several mergers in England",
        "affected_types": ["E06", "E07", "E08", "E09"],
        "details": "Northamptonshire split into North Northamptonshire and West Northamptonshire. Several Somerset districts merged.",
    },
    {
        "year": 2022,
        "month": 7,
        "description": "CCGs abolished, replaced by ICBs",
        "affected_types": ["E38", "E54"],
        "details": "All 106 Clinical Commissioning Groups (E38) replaced by 42 Integrated Care Boards (E54) on 1 July 2022.",
    },
    {
        "year": 2023,
        "month": 4,
        "description": "LSOA/MSOA boundaries updated for Census 2021",
        "affected_types": ["E01", "W01", "E02", "W02"],
        "details": "ONS redesigned LSOA and MSOA boundaries following Census 2021. New codes issued for all areas.",
    },
    {
        "year": 2023,
        "month": 4,
        "description": "Further LAD restructure",
        "affected_types": ["E06", "E07"],
        "details": "Cumberland and Westmorland and Furness created from former Cumbrian districts. Somerset Council created.",
    },
    {
        "year": 2024,
        "month": 4,
        "description": "LAD restructure - East Midlands and South Yorkshire",
        "affected_types": ["E06", "E07"],
        "details": "Several district councils merged into unitary authorities in Central Lincolnshire and elsewhere.",
    },
]

# CCG to ICB mapping (sample — key CCG codes to their successor ICB)
CCG_TO_ICB = {
    "E38000001": "E54000013",  # NHS Airedale, Wharfedale and Craven -> West Yorkshire
    "E38000010": "E54000028",  # NHS Barking and Dagenham -> North East London
    "E38000011": "E54000029",  # NHS Barnet -> North Central London
    "E38000016": "E54000030",  # NHS Bexley -> South East London
    "E38000018": "E54000033",  # NHS Birmingham and Solihull -> Birmingham and Solihull
    "E38000240": "E54000029",  # NHS North Central London -> North Central London
    "E38000244": "E54000030",  # NHS South East London -> South East London
    "E38000247": "E54000031",  # NHS South West London -> South West London
}

# LSOA 2011 to LSOA 2021 best-fit lookup (sample)
# Full lookup available from ONS: https://geoportal.statistics.gov.uk
LSOA_2011_TO_2021_SAMPLE = {
    "E01000001": "E01000001",  # unchanged
    "E01000002": "E01000002",  # unchanged
    # In reality ~3% of LSOAs changed boundaries
}

KNOWN_VINTAGES = {
    "LSOA": [2001, 2011, 2021],
    "MSOA": [2001, 2011, 2021],
    "LAD": list(range(2011, 2025)),
    "CCG": list(range(2013, 2023)),
    "ICB": [2022, 2023, 2024],
}
