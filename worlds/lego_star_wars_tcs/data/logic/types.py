from dataclasses import dataclass, field
from typing import Iterable

from rule_builder.rules import (
    Rule,
    True_,
    Or,
    CanReachRegion,
    CanReachLocation,
    CanReachEntrance,
)

from .extra_toggle import ExtraToggleRuleReplacer
from ..areas import Area
from ..characters import Character, UnlockMethod
from ..levels import Level


@dataclass(frozen=True)
class LocationData:
    region: str
    rule: Rule = field(default_factory=True_)
    er_rule: Rule | None = None
    """While ER is not implemented, comparing generation using the slower ER rules vs pre-optimised normal rules can
    identify issues in the logic if their two sets of rules don't produce identical results.
    If `er_rule` is None, use `rule` instead."""


@dataclass(frozen=True)
class StudsEventData(LocationData):
    stud_total: int = 0

    def __post_init__(self):
        if self.stud_total < 0:
            raise Exception(f"Invalid stud_total {self.stud_total}. stud_total must be greater than zero.")


@dataclass(frozen=True)
class MinikitData(LocationData):
    # Minikits that can be achieved by performing actions in multiple orders sometimes have different names depending on
    # which was the last action performed. This also allowed for minikit 'duplication' in vanilla, though the minikits
    # collected are technically unique, so it's not actually duplication. For randomizer purposes, these unique minikits
    # are considered the same AP location.
    pickup_names: tuple[str, ...] = ()

    def __post_init__(self):
        if not self.pickup_names:
            raise Exception("No pickup names provided")
        for name in self.pickup_names:
            # Minikit pickup names are null-terminated strings of up to 8 bytes, so only 7 bytes can be used when
            # including the null-terminator.
            byte_size = len(name.encode())
            if byte_size > 7:
                raise Exception(f"Invalid pickup name {name} encodes to {byte_size} bytes, but the max is 7.")


def minikit_data(region: str, rule: Rule | None = None, *, er_rule: Rule | None = None, pickup_name: str) -> MinikitData:
    """Helper for defining minikit data with a single pickup name."""
    if rule is None:
        return MinikitData(region, er_rule=er_rule, pickup_names=(pickup_name,))
    else:
        return MinikitData(region, rule, er_rule, (pickup_name,))


@dataclass(frozen=True)
class ExitData:
    to_region: str
    rule: Rule = field(default_factory=True_)
    er_rule: Rule | None = None
    name: str | None = None
    new_level: Level | None = None


@dataclass(frozen=True)
class RegionData:
    name: str
    exits: tuple[ExitData, ...]

    def __init__(self, name: str, *exits: ExitData):
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "exits", tuple(exits))


@dataclass
class ChapterHelper:
    name: str
    area: Area
    start_region: str
    _regions_used_in_can_reach: set[str] = field(default_factory=set, init=False)

    def can_reach_region(self, region_name: str):
        self._regions_used_in_can_reach.add(region_name)
        return CanReachRegion(f"{self.name} - {region_name}")

    def can_reach_location(self, location_name: str):
        return CanReachLocation(f"{self.name} - {location_name}")

    def can_reach_entrance(self, entrance_name: str):
        return CanReachEntrance(f"{self.name} - {entrance_name}")

    def make_chapter(
            self,
            regions: dict[str, tuple[ExitData, ...]],
            minikits: dict[str, MinikitData],
            power_brick: LocationData,
            # TODO: Add wip_true_jedi_rule
            ridables: dict[str, LocationData] | None = None,
            extra_chapter_entrance_rules: Rule | None = None,
    ):
        if ridables is None:
            ridables = {}
        if extra_chapter_entrance_rules is None:
            extra_chapter_entrance_rules = True_()
        return Chapter(
            name=self.name,
            area=self.area,
            start_region=self.start_region,
            regions=regions,
            minikits=minikits,
            power_brick=power_brick,
            ridables=ridables,
            extra_chapter_entrance_rules=extra_chapter_entrance_rules,
            regions_in_can_reach=self._regions_used_in_can_reach,
        )


