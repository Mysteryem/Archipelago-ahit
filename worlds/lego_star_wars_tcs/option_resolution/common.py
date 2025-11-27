from typing import TYPE_CHECKING

from ..levels import BONUS_NAME_TO_BONUS_AREA
from .universal_tracker import resolve_universal_tracker_options
from .normal import resolve_normal_options
from ..options import MinikitGoalAmount, GoalChapterLocationsMode


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

    world.prog_useful_level_access_threshold_count = int(world.PROG_USEFUL_LEVEL_ACCESS_THRESHOLD_PERCENT
                                                         * len(world.enabled_chapters))

    # enabled_chapters should always contain enabled_non_goal_chapters.
    assert world.enabled_non_goal_chapters <= world.enabled_chapters
    assert 0 <= len(world.enabled_chapters) - len(world.enabled_non_goal_chapters) <= 1
    assert world.enabled_chapters_with_locations <= world.enabled_chapters
    assert world.goal_chapter is None or world.goal_chapter in world.enabled_chapters

    if world.options.enable_story_character_unlock_locations:
        # There are often multiple Chapters that can send each Story character unlock location, so enable path
        # display in spoilers with paths enabled.
        world.topology_present = True

    # Calculate goal_area_completion_count when set to a non-zero percentage of available areas (chapters +
    # bonuses).
    # The option name uses "levels" as a user-facing term, but has the meaning of "areas" internally.
    complete_areas_goal_amount_percentage = world.options.complete_levels_goal_amount_percentage.value
    if complete_areas_goal_amount_percentage > 0:
        chapter_areas_count = len(world.enabled_chapters_with_locations)
        if world.goal_chapter and world.options.goal_chapter_locations_mode != GoalChapterLocationsMode.option_removed:
            # The goal chapter is locked behind the area completion count, so cannot contribute itself to the goal
            # requirement.
            chapter_areas_count -= 1
        # Only bonuses that award a Gold Brick on completion count towards the goal count.
        bonus_areas_count = sum(BONUS_NAME_TO_BONUS_AREA[name].gold_brick for name in world.enabled_bonuses)
        available_areas_count = chapter_areas_count + bonus_areas_count
        goal_area_completion_count = max(1, round(available_areas_count * complete_areas_goal_amount_percentage / 100))

        # If the Goal Chapter is enabled and has normal locations, so has Gold Bricks, then the Gold Bricks in the
        # Goal Chapter will not be usable to access Bonus Levels that can contribute level completion towards the
        # goal.
        if (world.goal_chapter
                and world.options.goal_chapter_locations_mode == GoalChapterLocationsMode.option_normal
                and world.enabled_bonuses):
            gold_bricks_per_chapter = (
                    1
                    + bool(world.options.enable_minikit_locations)
                    + bool(world.options.enable_true_jedi_locations)
            )
            chapter_gold_bricks = chapter_areas_count * gold_bricks_per_chapter
            gold_brick_bonuses = [BONUS_NAME_TO_BONUS_AREA[name] for name in world.enabled_bonuses
                                  if BONUS_NAME_TO_BONUS_AREA[name].gold_brick]
            # Sort lower requirement bonuses first.
            gold_brick_bonuses.sort(key=lambda bonus_area: bonus_area.gold_bricks_required)
            pre_goal_gold_bricks = chapter_gold_bricks
            pre_goal_completable_bonuses = 0
            for area in gold_brick_bonuses:
                if area.gold_bricks_required > pre_goal_gold_bricks:
                    # The bonuses were sorted on order of ascending gold brick requirements, so no other bonuses are
                    # reachable before the goal.
                    break
                pre_goal_completable_bonuses += 1
                pre_goal_gold_bricks += 1
            pre_goal_completable_areas = chapter_areas_count + pre_goal_completable_bonuses
            if goal_area_completion_count > pre_goal_completable_areas:
                # It is rather rare for this to actually happen.
                world.log_warning("Could not satisfy the desired %i%% (%i/%i) level completions for goal because %i"
                                  " bonus levels are only accessible after completing the goal. The number of level"
                                  " completions for the goal has been reduced to the maximum of %.2f%% (%i/%i)",
                                  complete_areas_goal_amount_percentage,
                                  goal_area_completion_count,
                                  available_areas_count,
                                  bonus_areas_count - pre_goal_completable_bonuses,
                                  pre_goal_completable_areas / available_areas_count * 100,
                                  pre_goal_completable_areas,
                                  available_areas_count)
                goal_area_completion_count = pre_goal_completable_areas
        world.goal_area_completion_count = goal_area_completion_count
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
