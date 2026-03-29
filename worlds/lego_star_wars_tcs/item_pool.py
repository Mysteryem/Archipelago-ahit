from collections import Counter
from dataclasses import dataclass
from functools import reduce
from operator import or_
from typing import TYPE_CHECKING, cast, Iterable

from BaseClasses import LocationProgressType, ItemClassification

from .constants import progression_deprioritized_skip_balancing, CharacterAbility, CHAPTER_SPECIFIC_FLAGS
from .items import (
    CHARACTERS_AND_VEHICLES_BY_NAME,
    GenericCharacterData,
    LegoStarWarsTCSItem,
    EXTRAS_BY_NAME,
    PURCHASABLE_NON_POWER_BRICK_EXTRAS,
    GENERIC_BY_NAME,
)
from .levels import (
    CHAPTER_AREA_STORY_CHARACTERS,
    VEHICLE_CHAPTER_SHORTNAMES,
    POWER_BRICK_REQUIREMENTS,
    SHORT_NAME_TO_CHAPTER_AREA,
    BONUS_NAME_TO_BONUS_AREA,
    DIFFICULT_OR_IMPOSSIBLE_TRUE_JEDI,
)
from .locations import LegoStarWarsTCSShopLocation
from .options import ChapterUnlockRequirement, GoalChapterLocationsMode


if TYPE_CHECKING:
    from . import LegoStarWarsTCSWorld
else:
    LegoStarWarsTCSWorld = object


progressive_score_multiplier_name = GENERIC_BY_NAME["Progressive Score Multiplier"].name


__all__ = [
    "create_item_pool"
]


@dataclass
class ItemPoolAbilityRequirements:
    required: CharacterAbility
    """Abilities that are logically required to reach every location in the world. In cases where there are multiple
    options, one option will be picked as required and the others as optional."""
    optional: CharacterAbility
    """Abilities that could have logical relevance to the player getting access to locations, but all locations would
    be reachable even if no items with these abilities existed in the item pool."""
    starting: CharacterAbility = CharacterAbility.NONE
    """Abilities that the player will be starting with."""

    def get_logically_irrelevant(self) -> CharacterAbility:
        """
        Get abilities that are logically irrelevant for items in the item pool. In slots with few chapters enabled, some
        abilities may not have any logical relevance.
        :return:
        """
        return ~(self.required | self.optional)

    def update_for_starting_abilities(self, starting_abilities: CharacterAbility) -> None:
        """
        Remove abilities present on characters in the player's starting inventory.
        If an ability is provided by starting inventory, then it does not need to be provided by the item pool.
        :param starting_abilities:
        :return:
        """
        self.required &= ~starting_abilities
        self.optional &= ~starting_abilities
        self.starting = starting_abilities

    def update_for_chapter_lock_requirements(self,
                                             world: LegoStarWarsTCSWorld,
                                             chapters_unlock_with_characters: bool) -> Counter[str]:
        """
        Update the ability requirements for what locks the chapter
        :param world:
        :param chapters_unlock_with_characters: Whether chapters unlock
        :return:
        """
        if chapters_unlock_with_characters:
            return self._update_for_character_locked_chapters(world)
        else:
            self._update_for_unlock_item_locked_chapters(world)
            return Counter()

    def _update_for_character_locked_chapters(self, world: LegoStarWarsTCSWorld) -> Counter[str]:
        # Unary `+` (__pos__) removes counts <= 0, if any are present.
        level_access_character_counts = +world.character_chapter_access_counts
        for name in level_access_character_counts.keys():
            abilities_provided_by_level_access = CHARACTERS_AND_VEHICLES_BY_NAME[name].abilities
            # Characters with these abilities do not need to be explicitly added to the item pool because these
            # abilities are provided by a character that is required to unlock a chapter.
            self.required &= ~abilities_provided_by_level_access
            self.optional |= abilities_provided_by_level_access
        return level_access_character_counts

    def _update_for_unlock_item_locked_chapters(self, world: LegoStarWarsTCSWorld):
        for chapter in sorted(world.enabled_chapters):
            chapter_obj = SHORT_NAME_TO_CHAPTER_AREA[chapter]
            # The item pool must provide the abilities require to complete the chapter.
            self.required |= chapter_obj.completion_main_ability_requirements
            # Alternative requirements that swap out a common ability for a rarer ability are relevant to logic, but
            # are not required to be included in the item pool.
            alt_requirements = chapter_obj.completion_alt_ability_requirements
            if alt_requirements:
                self.optional |= alt_requirements


class ItemCreator:
    _classification_lookup: dict[str, ItemClassification]
    _abilities_lookup: dict[str, CharacterAbility]
    _world: LegoStarWarsTCSWorld

    def __init__(self,
                 world: LegoStarWarsTCSWorld,
                 item_pool_ability_requirements: ItemPoolAbilityRequirements):
        """
        Create a class to help in create items in a performant manner, while stripping starting abilities from the
        created items.
        :param world: The world the created items will belong to.
        :param item_pool_ability_requirements: The required and optional abilities that must be provided by the item
         pool.
        """
        # If an ability is not relevant to logic at all, then it is undesirable for that ability to be in collects, and
        # any characters with only irrelevant abilities should lose their progression classification.
        # In larger worlds, it is unlikely for there to be any logically irrelevant abilities.
        logically_irrelevant_abilities = item_pool_ability_requirements.get_logically_irrelevant()

        self._world = world
        self._initialize_effective_data_lookups(logically_irrelevant_abilities)

    def _initialize_effective_data_lookups(self, logically_irrelevant_abilities: CharacterAbility) -> None:
        """
        Pre-calculate the effective character abilities and classification of each item, so that the creation of items
        with multiple copies can be sped up.
        :param logically_irrelevant_abilities: These abilities are logically irrelevant to created items, so do not need
         to be provided by created items, potentially changing the effective classifications of the items.
        """
        effective_character_abilities: dict[str, CharacterAbility] = {}

        for name, char in CHARACTERS_AND_VEHICLES_BY_NAME.items():
            # Remove abilities provided by the starting characters from other characters, potentially changing the
            # classification of other characters if all their abilities are covered by the starting characters.
            # This improves generation performance by reducing the number of extra collects when a character item is
            # collected.
            effective_abilities: CharacterAbility = char.abilities & ~logically_irrelevant_abilities
            effective_character_abilities[name] = effective_abilities

        effective_item_classifications: dict[str, ItemClassification] = {}
        effective_item_abilities: dict[str, CharacterAbility] = {}
        for item in self._world.item_name_to_id:
            classification, effective_abilities = self._world.evaluate_effective_item(item, effective_character_abilities)
            effective_item_classifications[item] = classification
            # The returned `effective_abiltiies` should be the same as what was in `effective_character_abilities`.
            # The returned `effective_abiltiies` is not actually needed here, but `effective_character_abilities` is not
            # always available when `self.evaluate_effective_item()` is called.
            assert effective_abilities is effective_character_abilities.get(item, CharacterAbility.NONE)
            effective_item_abilities[item] = effective_abilities

        self._classification_lookup = effective_item_classifications
        self._abilities_lookup = effective_item_abilities

    def create_item(self, name: str) -> LegoStarWarsTCSItem:
        """
        Create an item by name
        :param name: The name of the item. The name must exist in the world's datapackage.
        :return: The created item.
        """
        code = self._world.item_name_to_id[name]
        classification = self._classification_lookup[name]
        abilities = self._abilities_lookup[name]

        return LegoStarWarsTCSItem(name, classification, code, self._world.player, abilities)


