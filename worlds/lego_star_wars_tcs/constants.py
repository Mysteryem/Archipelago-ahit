import json
from pkgutil import get_data

from BaseClasses import ItemClassification

from .character_ability import *

_MANIFEST = json.loads(get_data("worlds.lego_star_wars_tcs", "archipelago.json"))

GAME_NAME = _MANIFEST["game"]

_MAJOR, _MINOR, _PATCH = map(int, _MANIFEST["world_version"].split("."))
AP_WORLD_VERSION: tuple[int, int, int] = (_MAJOR, _MINOR, _PATCH)
del _MANIFEST
# Logic version, used for Universal Tracker compatibility across patch versions.
UT_LOGIC_VERSION = 1

# todo: VEHICLE_TOW can probably be included in the future too.
# todo: GHOST can probably be included in the future too.
# todo: PROTOCOL_DROID_PANEL can probably be included in the future too.
RARE_AND_USEFUL_ABILITIES = ASTROMECH_PANEL | BOUNTY_HUNTER | HIGH_JUMP | SHORTIE | SITH | PROTOCOL_PANEL | HOVER

CHAPTER_SPECIFIC_FLAGS = (
        CAN_WEAR_HAT_AND_GRAPPLE
        | CAN_WEAR_HAT_AND_DOUBLE_JUMP
        | CAN_WEAR_HAT
        | ASTROMECH_DROID
        | IS_A_VEHICLE
        # Commander Cody in 3-3 and Darth Vader in 6-5 have IMPERIAL, but IMPERIAL is not needed to complete either
        # chapter. In 6-5, it is at least used for the Minikits.
        | IMPERIAL
        # SITH could be included here, but there is only 6-5 with a SITH Story character, and SITH is needed to
        # complete 6-5.
)
"""
These flags should not be required to access chapters based on the abilities of the Story characters because they are
only relevant to a limited number of chapters, where there are alternatives that the logic should consider.
"""

GOLD_BRICK_EVENT_NAME = "Gold Brick"

if AP_WORLD_VERSION >= (2, 0, 0):
    raise Exception("Deprecation: Use ItemClassification.progression_deprioritized_skip_balancing directly.")
# Use deprioritzed on AP 0.6.3+, but still allow generation on older AP versions.
progression_deprioritized_skip_balancing: ItemClassification = getattr(
    ItemClassification,
    "progression_deprioritized_skip_balancing",
    ItemClassification.progression_skip_balancing
)
progression_deprioritized: ItemClassification = getattr(
    ItemClassification,
    "progression_deprioritized",
    ItemClassification.progression
)
