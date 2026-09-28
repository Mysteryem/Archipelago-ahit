from typing import Optional, Literal, Mapping, AbstractSet, cast

from BaseClasses import Item, ItemClassification
from .constants import GAME_NAME
from .character_ability import *
from .data.areas import Area
from .data.characters import Character
from .data.extras import Extra
from .data.items import GenericItemData, GenericCharacterData
from .data.items.all_character_items import CHARACTER_TO_ITEM_DATA
from .data.items.character_items import NORMAL_CHARACTER_DATA, CharacterData
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
    *NORMAL_CHARACTER_DATA,
    *VEHICLE_DATA,
    *GENERIC_DATA,
    *EXTRA_DATA,
]


USEFUL_NON_PROGRESSION_CHARACTERS: set[str] = {
    CHARACTER_TO_ITEM_DATA[c].name for c in
    (
        # Ghosts are invincible and untargetable.
        Character.BEN_KENOBI_GHOST,
        Character.ANAKIN_SKYWALKER_GHOST,
        Character.YODA_GHOST,
        # Yoda is fast when jumping, and is usable in many tricks in higher logic difficulties.
        Character.YODA,
        # The fastest character (1.8).
        Character.DROIDEKA,
        # The second-fastest characters (1.5), though a bit clunky to use since they cannot jump properly, and either cannot
        # attack at all, or have a very slow attack.
        Character.WATTO,
        Character.GEONOSIAN,
        # The third-fastest character when Super Gonk is active (1.44), also has good jump height with Super Gonk active.
        Character.GONK_DROID,
        # Fastest vehicles.
        Character.ANAKINS_POD,
        Character.SEBULBAS_POD,
    )
}
"""Characters that should always have at least Useful Classification."""

TOO_LOGICALLY_POWERFUL_CHARACTERS: set[str] = {
    CHARACTER_TO_ITEM_DATA[c].name for c in
    (
        # Can access Bounty Hunter, Astromech and Protocol panels, as well as the usual benefits of being a Bounty
        # Hunter, being able to jump, ride vehicles, shoot, melee and grapple.
        Character.FOUR_LOM,
        Character.IG_88,
    )
}
"""Characters that should always have Useful Classification. When they are logically relevant they will be
Progression + Useful + Skip Balancing."""


ITEM_DATA_BY_NAME: Mapping[str, GenericItemData] = {data.name: data for data in ITEM_DATA}
ITEM_DATA_BY_ID: Mapping[int, GenericItemData] = cast(dict[int, GenericItemData],
                                                      {data.code: data for data in ITEM_DATA if data.is_sendable})
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

ITEM_NAME_TO_ID: dict[str, int] = cast(
    dict[str, int],
    {name: item.code for name, item in ITEM_DATA_BY_NAME.items() if item.is_sendable}
)

SUPER_GONK_ITEMS: frozenset[str] = frozenset(["Gonk Droid", "Super Gonk"])
SUPER_GONK_DROID_ABILITIES_VALUE: int = (
    CHARACTERS_AND_VEHICLES_BY_NAME["Super Gonk Droid"].abilities
    # Abilities provided by non-super Gonk Droid can be skipped.
    & ~CHARACTERS_AND_VEHICLES_BY_NAME["Gonk Droid"].abilities
).value
