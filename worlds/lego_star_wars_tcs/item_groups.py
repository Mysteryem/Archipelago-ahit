from typing import Mapping, Sequence

from .constants import CharacterAbility
from .data.items import GenericCharacterData
from .data.items.all_character_items import SENDABLE_CHARACTER_TO_ITEM_DATA
from .data.items.extra_items import EXTRA_DATA
from .data.items.generic_items import NonDataItemName
from .items import (
    MINIKITS_BY_COUNT,
    CHAPTER_UNLOCKS,
)
from .levels import CHAPTER_AREAS


def _ability_to_sendable_character() -> Mapping[CharacterAbility, Sequence[GenericCharacterData]]:
    ability_to_character: dict[CharacterAbility, list[GenericCharacterData]] = {}
    for char in SENDABLE_CHARACTER_TO_ITEM_DATA.values():
        for ability in char.abilities:
            ability_to_character.setdefault(ability, []).append(char)
    return {k: tuple(v) for k, v in ability_to_character.items()}


ABILITY_TO_SENDABLE_CHARACTERS: Mapping[CharacterAbility, Sequence[GenericCharacterData]]
ABILITY_TO_SENDABLE_CHARACTERS = _ability_to_sendable_character()
# ABILITY_TO_CHARACTER_NAMES: Mapping[CharacterAbility, Sequence[str]] = {
#     ability: tuple(char.name for char in characters) for ability, characters in ABILITY_TO_CHARACTERS.items()
# }


def ability_to_readable_group(ability: CharacterAbility) -> str:
    return ability.name.replace("_", " ").title() + " Characters"  # type: ignore # (.name is str | None)


REVERSE_READABLE_ABILITY_TO_ABILITY = {ability_to_readable_group(ability): ability for ability in CharacterAbility}


ITEM_GROUPS: dict[str, set[str]] = {
    **{ability_to_readable_group(ability): {c.name for c in characters if c.is_sendable}
       for ability, characters in ABILITY_TO_SENDABLE_CHARACTERS.items()},
    "Non-Vehicle Characters": {c.name for c in SENDABLE_CHARACTER_TO_ITEM_DATA.values()
                               if c.item_type == "Character"},
    "Vehicle Characters": {v.name for v in SENDABLE_CHARACTER_TO_ITEM_DATA.values()
                           if v.item_type == "Vehicle"},
    **{
        f"{chapter.short_name} Story Unlock Characters": set(chapter.character_requirements)
        for chapter in CHAPTER_AREAS
    },
    **{
        f"{chapter.short_name} Purchase Unlock Characters": set(chapter.alt_character_requirements)
        for chapter in CHAPTER_AREAS if chapter.alt_character_requirements
    },
    "Characters": {c.name for c in SENDABLE_CHARACTER_TO_ITEM_DATA.values()},
    "Extras": {e.name for e in EXTRA_DATA if e.is_sendable} | {NonDataItemName.PROGRESSIVE_SCORE_MULTIPLIER.value},
    "Minikits": {m.name for m in MINIKITS_BY_COUNT.values() if m.is_sendable},
    "Episode Unlocks": {f"Episode {i} Unlock" for i in "123456"},
    "Chapter Unlocks": {data.name for data in CHAPTER_UNLOCKS},
    "Junk": {
        name.value for name in (
            NonDataItemName.SILVER_STUD,
            NonDataItemName.GOLD_STUD,
            NonDataItemName.BLUE_STUD,
            NonDataItemName.PURPLE_STUD,
            NonDataItemName.POWER_UP,
        )
    }
}