@dataclass
class ItemLocationCounts:
    world: LegoStarWarsTCSWorld
    non_excluded_chapter_count: int
    goal_chapter_locations_excluded: bool

    completion: int = 0
    """Free spaces in the item pool for Level completion locations."""
    true_jedi: int = 0
    """Free spaces in the item pool for True Jedi locations."""

    free_minikit: int = 0
    """Free spaces in the item pool for Minikit locations."""
    free_character: int = 0
    """Free spaces in the item pool for Character unlock/purchase locations."""
    free_extra: int = 0
    """Free spaces in the item pool for Extra purchase locations."""
    free_ridesanity: int = 0
    """Free spaces in the item pool for ridesanity locations."""

    required_minikit: int = 0
    """The number of Minikit bundles that are required to exist in the item pool."""
    required_character: int = 0
    """The number of Characters that are required to exist in the item pool."""
    required_extra: int = 0
    """The number of Extras that are required to exist in the item pool."""
    required_additional: int = 0
    """The number of additional items that don't belong to a particular category, that are required to exist in the 
    pool."""

    reserved_character: int = 0
    """Try to add at least as many characters to the item pool as this."""
    reserved_extra: int = 0
    """Try to add at least as many Extras to the item pool as this."""

    free_consumed_for_required: int = 0
    """How many free locations have been consumed by items in the pool that do not have a corresponding vanilla 
    location."""
    reserved_consumed_for_required: int = 0
    """How many reserved locations have been consumed/un-reserved to ensure there is enough space in the item pool for
    all required items."""

    def set_character_counts(self, pool_required_characters: list[GenericCharacterData]) -> None:
        self.required_character = len(pool_required_characters)

        non_excluded_character_unlock_location_count = (
                self.world.character_unlock_location_count - self.world.goal_excluded_character_unlock_location_count
        )
        if (self.world.options.filler_reserve_characters
                or self.required_character >= non_excluded_character_unlock_location_count):
            self.reserved_character = non_excluded_character_unlock_location_count
            self.free_character = 0
        else:
            self.reserved_character = self.required_character
            self.free_character = non_excluded_character_unlock_location_count - self.reserved_character

        # Any goal excluded character unlock locations do not contribute Characters to the item pool (unless those
        # characters happen to be Filler classification). Enough Filler items for Excluded locations is checked and
        # satisfied later, so these locations are effectively free locations.
        self.free_character += self.world.goal_excluded_character_unlock_location_count

    def set_extra_counts(self, pool_required_extras: list[str]) -> None:
        self.required_extra = len(pool_required_extras)

        self.reserved_extra = self.non_excluded_chapter_count

        if self.world.options.enable_starting_extras_locations:
            self.reserved_extra += len(PURCHASABLE_NON_POWER_BRICK_EXTRAS)

        free_extra_location_count: int
        if self.world.options.filler_reserve_extras:
            # All the locations from Extras are reserved for putting Extra items into the item pool.
            self.free_extra = 0
        else:
            # Reserve only as many locations for Extras as the number of Extras that are required to be in the item
            # pool.
            initial_reserved_count = self.reserved_extra
            self.reserved_extra = min(self.required_extra, initial_reserved_count)
            self.free_extra = initial_reserved_count - self.reserved_extra
        if self.goal_chapter_locations_excluded:
            # The Extra location of the Goal Chapter is excluded, and does not contribute an Extra to the item pool.
            self.free_extra += 1

    def set_true_jedi_counts(self) -> None:
        # The vanilla rewards for True Jedi are Gold Bricks, which are events, so these are effectively free locations
        # for any kind of item when enabled.
        if self.world.options.enable_true_jedi_locations:
            self.true_jedi = self.non_excluded_chapter_count

            if self.goal_chapter_locations_excluded:
                # True Jedi locations are already free locations for any kind of item.
                self.true_jedi += 1
        else:
            self.true_jedi = 0

    def set_completion_counts(self) -> None:
        self.completion = self.non_excluded_chapter_count + len(self.world.enabled_bonuses)
        if self.goal_chapter_locations_excluded:
            # The completion location for the goal chapter is excluded, but is still a free location in the item pool
            # (space for filler needed to be placed at excluded locations is calculated separately from free locations).
            self.completion += 1

    def set_minikit_counts(self) -> None:
        # As many minikit bundles as this will always be created. This may be fewer than is required to goal, but
        # reducing the total bundle count can make a seed longer, so all minikit bundles should be considered to be
        # required.
        self.required_minikit = self.world.minikit_bundle_count

        if self.world.options.enable_minikit_locations:
            self.free_minikit = self.non_excluded_chapter_count * 10 - self.required_minikit
            if self.goal_chapter_locations_excluded:
                # The locations are excluded, but still count as free locations.
                self.free_minikit += 10
        else:
            if self.world.options.minikit_goal_amount != 0:
                assert self.world.options.minikit_bundle_size == 10
                assert self.world.minikit_bundle_name == "10 Minikits"
                assert self.world.minikit_bundle_count == len(self.world.enabled_non_goal_chapters)
                # Consume the free Chapter Completion locations to fit the Minikits.
                self.completion -= self.required_minikit
                self.free_minikit = 0
            else:
                assert self.required_minikit == 0
                self.free_minikit = 0

    def set_ridesanity_counts(self) -> None:
        # There are no corresponding items for ridesanity locations, so they are free locations for any item.
        self.free_ridesanity = self.world.ridesanity_location_count

    def set_additional_item_counts(self, pool_required_chapter_unlock_items: list[str]) -> tuple[int, list[str]]:
        other_required_items: list[str] = []
        start_inventory_tokens = 0
        # A few free locations may need to be used for episode unlock items and/or episode tokens.
        if self.world.options.episode_unlock_requirement == "episode_item":
            for i in self.world.enabled_episodes:
                if i != self.world.starting_episode:
                    other_required_items.append(f"Episode {i} Unlock")
        if self.world.options.all_episodes_character_purchase_requirements == "episodes_tokens":
            # One token is added to the item pool for every episode's worth of (6) chapters that are enabled.
            tokens_in_pool = max(1, round(len(self.world.enabled_chapters) / 6))
            start_inventory_tokens = 6 - tokens_in_pool
            assert 5 >= start_inventory_tokens >= 0
            for _ in range(tokens_in_pool):
                other_required_items.append("Episode Completion Token")
        # 7 free locations may need to be used for Kyber Bricks.
        if self.world.options.goal_requires_kyber_bricks:
            other_required_items.extend(("Kyber Brick",) * 7)

        # As many Chapter Unlock items as there are enabled Chapters, excluding the starting chapter.
        other_required_items.extend(pool_required_chapter_unlock_items)

        self.free_consumed_for_required += len(other_required_items)
        self.required_additional += len(other_required_items)
        return start_inventory_tokens, other_required_items

    def free_space_for_required_items(self):
        """
        Replace space in the item pool, reserved by non-required Extras and Characters, until there is enough space in
        the item pool for all required items.
        """
        free_location_count = self.free_location_count
        if free_location_count < 0:
            # There are not enough non-excluded locations for all required progression items.
            # Attempt to reduce reserved items until there is enough space.
            needed = -free_location_count
            # Subtract from reserved, but not required, counts.
            ok_to_replace_character_count = max(0, self.reserved_character - self.required_character)
            ok_to_replace_extras_count = max(0, self.reserved_extra - self.required_extra)
            total_replaceable = ok_to_replace_character_count + ok_to_replace_extras_count
            if needed > total_replaceable:
                if self.world.options.goal_requires_kyber_bricks:
                    # The Kyber Bricks goal adds 7 items that have no corresponding vanilla locations.
                    self.world.option_error(
                        "There are not enough locations to fit all required items. Enable additional locations,"
                        " increase the Minikit Bundle Size, or disable the Kyber Bricks goal to free up more locations."
                        " There were %i more required progression items than non-excluded locations.",
                        needed - total_replaceable)
                else:
                    self.world.option_error(
                        "There are not enough locations to fit all required items. Enable additional locations or"
                        " increase the Minikit Bundle Size to free up more locations. There were %i more required"
                        " progression items than locations.",
                        needed - total_replaceable)
            character_percentage = ok_to_replace_character_count / total_replaceable
            character_subtract = min(needed, round(character_percentage * needed))
            extra_subtract = needed - character_subtract
            self.reserved_character -= character_subtract
            self.reserved_extra -= extra_subtract
            self.reserved_consumed_for_required += (character_subtract + extra_subtract)
            assert self.reserved_consumed_for_required == needed
        assert self.free_location_count >= 0, "free_location_count must always be >= 0"

    @property
    def free_location_count(self):
        return (self.completion
                + self.true_jedi
                + self.free_minikit
                + self.free_character
                + self.free_extra
                + self.free_ridesanity
                - self.free_consumed_for_required
                + self.reserved_consumed_for_required)

    @property
    def locations_to_fill(self):
        return (self.reserved_character
                + self.reserved_extra
                + self.required_minikit
                + self.free_location_count
                + self.required_additional)