@dataclass(frozen=True)
class Chapter:
    name: str
    area: Area
    start_region: str
    regions: dict[str, tuple[ExitData, ...]]
    minikits: dict[str, MinikitData]
    power_brick: LocationData

    # TODO: Add wip_true_jedi_rule
    ridables: dict[str, LocationData] = field(default_factory=dict)
    extra_chapter_entrance_rules: Rule = field(default_factory=True_)
    regions_in_can_reach: Iterable[str] = ()

    story_characters: frozenset[Character] = field(init=False)
    purchase_characters: frozenset[Character] = field(init=False)
    extra_toggle_characters: frozenset[Character] = field(init=False)
    start_level: Level = field(init=False)
    level_minikits: dict[Level, dict[str, MinikitData]] = field(init=False, default_factory=dict)
    region_to_level: dict[str, Level] = field(init=False, default_factory=dict)

    def __post_init__(self):
        # Get story/purchase/Extra Toggle characters from the Area.
        purchase_characters = self.area.get_purchase_characters()
        story_characters = self.area.get_story_characters()
        extra_toggle_characters = self.area.get_extra_toggle_characters()
        object.__setattr__(self, "story_characters", story_characters)
        object.__setattr__(self, "purchase_characters", purchase_characters)
        object.__setattr__(self, "extra_toggle_characters", extra_toggle_characters)

        start_level = self.area.get_first_playable_level()
        if start_level is None:
            raise Exception(f"First playable level for {self.name} is None")
        object.__setattr__(self, "start_level", start_level)

        if self.extra_toggle_characters:
            extra_toggle_replacer = ExtraToggleRuleReplacer(self)
            for region_name, exits in self.regions.items():
                self.regions[region_name] = tuple(
                    extra_toggle_replacer.add_extra_toggle_rules(exit_) for exit_ in exits
                )
            for minikit_name, minikit_data in self.minikits.items():
                self.minikits[minikit_name] = extra_toggle_replacer.add_extra_toggle_rules(minikit_data)
            for ridable_name, ridable_data in self.ridables.items():
                self.ridables[ridable_name] = extra_toggle_replacer.add_extra_toggle_rules(ridable_data)
            replaced_power_brick_data = extra_toggle_replacer.add_extra_toggle_rules(self.power_brick)
            object.__setattr__(self, "power_brick", replaced_power_brick_data)

        # Automatically add in the Chapter Completion region because it is the same in every Chapter.
        self.regions["Chapter Completion"] = ()

        # FIFO queue Depth-First-Search. DFS vs BFS doesn't matter here, only that every region is visited, and every
        # exit is tried.
        region_queue: list[tuple[str, Level]] = [(self.start_region, self.start_level)]
        region_to_level = self.region_to_level
        while region_queue:
            region_name, region_level = region_queue.pop()

            if region_name in region_to_level:
                # Check that an alternative route has not propagated a different level name.
                # The "Chapter Completion" region's level is set automatically, so is ignored by this check.
                if region_to_level[region_name] != region_level and region_name != "Chapter Completion":
                    raise Exception(f"Already found that {region_name} is in level {region_to_level[region_name]}, but"
                                    f"now also found it in {region_level}.")
                continue
            else:
                region_to_level[region_name] = region_level
                for exit_data in self.regions[region_name]:
                    if exit_data.new_level:
                        # Traversing this exit loads a new level.
                        region_queue.append((exit_data.to_region, exit_data.new_level))
                    else:
                        # Traversing this exit continues within the current level.
                        region_queue.append((exit_data.to_region, region_level))

        # Automatically set the Level of the Chapter Completion region to the status level of this area.
        status_level = self.area.get_status_level()
        if status_level is None:
            raise Exception(f"Status level for {self.name} is None")
        region_to_level["Chapter Completion"] = status_level

        # Check that there exists a path to each region from self.start_region.
        for region_name in self.regions:
            if region_name not in region_to_level:
                raise Exception(f"No path to the {region_name} region was found.")

        for location_name, minikit in self.minikits.items():
            level = region_to_level[minikit.region]
            if level in self.level_minikits:
                minikits_dict = self.level_minikits[level]
            else:
                minikits_dict = {}
                self.level_minikits[level] = minikits_dict
            minikits_dict[location_name] = minikit

    @property
    def all_in_level_location_data(self) -> Iterable[LocationData]:
        """Yield all locations that are guaranteed to be unique to this chapter and are found within the chapter itself.

        Does not include locations that become accessible once the chapter is completed (these are always in the Chapter
        Completion region of the level, and most of the data for these locations is defined elsewhere)."""
        yield from self.minikits.values()
        yield from self.ridables.values()
        yield self.power_brick

    @property
    def area_id(self) -> int:
        return self.area.area_index

    @property
    def episode_number(self) -> int:
        return self.area.episode_index + 1

    @property
    def chapter_number(self) -> int:
        return self.area.area_index + 1

    @property
    def story_true_jedi(self) -> int:
        return self.area.story_true_jedi

    @property
    def free_play_true_jedi(self) -> int:
        return self.area.free_play_true_jedi

    @property
    def short_name(self) -> str:
        return f"{self.episode_number}-{self.chapter_number}"


