from collections import defaultdict
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from BaseClasses import Region, LocationProgressType, Location, Entrance
from rule_builder.rules import Rule, Has, True_, CanReachLocation, And, HasAll, HasFromListUnique

from .constants import GOLD_BRICK_EVENT_NAME
from .data.areas import Area, PURCHASABLE_NON_POWER_BRICK_EXTRAS
from .data.characters import UnlockMethod, Character
from .data.items.generic_items import NonDataItemName, EPISODE_UNLOCKS
from .data.logic import CHAPTERS_BY_NUMBERS
from .data.logic.rules import HasAnyAbilities, HasAllAbilities
from .data.logic.types import ExitData, Chapter
from .data.shop import UNLOCK_REQUIREMENT_TO_CHARACTERS
from .items import CHARACTERS_AND_VEHICLES_BY_NAME
from .levels import (
    BonusArea,
    BONUS_AREAS,
    SHORT_NAME_TO_CHAPTER_AREA,
    ChapterArea,
    DIFFICULT_OR_IMPOSSIBLE_TRUE_JEDI,
)
from .options import GoalChapterLocationsMode, ChapterUnlockRequirement, EpisodeUnlockRequirement
from .ridables import (
    BONUS_TO_RIDABLES,
    get_ridable_requirements,
)

if TYPE_CHECKING:
    from . import LegoStarWarsTCSWorld as TCSWorld
else:
    TCSWorld = object


@dataclass
class _RidableData:
    area: Area
    region: Region
    entrance_rule: Rule