def _determine_chapters(self: LegoStarWarsTCSWorld) -> tuple[set[str], set[str]]:
    """
    Return the set of chapter short names that have locations, and the set of chapter short names that have non-excluded
    locations.
    """
    if self.goal_chapter:
        if self.options.goal_chapter_locations_mode == GoalChapterLocationsMode.option_removed:
            chapters_with_locations = self.enabled_chapters - {self.goal_chapter}
            chapters_with_non_excluded_locations = self.enabled_non_goal_chapters
        elif self.options.goal_chapter_locations_mode == GoalChapterLocationsMode.option_excluded:
            chapters_with_locations = self.enabled_chapters
            chapters_with_non_excluded_locations = self.enabled_non_goal_chapters
        else:
            assert self.options.goal_chapter_locations_mode == GoalChapterLocationsMode.option_normal
            chapters_with_locations = self.enabled_chapters
            chapters_with_non_excluded_locations = self.enabled_chapters
    else:
        chapters_with_locations = self.enabled_chapters
        chapters_with_non_excluded_locations = self.enabled_chapters

    return chapters_with_locations, chapters_with_non_excluded_locations


def _create_possible_pool(self: LegoStarWarsTCSWorld) -> dict[str, GenericCharacterData]:
    # If Gunship Cavalry (Original), Pod Race (Original) and Anakin's Flight get updated to require Vehicles again,
    # then Republic Gunship, Anakin's Pod and Naboo Starfighter would be required items to included in the pool.
    # if not vehicle_chapters_enabled:
    #     if "Anakin's Flight" in self.enabled_bonuses:
    #         vehicle = CHARACTERS_AND_VEHICLES_BY_NAME["Naboo Starfighter"]
    #         possible_pool_character_items[vehicle.name] = vehicle
    #     if "Gunship Cavalry (Original)" in self.enabled_bonuses:
    #         vehicle = CHARACTERS_AND_VEHICLES_BY_NAME["Republic Gunship"]
    #         possible_pool_character_items[vehicle.name] = vehicle
    #     if "Mos Espa Pod Race (Original)" in self.enabled_bonuses:
    #         vehicle = CHARACTERS_AND_VEHICLES_BY_NAME["Anakin's Pod"]
    #         possible_pool_character_items[vehicle.name] = vehicle
    # todo: Reserve spaces in the item pool for vehicles and non-vehicles separately, based on how many locations
    #  unlock characters of the each type.
    vehicle_chapters_enabled = not VEHICLE_CHAPTER_SHORTNAMES.isdisjoint(self.enabled_chapters)

    possible_pool_character_items = {name: char for name, char in CHARACTERS_AND_VEHICLES_BY_NAME.items()
                                     if char.is_sendable and (vehicle_chapters_enabled
                                                              or char.item_type != "Vehicle")}
    if self.goal_chapter and self.options.goal_chapter_locations_mode == GoalChapterLocationsMode.option_removed:
        # Vehicle chapters could be disabled for normal chapters, but the goal chapter could be a vehicle chapter,
        # so the vehicles required for the goal chapter need to be forced into the item pool.
        for name in CHAPTER_AREA_STORY_CHARACTERS[self.goal_chapter]:
            if name not in possible_pool_character_items:
                possible_pool_character_items[name] = CHARACTERS_AND_VEHICLES_BY_NAME[name]

    return possible_pool_character_items


