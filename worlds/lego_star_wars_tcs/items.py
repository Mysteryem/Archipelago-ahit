from typing import Optional, Literal, Mapping, AbstractSet, cast

from BaseClasses import Item, ItemClassification
from .constants import GAME_NAME
from .character_ability import *
from .data.areas import Area
from .data.characters import Character
from .data.extras import Extra
from .data.items import GenericItemData, GenericCharacterData
from .data.items.character_items import CHARACTER_DATA, CharacterData
from .data.items.extra_items import EXTRA_DATA, ExtraData
from .data.items.generic_items import GENERIC_DATA, MinikitItemData, CHAPTER_TO_CHAPTER_UNLOCK_ITEM
from .data.items.vehicle_items import VEHICLE_DATA


ItemType = Literal["Character", "Vehicle", "Extra", "Generic", "Minikit"]


class LegoStarWarsTCSItem(Item):
    game = GAME_NAME
    # Most Progression items collect their abilities into the state through a world.collect() override.
    # `collect_abilities_int is not None` is faster than `collect_abilities_int != 0`, so `None` is used instead of `0`.
    collect_abilities_int: int | None
    abilities: CharacterAbility

    def __init__(self, name: str, classification: ItemClassification, code: Optional[int], player: int,
                 abilities: CharacterAbility | None = None):
        super().__init__(name, classification, code, player)
        if abilities is not None and abilities.value != 0:
            self.collect_abilities_int = abilities.value
            self.abilities = abilities
            assert ItemClassification.progression in classification, "All items with abilities should be progression."
        else:
            self.collect_abilities_int = None
            self.abilities = CharacterAbility.NONE


ITEM_DATA: list[GenericItemData] = [
    *CHARACTER_DATA,
    *VEHICLE_DATA,
    *GENERIC_DATA,
    *EXTRA_DATA,
]


USEFUL_NON_PROGRESSION_CHARACTERS: set[Character] = {
    # There is currently no Ghost logic for bypassing gas and other hazards, so give the Ghosts at least Useful
    # classification.
    Character.BEN_KENOBI_GHOST,
    Character.ANAKIN_SKYWALKER_GHOST,
    Character.YODA_GHOST,
    # There is currently no glitch logic for the glitchy mess that is Yoda, so ensure Yoda is never excluded by making
    # him Useful.
    Character.YODA,
    # The fastest character (1.8).
    Character.DROIDEKA,
    # The second-fastest character (1.5).
    Character.WATTO,
    # The third-fastest character when Super Gonk is active (1.44).
    Character.GONK_DROID,
    # Fastest vehicles.
    Character.ANAKINS_POD,
    Character.SEBULBAS_POD,
}


ITEM_DATA_BY_NAME: Mapping[str, GenericItemData] = {data.name: data for data in ITEM_DATA}
ITEM_DATA_BY_ID: Mapping[int, GenericItemData] = cast(dict[int, GenericItemData],
                                                      {data.code: data for data in ITEM_DATA if data.is_sendable})
EXTRAS_BY_NAME: Mapping[str, ExtraData] = {data.name: data for data in ITEM_DATA if isinstance(data, ExtraData)}
_POWER_BRICK_EXTRAS: set[Extra] = cast(set[Extra], {area.extra for area in Area if area.is_chapter()})
PURCHASABLE_NON_POWER_BRICK_EXTRAS: tuple[ExtraData, ...] = tuple(
    [extra for extra in EXTRAS_BY_NAME.values()
     if extra.extra.purchase_cost is not None and extra.extra not in _POWER_BRICK_EXTRAS]
)
CHARACTERS_AND_VEHICLES_BY_NAME: Mapping[str, GenericCharacterData] = {
    data.name: data for data in ITEM_DATA if isinstance(data, GenericCharacterData)}
LOGIC_CONSIDERED_CHARACTERS = {
    name: character for name, character in CHARACTERS_AND_VEHICLES_BY_NAME.items()
    # todo: Mark unsendable, but event characters instead of hardcoding Super Gonk Droid like this.
    if character.is_sendable or character.name == "Super Gonk Droid"
}
GENERIC_BY_NAME: Mapping[str, GenericItemData] = {data.name: data for data in ITEM_DATA if data.item_type == "Generic"}
MINIKITS_BY_NAME: Mapping[str, MinikitItemData] = {data.name: data for data in ITEM_DATA
                                                   if isinstance(data, MinikitItemData)}
NON_VEHICLE_CHARACTER_BY_INDEX: Mapping[Character, CharacterData] = {char.character: char
                                                               for char in CHARACTERS_AND_VEHICLES_BY_NAME.values()
                                                               if isinstance(char, CharacterData)}
AP_NON_VEHICLE_CHARACTER_INDICES: AbstractSet[Character] = {char.character
                                                      for char in NON_VEHICLE_CHARACTER_BY_INDEX.values()
                                                      if char.is_sendable}
CHAPTER_UNLOCKS = list(map(ITEM_DATA_BY_NAME.__getitem__, CHAPTER_TO_CHAPTER_UNLOCK_ITEM.values()))

ITEM_NAME_TO_ID: dict[str, int] = cast(
    dict[str, int],
    {name: item.code for name, item in ITEM_DATA_BY_NAME.items() if item.is_sendable}
)

MINIKITS_BY_COUNT: Mapping[int, GenericItemData] = {bundle.bundle_size: bundle for bundle in MINIKITS_BY_NAME.values()}
SUPER_GONK_ITEMS: frozenset[str] = frozenset(["Gonk Droid", "Super Gonk"])
SUPER_GONK_DROID_ABILITIES_VALUE: int = (
    CHARACTERS_AND_VEHICLES_BY_NAME["Super Gonk Droid"].abilities
    # Abilities provided by non-super Gonk Droid can be skipped.
    & ~CHARACTERS_AND_VEHICLES_BY_NAME["Gonk Droid"].abilities
).value


def _make_single_jump_distance_relevant_characters_by_jump_distance() -> dict[float, list[str]]:
    jump_distance_to_characters: dict[float, list[str]] = {}
    for c in LOGIC_CONSIDERED_CHARACTERS.values():
        if not isinstance(c, CharacterData):
            # Vehicles are irrelevant.
            continue
        if (HOVER | CAN_DOUBLE_JUMP) & c.abilities != 0:
            # Double jump and hover characters are always considered to have max jump distance.
            # Any need for logic beyond how far non-double-jump and non-hover characters can jump is handle separately.
            continue
        distance = c.single_jump_distance
        if distance in jump_distance_to_characters:
            jump_distance_to_characters[distance].append(c.name)
        else:
            jump_distance_to_characters[distance] = [c.name]

    # Sort by jump distance and then return.
    return dict(sorted(jump_distance_to_characters.items(), key=lambda t: t[0]))


SORTED_SINGLE_JUMP_DISTANCE_TO_CHARACTER_NAMES = _make_single_jump_distance_relevant_characters_by_jump_distance()
del _make_single_jump_distance_relevant_characters_by_jump_distance
