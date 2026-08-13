import dataclasses
import typing
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, Field
from types import UnionType, NoneType
from typing import Any, TYPE_CHECKING, Iterable, cast, Union, Optional, get_origin, AbstractSet
from typing_extensions import override

from Options import Option, OptionSet, Range, FreeText, OptionCounter, OptionDict
from worlds.AutoWorld import World

from . import constants
from .options import (
    TCSDirectSlotDataOptions,
    MinikitGoalAmount,
    ChapterUnlockRequirement,
    TextColorChoice,
)

if TYPE_CHECKING:
    from worlds.lego_star_wars_tcs import LegoStarWarsTCSWorld
else:
    LegoStarWarsTCSWorld = object


class OptionalSlotData(ABC):
    @staticmethod
    @abstractmethod
    def is_present(world: LegoStarWarsTCSWorld) -> bool:
        ...


class ApWorldVersion(Option[tuple[int, int, int]]):
    default = (0, 0, 0)

    def __init__(self, version: tuple[int, int, int]):
        self.value = version

    @classmethod
    def from_any(cls, data: Any) -> Option[tuple[int, int, int]]:
        if isinstance(data, World) and isinstance(data, LegoStarWarsTCSWorld):
            return cls(constants.AP_WORLD_VERSION)
        major, minor, patch = data
        return cls((major, minor, patch))


class LogicVersion(Range):
    range_start = 1
    range_end = 999_999_999

    @classmethod
    def from_any(cls, data: Any) -> Range:
        if isinstance(data, World) and isinstance(data, LegoStarWarsTCSWorld):
            return cls(constants.UT_LOGIC_VERSION)
        return super().from_any(data)


class EnabledChapters(OptionSet):
    @classmethod
    def from_any(cls, data: Any) -> OptionSet:
        if isinstance(data, World) and isinstance(data, LegoStarWarsTCSWorld):
            return cls(data.enabled_chapters)
        return super().from_any(data)


class EnabledEpisodes(Option[AbstractSet[int]]):
    default = frozenset()

    def __init__(self, episodes: Iterable[int]):
        self.value = set(episodes)

    @classmethod
    def from_any(cls, data: Any) -> Option[AbstractSet[int]]:
        if isinstance(data, World) and isinstance(data, LegoStarWarsTCSWorld):
            return cls(data.enabled_episodes)
        elif isinstance(data, Iterable):
            return cls(data)
        else:
            raise TypeError(f"Cannot create EnabledEpisodes from {data} of type {type(data)}")


class EnabledBonuses(OptionSet):
    @classmethod
    def from_any(cls, data: Any) -> OptionSet:
        if isinstance(data, World) and isinstance(data, LegoStarWarsTCSWorld):
            return cls(data.enabled_bonuses)
        return super().from_any(data)


class StartingChapter(FreeText):
    @classmethod
    def from_any(cls, data: Any) -> FreeText:
        if isinstance(data, World) and isinstance(data, LegoStarWarsTCSWorld):
            return cls(data.starting_chapter.short_name)
        return super().from_any(data)


class StartingEpisode(Range):
    range_start = 1
    range_end = 6

    @classmethod
    def from_any(cls, data: Any) -> Range:
        if isinstance(data, World) and isinstance(data, LegoStarWarsTCSWorld):
            return cls(data.starting_episode)
        return super().from_any(data)


class MinikitGoalAmountDerived(Range):
    range_start = MinikitGoalAmount.range_start
    range_end = MinikitGoalAmount.range_end

    @classmethod
    def from_any(cls, data: Any) -> Range:
        if isinstance(data, World) and isinstance(data, LegoStarWarsTCSWorld):
            return cls(data.goal_minikit_count)
        return super().from_any(data)


class EnabledBosses(OptionSet):
    @classmethod
    def from_any(cls, data: Any) -> OptionSet:
        if isinstance(data, World) and isinstance(data, LegoStarWarsTCSWorld):
            return cls(data.enabled_bosses)
        return super().from_any(data)


class GoalAreaCompletionCount(Range):
    range_start = 0
    range_end = 36 + 6  # Chapters (36) + Bonuses (6, the Indy Trailer does not count).

    @classmethod
    def from_any(cls, data: Any) -> Range:
        if isinstance(data, World) and isinstance(data, LegoStarWarsTCSWorld):
            return cls(data.goal_area_completion_count)
        return super().from_any(data)