def create_starting_characters_for_character_locked_chapters(
        self: LegoStarWarsTCSWorld,
        possible_pool_character_items: dict[str, GenericCharacterData],
) -> None:
    """

    :param self:
    :param possible_pool_character_items:
    :return:
    """
    # Add characters necessary to unlock the starting chapter into starting inventory.
    # The story character names are a `set`, so sort before iterating to get a deterministic iteration order.
    for name in sorted(CHAPTER_AREA_STORY_CHARACTERS[self.starting_chapter.short_name]):
        self.push_precollected(self.create_item(name))
        del possible_pool_character_items[name]


def create_starting_characters_for_unlock_item_locked_chapters(
        self: LegoStarWarsTCSWorld,
        possible_pool_character_items: dict[str, GenericCharacterData],
) -> None:
    """

    :param self:
    :param possible_pool_character_items:
    :return:
    """
    # Only give enough characters to fulfil the main requirements of the starting chapter.
    # The alt requirements, if they exist, often replace a common requirement with a rarer requirement.
    starting_chapter_entrance_abilities = self.starting_chapter.completion_main_ability_requirements

    starting_chapter_entrance_abilities_list = sorted(starting_chapter_entrance_abilities)

    # Shuffle the order the abilities will be fulfilled in.
    fulfilled_abilities: set[CharacterAbility] = set()
    self.random.shuffle(starting_chapter_entrance_abilities_list)

    # Always pick CAN_ abilities last to avoid picking very boring characters at the start with basically no
    # actual abilities.
    # Always pick VEHICLE_BLASTER last to avoid picking a VEHICLE_BLASTER, and then picking a VEHICLE_TOW that
    # also has VEHICLE_BLASTER.
    pick_order = {
        CharacterAbility.CAN_ATTACK_UP_CLOSE: 1,
        CharacterAbility.CAN_RIDE_VEHICLES: 1,
        CharacterAbility.CAN_JUMP_NORMALLY: 1,
        CharacterAbility.CAN_PULL_LEVERS: 1,
        CharacterAbility.CAN_PUSH_OBJECTS: 1,
        CharacterAbility.CAN_BUILD_BRICKS: 1,
        CharacterAbility.VEHICLE_BLASTER: 1,
        **dict.fromkeys(CHAPTER_SPECIFIC_FLAGS, 2),
    }
    starting_chapter_entrance_abilities_list.sort(key=lambda ability: pick_order.get(ability, 0))

    # Finally pick characters to fulfil the abilities.
    ability_costs = {
        CharacterAbility.SITH: 10,
        CharacterAbility.BOUNTY_HUNTER: 10,
        CharacterAbility.ASTROMECH: 8,
        CharacterAbility.SHORTIE: 8,
        CharacterAbility.HIGH_JUMP: 8,
        CharacterAbility.HOVER: 7,
        CharacterAbility.IMPERIAL: 6,
        CharacterAbility.CAN_WEAR_HAT: 0,
        CharacterAbility.JEDI: 2,
        CharacterAbility.BLASTER: 2,
        CharacterAbility.CAN_ATTACK_UP_CLOSE: 1,
        CharacterAbility.CAN_RIDE_VEHICLES: 1,
        CharacterAbility.CAN_JUMP_NORMALLY: 1,
        CharacterAbility.CAN_PULL_LEVERS: 1,
        CharacterAbility.VEHICLE_TOW: 10,
        CharacterAbility.VEHICLE_TIE: 8,
        CharacterAbility.VEHICLE_BLASTER: 2,
        CharacterAbility.IS_A_VEHICLE: 0,
    }

    def sort_func(data: GenericCharacterData):
        value = 0
        for ability in data.abilities:
            value += ability_costs.get(ability, 0)
        return value

    # Pre-calculate the list of characters that provide each individual ability.
    characters_by_ability: dict[CharacterAbility, list[GenericCharacterData]] = {}
    for character_data in possible_pool_character_items.values():
        for ability in character_data.abilities:
            characters_by_ability.setdefault(ability, []).append(character_data)

    for individual_ability in starting_chapter_entrance_abilities_list:
        if individual_ability in fulfilled_abilities:
            # A character picked earlier also had this ability, so there does not need to be another character
            # picked.
            continue
        candidates = characters_by_ability[individual_ability]
        # Shuffle first, so that ties on the sort have deterministically random order.
        self.random.shuffle(candidates)
        candidates.sort(key=sort_func)
        # Randomly pick from the first quarter to avoid always picking the character in the list with the lowest
        # ability score.
        picks = candidates[0:max(1, round(len(candidates) * 0.25))]
        picked = self.random.choice(picks)
        self.push_precollected(self.create_item(picked.name))
        del possible_pool_character_items[picked.name]
        fulfilled_abilities.update(picked.abilities)
        for ability in picked.abilities:
            # The ability is provided by the picked character, so it is no longer relevant for sorting future
            # picks.
            ability_costs[ability] = 0


def determine_item_pool_abilities(
        self: LegoStarWarsTCSWorld,
        chapters_with_locations: set[str]
) -> ItemPoolAbilityRequirements:
    # Determine what abilities must be supplied by the item pool for all locations to be reachable with all items in
    # the item pool.
    required_character_abilities_in_pool = CharacterAbility.NONE
    optional_character_abilities = CharacterAbility.NONE
    # `chapters_with_locations` is a `set`, so sort for deterministic results from the `self.random` usage.
    for shortname in sorted(chapters_with_locations):
        power_brick_abilities = POWER_BRICK_REQUIREMENTS[shortname][1]
        if power_brick_abilities is not None:
            if isinstance(power_brick_abilities, tuple):
                at_least_one_already_required = False
                for abilities in power_brick_abilities:
                    if abilities in required_character_abilities_in_pool:
                        at_least_one_already_required = True
                    # Mark the abilities as optional. They will be included in logic, but won't necessarily be
                    # guaranteed to be provided by the item pool.
                    optional_character_abilities |= abilities

                if not at_least_one_already_required:
                    # Pick any one of the abilities to be required to be provided by the item pool.
                    picked = self.random.choice(power_brick_abilities)
                    required_character_abilities_in_pool |= picked
            else:
                required_character_abilities_in_pool |= power_brick_abilities
        if self.options.enable_minikit_locations.value:
            for requirements in SHORT_NAME_TO_CHAPTER_AREA[shortname].all_minikits_ability_requirements:
                required_character_abilities_in_pool |= requirements
    for bonus_name in self.enabled_bonuses:
        area = BONUS_NAME_TO_BONUS_AREA[bonus_name]
        required_character_abilities_in_pool |= area.completion_ability_requirements
    for _area_name, ridable_spots in self.ridesanity_spots.items():
        for _spot, any_ridable_ability_requirements in ridable_spots:
            if any_ridable_ability_requirements:
                if len(any_ridable_ability_requirements) == 1:
                    required_character_abilities_in_pool |= any_ridable_ability_requirements[0]
                else:
                    at_least_one_already_required = False
                    for ridable_ability_requirements in any_ridable_ability_requirements:
                        if ridable_ability_requirements in required_character_abilities_in_pool:
                            at_least_one_already_required = True
                        # Mark the abilities as optional. They will be included in logic, but won't necessarily be
                        # guaranteed to be provided by the item pool.
                        optional_character_abilities |= ridable_ability_requirements

                    if not at_least_one_already_required:
                        # Pick any one of the abilities to be required to be provided by the item pool.
                        picked = self.random.choice(any_ridable_ability_requirements)
                        required_character_abilities_in_pool |= picked
    return ItemPoolAbilityRequirements(required_character_abilities_in_pool, optional_character_abilities)