@dataclass
class _RegionBuilder:
    """Small helper to store some data while creating regions."""

    world: TCSWorld
    """The world to create regions for."""

    available_minikits_check: int = 0
    """Double check that the minikit counts is as expected."""

    cantina: Region = field(init=False)
    """The origin region of the world, the Cantina."""

    story_character_unlock_regions: dict[Character, list[Region]] = field(default_factory=dict)
    """A dict mapping story characters by the regions that would unlock that character in vanilla."""

    ridable_character_regions: dict[Character, list[_RidableData]] = field(default_factory=dict)
    """A dict mapping ridable character names by the regions that feature that character."""

    goal_requires_area_completion: bool = field(init=False)
    """Whether the goal requires completing areas."""

    def __post_init__(self) -> None:
        # Create the origin region.
        self.cantina = self.world.create_region(self.world.origin_region_name)

        self.goal_requires_area_completion = self.world.goal_area_completion_count > 0

    def _get_score_multiplier_rule(self, studs_cost: int) -> Rule:
        count = self.world.get_score_multiplier_requirement(studs_cost)
        if count == 0:
            return True_()
        rule = Has(NonDataItemName.PROGRESSIVE_SCORE_MULTIPLIER.value, count)
        if self.world.is_universal_tracker():
            # All purchases can be made with enough grinding for studs, it just might take a long time.
            return rule | Has(self.world.glitches_item_name)
        else:
            return rule

    def _add_score_multiplier_rule(self, base_rule: Rule, studs_cost: int) -> Rule:
        to_add = self._get_score_multiplier_rule(studs_cost)
        if isinstance(to_add, True_):
            return base_rule
        return to_add & base_rule

    @staticmethod
    def _get_legacy_true_jedi_rule(legacy_chapter: ChapterArea):
        """True Jedi logic has not been defined yet, so the legacy rule is used."""
        # The logic is not fully prepared for this currently, so the entrance rule is also set to require
        # all the logical abilities of the Story characters of the Chapter, which will be overly
        # restrictive for many locations, but overly restrictive logic cannot result in impossible seeds.
        # A few chapters have chapter-specific logical requirements that get stripped from the requirements
        # of other chapters.
        main_ability_requirements = legacy_chapter.completion_main_ability_requirements
        alt_ability_requirements = legacy_chapter.completion_alt_ability_requirements

        if alt_ability_requirements:
            abilities_rule = HasAnyAbilities(main_ability_requirements) | HasAnyAbilities(alt_ability_requirements)
        else:
            abilities_rule =  HasAnyAbilities(main_ability_requirements)

        if legacy_chapter.short_name in DIFFICULT_OR_IMPOSSIBLE_TRUE_JEDI:
            return abilities_rule & Has(NonDataItemName.PROGRESSIVE_SCORE_MULTIPLIER.value)
        else:
            return abilities_rule

    @staticmethod
    def _make_all_minikits_rule(minikit_locations: list[Location]) -> Rule:
        # The last minikit location is generally the furthest into the level, so construct the rule such that it checks
        # the locations in reverse.
        return And(*(CanReachLocation(loc.name) for loc in reversed(minikit_locations)))

    @staticmethod
    def _exclude_location(location: Location) -> None:
        location.progress_type = LocationProgressType.EXCLUDED

    def make_victory_rule(self) -> Rule:
        world = self.world
        rule = True_()

        # Minikits goal.
        if world.goal_minikit_count > 0:
            rule &= Has(world.minikit_bundle_name, count=world.goal_minikit_bundle_count)

        # Bosses goal
        goal_boss_count = world.options.defeat_bosses_goal_amount.value
        if goal_boss_count > 0:
            if world.options.only_unique_bosses_count:
                bosses = {world.short_name_to_boss_character[chapter] for chapter in world.enabled_bosses}
                boss_items = sorted(f"{boss} Defeated" for boss in bosses)
                assert goal_boss_count <= len(boss_items)
                rule &= HasFromListUnique(*boss_items, count=goal_boss_count)
            else:
                rule &= Has("Boss Defeated", count=goal_boss_count)

        # Area completion goal.
        goal_area_completions = world.goal_area_completion_count
        if goal_area_completions > 0:
            # "Level" here is as a user-facing term, with the meaning of "Area" internally.
            rule &= Has("Level Completion", count=goal_area_completions)

        # Kyber Bricks Goal
        if world.options.goal_requires_kyber_bricks:
            rule &= Has("Kyber Brick", count=7)

        return rule

    def _create_chapter_entrance_rule(self, chapter: Chapter) -> tuple[Rule, set[str], int]:
        world = self.world
        short_name = chapter.short_name
        rule = chapter.extra_chapter_entrance_rules
        if world.options.chapter_unlock_requirement.is_characters():
            character_count = world.chapter_required_character_counts[short_name]
            if world.options.chapter_unlock_requirement == ChapterUnlockRequirement.option_vanilla_characters:
                if short_name in world.chapters_requiring_alt_characters:
                    characters = {c.readable_name for c in chapter.purchase_characters}
                else:
                    characters = {c.readable_name for c in chapter.story_characters}
                    # Remove characters excluded from being included in requirements.
                    characters.difference_update(world.options.chapter_unlock_story_characters_not_required.value)
            elif world.options.chapter_unlock_requirement == ChapterUnlockRequirement.option_random_characters:
                characters = set(world.chapter_random_character_requirements[short_name])
            else:
                world.raise_error(AssertionError,
                                  "Unexpected chapter unlock requirement %s",
                                  world.options.chapter_unlock_requirement)

            if len(characters) < 1:
                world.raise_error(AssertionError,
                                  "At least one character should always be required, but %s is requiring %i",
                                  short_name, character_count)
            if len(characters) < character_count:
                world.raise_error(AssertionError,
                                  "The number of required characters should always be less than or equal to the"
                                  " available count, but %s is requiring %i characters and only has a max of %i"
                                  " available",
                                  short_name, character_count, len(characters))

            if len(characters) == character_count:
                # HasFromListUnique does not perform this optimisation automatically.
                rule &= HasAll(*characters)
            else:
                rule &= HasFromListUnique(*characters, count=character_count)
        else:
            rule &= Has(f"{short_name} Unlock")
            characters = set()
            character_count = 0

        if world.options.episode_unlock_requirement == EpisodeUnlockRequirement.option_episode_item:
            rule &= Has(f"Episode {chapter.episode_number} Unlock")

        return rule, characters,character_count

    def _create_chapter(self, chapter: Chapter) -> Region:
        legacy_chapter = SHORT_NAME_TO_CHAPTER_AREA[chapter.short_name]
        area = chapter.area
        world = self.world

        # Regions (and finding Entrances).
        start_region_internal_name = chapter.start_region
        start_region_exits = chapter.regions[start_region_internal_name]
        region_data_stack: list[tuple[str, tuple[ExitData, ...]]] = [(start_region_internal_name, start_region_exits)]
        create_region = self.world.create_region
        prefix_name = area.prefix_name
        regions = {}
        resolved_rule: Rule.Resolved
        entrances_to_create: list[tuple[Region, str, str | None, Rule | Rule.Resolved]] = []
        while region_data_stack:
            internal_region_name, exits = region_data_stack.pop()
            if internal_region_name not in regions:
                r = create_region(prefix_name(internal_region_name))
                regions[internal_region_name] = r
            else:
                # Already processed.
                continue
            for exit_ in exits:
                try:
                    resolved_rule = exit_.rule.resolve(self.world)
                    if resolved_rule.always_false:
                        continue
                    entrances_to_create.append((r, exit_.to_region, exit_.name, resolved_rule))
                except KeyError:
                    # CanReachRegion rules cannot be resolved yet if the region they reference does not exist.
                    entrances_to_create.append((r, exit_.to_region, exit_.name, exit_.rule))
                region_data_stack.append((exit_.to_region, chapter.regions[exit_.to_region]))
        start_region = regions[start_region_internal_name]

        # Entrances.
        for r, to_region_name, entrance_name, rule in entrances_to_create:
            to_r = regions[to_region_name]
            r.connect(to_r, entrance_name, rule)

        completion_region = regions["Chapter Completion"]
        create_gold_bricks = bool(self.world.options.enable_bonus_locations)

        # Goal event.
        exclude_locations = False
        is_goal_chapter = chapter.short_name == world.goal_chapter
        if is_goal_chapter:
            world.add_event_pair(f"Complete Goal Chapter {world.goal_chapter}", completion_region, "Victory")

            goal_chapter_locations_mode = world.options.goal_chapter_locations_mode.value
            if goal_chapter_locations_mode == GoalChapterLocationsMode.option_removed:
                # The only location that will be placed in the chapter's Region is the Victory event used by the
                # completion_condition.
                return start_region
            if goal_chapter_locations_mode == GoalChapterLocationsMode.option_excluded:
                # When the locations are excluded, Gold Bricks from the Goal Chapter are removed from logic.
                create_gold_bricks = False
                exclude_locations = True

        # Completion Location + Events.
        completion_name = area.get_completion_name()
        completion_location = self.world.add_location(completion_name, completion_region)
        if exclude_locations:
            self._exclude_location(completion_location)
        if create_gold_bricks:
            # Completion Gold Brick event.
            world.add_gold_brick_event(f"{completion_name} - Gold Brick", completion_region)
        # Area completion.
        # The goal chapter does not contribute to Area Completion because the Goal Chapter requires completing
        # all other goals before it will unlock.
        if self.goal_requires_area_completion and not is_goal_chapter:
            # "Level" here is as a user-facing term, with the meaning of "Area" internally.
            world.add_event_pair(area.get_completion_name() + " (Event)", completion_region, "Level Completion")

        # True Jedi (legacy logic).
        if world.options.enable_true_jedi_locations:
            true_jedi_name = area.get_true_jedi_name()
            # With full True Jedi logic, the True Jedi location would likely end up in the start region because of score
            # multipliers when True Jedi is not set to scale with score multipliers.
            true_jedi_location = world.add_location(true_jedi_name, completion_region)
            legacy_rule = self._get_legacy_true_jedi_rule(legacy_chapter)
            world.set_rule(true_jedi_location, legacy_rule)
            if exclude_locations:
                self._exclude_location(true_jedi_location)
            if create_gold_bricks:
                # True Jedi Gold Brick event.
                true_jedi_event = world.add_gold_brick_event(f"{true_jedi_name} - Gold Brick", completion_region)
                world.set_rule(true_jedi_event, legacy_rule)

        # Power Brick Location.
        extra = chapter.area.extra
        assert extra is not None
        power_brick_location_name = extra.get_purchase_location_name()
        power_brick_region = regions[chapter.power_brick.region]
        studs_cost = extra.purchase_cost
        assert studs_cost is not None
        power_brick_loc = world.add_shop_location(power_brick_location_name, power_brick_region, studs_cost)
        world.set_rule(power_brick_loc, self._add_score_multiplier_rule(chapter.power_brick.rule, studs_cost))
        if exclude_locations:
            self._exclude_location(power_brick_loc)

        # Character Purchases in the shop.
        # Character purchases unlocked upon completing the chapter (normally in Story mode).
        for character in chapter.purchase_characters:
            location_name = character.get_purchase_location_name()
            studs_cost = character.purchase_cost
            assert studs_cost is not None
            purchase_location = world.add_shop_location(location_name, completion_region, studs_cost)
            world.set_rule(purchase_location, self._get_score_multiplier_rule(studs_cost))
            if exclude_locations:
                self._exclude_location(purchase_location)
        world.character_unlock_location_count += len(chapter.purchase_characters)

        # Minikits.
        minikits_from_chapter = 0
        if world.options.enable_minikit_locations:
            minikit_locations: list[Location] = []
            for minikit_name, location_data in chapter.minikits.items():
                r = regions[location_data.region]
                loc = self.world.add_location(prefix_name(minikit_name), r)
                self.world.set_rule(loc, location_data.rule)
                minikit_locations.append(loc)
                minikits_from_chapter += 1
            if exclude_locations:
                for loc in minikit_locations:
                    self._exclude_location(loc)
            if create_gold_bricks:
                # Minikits are generally in order of appearance within a level, so put the event in the same region as
                # the last minikit.
                # todo: Technically, higher logic would potentially be able to get this early in some levels that have
                #  minikit duplication glitches.
                event_region = minikit_locations[-1].parent_region
                assert event_region is not None
                all_minikits_loc = world.add_gold_brick_event(area.prefix_name("Collect All Minikits"), event_region)
                world.set_rule(all_minikits_loc, self._make_all_minikits_rule(minikit_locations))
        elif world.options.minikit_goal_amount != 0:
            # If Minikit locations are disabled, but the goal requires Minikits, the Chapter Completion location
            # is instead treated as if it was the vanilla location for a 10 Minikits bundle.
            minikits_from_chapter += 10

        # The goal chapter does not contribute Minikits because it is only accessible once the Minikits goal is
        # complete.
        if not is_goal_chapter:
            self.available_minikits_check += minikits_from_chapter

        # Story Character unlocks.
        if world.options.enable_story_character_unlock_locations:
            for character in chapter.story_characters:
                self.story_character_unlock_regions.setdefault(character, []).append(completion_region)

        # Checks for riding unique characters.
        if world.options.ridesanity:
            for ridable_character, ridable_location_data in chapter.ridables.items():
                ridable_region = regions[ridable_location_data.region]
                ridable_data = _RidableData(area, ridable_region, ridable_location_data.rule)
                self.ridable_character_regions.setdefault(ridable_character, []).append(ridable_data)

        # Boss.
        if chapter.short_name in world.enabled_bosses:
            assert chapter.short_name != world.goal_chapter, ("The Goal Chapter should never be selected as an "
                                                              "enabled boss")
            if world.options.only_unique_bosses_count:
                boss_event_item_name = f"{world.short_name_to_boss_character[chapter.short_name]} Defeated"
            else:
                boss_event_item_name = "Boss Defeated"
            world.add_event_pair(
                f"{chapter.short_name} Defeat {legacy_chapter.boss}", completion_region, boss_event_item_name)

        return regions[start_region_internal_name]

    def _create_episode(self, episode_number: int) -> None:
        world = self.world
        episode_room = world.create_region(f"Episode {episode_number} Room")
        self.cantina.connect(episode_room, f"Episode {episode_number} Door")
        for chapter_number, chapter in CHAPTERS_BY_NUMBERS[episode_number].items():
            if chapter.short_name not in world.enabled_chapters:
                continue
            chapter_start_region = self._create_chapter(chapter)

            t = self._create_chapter_entrance_rule(chapter)
            chapter_entrance_rule, characters_locking_access, character_count = t
            # Add Goal Chapter rules if this is the Goal Chapter.
            if world.goal_chapter and world.goal_chapter == chapter.short_name:
                chapter_entrance_rule &= self.make_victory_rule()

            # Create the entrance.
            main_entrance_name = f"Episode {episode_number} Room, Chapter {chapter_number} Door"
            episode_room.connect(chapter_start_region, main_entrance_name, chapter_entrance_rule)

            # Update the counts of chapters locked by each character.
            sorted_character_names = sorted(characters_locking_access)
            world.character_chapter_access_counts.update(sorted_character_names)
            # Prepare the requirements for writing to the spoiler.
            world.spoiler_chapter_character_requirements[chapter.short_name] = (character_count, sorted_character_names)

    def create_episodes(self) -> None:
        for episode_number in range(1, 7):
            if episode_number not in self.world.enabled_episodes:
                continue
            self._create_episode(episode_number)

    def create_story_character_unlock_locations(self) -> None:
        world = self.world

        excluded_goal_region: Region | None
        if (world.goal_chapter
                and world.options.goal_chapter_locations_mode.value == GoalChapterLocationsMode.option_excluded):
            excluded_goal_region = world.get_region(SHORT_NAME_TO_CHAPTER_AREA[world.goal_chapter].name)
        else:
            excluded_goal_region = None

        for character, parent_regions in self.story_character_unlock_regions.items():
            loc_name = character.get_level_completion_unlock_location_name()
            if len(parent_regions) == 1:
                parent_region = parent_regions[0]
                # The location is only accessed from 1 region, so put the location in that region. This slightly
                # improves logic performance.
                character_location = world.add_location(loc_name, parent_region)
                if parent_region == excluded_goal_region:
                    # The location is only accessed through the Goal Chapter which has its locations excluded, so this
                    # chapter completion character unlock location should also be excluded.
                    character_location.progress_type = LocationProgressType.EXCLUDED
                    world.goal_excluded_character_unlock_location_count += 1
            else:
                # The location is accessed from multiple regions, so put the location in its own region that those
                # regions can be connected to.
                character_region = world.create_region(character.get_level_completion_unlock_location_name())
                character_location = world.add_location(loc_name, character_region)
                for parent_region in parent_regions:
                    parent_region.connect(character_region)
                # There are multiple ways this location could be reached, so enable path display in the Spoiler (when
                # Playthrough Paths are enabled in the generator's host.yaml), so that the route the Playthrough used to
                # reach the location is clear.
                world.topology_present = True
            if excluded_goal_region is not None and excluded_goal_region in parent_regions:
                # If the location can be accessed through the Goal Chapter that has excluded locations, exclude the
                # location, even if it could be accessed from elsewhere. This prevents the possibility of the Goal
                # Chapter from locking access to locations.
                character_location.progress_type = LocationProgressType.EXCLUDED
                world.goal_excluded_character_unlock_location_count += 1

        world.character_unlock_location_count += len(self.story_character_unlock_regions)

    def create_bonus_locations(self) -> None:
        world = self.world
        # Bonuses.
        bonuses = world.create_region("Bonuses")
        self.cantina.connect(bonuses, "Bonuses Door")

        # Group Bonuses by gold brick costs so that the regions requiring progressively more Gold Bricks can be
        # chained together more easily.
        gold_brick_costs: dict[int, list[BonusArea]] = {}
        for legacy_area in BONUS_AREAS:
            if legacy_area.name not in world.enabled_bonuses:
                continue
            gold_bricks_required = legacy_area.gold_bricks_required
            if gold_bricks_required == 0:
                # No Gold Bricks are required to watch the Indy Trailer, so put it in the Bonuses region directly.
                assert legacy_area.name == "Indiana Jones: Trailer"
                world.add_location(Area(legacy_area.area_id).get_completion_name(), bonuses)
            else:
                gold_brick_costs.setdefault(gold_bricks_required, []).append(legacy_area)

        previous_gold_brick_region = bonuses
        for gold_brick_cost, areas in sorted(gold_brick_costs.items(), key=lambda t: t[0]):
            region = world.create_region(f"{gold_brick_cost} Gold Bricks Collected")
            previous_gold_brick_region.connect(
                region, f"Collect {gold_brick_cost} Gold Bricks",
                Has(GOLD_BRICK_EVENT_NAME, gold_brick_cost),
            )
            previous_gold_brick_region = region

            for legacy_area in areas:
                area_region = world.create_region(legacy_area.name)
                region.connect(area_region)
                area = Area(legacy_area.area_id)

                # Completion location.
                completion_rule = (
                        HasAllAbilities(legacy_area.completion_ability_requirements)
                        & HasAll(*legacy_area.item_requirements)
                )
                completion_location = world.add_location(area.get_completion_name(), area_region)
                world.set_rule(completion_location, completion_rule)

                if world.options.enable_story_character_unlock_locations:
                    for character in sorted(legacy_area.story_characters):
                        self.story_character_unlock_regions.setdefault(character, []).append(area_region)
                # todo: Item requirements have been removed for now because it is not currently possible to lock
                #  access to the bonus levels.
                if self.world.options.chapter_unlock_requirement == ChapterUnlockRequirement.option_vanilla_characters:
                    for item in legacy_area.item_requirements:
                        if item in CHARACTERS_AND_VEHICLES_BY_NAME:
                            world.character_chapter_access_counts[item] += 1
                assert legacy_area.gold_brick, "Every bonus that requires Gold Bricks to access should award a Gold Brick"

                gold_brick = world.add_gold_brick_event(f"{legacy_area.name} - Gold Brick", area_region)
                world.set_rule(gold_brick, completion_rule)

                if self.goal_requires_area_completion:
                    # "Level" here is as a user-facing term, with the meaning of "Area" internally.
                    world.add_event_pair(f"{legacy_area.name} Completion (Event)", area_region, "Level Completion")

                if world.options.ridesanity:
                    # Checks for riding unique characters
                    for ridable in BONUS_TO_RIDABLES.get(area, ()):
                        rule = get_ridable_requirements(Area(legacy_area.area_id), ridable.character)
                        ridable_data = _RidableData(area, area_region, rule)
                        self.ridable_character_regions.setdefault(ridable.character, []).append(ridable_data)

        # Indiana Jones shop purchase. Unlocks in the shop after watching the Lego Indiana Jones trailer.
        indiana_jones_purchase = world.add_location(Character.INDIANA_JONES.get_purchase_location_name(), bonuses)
        purchase_cost = Character.INDIANA_JONES.purchase_cost
        assert purchase_cost is not None
        world.set_rule(indiana_jones_purchase, self._get_score_multiplier_rule(purchase_cost))
        world.character_unlock_location_count += 1

    def create_ridesanity_locations(self) -> None:
        world = self.world

        excluded_goal_region: Region | None
        if (world.goal_chapter
                and world.options.goal_chapter_locations_mode.value == GoalChapterLocationsMode.option_excluded):
            excluded_goal_region = world.get_region(SHORT_NAME_TO_CHAPTER_AREA[world.goal_chapter].name)
        else:
            excluded_goal_region = None

        # Add the Cantina Car ridable found in the Cantina itself, it cannot be found anywhere else.
        cantina_car = Character.MAPCAR
        # Add it to the dict of regions.
        cantina_car_data = _RidableData(Area.MAP, self.cantina, get_ridable_requirements(Area.MAP, cantina_car))
        self.ridable_character_regions[cantina_car] = [cantina_car_data]

        ridesanity_spots: defaultdict[str, list[tuple[Location | Entrance, Rule]]]
        ridesanity_spots = defaultdict(list)
        for ridable, areas_list in self.ridable_character_regions.items():
            world.ridesanity_location_count += 1
            ridable_location_name = ridable.get_ridesanity_location_name()
            is_excluded_goal_chapter_location = False
            if len(areas_list) == 0:
                # There is only one region where this ridable can be found, so the ridable location can go directly in
                # that region.
                area_short_name, area_region = areas_list[0]
                ridable_location = world.add_location(ridable_location_name, area_region)
                # If there are any rules, they will be set on the location.
                requirements = get_ridable_requirements(area_short_name, ridable)
                ridesanity_spots[area_short_name].append((ridable_location, requirements))
                is_excluded_goal_chapter_location = area_region == excluded_goal_region
            else:
                # There are multiple regions this ridable can be found in, so create a new region just for this location
                # and
                ridable_region = world.create_region(ridable_location_name)
                for area_short_name, area_region in areas_list:
                    entrance = area_region.connect(ridable_region)
                    # If there are any rules, they will be set on the entrance.
                    requirements = get_ridable_requirements(area_short_name, ridable)
                    ridesanity_spots[area_short_name].append((entrance, requirements))
                    if area_region == excluded_goal_region:
                        is_excluded_goal_chapter_location = True
                ridable_location = world.add_location(ridable_location_name, ridable_region)
            if is_excluded_goal_chapter_location:
                # If the location can be accessed through the Goal Chapter that has excluded locations, exclude the
                # location, even if it could be accessed from elsewhere. This prevents the possibility of the Goal
                # Chapter from locking access to locations.
                ridable_location.progress_type = LocationProgressType.EXCLUDED
        world.ridesanity_spots.update(ridesanity_spots)

    def create_all_episodes_character_purchases(self) -> None:
        world = self.world
        all_episodes = world.create_region("All Episodes Unlocked")

        if world.options.all_episodes_character_purchase_requirements == "episodes_unlocked":
            entrance_rule = HasAll(*(EPISODE_UNLOCKS[i] for i in range(1, 7) if i in self.world.enabled_episodes))
            self.cantina.connect(all_episodes, "Unlock All Episodes Containing Enabled Chapters", entrance_rule)
        elif world.options.all_episodes_character_purchase_requirements == "episodes_tokens":
            entrance_rule = Has(NonDataItemName.EPISODE_COMPLETION_TOKEN, count=6)
            self.cantina.connect(all_episodes, "Collect 6 Episode Completion Tokens", entrance_rule)

        all_episodes_purchases = UNLOCK_REQUIREMENT_TO_CHARACTERS[UnlockMethod.ALL_EPISODES_COMPLETE]
        for character in all_episodes_purchases:
            purchase_cost = character.purchase_cost
            assert purchase_cost is not None
            loc = world.add_shop_location(character.get_purchase_location_name(), all_episodes, character.purchase_cost)
            world.set_rule(loc, self._get_score_multiplier_rule(purchase_cost))
        world.character_unlock_location_count += len(all_episodes_purchases)

    def create_starting_purchases(self) -> None:
        world = self.world
        starting_purchases = (Character.GONK_DROID, Character.PK_DROID)
        for character in starting_purchases:
            purchase_cost = character.purchase_cost
            assert purchase_cost is not None
            loc = world.add_shop_location(character.get_purchase_location_name(), self.cantina, character.purchase_cost)
            world.set_rule(loc, self._get_score_multiplier_rule(purchase_cost))
        world.character_unlock_location_count += len(starting_purchases)

        for extra in sorted(PURCHASABLE_NON_POWER_BRICK_EXTRAS):
            purchase_cost = extra.purchase_cost
            assert purchase_cost is not None
            loc = world.add_shop_location(extra.get_purchase_location_name(), self.cantina, purchase_cost)
            world.set_rule(loc, self._get_score_multiplier_rule(purchase_cost))
            if not world.options.enable_starting_extras_locations:
                loc.place_locked_item(world.create_item(extra.readable_name))

    def create_non_goal_chapter_victory(self) -> None:
        """Create the Victory event for the goal when the goal does not require completing a Goal Chapter."""
        victory = self.world.add_event_pair("Goal", self.cantina, "Victory")
        self.world.set_rule(victory, self.make_victory_rule())



