from typing import TYPE_CHECKING

from ..levels import BONUS_NAME_TO_BONUS_AREA
from .universal_tracker import resolve_universal_tracker_options
from .normal import resolve_normal_options
from ..options import MinikitGoalAmount


if TYPE_CHECKING:
    from .. import LegoStarWarsTCSWorld
else:
    LegoStarWarsTCSWorld = object


__all__ = [
    "resolve_options"
]


def _resolve_common_options(world: LegoStarWarsTCSWorld):
    """Called after resolving specific options for normal vs Universal Tracker generation."""
    # Calculate goal_minikit_count when set to a percentage of the available minikits.
    if world.options.minikit_goal_amount == MinikitGoalAmount.special_range_names["use_percentage_option"]:
        world.goal_minikit_count = max(1, round(
            world.available_minikits * world.options.minikit_goal_amount_percentage / 100))
    else:
        world.goal_minikit_count = world.options.minikit_goal_amount.value

    # Only whole bundles are counted for logic, so any partial bundles require an extra whole bundle to goal.
    bundle_size = world.options.minikit_bundle_size
    world.goal_minikit_bundle_count = (world.goal_minikit_count // bundle_size
                                       + (world.goal_minikit_count % bundle_size != 0))

    world.prog_useful_level_access_threshold_count = int(
        world.PROG_USEFUL_LEVEL_ACCESS_THRESHOLD_PERCENT * world.enabled_chapter_count)

    if world.options.enable_story_character_unlock_locations:
        # There are often multiple Chapters that can send each Story character unlock location, so enable path
        # display in spoilers with paths enabled.
        world.topology_present = True

    # Calculate goal_area_completion_count when set to a non-zero percentage of available areas (chapters +
    # bonuses).
    # The option name uses "levels" as a user-facing term, but has the meaning of "areas" internally.
    complete_areas_goal_amount_percentage = world.options.complete_levels_goal_amount_percentage.value
    if complete_areas_goal_amount_percentage > 0:
        chapter_areas_count = world.enabled_chapter_count
        # Only bonuses that award a Gold Brick on completion count towards the goal count.
        bonus_areas_count = sum(BONUS_NAME_TO_BONUS_AREA[name].gold_brick for name in world.enabled_bonuses)
        available_areas_count = chapter_areas_count + bonus_areas_count
        world.goal_area_completion_count = max(1, round(
            available_areas_count * complete_areas_goal_amount_percentage / 100))
    else:
        world.goal_area_completion_count = 0


def resolve_options(world: LegoStarWarsTCSWorld):
    # Universal Tracker Support
    if passthrough := getattr(world.multiworld, "re_gen_passthrough", {}).get(world.game):
        resolve_universal_tracker_options(world, passthrough)
    else:
        resolve_normal_options(world)
    _resolve_common_options(world)

    # # Debug check to help with comparing passthrough values
    # for k, v in vars(world).items():
    #     print(f"{k}: {v}")
    #
    # if not passthrough:
    #     world.multiworld.re_gen_passthrough = {world.game: world.fill_slot_data()}
    #     # Recursive call, but with passthrough this time.
    #     world.generate_early()
    # else:
    #     # No recursive call the second time around.
    #     return