def create_item_pool(self: LegoStarWarsTCSWorld):
    # Determine how many chapter worth's of locations are enabled.
    goal_chapter_locations_excluded = (
            self.goal_chapter
            and self.options.goal_chapter_locations_mode == GoalChapterLocationsMode.option_excluded
    )

    chapters_with_locations, chapters_with_non_excluded_locations = _determine_chapters(self)

    possible_pool_character_items = _create_possible_pool(self)

    pool_required_chapter_unlock_items: list[str]
    if self.options.chapter_unlock_requirement == ChapterUnlockRequirement.option_story_characters:
        chapters_unlock_with_characters = True
        pool_required_chapter_unlock_items = []

        create_starting_characters_for_character_locked_chapters(self, possible_pool_character_items)
    elif self.options.chapter_unlock_requirement == ChapterUnlockRequirement.option_chapter_item:
        chapters_unlock_with_characters = False
        starting_chapter_short_name = self.starting_chapter.short_name
        self.push_precollected(self.create_item(f"{starting_chapter_short_name} Unlock"))
        pool_required_chapter_unlock_items = [f"{short_name} Unlock" for short_name in self.enabled_chapters
                                              if short_name != starting_chapter_short_name]
        del starting_chapter_short_name

        create_starting_characters_for_unlock_item_locked_chapters(self, possible_pool_character_items)
    else:
        raise Exception(f"Unexpected Chapter Unlock Requirement {self.options.chapter_unlock_requirement}")

    # Create the starting Episode Unlock item if Episode Unlock items are required to access chapters within an Episode.
    if self.options.episode_unlock_requirement == "episode_item":
        self.push_precollected(self.create_item(f"Episode {self.starting_episode} Unlock"))

    item_pool_ability_requirements = determine_item_pool_abilities(self, chapters_with_locations)

    level_access_character_counts = item_pool_ability_requirements.update_for_chapter_lock_requirements(
        self, chapters_unlock_with_characters)

    # Gather the abilities of all items in starting inventory, so that they can be removed from other created items,
    # improving generation performance.
    initial_starting_items = cast(list[LegoStarWarsTCSItem], self.multiworld.precollected_items[self.player])
    starting_abilities = CharacterAbility.NONE
    for item in initial_starting_items:
        starting_abilities |= item.abilities

    item_pool_ability_requirements.update_for_starting_abilities(starting_abilities)

    return _create_items(
        self,
        level_access_character_counts,
        possible_pool_character_items,
        len(chapters_with_non_excluded_locations),
        goal_chapter_locations_excluded,
        pool_required_chapter_unlock_items,
        chapters_unlock_with_characters,
        item_pool_ability_requirements,
    )


def _append_level_access_required_characters(
        pool_required_characters: list[GenericCharacterData],
        level_access_character_counts: Counter[str],
        possible_pool_character_items: dict[str, GenericCharacterData],
        item_pool_ability_requirements: ItemPoolAbilityRequirements,
) -> None:
    for name in level_access_character_counts.keys():
        if name not in possible_pool_character_items:
            continue
        assert level_access_character_counts[name] > 0
        char = CHARACTERS_AND_VEHICLES_BY_NAME[name]
        item_pool_ability_requirements.required &= ~char.abilities
        pool_required_characters.append(char)
        del possible_pool_character_items[name]


def _append_remaining_required_characters(
        pool_required_characters: list[GenericCharacterData],
        self: LegoStarWarsTCSWorld,
        possible_pool_character_items: dict[str, GenericCharacterData],
        item_pool_ability_requirements: ItemPoolAbilityRequirements,
) -> None:
    possible_pool_character_names = list(possible_pool_character_items.values())
    self.random.shuffle(possible_pool_character_names)
    # Sort preferred characters first so that they are picked in preference.
    preferred_characters = self.options.preferred_characters.value
    if preferred_characters:
        possible_pool_character_names.sort(key=lambda char: -1 if char.name in preferred_characters else 0)

    for character in possible_pool_character_names:
        if item_pool_ability_requirements.required & character.abilities:
            pool_required_characters.append(character)
            item_pool_ability_requirements.required &= ~character.abilities
            del possible_pool_character_items[character.name]


def prepare_extras(world: LegoStarWarsTCSWorld) -> tuple[list[str], list[str]]:
    """
    Pre-collect starting Extras and get lists of the required and non-required Extras to be included in the item pool.
    :param world: The world that is creating items.
    :return: A list of item names required to be included in the item pool and a list of item names not required to be
     included in the item pool.
    """
    # Start with all sendable Extras as possible to add to the item pool.
    possible_pool_extras = {name: extra for name, extra in EXTRAS_BY_NAME.items() if extra.is_sendable}

    if not world.options.enable_starting_extras_locations:
        # The starting Extra purchases are vanilla, so don't include their Extras in the pool.
        for extra in PURCHASABLE_NON_POWER_BRICK_EXTRAS:
            del possible_pool_extras[extra.name]

    if world.options.start_with_detectors:
        detectors = {"Minikit Detector", "Power Brick Detector"}
        assert detectors <= set(possible_pool_extras.keys())
        # The detector Extras are being given to the player at the start, so don't include their Extras in the pool.
        for extra_name in detectors:
            del possible_pool_extras[extra_name]
        for detector in sorted(detectors):
            world.push_precollected(world.create_item(detector))

    non_required_extras: list[str] = list(possible_pool_extras.keys())

    max_studs_purchase = max(loc.studs_cost for loc in world.get_locations()
                             if isinstance(loc, LegoStarWarsTCSShopLocation))

    required_score_multipliers = world.get_score_multiplier_requirement(max_studs_purchase)
    # Increase required_score_multipliers to at least 1 if there are any enabled chapters with difficult or
    # potentially impossible True Jedi.
    if (required_score_multipliers < 1
            and world.options.enable_true_jedi_locations
            and not world.options.easier_true_jedi
            and not DIFFICULT_OR_IMPOSSIBLE_TRUE_JEDI.isdisjoint(world.enabled_chapters_with_locations)):
        required_score_multipliers = 1

    non_required_score_multipliers = 5 - required_score_multipliers
    assert 0 <= required_score_multipliers <= 5
    pool_required_extras: list[str] = [progressive_score_multiplier_name] * required_score_multipliers
    non_required_extras.extend([progressive_score_multiplier_name] * non_required_score_multipliers)
    return pool_required_extras, non_required_extras


