import logging
from typing import Callable

from ...common_addresses import StaticBOOL
from ...type_aliases import TCSContext
from .free_play_character_categories import set_custom_character_categories
from .add_flags_to_characters import (
    set_ig88_and_4lom_as_protocol_droids,
    set_astromech_panel_users_as_tightrope_walk,
    set_droideka_as_tightrope_tilt,
    set_high_jump_slam_as_has_super_strength,
    set_fetts_to_can_bypass_security,
    set_can_zap_characters_as_got_batarang,
)


logger = logging.getLogger("Client")


# This is the last flag in the last CHARCATEGORY in _LSW_CharCategory. The last element is intentionally empty to
# signify the end of the array, but the game appears to only check the name pointer in this last element, so the two
# flags are free game for storing whether game patches have been applied.
PATCHES_APPLIED_ADDR = StaticBOOL(0x7f2664)


MemoryPatch = Callable[[TCSContext], None]
PATCHES: list[MemoryPatch] = [
    set_custom_character_categories,
    set_ig88_and_4lom_as_protocol_droids,
    set_astromech_panel_users_as_tightrope_walk,
    set_droideka_as_tightrope_tilt,
    set_high_jump_slam_as_has_super_strength,
    set_fetts_to_can_bypass_security,
    set_can_zap_characters_as_got_batarang,
]


def apply_game_patches(ctx: TCSContext):
    if not PATCHES_APPLIED_ADDR.get(ctx):
        for patch in PATCHES:
            patch(ctx)
        PATCHES_APPLIED_ADDR.set(ctx, True)
        logger.info("Applied AP patches")
    else:
        logger.info("AP patches have already been applied this session")
