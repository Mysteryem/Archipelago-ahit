from typing import Optional, Literal, Mapping, cast, TYPE_CHECKING

from BaseClasses import Item, ItemClassification
from .constants import GAME_NAME, progression_deprioritized_skip_balancing
from .character_ability import *
from .data.areas import PURCHASABLE_NON_POWER_BRICK_EXTRAS
from .data.characters import Character
from .data.extras import Extra
from .data.items import GenericItemData, GenericCharacterData
from .data.items.all_character_items import CHARACTER_TO_ITEM_DATA
from .data.items.character_items import NORMAL_CHARACTER_DATA
from .data.items.extra_items import EXTRA_DATA, ExtraData
from .data.items.generic_items import GENERIC_DATA, MINIKITS_BY_NAME
from .data.items.vehicle_items import VEHICLE_DATA
from .options import AllEpisodesCharacterPurchaseRequirements, EpisodeUnlockRequirement


if TYPE_CHECKING:
    from . import LegoStarWarsTCSWorld
else:
    LegoStarWarsTCSWorld = object


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


def evaluate_effective_item(self: LegoStarWarsTCSWorld,
                            name: str,
                            effective_character_abilities_lookup: dict[str, CharacterAbility] | None = None,
                            relevant_item_counts: dict[str, int] | None = None,
                            ) -> tuple[ItemClassification, CharacterAbility]:
    classification = ItemClassification.filler
    abilities = CharacterAbility.NONE

    item_data = ITEM_DATA_BY_NAME[name]
    code = item_data.code
    if code is None or code < 1:
        raise RuntimeError(f"Error: Item '{name}' cannot be created")
    assert item_data.code != -1
    if isinstance(item_data, ExtraData):
        if relevant_item_counts is not None:
            if relevant_item_counts.get(name, 0) > 0:
                classification = ItemClassification.progression
            elif item_data not in PURCHASABLE_NON_POWER_BRICK_EXTRAS or name == Extra.EXTRA_TOGGLE.readable_name:
                classification = ItemClassification.useful
        else:
            if item_data in PURCHASABLE_NON_POWER_BRICK_EXTRAS:
                # Only Extra Toggle is useful out of these Extras due to the high movement speed Mouse Droid and a
                # few logic uses.
                if name == "Extra Toggle":
                    if self.options.logic_difficulty.normal_plus:
                        classification = ItemClassification.progression
                    else:
                        classification = ItemClassification.useful
            else:
                # Many Power Brick Extras provide cheat-like abilities to the player, so should be given at least
                # Useful classification.
                if self.options.logic_difficulty.normal_plus:
                    classification = ItemClassification.progression
                else:
                    classification = ItemClassification.useful
    elif isinstance(item_data, GenericCharacterData):
        if effective_character_abilities_lookup is not None:
            abilities = effective_character_abilities_lookup[name]
        else:
            abilities = item_data.abilities & ~self.starting_character_abilities

        if self.character_chapter_access_counts[name] > 0:
            if self.character_chapter_access_counts[name] >= self.prog_useful_level_access_threshold_count:
                # Characters that block access to a large number of chapters get progression + useful
                # classification. This is functionally identical to progression classification, but some
                # games/clients may specially highlight progression + useful items.
                classification = ItemClassification.progression | ItemClassification.useful
            else:
                classification = ItemClassification.progression
        elif abilities.contains_rare_and_useful_abilities():
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

        if name == Character.ADMIRAL_ACKBAR.readable_name:
            # There is no trap functionality, this trap classification is a joke.
            # Maybe once/if the world switches to modding, receiving this item could play the iconic "It's a trap!"
            # line.
            classification |= ItemClassification.trap

        # If the character is not currently progression, but is used directly in some rules, then they need to be
        # considered as progression.
        if (relevant_item_counts is not None
                and classification & ItemClassification.progression == 0
                and relevant_item_counts.get(name, 0) > 0):
            # Remove useful classification, if set.
            classification &= ~ItemClassification.useful
            # And add progression classification.
            classification |= ItemClassification.progression

        # Some characters are really logically powerful so should be Prog+Useful, or at least Useful if they are not
        # Progression. It is desirable to mark them as Skip Balancing to disallow progression balancing from moving
        # them earlier.
        if name in TOO_LOGICALLY_POWERFUL_CHARACTERS:
            classification |= ItemClassification.useful
            if ItemClassification.progression in classification:
                classification |= ItemClassification.skip_balancing
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
        # todo: Compare against the enum name
        elif name == "Progressive Score Multiplier":
            # Generic item that grants Score multiplier Extras, which are used in logic for purchases from the shop.
            if relevant_item_counts is not None:
                if relevant_item_counts.get(name, 0) > 0:
                    classification = ItemClassification.progression
                else:
                    classification = ItemClassification.useful
            else:
                # todo: Vary between progression and progression_skip_balancing depending on what percentage of
                #  locations need them.
                classification = ItemClassification.progression
        # todo: Compare against the enum name
        elif name == "Episode Completion Token":
            # Very few location checks and typically late into a seed.
            if (self.options.all_episodes_character_purchase_requirements
                    == AllEpisodesCharacterPurchaseRequirements.option_episodes_tokens):
                classification = ItemClassification.progression_skip_balancing
        # todo: Compare against the enum name
        elif name == "Kyber Brick":
            # Kyber Bricks are only logically relevant to the Kyber Bricks goal and do not unlock any locations, so
            # should skip progression balancing.
            if self.options.goal_requires_kyber_bricks:
                classification = ItemClassification.progression_skip_balancing
        # todo: Clean this up by using the item_data
        elif name.startswith("Episode ") and name.endswith(" Unlock"):
            if (int(name[len("Episode ")]) in self.enabled_episodes
                    and self.options.episode_unlock_requirement == EpisodeUnlockRequirement.option_episode_item):
                classification = ItemClassification.progression | ItemClassification.useful
        # todo: Clean this up by using the item_data
        elif name[:3] in self.enabled_chapters and name[3:] == " Unlock":
            # Chapter Unlock item.
            classification = ItemClassification.progression

    return classification, abilities