def _sort_for_preferred_extras(non_required_extras: list[str], self: LegoStarWarsTCSWorld) -> list[str]:
    """
    Sort preferred Extras to the front of `non_required_extras`.
    :param non_required_extras:
    :param self:
    :return:
    """
    preferred_extras = self.options.preferred_extras.value
    if not preferred_extras:
        return non_required_extras
    # The score multipliers are in descending order because Score x10 means the player prefers all score multipliers
    # to be in the item pool
    individual_score_multipliers = [
        "Score x10",
        "Score x8",
        "Score x6",
        "Score x4",
        "Score x2",
    ]
    non_required_score_multiplier_indices = [i for i, extra in enumerate(non_required_extras)
                                             if extra == progressive_score_multiplier_name]
    if not non_required_score_multiplier_indices or preferred_extras.isdisjoint(individual_score_multipliers):
        num_preferred_non_required_score_multipliers = 0
    else:
        # Find the highest preferred Score multiplier and ensure the lower multipliers are also preferred.
        num_preferred_non_required_score_multipliers = len(non_required_score_multiplier_indices)
        # Score x10 -> All non-required are preferred.
        # Score x8 -> (All - 1) non-required are preferred.
        # ...
        # Score x2 -> (All - 4) non-required are preferred.
        for count_not_preferred, multiplier in enumerate(individual_score_multipliers):
            if multiplier in preferred_extras:
                num_preferred_non_required_score_multipliers -= count_not_preferred
                break
        else:
            raise Exception("Unreachable. At least one score multiplier in `individual_score_multipliers` must be"
                            " present in `preferred_extras` because of the `not a.isdisjoint(b)` check, so the loop"
                            " should always break.")

    if num_preferred_non_required_score_multipliers <= 0:
        # Simply sort preferred extras to the front so that they get picked first.
        non_required_extras.sort(key=lambda extra: -1 if extra in preferred_extras else 0)
        return non_required_extras
    else:
        # Pick the Progressive Score Multipliers randomly for fairness.
        picked_preferred_score_multiplier_indices = self.random.sample(non_required_score_multiplier_indices,
                                                                       num_preferred_non_required_score_multipliers)
        # Sort preferred extras to the front by splitting the extras into two lists of preferred and non-preferred.
        preferred_extras_list = []
        non_preferred_extras_list = []
        for i, item in enumerate(non_required_extras):
            if item in preferred_extras:
                preferred_extras_list.append(item)
            elif item == progressive_score_multiplier_name and i in picked_preferred_score_multiplier_indices:
                preferred_extras_list.append(item)
            else:
                non_preferred_extras_list.append(item)
        return preferred_extras_list + non_preferred_extras_list


