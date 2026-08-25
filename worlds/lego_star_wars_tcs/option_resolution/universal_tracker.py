import dataclasses
from typing import TYPE_CHECKING, Any

from Options import Option

from ..items import MINIKITS_BY_COUNT
from ..levels import SHORT_NAME_TO_CHAPTER_AREA, BONUS_NAME_TO_BONUS_AREA
from ..options import LegoStarWarsTCSOptions, OnlyUniqueBossesCountTowardsGoal, GoalChapterLocationsMode
from ..slot_data import TCSSlotDataOptions, TCSDirectSlotDataOptions

from ..data.items.all_character_items import CODE_TO_ITEM_DATA


if TYPE_CHECKING:
    from .. import LegoStarWarsTCSWorld
else:
    LegoStarWarsTCSWorld = object


def _direct_slot_data_options(self: LegoStarWarsTCSWorld, slot_data: TCSSlotDataOptions):
    """Options directly set from slot data."""
    options = self.options

    # Directly exported to slot data and directly imported from slot data.
    for field in dataclasses.fields(TCSDirectSlotDataOptions):
        field_name = field.name
        world_option: Option[Any] = getattr(self.options, field_name)
        slot_data_option: Option[Any] = getattr(slot_data, field_name)
        world_option.value = slot_data_option.value

    # Exported to slot data through other means, but imported directly.
    options.minikit_goal_amount.value = slot_data.minikit_goal_amount.value


def _derived_attributes_from_options(self: LegoStarWarsTCSWorld, slot_data: TCSSlotDataOptions):
    """Attributes normally derived from options during generate_early."""
    # Derived Chapter/Episode attributes.
    self.enabled_chapters = slot_data.enabled_chapters.value
    self.enabled_episodes = set(slot_data.enabled_episodes.value)
    # The enabled bonuses are set depending on the number of Gold Bricks available
    self.enabled_bonuses = slot_data.enabled_bonuses.value
    self.starting_chapter = SHORT_NAME_TO_CHAPTER_AREA[slot_data.starting_chapter.value]
    assert self.starting_episode == slot_data.starting_episode.value, ("Starting episode from slot_data did not match "
                                                                      "the starting chapter from slot_data.")

    # Derived Chapter Unlock requirements.
    alt_characters_option = slot_data.chapters_requiring_alt_characters
    self.chapters_requiring_alt_characters = set() if alt_characters_option is None else alt_characters_option.value

    required_counts_option = slot_data.chapter_required_character_counts
    self.chapter_required_character_counts = {} if required_counts_option is None else required_counts_option.value

    random_requirements_option = slot_data.chapter_random_character_requirements
    random_requirements: dict[str, list[int]]
    random_requirements = {} if random_requirements_option is None else random_requirements_option.value
    self.chapter_random_character_requirements = {
        chapter: [CODE_TO_ITEM_DATA[c] for c in character_item_ids]
        for chapter, character_item_ids in random_requirements.items()
    }

    # Derived Goal attributes.
    self.enabled_bosses = slot_data.enabled_bosses.value
    self.goal_area_completion_count = slot_data.goal_area_completion_count.value

    goal_chapter_option = slot_data.goal_chapter
    if goal_chapter_option is not None:
        self.goal_chapter = goal_chapter_option.value
    else:
        self.goal_chapter = None

    if self.goal_chapter:
        assert self.goal_chapter in self.enabled_chapters
        self.enabled_non_goal_chapters = self.enabled_chapters - {self.goal_chapter}
        if self.options.goal_chapter_locations_mode == GoalChapterLocationsMode.option_removed:
            self.enabled_chapters_with_locations = self.enabled_chapters
        else:
            self.enabled_chapters_with_locations = self.enabled_non_goal_chapters
    else:
        self.enabled_non_goal_chapters = self.enabled_chapters

    # Derived Minikit attributes.
    if self.options.minikit_goal_amount != 0 or self.options.enable_minikit_locations:
        # 10 Minikits per chapter.
        self.available_minikits = len(self.enabled_non_goal_chapters) * 10
    else:
        # There are no minikits if the locations are not enabled and the goal does not require minikits.
        self.available_minikits = 0
    bundle_size = self.options.minikit_bundle_size.value
    self.minikit_bundle_name = MINIKITS_BY_COUNT[bundle_size].name
    self.minikit_bundle_count = (self.available_minikits // bundle_size
                                 + (self.available_minikits % bundle_size != 0))


def _override_options_with_derived_rolled_values(self: LegoStarWarsTCSWorld):
    """Override options with their derived/rolled values."""
    # Override the enable_chapter count to match the number that are enabled.
    self.options.enabled_chapters_count.value = len(self.enabled_chapters)
    # Unrandomize the starting chapter choice with the starting chapter that was actually picked.
    self.options.starting_chapter.set_from_string(self.starting_chapter.short_name)
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
        if self.goal_chapter and self.options.goal_chapter_locations_mode == GoalChapterLocationsMode.option_normal:
            chapters_with_gold_bricks = len(self.enabled_chapters)
        else:
            chapters_with_gold_bricks = len(self.enabled_non_goal_chapters)
        gold_bricks_from_chapters = chapters_with_gold_bricks * gold_bricks_per_chapter
        areas_gen = (BONUS_NAME_TO_BONUS_AREA[area_name] for area_name in self.enabled_bonuses)
        gold_bricks_from_bonuses = sum(area.gold_brick for area in areas_gen)
        self.expected_gold_brick_event_count = gold_bricks_from_chapters + gold_bricks_from_bonuses
    else:
        # Gold Brick events are only relevant when bonuses are enabled.
        self.expected_gold_brick_event_count = 0


def resolve_universal_tracker_options(self: LegoStarWarsTCSWorld, passthrough: dict[str, Any]):
    slot_data_options = TCSSlotDataOptions.from_slot_data(passthrough)
    _direct_slot_data_options(self, slot_data_options)
    _derived_attributes_from_options(self, slot_data_options)
    _override_options_with_derived_rolled_values(self)
    _compute_boss_names(self)
    _compute_expected_gold_brick_event_count(self)
