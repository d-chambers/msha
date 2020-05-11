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
EASTERN_STATE_CODES = ('KY', "WV", "PA", "VA", "TX", "AL", "NY", "TN", "AK",
                  "FL", "VT",)