# todo: This function is still too large, and should be broken up into smaller parts.
def _create_items(
        self: LegoStarWarsTCSWorld,
        level_access_character_counts: Counter[str],
        possible_pool_character_items: dict[str, GenericCharacterData],
        non_excluded_chapter_count: int,
        goal_chapter_locations_excluded: bool,
        pool_required_chapter_unlock_items: list[str],
        chapters_unlock_with_characters: bool,
        item_pool_ability_requirements: ItemPoolAbilityRequirements,
) -> list[LegoStarWarsTCSItem]:
    """
    Main item pool creation function.
    :param self:
    :param level_access_character_counts: The names of characters that lock access to levels, and the count of levels
    that character locks access to for the current player.
    :param possible_pool_character_items: Character item names and their data that are possible to include in the item
    pool.
    :param non_excluded_chapter_count: The number of enabled chapters that do not have their locations automatically
    excluded.
    :param goal_chapter_locations_excluded: Whether the goal chapter's locations are automatically excluded.
    :param pool_required_chapter_unlock_items: Chapter Unlock item names that must be provided by the item pool.
    :param chapters_unlock_with_characters: Whether chapters are locked by characters, rather than by unlock items.
    :param item_pool_ability_requirements: CharacterAbility requirements for the item pool.
    :return:
    """
    item_creator = ItemCreator(self, item_pool_ability_requirements)

    # These abilities are provided by the starting characters, so these abilities can be stripped from other
    # characters, improving logic performance.
    self.starting_character_abilities = item_pool_ability_requirements.starting

    # The abilities that need to be fulfilled by the item pool, retrieved, before modification, to double-check that all
    # required abilities are accounted for.
    required_abilities_to_fulfil = item_pool_ability_requirements.required

    pool_required_characters: list[GenericCharacterData] = []
    # Append characters that are required to access levels, updating `item_pool_ability_requirements` as characters are
    # appended.
    _append_level_access_required_characters(pool_required_characters,
                                             level_access_character_counts,
                                             possible_pool_character_items,
                                             item_pool_ability_requirements)
    # Append additional characters to satisfy the remaining required abilities in `item_pool_ability_requirements`.
    _append_remaining_required_characters(pool_required_characters,
                                          self,
                                          possible_pool_character_items,
                                          item_pool_ability_requirements)

    non_required_characters = list(possible_pool_character_items.values())

    assert item_pool_ability_requirements.required is CharacterAbility.NONE, \
           "There are required abilities remaining that have not been fulfilled."
    assert required_abilities_to_fulfil in reduce(
        or_, (data.abilities for data in pool_required_characters), CharacterAbility.NONE), \
        "The abilities of the required characters are not a subset of the required abilities."

    # Get the required, and non-required extras.
    pool_required_extras, non_required_extras = prepare_extras(self)

    item_location_counts = ItemLocationCounts(self, non_excluded_chapter_count, goal_chapter_locations_excluded)
    item_location_counts.set_character_counts(pool_required_characters)
    item_location_counts.set_extra_counts(pool_required_extras)
    item_location_counts.set_true_jedi_counts()
    item_location_counts.set_completion_counts()
    item_location_counts.set_minikit_counts()
    item_location_counts.set_ridesanity_counts()

    free_location_count = item_location_counts.free_location_count

    assert free_location_count >= 0, "initial free_location_count should always be >= 0"

    # Get other required items that don't belong to any particular category, and don't have associated vanilla
    # locations, and consume free locations to fit these items into the pool.
    start_inventory_token_count, other_required_items = item_location_counts.set_additional_item_counts(
        pool_required_chapter_unlock_items)

    # Pre-collect the Episode Completion Tokens that won't be in the pool, but the player will start with.
    for _ in range(start_inventory_token_count):
        self.push_precollected(item_creator.create_item("Episode Completion Token"))

    # If there was not enough space for all required items, replace reserved space, for non-required items, until there
    # is enough space, or raise an OptionError if there is still not enough space, even with all reserved space
    # replaced.
    item_location_counts.free_space_for_required_items()

    # Check that the number of locations that are expected to be filled matches the number of locations that are
    # unfilled.
    expected_num_to_fill = item_location_counts.locations_to_fill
    unfilled_locations = self.multiworld.get_unfilled_locations(self.player)
    num_to_fill = len(self.multiworld.get_unfilled_locations(self.player))

    assert num_to_fill == expected_num_to_fill, \
        f"Expected {expected_num_to_fill} locations to fill, but got {num_to_fill}"

    # Ensure there is enough space in the item pool for as many filler items as there are excluded locations.
    required_excludable_count = (
            sum(loc.progress_type == LocationProgressType.EXCLUDED for loc in unfilled_locations)
    )

    # fixme: Some reserved characters can be Filler classification, which would be fine being placed on excluded
    #  locations, so this check is currently overly strict because it assumes that reserved characters will be
    #  Useful or Progression.
    if free_location_count < required_excludable_count:
        # This shouldn't really happen unless basically the entire world is excluded and/or barely any locations
        # are enabled.
        needed = required_excludable_count - free_location_count
        # Find how many character/extra locations can be used for filler placement without issue.
        ok_to_replace_character_count = max(0, item_location_counts.reserved_character - item_location_counts.required_character)
        ok_to_replace_extras_count = max(0, item_location_counts.reserved_extra - item_location_counts.required_extra)
        total_replaceable = ok_to_replace_character_count + ok_to_replace_extras_count
        if needed > total_replaceable:
            # There are too many non-excludable items for the number of excluded locations.
            # Give up.
            # If this is too common of an issue, it would be possible to add some of the required characters/extras
            # to start inventory instead of erroring here.
            non_excluded_count = num_to_fill - required_excludable_count
            required_count = (
                    item_location_counts.required_extra
                    + item_location_counts.required_character
                    + item_location_counts.required_minikit
                    + len(other_required_items)
            )
            self.option_error("There are too few non-excluded locations to fit all required progression items."
                              " There are %i locations, %i of which are not excluded, but there are %i required"
                              " items that cannot be placed on excluded locations.",
                              num_to_fill, non_excluded_count, required_count)
        character_percentage = ok_to_replace_character_count / total_replaceable
        character_subtract = min(needed, round(character_percentage * needed))
        extra_subtract = needed - character_subtract
        item_location_counts.reserved_character -= character_subtract
        item_location_counts.reserved_extra -= extra_subtract
        free_location_count = 0
    else:
        free_location_count -= required_excludable_count

    item_pool: list[LegoStarWarsTCSItem] = []

    created_item_names: set[str] = set()

    def add_to_pool(item: LegoStarWarsTCSItem):
        item_pool.append(item)
        created_item_names.add(item.name)

    # Create required generic items that don't fall into any particular category.
    for name in other_required_items:
        add_to_pool(item_creator.create_item(name))
    num_to_fill -= len(other_required_items)

    # Create required characters.
    start_inventory_required_characters_count: int
    if item_location_counts.reserved_character < item_location_counts.required_character:
        # If there are not enough reserved character unlock locations for the required characters, subtract from the
        # free location count.
        to_subtract = item_location_counts.required_character - item_location_counts.reserved_character
        if free_location_count < to_subtract:
            # If there are not enough free locations, some of the required characters will have to be added to start
            # inventory.
            start_inventory_required_characters_count = to_subtract - free_location_count
            self.log_warning("There were not enough locations to add all required characters to the item pool,"
                             " some of them have been added to starting inventory")
            free_location_count = 0
        else:
            free_location_count -= to_subtract
            start_inventory_required_characters_count = 0
        item_location_counts.reserved_character = 0
    else:
        item_location_counts.reserved_character -= item_location_counts.required_character
        start_inventory_required_characters_count = 0

    self.random.shuffle(pool_required_characters)
    pool_required_chars = pool_required_characters[start_inventory_required_characters_count:]
    start_required_chars = pool_required_characters[:start_inventory_required_characters_count]
    for character in pool_required_chars:
        add_to_pool(item_creator.create_item(character.name))
    num_to_fill -= len(pool_required_chars)
    assert num_to_fill >= 0
    for character in start_required_chars:
        self.push_precollected(item_creator.create_item(character.name))

    # Create required extras.
    start_inventory_required_extras_count: int
    if item_location_counts.reserved_extra < item_location_counts.required_extra:
        to_subtract = item_location_counts.required_extra - item_location_counts.reserved_extra
        if free_location_count < to_subtract:
            start_inventory_required_extras_count = to_subtract - free_location_count
            self.log_warning("There were not enough locations to add all required Extras to the item pool,"
                             " some of them have been added to starting inventory")
            free_location_count = 0
        else:
            free_location_count -= to_subtract
            start_inventory_required_extras_count = 0
        item_location_counts.reserved_extra = 0
    else:
        item_location_counts.reserved_extra -= item_location_counts.required_extra
        start_inventory_required_extras_count = 0

    self.random.shuffle(pool_required_extras)
    start_required_extras = pool_required_extras[:start_inventory_required_extras_count]
    pool_required_extras = pool_required_extras[start_inventory_required_extras_count:]
    for extra_name in pool_required_extras:
        add_to_pool(item_creator.create_item(extra_name))
    num_to_fill -= len(pool_required_extras)
    assert num_to_fill >= 0
    for extra_name in start_required_extras:
        self.push_precollected(item_creator.create_item(extra_name))

    # Create required minikits.
    for _ in range(self.minikit_bundle_count):
        add_to_pool(item_creator.create_item(self.minikit_bundle_name))
    num_to_fill -= self.minikit_bundle_count
    assert num_to_fill >= 0

    # Create as many non-required characters as there are reserved character locations.
    self.random.shuffle(non_required_characters)
    # Sort preferred characters first so that they are picked in preference.
    preferred_characters = self.options.preferred_characters.value
    if preferred_characters:
        non_required_characters.sort(key=lambda char: -1 if char.name in preferred_characters else 0)
    picked_chars = non_required_characters[:item_location_counts.reserved_character]
    leftover_chars = non_required_characters[item_location_counts.reserved_character:]
    for char in picked_chars:
        item = item_creator.create_item(char.name)
        add_to_pool(item)
        if required_excludable_count > 0 and item.excludable:
            required_excludable_count -= 1
    num_to_fill -= len(picked_chars)
    assert num_to_fill >= 0

    # Create as many non-required extras as there are reserved power brick locations.
    self.random.shuffle(non_required_extras)
    # Sort preferred Extras first so that they are picked in preference.
    non_required_extras = _sort_for_preferred_extras(non_required_extras, self)

    picked_extras = non_required_extras[:item_location_counts.reserved_extra]
    leftover_extras = non_required_extras[item_location_counts.reserved_extra:]
    for extra in picked_extras:
        item = item_creator.create_item(extra)
        add_to_pool(item)
        if required_excludable_count > 0 and item.excludable:
            required_excludable_count -= 1
    num_to_fill -= len(picked_extras)
    assert num_to_fill >= 0

    # Determine items to fill out the rest of the item pool according to the weights in the options.
    leftover_choices: list[list[LegoStarWarsTCSItem]] = []
    leftover_weights: list[int] = []

    leftover_character_items = list(map(item_creator.create_item, (char.name for char in leftover_chars)))
    character_weight = self.options.filler_weight_characters.value
    if character_weight and leftover_character_items:
        leftover_choices.append(leftover_character_items)
        leftover_weights.append(character_weight)

    leftover_extra_items = list(map(item_creator.create_item, leftover_extras))
    extras_weight = self.options.filler_weight_extras.value
    if extras_weight and leftover_extra_items:
        leftover_choices.append(leftover_extra_items)
        leftover_weights.append(extras_weight)

    junk_names_and_weights = self.options.junk_weights.value
    junk_names = tuple(junk_names_and_weights.keys())
    junk_weights = tuple(junk_names_and_weights.values())

    def create_excludable_junk_items(count: int) -> list[LegoStarWarsTCSItem]:
        names = self.random.choices(junk_names, junk_weights, k=count)
        return list(map(item_creator.create_item, names))

    junk_weight = self.options.filler_weight_junk.value
    if junk_weight:
        leftover_junk = create_excludable_junk_items(max(num_to_fill, required_excludable_count))
        leftover_choices.append(leftover_junk)
        leftover_weights.append(junk_weight)

    all_leftover_items: Iterable[LegoStarWarsTCSItem]
    if not leftover_choices:
        # While there is always at least one nonzero weight, it's possible to have run out of Extras or Characters.
        all_leftover_items = []
    elif len(leftover_choices) == 1:
        all_leftover_items = leftover_choices[0]
    else:
        weighted_leftover_items: list[LegoStarWarsTCSItem] = []
        needed_excludable = required_excludable_count
        # Items will be popped from the ends rather than taken from the start, so reverse the lists.
        for item_list in leftover_choices:
            item_list.reverse()
        while (len(weighted_leftover_items) < num_to_fill or needed_excludable > 0) and leftover_choices:
            picked_list = self.random.choices(leftover_choices, leftover_weights, k=1)[0]
            item = picked_list.pop()
            if needed_excludable > 0 and item.excludable:
                needed_excludable -= 1
            weighted_leftover_items.append(item)
            if not picked_list:
                # The picked list is now empty, so update leftover_choices
                next_leftover_choices: list[list[LegoStarWarsTCSItem]] = []
                next_leftover_weights: list[int] = []
                for item_list, weight in zip(leftover_choices, leftover_weights):
                    if item_list:
                        next_leftover_choices.append(item_list)
                        next_leftover_weights.append(weight)

                leftover_choices = next_leftover_choices
                leftover_weights = next_leftover_weights

                if len(leftover_choices) == 1:
                    # There is only one list left, so append all elements from it.
                    remaining_list = next_leftover_choices[0]
                    weighted_leftover_items.extend(reversed(remaining_list))
                    remaining_list.clear()
                    break

        all_leftover_items = weighted_leftover_items

    # Split the all_leftover_items into separate lists for required excludable items and other leftover items.
    excludable_leftover_items = []
    leftover_items = []
    for item in all_leftover_items:
        if required_excludable_count > 0 and item.excludable:
            excludable_leftover_items.append(item)
            required_excludable_count -= 1
        else:
            leftover_items.append(item)
    if len(excludable_leftover_items) < required_excludable_count:
        excludable_leftover_items.extend(create_excludable_junk_items(required_excludable_count))
    # Required excludable items must be picked first.
    leftover_items = excludable_leftover_items + leftover_items
    if len(leftover_items) < num_to_fill:
        leftover_items.extend(create_excludable_junk_items(num_to_fill - len(leftover_items)))
    else:
        leftover_items = leftover_items[:num_to_fill]
    assert len(leftover_items) == num_to_fill

    for item in leftover_items:
        add_to_pool(item)

    assert len(item_pool) == len(unfilled_locations)

    # todo: In the future, individual characters may be relevant to logic, e.g. Droideka, which should never be
    #  given deprioritized + skip_balancing.
    # Give deprioritized + skip_balancing to characters with only common abilities, and that do not give access to
    # levels.
    non_level_access_character_items: list[LegoStarWarsTCSItem] = []
    non_deprioritize_ability_counts: Counter[CharacterAbility] = Counter()
    for item in item_pool:
        if item.advancement and item.name in CHARACTERS_AND_VEHICLES_BY_NAME:
            if progression_deprioritized_skip_balancing in item.classification:
                # Don't count abilities from characters that are already deprioritized + skip_balancing.
                continue
            abilities = item.abilities
            if abilities:
                non_deprioritize_ability_counts.update(abilities)
            if chapters_unlock_with_characters:
                if level_access_character_counts[item.name] == 0:
                    assert abilities, ("No abilities should mean the character item is not progression currently if"
                                       " the character does not unlock levels")
                    non_level_access_character_items.append(item)
            else:
                non_level_access_character_items.append(item)
    self.random.shuffle(non_level_access_character_items)
    for item in non_level_access_character_items:
        abilities = item.abilities
        for ability in abilities:
            # 3 is a magic number and could be changed if other values produce nicer results.
            if non_deprioritize_ability_counts[ability] <= 3:
                # One of the abilities is uncommon.
                break
        else:
            # None of the abilities were uncommon, so add the deprioritize and skip balancing classifications.
            item.classification |= progression_deprioritized_skip_balancing
            if abilities:
                # Reduce the remaining ability counts from non-deprioritized characters
                non_deprioritize_ability_counts.subtract(abilities)
    assert all(ability.bit_count() == 1 for ability in non_deprioritize_ability_counts)

    return item_pool
