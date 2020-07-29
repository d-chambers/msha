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
    "DAYS AWAY FROM WORK ONLY": "lost time",
    "NO DYS AWY FRM WRK,NO RSTR ACT": "no lost time",
    "DAYS RESTRICTED ACTIVITY ONLY": "restricted activity",
    "DYS AWY FRM WRK & RESTRCTD ACT": "lost time",
    "ALL OTHER CASES (INCL 1ST AID)": "no lost time",
    "PERM TOT OR PERM PRTL DISABLTY": "fatality/disability",
    "FATALITY": "fatality/disability",
}

DEGREE_ORDER = (
    "fatality/disability",
    "restricted activity",
    "lost time",
    "no lost time",
)


# Words which only occur in rockbust narratives and not in non-rockburst ones
STRICTLY_ROCKBURST_WORDS = {
    'rib bounce',
    'rib bump',
    'rib burst',
    'coal bounce',
    'coal burst',
    "mine bounce",
    'coal bump',
    'top bounce',
    "bottom bump",
    'pillar bounce',
    'outburst',
    'outbursts',
    'rockburst',
    'rockbursts',
    'mountain bump',
    'top bump',
    'top bounce',
    "face bounce",
    "face bump",
    "face burst",
    "burst rib",
    "had burst",
    "floor burst",
    "floor heave",
    "floor bounce",
    "roof bump",
    "roof burst",
    'burst',
    # these are clearly overfitting on crapy grammer
    'bounce on tail1ate',
    "SUDDENLY BURST".lower(),
    "OLUTBURST".lower(),
    "BOUNCED OCCURED".lower(),
    "bumped-coal",
    "severe bounce",
    "outrburst",
    "when it bounced",

}

ROCKBURSTY_WORDS = (
    "bump",
    "bumps",
    "bump(s)",
    "coal bump",
    "coal bounce",
    "burst",
    "bounce",
    "bounces",
    'bounced',
    'bursted',
    "rockburst",
    "outburst",
    "rockbursts",
    "outbursts",
)

THINGS_THAT_BURST = (
    'top', 'back', 'pillar', 'coal', 'floor', 'rib',
)
