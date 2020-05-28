"""
Constants for MSHA.
"""
# Accident classification which are considered ground control
GROUND_CONTROL_CLASSIFICATIONS = {
    "FALL OF ROOF OR BACK",
    "FALL OF FACE/RIB/PILLAR/SIDE/HIGHWALL",
}

NON_INJURY_DEGREES = {
    "ACCIDENT ONLY",
}

SEVERE_INJURY_DEGREES = {
    "PERM TOT OR PERM PRTL DISABLTY",
    "FATALITY",
}

# tuple of eastern state codes as used in the mine_df
EASTERN_STATE_CODES = (
    "KY",
    "WV",
    "PA",
    "VA",
    "TX",
    "AL",
    "NY",
    "TN",
    "AK",
    "FL",
    "VT",
)

# a map of degree injury
DEGREE_MAP = {
    "DAYS AWAY FROM WORK ONLY": 'lost time',
    "NO DYS AWY FRM WRK,NO RSTR ACT": "no lost time",
    "DAYS RESTRICTED ACTIVITY ONLY": "restricted activity",
    "DYS AWY FRM WRK & RESTRCTD ACT": "lost time",
    "ALL OTHER CASES (INCL 1ST AID)": "no lost time",
    "PERM TOT OR PERM PRTL DISABLTY": "fatality/disability",
    'FATALITY': "fatality/disability",
}

DEGREE_ORDER = (
    'fatality/disability',
    'restricted activity',
    'lost time',
    'no lost time',
)
