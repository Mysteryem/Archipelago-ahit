from dataclasses import dataclass, field
from typing import Iterable

from rule_builder.rules import Rule, True_


@dataclass(frozen=True)
class LocationData:
    region: str
    rule: Rule = field(default_factory=True_)


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


def minikit_data(region: str, rule: Rule | None = None, *, pickup_name: str) -> MinikitData:
    """Helper for defining minikit data with a single pickup name."""
    if rule is None:
        return MinikitData(region, pickup_names=(pickup_name,))
    else:
        return MinikitData(region, rule, (pickup_name,))


@dataclass(frozen=True)
class ExitData:
    to_region: str
    rule: Rule = field(default_factory=True_)
    name: str | None = None
    new_level: str | None = None


@dataclass(frozen=True)
class RegionData:
    name: str
    exits: tuple[ExitData, ...]

    def __init__(self, name: str, *exits: ExitData):
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "exits", tuple(exits))


@dataclass(frozen=True)
class Chapter:
    name: str
    episode_number: int
    chapter_number: int
    start_region: str
    start_level: str
    regions: dict[str, tuple[ExitData, ...]]
    minikits: dict[str, MinikitData]
    power_brick: LocationData
    # todo: It's probably better to keep the characters data separate.
    # story_characters: tuple[str, ...] = ()
    # purchase_characters: tuple[str, ...] = ()
    ridables: dict[str, LocationData] = field(default_factory=dict)
    extra_chapter_entrance_rules: Rule = field(default_factory=True_)
    story_characters: tuple[str, ...] = ()
    purchase_characters: dict[str, int] = field(default_factory=dict)
    level_minikits: dict[str, dict[str, MinikitData]] = field(init=False, default_factory=dict)
    level_names: frozenset[str] = field(init=False)
    region_to_level: dict[str, str] = field(init=False, default_factory=dict)

    def __post_init__(self):
        # Automatically add in the Chapter Completion region because it is the same in every Chapter.
        self.regions["Chapter Completion"] = ()

        # FIFO queue Depth-First-Search. DFS vs BFS doesn't matter here, only that every region is visited, and every
        # exit is tried.
        region_queue: list[tuple[str, str]] = [(self.start_region, self.start_level)]
        region_to_level = self.region_to_level
        while region_queue:
            region_name, region_level = region_queue.pop()

            if region_name in region_to_level:
                # Check that an alternative route has not propagated a different level name.
                if region_to_level[region_name] != region_level:
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

        # Check that there exists a path to each region from self.start_region.
        for region_name in self.regions:
            if region_name not in region_to_level:
                raise Exception(f"No path to the {region_name} region was found.")

        object.__setattr__(self, "level_names", frozenset(region_to_level.values()))

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
    def short_name(self) -> str:
        return f"{self.episode_number}-{self.chapter_number}"
