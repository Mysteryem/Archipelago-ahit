import logging
import random  # For picking whether P1 or P2 gets remainder studs after halving.
from typing import Mapping


from ..common import UintField
from ..common_addresses import player_character_entity_iter, is_in_chapter_free_play, CHARACTER_POWER_UP_TIMER
from ..type_aliases import TCSContext
from ...items import GENERIC_BY_NAME


logger = logging.getLogger("Client")


# TODO: We should add to the in-level studs instead, additionally adding to the True Jedi meter. If the player exits
#  without saving, then they will enter the Cantina and receive the Studs there instead, so they cannot abuse exiting
#  without saving re-giving them the studs, which would have otherwise allowed for entering another level and getting
#  the True Jedi progress there.
# Note, this is not the in-level stud count. We don't add to that, because it is not saved.
STUD_COUNT_ADDRESS = 0x86E4DC
MAX_STUD_COUNT = 4_000_000_000


STUDS_AP_ID_TO_VALUE: Mapping[int, int] = {
    # For when additional Stud items are added.
    # GENERIC_BY_NAME["Silver Stud"].code: 10
    # GENERIC_BY_NAME["Gold Stud"].code: 100
    # GENERIC_BY_NAME["Blue Stud"].code: 1000
    GENERIC_BY_NAME["Purple Stud"].code: 10000
}


CHARACTER_STUD_COUNTER_POINTER = UintField(0x7fc)


# todo?: The stud counts for each player appear to be static addresses, which begs the question of why each player
#  controlled character entity has a pointer to one of these addresses.
# CURRENT_AREA_STUDS_P1_ADDRESS = 0x855F38
# CURRENT_AREA_STUDS_P2_ADDRESS = 0x855F48


def give_studs(ctx: TCSContext, ap_item_id: int):
    """
    Grant Studs to the player. Unlike other items, Studs are a consumable resource, so cannot simply be set to the
    number of received studs and instead must use the last/next item index from AP to determine when a Studs item is
    newly received by the current save file.
    """
    studs_to_add = STUDS_AP_ID_TO_VALUE.get(ap_item_id)
    if studs_to_add is None:
        logger.warning("Tried to receive unknown Studs item with item ID %i", ap_item_id)
        return

    # Multiply by the player's current maximum score multiplier.
    # The currently enabled score multipliers are not used because players could forget to enable them and then receive
    # a load of studs and then feel bad that they forgot to enable their multipliers.
    studs_to_add *= ctx.acquired_generic.current_score_multiplier

    # Keep studs to increments of 10 (1x Silver Stud)
    remainder = studs_to_add % 10
    studs_to_add -= remainder

    in_level_studs_addresses = []
    if is_in_chapter_free_play(ctx):
        for _, character_address in player_character_entity_iter(ctx):
            studs_address = CHARACTER_STUD_COUNTER_POINTER.get(ctx, character_address)
            if studs_address != 0:
                # Power Up doubles received studs.
                # todo: Add support for further doubling received studs when in a Double Score Zone.
                multiplier = 2 if CHARACTER_POWER_UP_TIMER.get(ctx, character_address) > 0.0 else 1
                in_level_studs_addresses.append((studs_address, multiplier))

    if in_level_studs_addresses:
        # Add the studs directly to the player(s)' stud counters.
        if len(in_level_studs_addresses) == 1:
            in_level_studs_address, multiplier = in_level_studs_addresses[0]
            current_stud_count = ctx.read_uint(in_level_studs_address, raw=True)
            new_stud_count = current_stud_count + studs_to_add * multiplier
            ctx.write_uint(in_level_studs_address, new_stud_count, raw=True)
        else:
            # Always keep granted studs to increments of 10. The amount will be halved to give half to each player, so
            # check the remainder for 20 which will become 10 after halving.
            remainder_after_halving = studs_to_add % 20
            studs_to_add -= remainder_after_halving
            p1_studs = studs_to_add // 2
            p2_studs = p1_studs
            if remainder_after_halving:
                # Pick randomly who gets the 10 studs remainder.
                if random.randint(0, 1):
                    p1_studs += remainder_after_halving
                else:
                    p2_studs += remainder_after_halving

            # Give the studs to each player, taking into account any additional multipliers they each have.
            for (in_level_studs_address, multiplier), player_studs_to_add in zip(in_level_studs_addresses,
                                                                                 (p1_studs, p2_studs)):
                current_stud_count = ctx.read_uint(in_level_studs_address, raw=True)
                new_stud_count = current_stud_count + player_studs_to_add * multiplier
                ctx.write_uint(in_level_studs_address, new_stud_count, raw=True)
    else:
        # Add the studs directly to the save data's stud counter.
        current_stud_count = ctx.read_uint(STUD_COUNT_ADDRESS)
        new_stud_count = min(current_stud_count + studs_to_add, MAX_STUD_COUNT)
        ctx.write_uint(STUD_COUNT_ADDRESS, new_stud_count)
