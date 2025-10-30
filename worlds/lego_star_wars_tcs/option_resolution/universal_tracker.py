from typing import TYPE_CHECKING, Any

from ..items import MINIKITS_BY_COUNT
from ..levels import SHORT_NAME_TO_CHAPTER_AREA, BONUS_NAME_TO_BONUS_AREA
from ..options import OnlyUniqueBossesCountTowardsGoal


if TYPE_CHECKING:
    from .. import LegoStarWarsTCSWorld
else:
    LegoStarWarsTCSWorld = object


def _direct_slot_data_options(self: LegoStarWarsTCSWorld, passthrough: dict[str, Any]):
    """Options directly set from slot data."""
    self.options.minikit_goal_amount.value = passthrough["minikit_goal_amount"]
    self.options.minikit_bundle_size.value = passthrough["minikit_bundle_size"]
    self.options.episode_unlock_requirement.value = passthrough["episode_unlock_requirement"]
    self.options.all_episodes_character_purchase_requirements.value = (
        passthrough["all_episodes_character_purchase_requirements"])
    self.options.most_expensive_purchase_with_no_multiplier.value = (
        passthrough["most_expensive_purchase_with_no_multiplier"])
    self.options.enable_bonus_locations.value = passthrough["enable_bonus_locations"]
    self.options.enable_story_character_unlock_locations.value = (
        passthrough["enable_story_character_unlock_locations"])
    self.options.enable_all_episodes_purchases.value = passthrough["enable_all_episodes_purchases"]
    self.options.defeat_bosses_goal_amount.value = passthrough["defeat_bosses_goal_amount"]
    self.options.only_unique_bosses_count.value = passthrough["only_unique_bosses_count"]
    self.options.defeat_bosses_goal_amount.value = passthrough["defeat_bosses_goal_amount"]
    self.options.enable_minikit_locations.value = passthrough["enable_minikit_locations"]
    self.options.enable_true_jedi_locations.value = passthrough["enable_true_jedi_locations"]


def _derived_attributes_from_options(self: LegoStarWarsTCSWorld, passthrough: dict[str, Any]):
    """Attributes normally derived from options during generate_early."""
    # Derived Chapter/Episode attributes.
    self.enabled_chapters = set(passthrough["enabled_chapters"])
    self.enabled_chapter_count = len(self.enabled_chapters)
    self.enabled_episodes = set(passthrough["enabled_episodes"])
    # The enabled bonuses are set depending on the number of Gold Bricks available
    self.enabled_bonuses = set(passthrough["enabled_bonuses"])
    self.starting_chapter = passthrough["starting_chapter"]
    self.starting_episode = passthrough["starting_episode"]

    # Derived Minikit attributes.
    self.available_minikits = self.enabled_chapter_count * 10
    bundle_size = self.options.minikit_bundle_size.value
    self.minikit_bundle_name = MINIKITS_BY_COUNT[bundle_size].name
    self.minikit_bundle_count = (self.available_minikits // bundle_size
                                 + (self.available_minikits % bundle_size != 0))

    # Derived Goal attributes.
    self.enabled_bosses = set(passthrough["enabled_bosses"])
    self.goal_area_completion_count = passthrough["goal_area_completion_count"]


def _override_options_with_derived_rolled_values(self: LegoStarWarsTCSWorld):
    """Override options with their derived/rolled values."""
    # Override the enable_chapter count to match the number that are enabled.
    self.options.enabled_chapters_count.value = len(self.enabled_chapters)
    # Unrandomize the starting chapter choice with the starting chapter that was actually picked.
    self.options.starting_chapter.set_from_string(self.starting_chapter)
    # Override the allowed chapters with all the chapters that rolled as enabled.
    self.options.allowed_chapters.value = set(self.enabled_chapters)
    # Act as if there was no filtering of allowed chapter types.
    self.options.allowed_chapter_types.set_from_string("all")


def _compute_boss_names(self: LegoStarWarsTCSWorld):
    """Compute boss names when unique bosses are enabled."""
    unique_bosses_only = (
            self.options.only_unique_bosses_count != OnlyUniqueBossesCountTowardsGoal.option_disabled)
    unique_bosses_anakin_as_darth_vader = (
            self.options.only_unique_bosses_count
            == OnlyUniqueBossesCountTowardsGoal.option_enabled_and_count_anakin_as_vader
    )
    if unique_bosses_only:
        short_name_to_boss_character: dict[str, str] = {}
        for chapter in self.enabled_bosses:
            boss_character = SHORT_NAME_TO_CHAPTER_AREA[chapter].boss
            if unique_bosses_anakin_as_darth_vader and boss_character == "Anakin Skywalker":
                boss_character = "Darth Vader"
            assert boss_character is not None
            short_name_to_boss_character[chapter] = boss_character
    else:
        short_name_to_boss_character = {}
    self.short_name_to_boss_character = short_name_to_boss_character


def _compute_expected_gold_brick_event_count(self: LegoStarWarsTCSWorld):
    """Compute expected Gold Brick event count."""
    if self.options.enable_bonus_locations:
        gold_bricks_per_chapter = (
                1
                + bool(self.options.enable_minikit_locations)
                + bool(self.options.enable_true_jedi_locations)
        )
        gold_bricks_from_chapters = self.enabled_chapter_count * gold_bricks_per_chapter
        areas_gen = (BONUS_NAME_TO_BONUS_AREA[area_name] for area_name in self.enabled_bonuses)
        gold_bricks_from_bonuses = sum(area.gold_brick for area in areas_gen)
        self._expected_gold_brick_event_count = gold_bricks_from_chapters + gold_bricks_from_bonuses
    else:
        # Gold Brick events are only relevant when bonuses are enabled.
        self._expected_gold_brick_event_count = 0


def resolve_universal_tracker_options(self: LegoStarWarsTCSWorld, passthrough: dict[str, Any]):
    _direct_slot_data_options(self, passthrough)
    _derived_attributes_from_options(self, passthrough)
    _override_options_with_derived_rolled_values(self)
    _compute_boss_names(self)
    _compute_expected_gold_brick_event_count(self)
