import logging
from collections import Counter
from typing import Mapping, Any, NoReturn, Callable, ClassVar, TextIO

from BaseClasses import (
    Region,
    ItemClassification,
    CollectionState,
    Location,
    Entrance,
    Tutorial,
    Item,
    MultiWorld,
)
from Options import OptionError
from worlds.AutoWorld import WebWorld, World
from worlds.LauncherComponents import components, Component, launch_subprocess, Type
from worlds.generic.Rules import set_rule, add_rule

from . import constants, regions, item_pool
from .constants import (
    CharacterAbility,
    GOLD_BRICK_EVENT_NAME,
    GAME_NAME,
    CHAPTER_SPECIFIC_FLAGS,
    progression_deprioritized_skip_balancing,
)
from .items import (
    ITEM_NAME_TO_ID,
    LegoStarWarsTCSItem,
    ExtraData,
    NonPowerBrickExtraData,
    VehicleData,
    CharacterData,
    GenericCharacterData,
    ITEM_DATA_BY_NAME,
    CHARACTERS_AND_VEHICLES_BY_NAME,
    USEFUL_NON_PROGRESSION_CHARACTERS,
    MINIKITS_BY_COUNT,
    MINIKITS_BY_NAME,
    EXTRAS_BY_NAME,
    SHOP_SLOT_REQUIREMENT_TO_UNLOCKS,
    PURCHASABLE_NON_POWER_BRICK_EXTRAS,
)
from .levels import (
    BonusArea,
    ChapterArea,
    CHAPTER_AREAS,
    BONUS_AREAS,
    EPISODE_TO_CHAPTER_AREAS,
    CHAPTER_AREA_STORY_CHARACTERS,
    ALL_AREA_REQUIREMENT_CHARACTERS,
    VEHICLE_CHAPTER_SHORTNAMES,
    SHORT_NAME_TO_CHAPTER_AREA,
    POWER_BRICK_REQUIREMENTS,
    ALL_MINIKITS_REQUIREMENTS,
    BONUS_NAME_TO_BONUS_AREA,
    BOSS_UNIQUE_NAME_TO_CHAPTER,
    DIFFICULT_OR_IMPOSSIBLE_TRUE_JEDI,
    CHAPTER_SPECIFIC_REQUIREMENTS,
)
from .locations import LOCATION_NAME_TO_ID, LegoStarWarsTCSLocation, LEVEL_SHORT_NAMES_SET, LegoStarWarsTCSShopLocation
from .options import (
    LegoStarWarsTCSOptions,
    StartingChapter,
    AllEpisodesCharacterPurchaseRequirements,
    MinikitGoalAmount,
    OnlyUniqueBossesCountTowardsGoal,
    OPTION_GROUPS,
    GoalChapterLocationsMode,
    ChapterUnlockRequirement,
)
from .option_resolution.common import resolve_options
from .ridables import RIDABLES_REQUIREMENTS
from .item_groups import ITEM_GROUPS
from .location_groups import LOCATION_GROUPS


def launch_client(*args: str):
    # Lazy import. Generation does not need to even load client modules, it would just be a waste of memory.
    from .client import launch
    launch_subprocess(launch, name="LegoStarWarsTheCompleteSagaClient", args=args)


components.append(Component("Lego Star Wars: The Complete Saga Client",
                            func=launch_client,
                            component_type=Type.CLIENT))


class TCSUniversalTrackerAPWorldVersionMismatchError(Exception):
    """
    Raised when Universal Tracker attempts to connect to a multiworld generated with a different APWorld version to the
    client's APWorld version.
    """


class LegoStarWarsTCSWebWorld(WebWorld):
    theme = "partyTime"
    option_groups = OPTION_GROUPS
    tutorials = [Tutorial(
        "Multiworld Setup Guide",
        "A guide for setting up Lego Star Wars: The Complete Saga to be played in Archipelago.",
        "English",
        "setup_en.md",
        "setup/en",
        ["Mysteryem"]
    )]


logger = logging.getLogger("Lego Star Wars TCS")