def create_regions(world: TCSWorld) -> None:
    builder = _RegionBuilder(world)

    builder.create_episodes()

    # Available minikit count is calculated in generate_early.
    if world.available_minikits != builder.available_minikits_check:
        world.raise_error(AssertionError,
                          "Available minikits in create_regions did not match. %i from generate_early and %i"
                          " from create_regions. Please report this as a bug in the apworld.",
                          world.available_minikits,
                          builder.available_minikits_check)

    if world.options.enable_bonus_locations:
        builder.create_bonus_locations()

    if world.options.enable_story_character_unlock_locations:
        if builder.story_character_unlock_regions:
            builder.create_story_character_unlock_locations()
        else:
            # Every Chapter has at least 1 Story Character, so if none exist in a generation, the locations should be
            # disabled.
            assert not builder.world.options.enable_story_character_unlock_locations

    if world.options.ridesanity:
        builder.create_ridesanity_locations()

    # 'All Episodes' character purchases.
    if world.options.enable_all_episodes_purchases:
        builder.create_all_episodes_character_purchases()

    builder.create_starting_purchases()

    # General Victory event.
    if not world.goal_chapter:
        builder.create_non_goal_chapter_victory()

    # For debugging.
    # from Utils import visualize_regions
    # visualize_regions(cantina, "LegoStarWarsTheCompleteSaga_Regions.puml", show_entrance_names=True)
