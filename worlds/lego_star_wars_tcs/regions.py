from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from BaseClasses import Region, LocationProgressType, Location

from .constants import GOLD_BRICK_EVENT_NAME
from .items import CHARACTERS_AND_VEHICLES_BY_NAME, SHOP_SLOT_REQUIREMENT_TO_UNLOCKS
from .levels import (
    EPISODE_TO_CHAPTER_AREAS,
    CHAPTER_AREA_STORY_CHARACTERS,
    DIFFICULT_OR_IMPOSSIBLE_TRUE_JEDI,
    BonusArea,
    BONUS_AREAS,
    SHORT_NAME_TO_CHAPTER_AREA,
)
from .locations import LegoStarWarsTCSLocation
from .options import GoalChapterLocationsMode

if TYPE_CHECKING:
    from . import LegoStarWarsTCSWorld as TCSWorld
else:
    TCSWorld = object


@dataclass
class _RegionBuilder:
    """Small helper to store some data while creating regions."""

    world: TCSWorld
    """The world to create regions for."""

    available_minikits_check: int = 0
    """Double check that the minikit counts is as expected."""

    gold_brick_event_count: int = 0
    """The number of Gold Brick events created. Compared against the expected number calculated in generate_early."""

    cantina: Region = field(init=False)
    """The origin region of the world, the Cantina."""

    story_character_unlock_regions: dict[str, list[Region]] = field(default_factory=dict)
    """A dict mapping story character names by the regions that would unlock that character in vanilla."""

    goal_requires_area_completion: bool = field(init=False)
    """Whether the goal requires completing areas."""

    def __post_init__(self) -> None:
        # Create the origin region.
        self.cantina = self.world.create_region(self.world.origin_region_name)

        self.goal_requires_area_completion = self.world.goal_area_completion_count > 0

    def _create_episode(self, episode_number: int) -> None:
        world = self.world
        episode_room = world.create_region(f"Episode {episode_number} Room")
        self.cantina.connect(episode_room, f"Episode {episode_number} Door")

        episode_chapters = EPISODE_TO_CHAPTER_AREAS[episode_number]
        for chapter_number, chapter in enumerate(episode_chapters, start=1):
            assert chapter.episode == episode_number
            assert chapter.number_in_episode == chapter_number
            if chapter.short_name not in world.enabled_chapters:
                continue
            # Update the count of how many chapters this character blocks access to.
            world.character_chapter_access_counts.update(chapter.character_requirements)
            chapter_region = world.create_region(chapter.name)

            entrance_name = f"Episode {episode_number} Room, Chapter {chapter_number} Door"
            episode_room.connect(chapter_region, entrance_name)

            create_gold_bricks = bool(world.options.enable_bonus_locations)
            exclude_locations = False
            is_goal_chapter = chapter.short_name == world.goal_chapter
            if is_goal_chapter:
                victory = LegoStarWarsTCSLocation(
                    world.player, f"Complete Goal Chapter {world.goal_chapter}", parent=chapter_region)
                victory.place_locked_item(world.create_event("Victory"))
                chapter_region.locations.append(victory)

                goal_chapter_locations_mode = world.options.goal_chapter_locations_mode.value
                if goal_chapter_locations_mode == GoalChapterLocationsMode.option_removed:
                    # The only location that will be placed in the chapter's Region is the Victory event used by the
                    # completion_condition.
                    continue
                if goal_chapter_locations_mode == GoalChapterLocationsMode.option_excluded:
                    # When the locations are excluded, Gold Bricks from the Goal Chapter are removed from logic.
                    create_gold_bricks = False
                    exclude_locations = True

            # Completion.
            completion_name = f"{chapter.short_name} Completion"
            completion_loc = LegoStarWarsTCSLocation(world.player, completion_name,
                                                     world.location_name_to_id[completion_name], chapter_region)
            chapter_region.locations.append(completion_loc)
            if create_gold_bricks:
                # Completion Gold Brick event.
                completion_gold_brick = LegoStarWarsTCSLocation(world.player, f"{completion_name} - Gold Brick",
                                                                None, chapter_region)
                completion_gold_brick.place_locked_item(world.create_event(GOLD_BRICK_EVENT_NAME))
                self.gold_brick_event_count += 1
                chapter_region.locations.append(completion_gold_brick)

            # True Jedi.
            if world.options.enable_true_jedi_locations:
                true_jedi_name = f"{chapter.short_name} True Jedi"
                true_jedi_loc = LegoStarWarsTCSLocation(world.player, true_jedi_name,
                                                        world.location_name_to_id[true_jedi_name], chapter_region)
                chapter_region.locations.append(true_jedi_loc)
                if create_gold_bricks:
                    # True Jedi Gold Brick event.
                    true_jedi_gold_brick = LegoStarWarsTCSLocation(world.player, f"{true_jedi_name} - Gold Brick",
                                                                   None, chapter_region)
                    true_jedi_gold_brick.place_locked_item(world.create_event(GOLD_BRICK_EVENT_NAME))
                    self.gold_brick_event_count += 1
                    chapter_region.locations.append(true_jedi_gold_brick)

            # Power Brick.
            power_brick_location_name = chapter.power_brick_location_name
            power_brick_location = LegoStarWarsTCSLocation(world.player, power_brick_location_name,
                                                           world.location_name_to_id[power_brick_location_name],
                                                           chapter_region)
            chapter_region.locations.append(power_brick_location)
            world.required_score_multiplier_count = max(
                world.required_score_multiplier_count,
                world._get_score_multiplier_requirement(chapter.power_brick_studs_cost))

            # Character Purchases in the shop.
            # Character purchases unlocked upon completing the chapter (normally in Story mode).
            for shop_unlock, studs_cost in chapter.character_shop_unlocks.items():
                shop_location = LegoStarWarsTCSLocation(world.player, shop_unlock,
                                                        world.location_name_to_id[shop_unlock], chapter_region)
                chapter_region.locations.append(shop_location)
                world.required_score_multiplier_count = max(
                    world.required_score_multiplier_count,
                    world._get_score_multiplier_requirement(studs_cost))
            world.character_unlock_location_count += len(chapter.character_shop_unlocks)

            # Minikits.
            minikits_from_chapter = 0
            if world.options.enable_minikit_locations:
                chapter_minikits = world.create_region(f"{chapter.name} Minikits")
                chapter_region.connect(chapter_minikits, f"{chapter.name} - Collect All Minikits")
                for i in range(1, 11):
                    loc_name = f"{chapter.short_name} Minikit {i}"
                    location = LegoStarWarsTCSLocation(world.player, loc_name, world.location_name_to_id[loc_name],
                                                       chapter_minikits)
                    chapter_minikits.locations.append(location)
                    minikits_from_chapter += 1
                if exclude_locations:
                    # Exclude the minikit locations.
                    for loc in chapter_minikits.locations:
                        assert not loc.is_event  # At this point, only non-event locations should be created.
                        loc.progress_type = LocationProgressType.EXCLUDED
                if create_gold_bricks:
                    # All Minikits Gold Brick.
                    all_minikits_gold_brick = LegoStarWarsTCSLocation(
                        world.player, f"{chapter_minikits.name} - Gold Brick", None, chapter_minikits)
                    all_minikits_gold_brick.place_locked_item(world.create_event(GOLD_BRICK_EVENT_NAME))
                    self.gold_brick_event_count += 1
                    chapter_minikits.locations.append(all_minikits_gold_brick)
            elif world.options.minikit_goal_amount != 0:
                # If Minikit locations are disabled, but the goal requires Minikits, the Chapter Completion location
                # is instead treated as if it was the vanilla location for a 10 Minikits bundle.
                minikits_from_chapter += 10

            # The goal chapter does not contribute Minikits because it is only accessible once the Minikits goal is
            # complete.
            if not is_goal_chapter:
                self.available_minikits_check += minikits_from_chapter

            if world.options.enable_story_character_unlock_locations:
                # Story Character unlocks.
                for character in sorted(CHAPTER_AREA_STORY_CHARACTERS[chapter.short_name]):
                    self.story_character_unlock_regions.setdefault(character, []).append(chapter_region)

            # Boss.
            if chapter.short_name in world.enabled_bosses:
                assert chapter.short_name != world.goal_chapter, ("The Goal Chapter should never be selected as an "
                                                                  "enabled boss")
                loc_name = f"{chapter.short_name} Defeat {chapter.boss}"
                boss_event_location = LegoStarWarsTCSLocation(world.player, loc_name, None, chapter_region)
                if world.options.only_unique_bosses_count:
                    boss_event_item = world.create_event(
                        f"{world.short_name_to_boss_character[chapter.short_name]} Defeated")
                else:
                    boss_event_item = world.create_event("Boss Defeated")
                boss_event_location.place_locked_item(boss_event_item)
                chapter_region.locations.append(boss_event_location)

            # Area completion.
            # The goal chapter does not contribute to Area Completion because the Goal Chapter requires completing
            # all other goals before it will unlock.
            if self.goal_requires_area_completion and not is_goal_chapter:
                loc_name = f"{chapter.short_name} Completion (Event)"
                completion_event_location = LegoStarWarsTCSLocation(world.player, loc_name, None, chapter_region)
                # "Level" here is as a user-facing term, with the meaning of "Area" internally.
                completion_event_item = world.create_event("Level Completion")
                completion_event_location.place_locked_item(completion_event_item)
                chapter_region.locations.append(completion_event_location)

            if exclude_locations:
                # Exclude the non-event locations in the chapter's region.
                loc: Location
                for loc in chapter_region.locations:
                    if not loc.is_event:
                        loc.progress_type = LocationProgressType.EXCLUDED

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
            loc_name = f"Chapter Completion - Unlock {character}"
            if len(parent_regions) == 1:
                parent_region = parent_regions[0]
                # The location is only accessed from 1 region, so put the location in that region. This slightly
                # improves logic performance.
                character_location = LegoStarWarsTCSLocation(
                    world.player, loc_name, world.location_name_to_id[loc_name], parent_region
                )
                if parent_region == excluded_goal_region:
                    # The location is only accessed through the Goal Chapter which has its locations excluded, so this
                    # chapter completion character unlock location should also be excluded.
                    character_location.progress_type = LocationProgressType.EXCLUDED
                    world.goal_excluded_character_unlock_location_count += 1
            else:
                # The location is accessed from multiple regions, so put the location in its own region that those
                # regions can be connected to.
                character_region = world.create_region(f"Unlock {character}")
                character_location = LegoStarWarsTCSLocation(
                    world.player, loc_name, world.location_name_to_id[loc_name], character_region
                )
                character_region.locations.append(character_location)
                for parent_region in parent_regions:
                    parent_region.connect(character_region)
                # There are multiple ways this location could be reached, so enable path display in the Spoiler (when
                # Playthrough Paths are enabled in the generator's host.yaml), so that the route the Playthrough used to
                # reach the location is clear.
                world.topology_present = True

        world.character_unlock_location_count += len(self.story_character_unlock_regions)

    def create_bonus_locations(self) -> None:
        world = self.world
        # Bonuses.
        bonuses = world.create_region("Bonuses")
        self.cantina.connect(bonuses, "Bonuses Door")

        # Group Bonuses by gold brick costs so that the regions requiring progressively more Gold Bricks can be
        # chained together more easily.
        gold_brick_costs: dict[int, list[BonusArea]] = {}
        for area in BONUS_AREAS:
            if area.name not in world.enabled_bonuses:
                continue
            gold_brick_costs.setdefault(area.gold_bricks_required, []).append(area)

        previous_gold_brick_region = bonuses
        for gold_brick_cost, areas in sorted(gold_brick_costs.items(), key=lambda t: t[0]):
            if gold_brick_cost == 0:
                region = bonuses
            else:
                region = world.create_region(f"{gold_brick_cost} Gold Bricks Collected")
                player = world.player
                previous_gold_brick_region.connect(
                    region, f"Collect {gold_brick_cost} Gold Bricks",
                    lambda state, cost_=gold_brick_cost, item_=GOLD_BRICK_EVENT_NAME: (
                        state.has(item_, player, cost_)))
                previous_gold_brick_region = region

            for area in areas:
                location = LegoStarWarsTCSLocation(
                    world.player, area.name, world.location_name_to_id[area.name], region)
                region.locations.append(location)
                # todo: Item requirements have been removed for now because it is not currently possible to lock
                #  access to the bonus levels.
                for item in area.item_requirements:
                    if item in CHARACTERS_AND_VEHICLES_BY_NAME:
                        world.character_chapter_access_counts[item] += 1
                if not area.gold_brick:
                    continue
                gold_brick_location = LegoStarWarsTCSLocation(
                    world.player, f"{area.name} - Gold Brick", None, region)
                gold_brick_location.place_locked_item(world.create_event(GOLD_BRICK_EVENT_NAME))
                self.gold_brick_event_count += 1
                region.locations.append(gold_brick_location)

                if self.goal_requires_area_completion:
                    loc_name = f"{area.name} Completion (Event)"
                    completion_event_location = LegoStarWarsTCSLocation(world.player, loc_name, None, region)
                    # "Level" here is as a user-facing term, with the meaning of "Area" internally.
                    completion_event_item = world.create_event("Level Completion")
                    completion_event_location.place_locked_item(completion_event_item)
                    region.locations.append(completion_event_location)

        # Indiana Jones shop purchase. Unlocks in the shop after watching the Lego Indiana Jones trailer.
        purchase_indy_name = "Purchase Indiana Jones"
        purchase_indy = LegoStarWarsTCSLocation(world.player, purchase_indy_name,
                                                world.location_name_to_id[purchase_indy_name], bonuses)
        bonuses.locations.append(purchase_indy)
        world.character_unlock_location_count += 1

    def create_all_episodes_character_purchases(self) -> None:
        world = self.world
        all_episodes = world.create_region("All Episodes Unlocked")
        self.cantina.connect(all_episodes, "Unlock All Episodes")
        all_episodes_purchases = SHOP_SLOT_REQUIREMENT_TO_UNLOCKS["ALL_EPISODES"]
        for character_name in all_episodes_purchases.keys():
            purchase = f"Purchase {character_name}"
            location = LegoStarWarsTCSLocation(world.player, purchase, world.location_name_to_id[purchase],
                                               all_episodes)
            all_episodes.locations.append(location)
            purchase_cost = CHARACTERS_AND_VEHICLES_BY_NAME[character_name].purchase_cost
            world.required_score_multiplier_count = max(world.required_score_multiplier_count,
                                                        world._get_score_multiplier_requirement(purchase_cost))
        world.character_unlock_location_count += len(all_episodes_purchases)

    def create_starting_purchases(self) -> None:
        world = self.world
        starting_purchases = [
            "Purchase Gonk Droid",
            "Purchase PK Droid",
        ]
        for purchase in starting_purchases:
            location = LegoStarWarsTCSLocation(world.player, purchase, world.location_name_to_id[purchase],
                                               self.cantina)
            self.cantina.locations.append(location)
        world.character_unlock_location_count += len(starting_purchases)

    def create_non_goal_chapter_victory(self) -> None:
        world = self.world
        victory = LegoStarWarsTCSLocation(world.player, "Goal", parent=self.cantina)
        victory.place_locked_item(world.create_event("Victory"))
        self.cantina.locations.append(victory)


