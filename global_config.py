"""
Gaming Platform Data Module

This module contains the platform data and constants used for OCR similarity matching.
"""

import re
from functools import lru_cache
from typing import Dict, List, Set, Tuple

# Pre-compile regex patterns for performance
PUNCTUATION_PATTERN = re.compile(r'[^\w\s]')
MULTI_SPACE_PATTERN = re.compile(r'\s+')
WORD_BOUNDARY_PATTERN = re.compile(r'\b')

# Define gaming platforms with common OCR variations and misspellings
GAMING_PLATFORMS = {
    "playstation": [
        # Basic variations
        "playstation", "playstaton", "playsation", "play station", "playstatlon", 
        "playstatidn", "pleystation", "plaustation", "playststion", "piaystation",
        "playstotion", "plsyst", "plsystn", "playstatn", "plstation", "playet",
        "ploystafion", "playxtation", "p|aystation", "playsration",
        
        # Model numbers and variations
        "ps4", "ps5", "ps3", "ps2", "ps1", "psx", "p54", "p55", "p53", "p52", "p51",
        "ps 4", "ps 5", "ps 3", "ps 2", "ps 1", "ps x", "p s4", "p s5", "playstation4",
        "playstation5", "playstation3", "playstation2", "playstation1", "playstationx",
        "ps4 pro", "ps5 pro", "ps4pro", "ps5pro", "ps 4 pro", "ps 5 pro",
        
        # Brand associations
        "sony playstation", "sony play station", "sony", "sonyplay", "s0ny", "s0ny playstation",
        "sony ps", "somy playstation", "sanyo playstation",  # common OCR errors
        
        # Severe OCR errors
        "play statian", "plehstatien", "pfaystation", "plavstanon", "playstaticn",
        "olavstation", "pleystetion", "playststn", "playstatinn", "p|aystatlon",
        "p1aystation", "playstat|on", "p!aystation", "plays+ation", "plcystation",
        "piayst", "playztation", "plays7ation", "play$tation", "playstation®",
        "play-station", "play.station",
        
        # Fragments that likely indicate PlayStation
        "dualshock", "dualsense", "dualsh", "dualsens", "dual shock", "dual sense"
    ],
    "xbox": [
        # Basic variations
        "xbox", "xbax", "x box", "x-box", "xboxx", "xbx", "xb0x", "xhox", "xdox",
        "xboc", "xboe", "xb", "xbex", "x b o x", "x-b-o-x", "x80x", "×box", "xhox",
        "×b0×", "xbnx", "×b0x", "xbux", "xbax", "×bo×", "xbcx", "×box", "xb9x",
        
        # Model variations
        "xbox one", "xbox series", "xbox series x", "xbox series s", 
        "xboxone", "xboxseriesx", "xboxseriess", "xboxserjes", "xboxseries×",
        "xbox one x", "xbox one s", "xboxonex", "xboxones", "xbox1", "xbox 1",
        "x box one", "x-box one", "x box series", "series x", "series s",
        "xbox 360", "xbox360", "x360", "x 360", "360", "xbox live", "xbl",
        
        # Brand associations
        "microsoft xbox", "microsoft", "msft xbox", "ms xbox", "micr0s0ft xbox",
        
        # Severe OCR errors
        "×b0× one", "×box series", "xb0x ser1es", "xbax 0ne", "xbux series", "×b0× series ×",
        "xb serles", "x bax", "x b0x", "×-box", "xbo×", "×box", "x-b-o-x", "x. box",
        "x_box", "x/box", "x.b.o.x", "x, box", "xboc one", "xboc series",
        
        # Controller related
        "controller for xbox", "xbox controller", "xb controller", "xbox gamepad",
        "xbox wireless", "xinput"
    ],
    "nintendo": [
        # Basic variations
        "nintendo", "nintondo", "nintend0", "nlntendo", "nlntend0", "nintenda", 
        "nitendo", "nintedo", "ninten", "nihtendo", "nintehdo", "nntendo", "nitend",
        "nlntend", "nlntand", "ninfendo", "nintondo", "n1ntendo", "nlnt", "nin10do",
        "nirtendo", "nlmtendo", "n!ntendo", "ninte", "ndo", "n|ntendo", "n7ntendo",
        
        # Switch variations
        "switch", "swtch", "swltch", "nintendo switch", "nintindo switch", "nintemdo switch",
        "switch console", "nintendo swltch", "nlntendo switch", "nitend switch", "nln switch",
        "switch gaming", "swich", "swi+ch", "switoh", "swikh", "zwitch", "svvitch", "svvltch",
        "nintendo sw", "nintnd sw", "nin10do sw", "nin sw", "switch lite",
        
        # Wii variations
        "wii", "wiiu", "wil", "wll", "nintendo wii", "wlio", "wlie", "wiii", "wi",
        "wii u", "wii console", "wiimote", "wii remote", "wii fit", "vvii", "vvil",
        "wil u", "wll u", "vvilu", "vvii u", "wiifi", "wii sports", "wii play",
        
        # N64 variations
        "n64", "n-64", "n 64", "nlntendo 64", "nintendo64", "nintendo 64", "n6a",
        "n 6a", "nin64", "nin 64", "n-sixty-four", "n.64", "n.6.4", "n sixty four",
        
        # GameCube variations
        "gamecube", "game cube", "game-cube", "nintendogamecube", "gome cube",
        "gamecube console", "gcn", "gc", "nintendo gc", "nintendo gcn", "game qube",
        "gameqube", "game cuhe", "gome cuhe", "gcube", "g cube", "g-cube",
        
        # Handheld variations
        "3ds", "2ds", "3 ds", "2 ds", "nintend0 3ds", "nintendo3ds", "nintendo 3ds",
        "nintendo 2ds", "nintendo2ds", "ninten 3ds", "ninten 2ds", "3d5", "2d5",
        "3 d5", "2 d5", "3ds xl", "new 3ds", "new 2ds", "3dsxl", "new3ds", "new2ds"
    ],
    "pc": [
        # Basic variations
        "pc", "p c", "pc gaming", "personal computer", "desktop", "gaming pc", 
        "gaming p c", "windows", "win", "windowz", "p-c", "stearn", "steam",
        "computer", "laptop", "p.c.", "pc game", "p.c. game", "pc-game",
        "p.c gaming", "pee-cee", "p_c", "pc.", ".pc", "(pc)", "[pc]", "{pc}",
        "p>c", "p<c", "p^c", "p=c", "pc=", "p=c=", "p/ c", "p\\c", "p|c",
        
        # Windows variations
        "windows 10", "windows 11", "win10", "win11", "win 10", "win 11",
        "windows ten", "windows eleven", "microsoft windows", "ms windows",
        "window", "windoze", "winblows", "windos", "wndws", "win7", "win8", 
        "windows7", "windows8", "windows 7", "windows 8",
        
        # Gaming related
        "steam deck", "steamdeck", "steam platform", "valve", "valve steam",
        "steam download", "steam key", "steam version", "origin", "ea origin",
        "epic games", "epic", "epic store", "epic game store", "battle.net", "battlenet",
        "uplay", "ubisoft connect", "gog", "good old games", "gog.com"
    ],
    "sega": [
        # Basic variations
        "sega", "saga", "sege", "segc", "sogo", "sego", "seg", "5ega", "s3ga", "segd",
        "cega", "zega", "seqa", "se9a", "se6a", "seva", "s€ga", "s€6a", "segα", "s-ga",
        
        # Console variations
        "dreamcast", "dream cast", "dream-cast", "dreamcost", "drecmcast", "dreomcast",
        "dreamc", "drcast", "drm cst", "drmcst", "dreamcas+", "dreamcas7", "drecmcas+",
        "sega saturn", "saturn", "soturn", "sega genesis", "genesis", "mega drive",
        "megadrive", "mega-drive", "mego drive", "master system", "mastersystem",
        "game gear", "gamegear", "sg-1000", "sg1000", "sega cd", "segacd", "32x",
        "sega 32x", "sega32x", "pico", "sega pico", "segapico"
    ]
}