@dataclass
class LegacyMinikitData:
    level: str
    pickup_names: tuple[str, ...]

    @classmethod
    def new(cls, level: str, pickup_name: str):
        return cls(level, (pickup_name,))


def _make_legacy_chapter(
        name: str,
        episode_number: int,
        chapter_number: int,
        minikits_rule: Rule,
        completion_rule: Rule,
        #true_jedi_rule: Rule,
        power_brick_rule: Rule,
        minikits: dict[str, LegacyMinikitData],
        ridables: dict[str, Rule],
        extra_chapter_entrance_rules: Rule,
        story_characters: Iterable[str] = (),
        purchase_characters: dict[str, int] | None = None,
        extra_toggle_characters: Iterable[str] = (),
):
    if purchase_characters is None:
        purchase_characters = {}

    for area in Area:
        if area.episode_index == episode_number - 1 and area.area_index == chapter_number - 1:
            break
    else:
        raise Exception(f"Could not find Area for {episode_number}-{chapter_number}")

    required_minikit_levels = {data.level for data in minikits.values()}

    minikit_level_region_names = sorted(required_minikit_levels)

    start_region = "Spawn"

    regions: dict[str, tuple[ExitData, ...]] = {
        start_region: (
            ExitData("Chapter Completion", completion_rule),
            ExitData("Minikits", minikits_rule),
        ),
        "Minikits": tuple(ExitData(level, new_level=Level[level.upper()]) for level in minikit_level_region_names)}
    # Add exits from the Minikits region to each additional level region that is required.

    # Add the required additional level regions.
    for level in minikit_level_region_names:
        regions[level] = ()

    # Convert the placeholder minikit data into real MinikitData referencing regions with the correct level names.
    minikits_data: dict[str, MinikitData] = {}
    for minikit_name, placeholder_minikit_data in minikits.items():
        region = placeholder_minikit_data.level
        minikits_data[minikit_name] = MinikitData(region, pickup_names=placeholder_minikit_data.pickup_names)

    ridables_data: dict[str, LocationData] = {}
    for ridable_name, rule in ridables.items():
        ridables_data[ridable_name] = LocationData(start_region, rule)

    return Chapter(
        name=name,
        area=area,
        start_region=start_region,
        regions=regions,
        minikits=minikits_data,
        power_brick=LocationData(start_region, power_brick_rule),
        ridables=ridables_data,
        extra_chapter_entrance_rules=extra_chapter_entrance_rules,
    )


def make_legacy_chapter(
        short_name: str,
        minikits: dict[str, LegacyMinikitData],
):
    from ...levels import SHORT_NAME_TO_CHAPTER_AREA, VEHICLE_CHAPTER_SHORTNAMES
    from .rules import HasAllAbilities, HasAbility
    from ...ridables import CHAPTER_TO_RIDABLES, get_ridable_requirements
    from ...character_ability import CharacterAbility
    from ...items import CHARACTERS_AND_VEHICLES_BY_NAME
    area = SHORT_NAME_TO_CHAPTER_AREA[short_name]

    if area.completion_alt_ability_requirements is not None:
        completion_rule = Or(
            HasAllAbilities(area.completion_main_ability_requirements),
            HasAllAbilities(area.completion_alt_ability_requirements),
        )
    else:
        completion_rule = HasAllAbilities(area.completion_main_ability_requirements)

    chapter_ridables = CHAPTER_TO_RIDABLES.get(short_name, [])
    ridables: dict[str, Rule] = {}
    for ridable in chapter_ridables:
        requirements = get_ridable_requirements(short_name, ridable.user_facing_name)
        ridables[ridable.user_facing_name] = Or(*map(HasAllAbilities, requirements))

    return _make_legacy_chapter(
        name=area.name,
        episode_number=area.episode,
        chapter_number=area.number_in_episode,
        minikits_rule=Or(*map(HasAllAbilities, area.all_minikits_ability_requirements)),
        completion_rule=completion_rule,
        power_brick_rule=Or(*map(HasAllAbilities, area.power_brick_ability_requirements)),
        minikits=minikits,
        ridables=ridables,
        extra_chapter_entrance_rules=(HasAbility(CharacterAbility.IS_A_VEHICLE)
                                      if short_name in VEHICLE_CHAPTER_SHORTNAMES else True_()),
    )