class GoalChapterShortName(FreeText, OptionalSlotData):
    @classmethod
    def from_any(cls, data: Any) -> FreeText:
        if isinstance(data, World) and isinstance(data, LegoStarWarsTCSWorld):
            return cls(data.goal_chapter if data.goal_chapter else "")
        return super().from_any(data)

    @override
    @staticmethod
    def is_present(world: LegoStarWarsTCSWorld) -> bool:
        return world.goal_chapter is not None


class ItemColors(Option[tuple[int, int, int, int, int, int, int]]):
    default = (TextColorChoice.option_white_ffffff,) * 7

    def __init__(self, colors: tuple[int, int, int, int, int, int, int]):
        self.value = colors

    @classmethod
    def from_any(cls, data: Any) -> Option[tuple[int, int, int, int, int, int, int]]:
        if isinstance(data, World) and isinstance(data, LegoStarWarsTCSWorld):
            return cls(data.options.item_colors_to_slot_data())
        (
            prog_useful,
            prog,
            useful,
            filler,
            trap,
            player,
            location,
            *_,  # Don't crash if there are extra colors included in a newer patch version.
        ) = data
        return cls((
            prog_useful,
            prog,
            useful,
            filler,
            trap,
            player,
            location,
        ))


class ChaptersRequiringAltCharacters(OptionSet, OptionalSlotData):
    @classmethod
    def from_any(cls, data: Any) -> OptionSet:
        if isinstance(data, World) and isinstance(data, LegoStarWarsTCSWorld):
            return cls(data.chapters_requiring_alt_characters)
        return super().from_any(data)

    @override
    @staticmethod
    def is_present(world: LegoStarWarsTCSWorld) -> bool:
        return world.options.chapter_unlock_requirement == ChapterUnlockRequirement.option_vanilla_characters


class ChapterRequiredCharacterCounts(OptionCounter, OptionalSlotData):
    @classmethod
    def from_any(cls, data: Any) -> OptionDict:
        if isinstance(data, World) and isinstance(data, LegoStarWarsTCSWorld):
            return cls(data.chapter_required_character_counts)
        return super().from_any(data)

    @override
    @staticmethod
    def is_present(world: LegoStarWarsTCSWorld) -> bool:
        return world.options.chapter_unlock_requirement.is_characters()


class ChapterRandomCharacterRequirements(Option[dict[str, list[int]]], OptionalSlotData):
    default = {}

    def __init__(self, value: dict[str, list[int]]):
        self.value = value

    @classmethod
    def from_any(cls, data: typing.Any) -> Option[dict[str, list[int]]]:
        if isinstance(data, World) and isinstance(data, LegoStarWarsTCSWorld):
            return cls({
                chapter: cast(list[int], [c.code for c in characters])
                for chapter, characters in data.chapter_random_character_requirements.items()
            })
        if isinstance(data, dict):
            return cls({
                chapter: list(ids) for chapter, ids in data.items()
            })
        raise TypeError(f"Cannot create ChapterRandomCharacterRequirements from {data} of type {type(data)}")

    @override
    @staticmethod
    def is_present(world: LegoStarWarsTCSWorld) -> bool:
        return world.options.chapter_unlock_requirement == ChapterUnlockRequirement.option_random_characters

_DIRECT_FIELD_NAMES: frozenset[str] = frozenset({field.name for field in dataclasses.fields(TCSDirectSlotDataOptions)})