# Pre-process data for faster lookup
PLATFORM_TERM_CATEGORY = {}  # Maps term to its platform category
ALL_PLATFORM_TERMS = []      # List of all platform terms

for platform, terms in GAMING_PLATFORMS.items():
    for term in terms:
        ALL_PLATFORM_TERMS.append(term)
        PLATFORM_TERM_CATEGORY[term] = platform

# Gaming context markers that can help identify platform references
CONTEXT_MARKERS = [
    'game', 'gaming', 'console', 'play', 'system', 'version', 'compatible',
    'controller', 'works on', 'for', 'playable', 'available on', 'platform'
]

# High-confidence platform indicators
HIGH_CONFIDENCE_INDICATORS = {
    'playstation': ['ps5', 'ps4', 'ps3', 'dualshock', 'dualsense', 'sony', 'ps plus'],
    'xbox': ['series x', 'series s', 'xbox one', 'xbox live', 'game pass', 'microsoft'],
    'nintendo': ['switch', 'wiiu', 'joycon', 'joy-con', '3ds', 'amiibo'],
    'pc': ['windows', 'steam', 'rtx', 'geforce', 'gaming computer', 'gaming desktop'],
    'sega': ['dreamcast', 'saturn', 'genesis', 'mega drive', 'sonic']
}

# Weights for different metrics 
DEFAULT_WEIGHTS = {
    'levenshtein': 0.25,
    'jaro_winkler': 0.25,
    'char_ngram': 0.20,
    'phonetic': 0.15,
    'fuzzy': 0.15
}

# Weights for very short queries
SHORT_QUERY_WEIGHTS = {
    'levenshtein': 0.4,
    'jaro_winkler': 0.3,
    'char_ngram': 0.1,
    'phonetic': 0.1,
    'fuzzy': 0.1
}

# Common abbreviations that should have a lower threshold
COMMON_ABBREVIATIONS = {'ps4', 'ps5', 'xb1', 'xsx', 'pc', 'win', 'ps', 'xb', 'gc'}