class LegoStarWarsTCSWorld(World):
    """Lego Star Wars: The Complete Saga"""

    game = constants.GAME_NAME
    web = LegoStarWarsTCSWebWorld()
    options: LegoStarWarsTCSOptions
    options_dataclass = LegoStarWarsTCSOptions

    item_name_to_id = ITEM_NAME_TO_ID
    location_name_to_id = LOCATION_NAME_TO_ID
    item_name_groups = ITEM_GROUPS
    location_name_groups = LOCATION_GROUPS

    origin_region_name = "Cantina"

    # Requires Universal Tracker 0.2.12 or newer because the game name contains a colon.
    ut_can_gen_without_yaml = True  # Used by Universal Tracker to allow generation without player yaml.

    PROG_USEFUL_LEVEL_ACCESS_THRESHOLD_PERCENT: ClassVar[float] = 1/6
    prog_useful_level_access_threshold_count: int = 6
    character_chapter_access_counts: Counter[str]

    starting_character_abilities: CharacterAbility = CharacterAbility.NONE

    effective_character_abilities: dict[str, CharacterAbility]
    effective_item_classifications: dict[str, ItemClassification]

    enabled_chapters: set[str]
    enabled_chapters_with_locations: set[str]  # Includes the Goal Chapter when it has locations.
    enabled_non_goal_chapters: set[str]
    enabled_episodes: set[int]
    enabled_bonuses: set[str]
    enabled_bosses: set[str]
    short_name_to_boss_character: dict[str, str]
    goal_chapter: str | None

    starting_chapter: ChapterArea = SHORT_NAME_TO_CHAPTER_AREA["1-1"]
    minikit_bundle_name: str = ""
    available_minikits: int = -1
    minikit_bundle_count: int = -1
    goal_minikit_count: int = -1
    goal_minikit_bundle_count: int = -1
    goal_boss_count: int = -1
    goal_area_completion_count: int = 0
    gold_brick_event_count: int = 0
    # Used in generation to check that created Gold Bricks match the number expected to be created from options.
    expected_gold_brick_event_count: int = -1
    character_unlock_location_count: int = 0
    goal_excluded_character_unlock_location_count: int = 0

    ridesanity_spots: dict[str, list[tuple[Location | Entrance, tuple[CharacterAbility, ...]]]]
    ridesanity_location_count: int = 0

    def __init__(self, multiworld: MultiWorld, player: int):
        super().__init__(multiworld, player)
        self.enabled_chapters = set()
        self.enabled_chapters_with_locations = set()
        self.enabled_non_goal_chapters = set()
        self.enabled_episodes = set()
        self.enabled_bonuses = set()
        self.character_chapter_access_counts = Counter()
        self.short_name_to_boss_character = {}
        self.ridesanity_spots = {}

    def log_info(self, message: str, *args) -> None:
        logger.info("Lego Star Wars TCS (%s): " + message, self.player_name, *args)

    def log_warning(self, message: str, *args) -> None:
        logger.warning("Lego Star Wars TCS (%s): " + message, self.player_name, *args)

    def log_error(self, message: str, *args) -> None:
        logger.error("Lego Star Wars TCS (%s): " + message, self.player_name, *args)

    def raise_error(self, ex_type: Callable[[str], Exception], message: str, *args) -> NoReturn:
        raise ex_type(("Lego Star Wars TCS (%s): " + message) % (self.player_name, *args))

    def option_error(self, message: str, *args) -> NoReturn:
        self.raise_error(OptionError, message, *args)

    def is_universal_tracker(self) -> bool:
        """Return whether the current generation is being done with Universal Tracker rather than a real generation."""
        # The `generation_is_fake` attribute is added by Universal Tracker to allow detection of generation with
        # Universal Tracker rather than real generation.
        return hasattr(self.multiworld, "generation_is_fake")

    @property
    def starting_episode(self) -> int:
        return self.starting_chapter.episode

    def generate_early(self) -> None:
        resolve_options(self)

    def evaluate_effective_item(self,
                                name: str,
                                effective_character_abilities_lookup: dict[str, CharacterAbility] | None = None,
                                ) -> tuple[ItemClassification, CharacterAbility]:
        classification = ItemClassification.filler
        abilities = CharacterAbility.NONE

        item_data = ITEM_DATA_BY_NAME[name]
        if item_data.code < 1:
            raise RuntimeError(f"Error: Item '{name}' cannot be created")
        assert item_data.code != -1
        if isinstance(item_data, ExtraData):
            if isinstance(item_data, NonPowerBrickExtraData):
                # Only Extra Toggle is useful out of these Extras due to the high movement speed Mouse Droid and a few
                # logic breaks in Blaster/Imperial logic.
                if name == "Extra Toggle":
                    classification = ItemClassification.useful
            else:
                # Many Power Brick Extras provide cheat-like abilities to the player, or allow breaking logic (to be
                # included in logic in the future), so should be given Useful classification.
                classification = ItemClassification.useful
        elif isinstance(item_data, GenericCharacterData):
            if effective_character_abilities_lookup is not None:
                abilities = effective_character_abilities_lookup[name]
            else:
                abilities = item_data.abilities & ~self.starting_character_abilities

            if name in self.character_chapter_access_counts:
                if self.character_chapter_access_counts[name] >= self.prog_useful_level_access_threshold_count:
                    # Characters that block access to a large number of chapters get progression + useful
                    # classification. This is functionally identical to progression classification, but some
                    # games/clients may specially highlight progression + useful items.
                    classification = ItemClassification.progression | ItemClassification.useful
                else:
                    classification = ItemClassification.progression
            elif abilities & constants.RARE_AND_USEFUL_ABILITIES:
                # These abilities are typically much less common, so the characters should never be given skip_balancing
                # classification.
                classification = ItemClassification.progression
            elif abilities:
                # Characters, with only abilities where there are many other characters in the item pool providing those
                # abilities, are given deprioritized and skip_balancing classifications towards the end of create_items.
                classification = ItemClassification.progression
            elif name in USEFUL_NON_PROGRESSION_CHARACTERS:
                # Force ghosts, glitchy characters and fast characters.
                classification = ItemClassification.useful

            if name == "Admiral Ackbar":
                # There is no trap functionality, this trap classification is a joke.
                # Maybe once/if the world switches to modding, receiving this item could play the iconic "It's a trap!"
                # line.
                classification |= ItemClassification.trap
        else:
            if name in MINIKITS_BY_NAME:
                # A goal macguffin.
                if self.goal_minikit_count > 0:
                    if self.options.accessibility == "minimal" or self.minikit_bundle_count > 10:
                        # Minikits are sorted first for minimal players in stage_fill_hook to reduce generation
                        # failures, so should always be deprioritized for minimal players.
                        classification = progression_deprioritized_skip_balancing
                    else:
                        # If there are only very few bundles, e.g. the bundles are 10 minikits at a time and there are
                        # not many in the pool, then don't use deprioritized classification.
                        classification = ItemClassification.progression_skip_balancing
                else:
                    classification = ItemClassification.filler
            elif name == "Progressive Score Multiplier":
                # todo: Vary between progression and progression_skip_balancing depending on what percentage of
                #  locations need them. Make them Useful if none are needed.
                # Generic item that grants Score multiplier Extras, which are used in logic for purchases from the shop.
                classification = ItemClassification.progression
            elif name == "Episode Completion Token":
                # Very few location checks and typically late into a seed.
                classification = ItemClassification.progression_skip_balancing
            elif name == "Kyber Brick":
                # Kyber Bricks are only logically relevant to the Kyber Bricks goal and do not unlock any locations, so
                # should skip progression balancing.
                classification = ItemClassification.progression_skip_balancing
            elif name.startswith("Episode ") and name.endswith(" Unlock"):
                classification = ItemClassification.progression | ItemClassification.useful
            elif name[:3] in self.enabled_chapters and name[3:] == " Unlock":
                # Chapter Unlock item.
                classification = ItemClassification.progression

        return classification, abilities

    def get_filler_item_name(self) -> str:
        junk_weights: dict[str, int] = self.options.junk_weights.value
        return self.random.choices(tuple(junk_weights), tuple(junk_weights.values()))[0]

    def create_item(self, name: str) -> LegoStarWarsTCSItem:
        code = self.item_name_to_id[name]
        classification, collect_abilities = self.evaluate_effective_item(name)

        return LegoStarWarsTCSItem(name, classification, code, self.player, collect_abilities)

    def create_event(self, name: str) -> LegoStarWarsTCSItem:
        return LegoStarWarsTCSItem(name, ItemClassification.progression, None, self.player)

    def create_items(self) -> None:
        self.multiworld.itempool.extend(item_pool.create_item_pool(self))

        if self.is_universal_tracker():
            # Universal Tracker deletes the items added to precollected_items by create_items, instead later creating
            # all items with create_item(), but starting characters need to be created before
            # self.starting_character_abilities is set to `starting_abilities` otherwise the starting characters will
            # lose all their abilities. To work around this, Universal Tracker is made to pretend that the starting
            # characters had no abilities, so no abilities will be stripped from any characters created later on with
            # create_item().
            self.starting_character_abilities = CharacterAbility.NONE

    def create_region(self, name: str) -> Region:
        r = Region(name, self.player, self.multiworld)
        self.multiworld.regions.append(r)
        return r

    def create_regions(self) -> None:
        regions.create_regions(self)
        # Check that the number of Gold Brick events created matched what was expected from the calculation in
        # generate_early.
        assert self.gold_brick_event_count == self.expected_gold_brick_event_count, \
            "Created Gold Bricks did not match expected Gold Bricks, something is wrong."

    def add_location(self, name: str, region: Region) -> LegoStarWarsTCSLocation:
        location = LegoStarWarsTCSLocation(self.player, name, self.location_name_to_id[name], region)
        region.locations.append(location)
        return location

    def add_shop_location(self, name: str, region: Region, purchase_cost: int) -> LegoStarWarsTCSLocation:
        location = LegoStarWarsTCSShopLocation(self.player, name, self.location_name_to_id[name], region, purchase_cost)
        region.locations.append(location)
        return location

    def add_event_pair(self, location_name: str, region: Region, item_name: str = "", hide_in_spoiler: bool = True
                       ) -> LegoStarWarsTCSLocation:
        if not item_name:
            item_name = location_name
        location = LegoStarWarsTCSLocation(self.player, location_name, None, region)
        # Showing in the spoiler is only useful if the event is randomized in some way.
        # This does no affect whether events are shown in a spoiler playthrough.
        location.show_in_spoiler = not hide_in_spoiler
        item = self.create_event(item_name)
        location.place_locked_item(item)
        region.locations.append(location)
        return location

    def add_gold_brick_event(self, location_name: str, region: Region) -> LegoStarWarsTCSLocation:
        self.gold_brick_event_count += 1
        return self.add_event_pair(location_name, region, GOLD_BRICK_EVENT_NAME)

    def set_abilities_rule(self, spot: Location | Entrance, abilities: CharacterAbility):
        player = self.player
        abilities_as_int: int = abilities.value
        if abilities_as_int == 0:
            set_rule(spot, Location.access_rule if isinstance(spot, Location) else Entrance.access_rule)
        elif abilities_as_int.bit_count == 1:
            # There is only 1 bit, so a match is all that is needed.
            set_rule(spot, lambda state: state.count("COMBINED_ABILITIES", player) & abilities_as_int)
        else:
            # There are multiple bits, so all bits need to be present.
            set_rule(spot, lambda state: state.count("COMBINED_ABILITIES", player) & abilities_as_int == abilities_as_int)

    def set_any_abilities_rule(self, spot: Location | Entrance, *any_abilities: CharacterAbility):
        for any_ability in any_abilities:
            if not any_ability:
                # No requirements overrides any other ability requirements
                self.set_abilities_rule(spot, any_ability)
                return
        if not any_abilities:
            self.set_abilities_rule(spot, CharacterAbility.NONE)
            return
        any_abilities_set = set(any_abilities)
        if len(any_abilities_set) == 1:
            self.set_abilities_rule(spot, next(iter(any_abilities_set)))
        else:
            sorted_abilities = sorted(any_abilities_set, key=lambda a: (a.bit_count(), a.value))
            abilities_as_ints: list[int] = [any_ability.value for any_ability in sorted_abilities]
            if all(ability_as_int.bit_count() == 1 for ability_as_int in abilities_as_ints):
                # Optimize for all abilities being only a single bit each.
                single_bit_abilities = 0
                for ability_as_int in abilities_as_ints:
                    single_bit_abilities |= ability_as_int
                # Any bit matching is all that is needed.
                set_rule(spot, lambda state, p=self.player: state.count("COMBINED_ABILITIES", p) & single_bit_abilities)
            elif all(ability_as_int.bit_count() > 1 for ability_as_int in abilities_as_ints):
                # Optimize for all abilities being multiple bits each.
                def rule(state: CollectionState):
                    combined_abilities = state.count("COMBINED_ABILITIES", self.player)
                    for ability_as_int in abilities_as_ints:
                        # All the bits in the ability need to be present.
                        if combined_abilities & ability_as_int == ability_as_int:
                            return True
                    return False

                set_rule(spot, rule)
            else:
                # I am unsure if this is faster than pretending all abilities have multiple bits.
                single_bit_abilities = 0
                multi_bit_abilities = []
                for ability_as_int in abilities_as_ints:
                    if ability_as_int.bit_count() == 1:
                        single_bit_abilities |= ability_as_int
                    else:
                        multi_bit_abilities.append(ability_as_int)

                def rule(state: CollectionState):
                    combined_abilities = state.count("COMBINED_ABILITIES", self.player)
                    if combined_abilities & single_bit_abilities:
                        # Any 1 of the bits matching is enough because each ability to check here is only a single bit.
                        return True
                    for ability_as_int in multi_bit_abilities:
                        # All the bits in the ability need to be present.
                        if combined_abilities & ability_as_int == ability_as_int:
                            return True
                    return False

                set_rule(spot, rule)

    def _get_score_multiplier_requirement(self, studs_cost: int):
        max_no_multiplier_cost = self.options.most_expensive_purchase_with_no_multiplier.value * 1000
        count: int
        if studs_cost <= max_no_multiplier_cost:
            count = 0
        elif studs_cost <= max_no_multiplier_cost * 2:
            count = 1  # x2
        elif studs_cost <= max_no_multiplier_cost * 8:
            count = 2  # x2 x4 = x8
        elif studs_cost <= max_no_multiplier_cost * 48:
            count = 3  # x2 x4 x6 = x48
        elif studs_cost <= max_no_multiplier_cost * 384:
            count = 4  # x2 x4 x6 x8 = x384
        elif studs_cost <= max_no_multiplier_cost * 3840:
            count = 5  # x2 x4 x6 x8 x10 = x3840
        else:
            # The minimum value of the option range guarantee that x3840 is enough to purchase everything.
            raise AssertionError(f"Studs cost {studs_cost} is too large. This is an error with the apworld.")

        return count

    def _add_score_multiplier_rule(self, spot: Location, studs_cost: int):
        count = self._get_score_multiplier_requirement(studs_cost)
        if count > 0:
            add_rule(spot, lambda state, p=self.player, c=count: state.has("Progressive Score Multiplier", p, c))

    def set_rules(self) -> None:
        player = self.player

        created_chapters = self.enabled_chapters

        # Episodes.
        for episode_number in range(1, 7):
            if episode_number not in self.enabled_episodes:
                continue
            episode_entrance = self.get_entrance(f"Episode {episode_number} Door")
            if self.options.episode_unlock_requirement == "episode_item":
                item = f"Episode {episode_number} Unlock"
                set_rule(episode_entrance, lambda state, item_=item: state.has(item_, player))
            elif self.options.episode_unlock_requirement == "open":
                pass
            else:
                self.raise_error(AssertionError, "Unreachable: Unexpected episode unlock requirement %s",
                                 self.options.episode_unlock_requirement)

            # Set chapter requirements.
            if self.options.chapter_unlock_requirement == ChapterUnlockRequirement.option_story_characters:
                story_characters_for_chapters = True
            elif self.options.chapter_unlock_requirement == ChapterUnlockRequirement.option_chapter_item:
                story_characters_for_chapters = False
            else:
                raise Exception(f"Unexpected ChapterUnlockRequirement: {self.options.chapter_unlock_requirement}")
            episode_chapters = EPISODE_TO_CHAPTER_AREAS[episode_number]
            for chapter_number, chapter in enumerate(episode_chapters, start=1):
                assert chapter.episode == episode_number
                assert chapter.number_in_episode == chapter_number
                if chapter.short_name not in created_chapters:
                    continue
                entrance = self.get_entrance(f"Episode {episode_number} Room, Chapter {chapter_number} Door")

                is_goal_chapter_without_locations = (
                        chapter.short_name == self.goal_chapter
                        and self.options.goal_chapter_locations_mode == GoalChapterLocationsMode.option_removed
                )

                if story_characters_for_chapters:
                    required_character_names = CHAPTER_AREA_STORY_CHARACTERS[chapter.short_name]
                    entrance_abilities = CharacterAbility.NONE
                    for character_name in required_character_names:
                        generic_character = CHARACTERS_AND_VEHICLES_BY_NAME[character_name]
                        entrance_abilities |= generic_character.abilities

                    if len(required_character_names) == 1:
                        character_name = next(iter(required_character_names))
                        set_rule(entrance, lambda state, item_=character_name: state.has(item_, player))
                    elif len(required_character_names) > 1:
                        character_names = tuple(sorted(required_character_names))
                        set_rule(entrance, lambda state, items_=character_names: state.has_all(items_, player))
                    # Even if some of the abilities are chapter-specific, it doesn't matter, the player needs all of
                    # these characters to access the chapter at all, and will therefore have access to all their
                    # combined abilities, chapter-specific abilities included.
                    strictly_required_entrance_abilities = entrance_abilities
                    assert (set(chapter.completion_main_ability_requirements)
                            <= set(strictly_required_entrance_abilities)), \
                        ("The main abilities were not a subset of the character abilities. The main abilities should be"
                         " calculated from the character abilities, with chapter-specific abilities removed besides the"
                         " chapter-specific abilities of this chapter, so something is wrong.")
                else:
                    # The entrance requires a 'Chapter Unlock' item.
                    # The logic is not fully prepared for this currently, so the entrance rule is also set to require
                    # all the logical abilities of the Story characters of the Chapter, which will be overly
                    # restrictive for many locations, but overly restrictive logic cannot result in impossible seeds.
                    # A few chapters have chapter-specific logical requirements that get stripped from the requirements
                    # of other chapters.
                    main_ability_requirements = chapter.completion_main_ability_requirements
                    alt_ability_requirements = chapter.completion_alt_ability_requirements
                    if alt_ability_requirements:
                        self.set_any_abilities_rule(entrance, main_ability_requirements, alt_ability_requirements)
                        strictly_required_entrance_abilities = main_ability_requirements & alt_ability_requirements
                    else:
                        self.set_abilities_rule(entrance, main_ability_requirements)
                        strictly_required_entrance_abilities = main_ability_requirements

                    add_rule(entrance,
                             lambda state, item_=f"{episode_number}-{chapter_number} Unlock": state.has(item_, player))
                    # TODO: .levels.HAT_MACHINE_CHAPTERS provides alternative logic to Hat Machine logic abilities.
                    #  Levels should be accessible with either the hat machine logic, or the ability logic.

                if is_goal_chapter_without_locations:
                    # There are no locations, so there is no additional logic to add.
                    continue

                def set_chapter_spot_abilities_rule(spot: Location | Entrance, *abilities: CharacterAbility):
                    # Remove any requirements already satisfied by the chapter entrance before setting the rule.
                    self.set_any_abilities_rule(
                        spot, *[ability & ~strictly_required_entrance_abilities for ability in abilities])

                # Set Power Brick logic. Score multiplier requirements are added later.
                power_brick = self.get_location(chapter.power_brick_location_name)
                set_chapter_spot_abilities_rule(power_brick, *chapter.power_brick_ability_requirements)

                # Set Minikits logic
                if self.options.enable_minikit_locations:
                    all_minikits_entrance = self.get_entrance(f"{chapter.name} - Collect All Minikits")
                    set_chapter_spot_abilities_rule(all_minikits_entrance, *chapter.all_minikits_ability_requirements)

                # Set True Jedi logic
                if self.options.enable_true_jedi_locations and not self.options.easier_true_jedi:
                    if chapter.short_name in DIFFICULT_OR_IMPOSSIBLE_TRUE_JEDI:
                        true_jedi = self.get_location(f"{chapter.short_name} True Jedi")
                        set_rule(true_jedi, lambda state: state.has("Progressive Score Multiplier", player))

                # Ridesanity.
                for spot, ability_requirements in self.ridesanity_spots.get(chapter.short_name, ()):
                    set_chapter_spot_abilities_rule(spot, *ability_requirements)

        # Bonus levels.
        gold_brick_requirements: set[int] = set()
        for area in BONUS_AREAS:
            if area.name not in self.enabled_bonuses:
                continue
            # Gold brick requirements are set on entrances, so do not need to be set on the locations themselves.
            gold_brick_requirements.add(area.gold_bricks_required)
            completion = self.get_location(area.completion_location_name)
            if area.completion_ability_requirements:
                self.set_abilities_rule(completion, area.completion_ability_requirements)
            if area.item_requirements:
                add_rule(completion, lambda state, items_=area.item_requirements: state.has_all(items_, player))
            if area.gold_brick:
                gold_brick = self.get_location(f"{area.name} - Gold Brick")
                set_rule(gold_brick, completion.access_rule)
            # Ridesanity.
            for spot, ability_requirements in self.ridesanity_spots.get(area.name, ()):
                self.set_any_abilities_rule(spot, *ability_requirements)
        # Locations with 0 Gold Bricks required are added to the base Bonuses region.
        gold_brick_requirements.discard(0)

        for gold_brick_count in gold_brick_requirements:
            entrance = self.get_entrance(f"Collect {gold_brick_count} Gold Bricks")
            set_rule(
                entrance,
                lambda state, item_=GOLD_BRICK_EVENT_NAME, count_=gold_brick_count: state.has(item_, player, count_))

        # 'All Episodes' character unlocks.
        if self.options.enable_all_episodes_purchases:
            entrance = self.get_entrance("Unlock All Episodes")
            if self.options.all_episodes_character_purchase_requirements == "episodes_unlocked":
                entrance_unlocks = tuple([f"Episode {i} Unlock" for i in range(1, 7) if i in self.enabled_episodes])
                set_rule(entrance, lambda state, items_=entrance_unlocks, p=player: state.has_all(items_, p))
            elif self.options.all_episodes_character_purchase_requirements == "episodes_tokens":
                set_rule(entrance,
                         lambda state, p=player: state.has("Episode Completion Token", p, 6))

        # Cantina Ridesanity.
        for spot, ability_requirements in self.ridesanity_spots.get("cantina", ()):
            self.set_any_abilities_rule(spot, *ability_requirements)

        # Add Score Multiplier requirements to shop purchase locations.
        for loc in self.get_locations():
            if isinstance(loc, LegoStarWarsTCSShopLocation):
                self._add_score_multiplier_rule(loc, loc.studs_cost)

        # Victory.
        victory: Location | Entrance
        if self.goal_chapter:
            # When the goal chapter is enabled, the other goal requirements have to be completed before the goal chapter
            # can be accessed.
            goal_chapter = SHORT_NAME_TO_CHAPTER_AREA[self.goal_chapter]
            victory = self.get_entrance(
                f"Episode {goal_chapter.episode} Room, Chapter {goal_chapter.number_in_episode} Door")
        else:
            victory = self.get_location("Goal")
        # Minikits goal.
        if self.goal_minikit_count > 0:
            add_rule(victory, lambda state: state.has(self.minikit_bundle_name, player, self.goal_minikit_bundle_count))
        # Bosses goal.
        goal_boss_count = self.options.defeat_bosses_goal_amount.value
        if goal_boss_count > 0:
            if self.options.only_unique_bosses_count:
                bosses = {self.short_name_to_boss_character[chapter] for chapter in self.enabled_bosses}
                boss_items = sorted(f"{boss} Defeated" for boss in bosses)
                assert goal_boss_count <= len(boss_items)
                add_rule(
                    victory, (
                        lambda state, i_=tuple(boss_items), p_=player, c_=goal_boss_count:
                        state.has_from_list_unique(i_, p_, c_)
                    )
                )
            else:
                add_rule(victory, lambda state, p_=player, c_=goal_boss_count: state.has("Boss Defeated", p_, c_))
        # Area completion goal.
        goal_area_completions = self.goal_area_completion_count
        if goal_area_completions > 0:
            # "Level" here is as a user-facing term, with the meaning of "Area" internally.
            add_rule(victory, lambda state, p_=player, c_=goal_area_completions: state.has("Level Completion", p_, c_))
        # Kyber Bricks goal.
        if self.options.goal_requires_kyber_bricks:
            add_rule(victory, lambda state, p_=player: state.has("Kyber Brick", p_, 7))

        self.multiworld.completion_condition[self.player] = lambda state: state.has("Victory", player)

    @classmethod
    def stage_fill_hook(cls,
                        multiworld: MultiWorld,
                        progitempool: list[Item],
                        usefulitempool: list[Item],
                        filleritempool: list[Item],
                        fill_locations: list[Location],
                        ) -> None:
        game_players = multiworld.get_game_players(cls.game)
        # Get all player IDs that have progression classification minikits.
        minikit_player_ids = {player for player in game_players if multiworld.worlds[player].goal_minikit_count > 0}
        # Get the player IDs of those that are using minimal accessibility.
        minikit_minimal_player_ids = {player for player in game_players
                                      if multiworld.worlds[player].options.accessibility == "minimal"}

        def sort_func(item: Item):
            if item.player in minikit_player_ids and item.name in MINIKITS_BY_NAME:
                if item.player in minikit_minimal_player_ids:
                    # For minimal players, place goal macguffins first. This helps prevent fill from dumping logically
                    # relevant items into unreachable locations and reducing the number of reachable locations to fewer
                    # than the number of items remaining to be placed.
                    #
                    # Placing only the non-required goal macguffins first or slightly more than the number of
                    # non-required goal macguffins first was also tried, but placing all goal macguffins first seems to
                    # give fill the best chance of succeeding.
                    #
                    # All sizes of minikit bundles, are given the *deprioritized* classification for minimal players,
                    # which avoids them being placed on priority locations, which would otherwise occur due to them
                    # being sorted to be placed first.
                    return 1
                else:
                    # For non-minimal players, place goal macguffins last. The helps prevent fill from filling most/all
                    # reachable locations with the goal macguffins that are only required for the goal.
                    return -1
            else:
                # Python sorting is stable, so this will leave everything else in its original order.
                return 0

        progitempool.sort(key=sort_func)

    def collect(self, state: CollectionState, item: LegoStarWarsTCSItem) -> bool:
        if super().collect(state, item):
            abilities_as_int = item.collect_abilities_int
            if abilities_as_int is not None:
                # The collected item has abilities, so collect them into the state too.
                player_prog = state.prog_items[self.player]
                player_prog["COMBINED_ABILITIES"] |= abilities_as_int
                # state.prog_items is typed as Counter[str], but `abilities_as_int` is an `int`, so this is technically
                # not allowed, but works for now.
                player_prog[abilities_as_int] += 1
            return True
        return False

    def remove(self, state: CollectionState, item: LegoStarWarsTCSItem) -> bool:
        if super().remove(state, item):
            abilities_as_int = item.collect_abilities_int
            if abilities_as_int is not None:
                # The removed item has abilities, so remove them from the state too.
                player_prog = state.prog_items[self.player]
                current_abilities_int_count = player_prog[abilities_as_int]
                if current_abilities_int_count == 1:
                    del player_prog[abilities_as_int]
                    new_combined_abilities = 0
                    key: int | str
                    # This is not fast, but `remove()` is barely ever called by Core AP.
                    # If it is needed to make this faster, then TCS could stop abusing `state.prog_items`, and put its
                    # own `state.tcs_abilities` on the state instead as a `Counter[int, int]`.
                    for key in player_prog:
                        if type(key) is int:
                            new_combined_abilities |= key
                    player_prog["COMBINED_ABILITIES"] = new_combined_abilities
                else:
                    # At least one other collected item is providing the same combination of abilities, so the combined
                    # abilities won't have changed.
                    player_prog[abilities_as_int] = current_abilities_int_count - 1
            return True
        return False

    def fill_slot_data(self) -> Mapping[str, Any]:
        return {
            # todo: A number of the slot data keys here could be inferred from what locations exist in the multiworld.
            "apworld_version": constants.AP_WORLD_VERSION,
            "enabled_chapters": sorted(self.enabled_chapters),
            "enabled_episodes": sorted(self.enabled_episodes),
            "enabled_bonuses": sorted(self.enabled_bonuses),
            "starting_chapter": self.starting_chapter.short_name,
            "starting_episode": self.starting_episode,
            "minikit_goal_amount": self.goal_minikit_count,
            "enabled_bosses": self.enabled_bosses,
            "goal_area_completion_count": self.goal_area_completion_count,
            "goal_chapter": self.goal_chapter,
            "item_colors": self.options.item_colors_to_slot_data(),
            **self.options.as_dict(
                "received_item_messages",
                "checked_location_messages",
                "minikit_bundle_size",
                "episode_unlock_requirement",
                "all_episodes_character_purchase_requirements",
                "most_expensive_purchase_with_no_multiplier",
                "enable_bonus_locations",
                "enable_story_character_unlock_locations",
                "enable_all_episodes_purchases",
                "defeat_bosses_goal_amount",
                "only_unique_bosses_count",
                "defeat_bosses_goal_amount",
                "enable_minikit_locations",
                "enable_true_jedi_locations",
                "death_link",
                "death_link_amnesty",
                "vehicle_death_link_amnesty",
                "easier_true_jedi",
                "uncap_original_trilogy_high_jump",
                "scale_true_jedi_with_score_multipliers",
                "goal_requires_kyber_bricks",
                "goal_chapter_locations_mode",
                "minikit_goal_completion_method",
                "kyber_brick_goal_completion_method",
                "death_link_studs_loss",
                "death_link_studs_loss_scaling",
                "ridesanity",
                "enable_starting_extras_locations",
                "chapter_unlock_requirement",
            )
        }

    @classmethod
    def stage_write_spoiler_header(cls, multiworld: MultiWorld, spoiler_handle: TextIO):
        spoiler_handle.write(f"Generated with {cls.game} Apworld version {constants.AP_WORLD_VERSION}\n")

    def write_spoiler_header(self, spoiler_handle: TextIO) -> None:
        super().write_spoiler_header(spoiler_handle)

        spoiler_handle.write(f"Starting Chapter: {self.starting_chapter.short_name}\n")

        enabled_episodes = sorted(self.enabled_episodes)
        spoiler_handle.write(f"Enabled Episodes: {enabled_episodes}\n")

        enabled_chapters = sorted(self.enabled_chapters)
        spoiler_handle.write(f"Enabled Chapters: {enabled_chapters}\n")

        enabled_bonuses = sorted(self.enabled_bonuses)
        spoiler_handle.write(f"Enabled Bonuses: {enabled_bonuses}\n")

        enabled_bosses = sorted(self.enabled_bosses)
        spoiler_handle.write(f"Enabled Bosses: {enabled_bosses}\n")

    @staticmethod
    def interpret_slot_data(slot_data: dict[str, Any]) -> dict[str, Any] | None:
        slot_data_version = tuple(slot_data["apworld_version"])
        if slot_data_version != constants.AP_WORLD_VERSION:
            raise TCSUniversalTrackerAPWorldVersionMismatchError(
                f"LSW TCS version error: The version of the apworld used to generate this world ({slot_data_version})"
                f" does not match the version of your installed apworld ({constants.AP_WORLD_VERSION})."
            )
        return slot_data