@dataclass
class TCSSlotDataOptions(TCSDirectSlotDataOptions):
    ap_world_version: ApWorldVersion = field()
    enabled_chapters: EnabledChapters
    enabled_episodes: EnabledEpisodes
    enabled_bonuses: EnabledBonuses
    starting_chapter: StartingChapter
    starting_episode: StartingEpisode
    minikit_goal_amount: MinikitGoalAmountDerived
    enabled_bosses: EnabledBosses
    goal_area_completion_count: GoalAreaCompletionCount
    item_colors: ItemColors
    logic_version: LogicVersion  # = field(default_factory=lambda: LogicVersion(1), metadata=_since(1, 4, 0)) # Example
    goal_chapter: GoalChapterShortName | None = field(default=None)
    chapters_requiring_alt_characters: ChaptersRequiringAltCharacters | None = field(default=None)
    chapter_required_character_counts: ChapterRequiredCharacterCounts | None = field(default=None)
    chapter_random_character_requirements: ChapterRandomCharacterRequirements | None = field(default=None)

    @staticmethod
    def _get_option_type_from_hint(field_obj: Field) -> type[Option[Any]]:
        field_type = field_obj.type
        origin = get_origin(field_type)
        # At the time of writing, on Python 3.13, "X | None" produces a UnionType, but check for each origin for
        # compatibility purposes.
        if origin is UnionType or origin is Union or origin is Optional:
            non_optional_types: list[type] = []
            for arg in typing.get_args(field_type):
                if arg is NoneType:
                    continue
                non_optional_types.append(arg)
            if len(non_optional_types) != 1:
                raise Exception(f"Expected exactly one non-optional type for '{field_obj.name}', but got"
                                f" {len(non_optional_types)} ({non_optional_types}).")
            option_type = non_optional_types[0]
            if not issubclass(option_type, OptionalSlotData):
                raise Exception(f"All optional slot data options should extend OptionalSlotData, but {option_type}"
                                f" does not.")
            return option_type
        # Options use a metaclass, so the type of their type won't be `type`, but rather that metaclass.
        elif not isinstance(field_type, type) or not issubclass(field_type, Option):
            raise Exception(f"Expected an Option type for '{field_obj.name}', but got '{field_type}', a"
                            f" '{type(field_type)}'.")
        else:
            assert not issubclass(field_type, OptionalSlotData), "Required slot data should not be OptionalSlotData"
            return field_type

    def fill_slot_data(self, slot_data: dict[str, Any]) -> None:
        for field_obj in dataclasses.fields(self):
            field_name = field_obj.name
            field_option: Option[Any] | None = getattr(self, field_name)
            if field_option is None:
                # There is no option instance, so do not include anything in slot data.
                continue
            field_option: Option[Any] = getattr(self, field_name)
            field_value = field_option.value
            if isinstance(field_value, set):
                field_value = sorted(field_value)
            slot_data[field_name] = field_value

    @classmethod
    def from_world(cls, world: LegoStarWarsTCSWorld) -> "TCSSlotDataOptions":
        options = world.options
        constructor_kwargs: dict[str, Any] = {}
        for field_obj in dataclasses.fields(TCSSlotDataOptions):
            field_name = field_obj.name
            if field_name in _DIRECT_FIELD_NAMES:
                constructor_kwargs[field_name] = getattr(options, field_name)
            else:
                option_type: type[Option[Any]] = cls._get_option_type_from_hint(field_obj)
                if issubclass(option_type, OptionalSlotData) and not option_type.is_present(world):
                    constructor_kwargs[field_name] = None
                else:
                    option_instance = option_type.from_any(world)
                    constructor_kwargs[field_name] = option_instance
        return cls(**constructor_kwargs)

    @classmethod
    def from_slot_data(cls, slot_data: dict[str, Any]) -> "TCSSlotDataOptions":
        # todo: Need to handle defaults for options that are not present because of an older generator version
        constructor_kwargs: dict[str, Any] = {}
        missing_required_fields: dict[Option[Any], Field[Any]] = {}
        for field_obj in dataclasses.fields(TCSSlotDataOptions):
            field_name = field_obj.name
            if field_name in _DIRECT_FIELD_NAMES:
                option_type = field_obj.type
                assert issubclass(option_type, Option), \
                    "All direct slot data fields should have a type hint that is an Option subclass"
                if field_name not in slot_data:
                    missing_required_fields[option_type] = field_obj
                    continue
                option_value = slot_data[field_name]
                assert issubclass(option_type, Option)
                option = option_type.from_any(option_value)
                constructor_kwargs[field_name] = option
            else:
                option_type: type[Option[Any]] = cls._get_option_type_from_hint(field_obj)
                if field_name not in slot_data:
                    if not issubclass(option_type, OptionalSlotData):
                        missing_required_fields.append(field_obj)
                    else:
                        # Use the default/default_factory.
                        pass
                    continue
                option_value = slot_data[field_name]
                option = option_type.from_any(option_value)
                constructor_kwargs[field_name] = option
        if missing_required_fields:
            if ApWorldVersion in missing_required_fields:
                raise Exception("The version of the AP World that generated this multiworld is missing from slot data.")
            ap_world_version = next(v for v in constructor_kwargs.values() if isinstance(v, ApWorldVersion))
            ap_world_version_value = ap_world_version.value
            for field_obj in missing_required_fields.values():
                metadata = field_obj.metadata
                if metadata is None or "since" not in metadata or metadata["since"] <= ap_world_version_value:
                    raise Exception(f"Missing required slot data for {field_obj.name}")
                if field_obj.default is dataclasses.MISSING and field_obj.default_factory is dataclasses.MISSING:
                    raise AssertionError(f"Missing default for {field_obj.name}")
                # The default value/default_factory will be used.
        return cls(**constructor_kwargs)