def create_regions(world: TCSWorld) -> None:
    builder = _RegionBuilder(world)

    builder.create_episodes()

    if builder.story_character_unlock_regions:
        builder.create_story_character_unlock_locations()
    else:
        # Every Chapter has at least 1 Story Character, so if none exist in a generation, the locations should be
        # disabled.
        assert not builder.world.options.enable_story_character_unlock_locations

    # Adjust required score multipliers for any enabled chapters with difficult or potentially impossible True Jedi.
    if (world.options.enable_true_jedi_locations
            and not DIFFICULT_OR_IMPOSSIBLE_TRUE_JEDI.isdisjoint(world.enabled_chapters_with_locations)):
        world.required_score_multiplier_count = max(1, world.required_score_multiplier_count)

    # Available minikit count is calculated in generate_early.
    if world.available_minikits != builder.available_minikits_check:
        world.raise_error(AssertionError,
                          "Available minikits in create_regions did not match. %i from generate_early and %i"
                          " from create_regions. Please report this as a bug in the apworld.",
                          world.available_minikits,
                          builder.available_minikits_check)

    if world.options.enable_bonus_locations:
        builder.create_bonus_locations()

    # Check that the number of Gold Brick events created matched what was expected from the calculation in
    # generate_early.
    assert builder.gold_brick_event_count == world.expected_gold_brick_event_count

    # 'All Episodes' character purchases.
    if world.options.enable_all_episodes_purchases:
        builder.create_all_episodes_character_purchases()

    # General Victory event.
    if not world.goal_chapter:
        builder.create_non_goal_chapter_victory()

    # For debugging.
    # from Utils import visualize_regions
    # visualize_regions(cantina, "LegoStarWarsTheCompleteSaga_Regions.puml", show_entrance_names=True)
