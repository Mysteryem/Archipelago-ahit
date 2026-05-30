import itertools
import re
from dataclasses import dataclass, field
from enum import IntEnum, auto
from typing import Optional, ClassVar, Literal, Mapping, AbstractSet

from BaseClasses import Item, ItemClassification
from .constants import GAME_NAME
from .character_ability import *


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


class Alignment(IntEnum):
    GOOD = auto()  # Enemies will attack on sight.
    NEUTRAL = auto()  # Enemies will only attack if attacked first (or attacks are used nearby).
    PASSIVE = auto()  # Enemies will not attack. Switching to a passive character will lose aggro.
    # Enemies will only attack if attacked first (or attacks are used nearby). These characters have the "baddie" tag.
    EVIL = auto()


@dataclass(frozen=True)
class GenericItemData:
    code: int
    name: str
    item_type: ClassVar[ItemType] = "Generic"

    @property
    def is_sendable(self):
        return self.code > 0


@dataclass(frozen=True)
class MinikitItemData(GenericItemData):
    bundle_size: int
    item_type: ClassVar[ItemType] = "Minikit"


@dataclass(frozen=True)
class GenericCharacterData(GenericItemData):
    character_index: int
    abilities: CharacterAbility
    run_speed: float  # The majority of characters have 1.2.
    # Jump height is calculated through jump_speed**2/(2*air_gravity) (v0**2/2g: v0 = jump_speed, g=-air_gravity
    single_jump_height: float  # The majority of characters have 0.44 (Jedi and many other decent jumpers).
    # Jump distance is calculated through air_time = 2*jump_speed/abs(air_gravity); jump_distance = air_time * run_speed
    single_jump_distance: float
    shop_slot: int = field(init=False)
    purchase_cost: int = field(init=False)

    def __post_init__(self):
        shop_slot = CHARACTER_TO_SHOP_SLOT.get(self.name, -1)
        object.__setattr__(self, "shop_slot", shop_slot)
        _unlock_method, studs_cost = CHARACTER_SHOP_SLOTS.get(self.name, (..., 0))
        object.__setattr__(self, "purchase_cost", studs_cost)

    @property
    def purchase_location_name(self) -> str:
        if self.shop_slot == -1:
            raise RuntimeError(f"{self.name} has no shop slot, so cannot be purchased.")
        chapter_short_name, _slot = CHARACTER_SHOP_SLOTS[self.name]
        if chapter_short_name and re.fullmatch(r"\d-\d", chapter_short_name[:3]):
            return f"Purchase {self.name} ({chapter_short_name[:3]})"
        else:
            return f"Purchase {self.name}"


@dataclass(frozen=True)
class CharacterData(GenericCharacterData):
    alignment: Alignment = Alignment.GOOD
    item_type: ClassVar[ItemType] = "Character"

    def __post_init__(self):
        super().__post_init__()

        # Automatically set some implied abilities as a safeguard.
        abilities = self.abilities

        if self.single_jump_height >= 0.44:
            abilities |= CAN_JUMP_0_44 | CAN_JUMP_HEIGHT_0_37
        elif self.single_jump_height >= 0.37:
            abilities |= CAN_JUMP_HEIGHT_0_37

        if self.single_jump_distance >= 0.7:
            abilities |= CAN_JUMP_DISTANCE_0_69

        # All Sith are Jedi.
        if SITH in abilities:
            abilities |= JEDI
            assert self.alignment is Alignment.EVIL, f"{self.name} is a Sith, but is not EVIL alignment."

        # All characters that can Grapple happen to have Blasters.
        if GRAPPLE in abilities:
            abilities |= BLASTER

        # These can all melee.
        if JEDI in abilities or BOUNTY_HUNTER in abilities or CAN_HIGH_JUMP_SLAM in abilities:
            abilities |= CAN_MELEE

        # All Bounty Hunters can use blasters.
        if BOUNTY_HUNTER in abilities:
            abilities |= BLASTER

        assert CAN_BUILD_BRICKS not in abilities or CAN_JUMP_HEIGHT_0_37 in abilities, \
            f"All characters that can build should be able to jump 0.37 or higher, but {self.name} cannot."

        assert BOUNTY_HUNTER not in abilities or self.alignment is Alignment.EVIL, \
            f"{self.name} is a Bounty Hunter, but is not EVIL alignment."

        if (HIGH_JUMP | JEDI) & abilities != 0:
            abilities |= CAN_JUMP_0_44
            abilities |= CAN_DOUBLE_JUMP
            abilities |= CAN_JUMP_DISTANCE_0_69
        if CAN_JUMP_0_44 in abilities:
            abilities |= CAN_FLOP_JUMP
        if CAN_FLOP_JUMP in abilities:
            abilities |= CAN_JUMP_HEIGHT_0_37
        if CAN_JUMP_HEIGHT_0_37 in abilities:
            # Normal jump distance is not guaranteed.
            abilities |= CAN_BARELY_JUMP
            if self.run_speed >= 1.2:
                abilities |= CAN_JUMP_DISTANCE_0_69

        # Jetpacks are a superior version of Astromech hovering.
        if JETPACK in abilities:
            abilities |= HOVER
        # Hovering is the superior version of jump distance.
        if HOVER in abilities:
            abilities |= CAN_JUMP_DISTANCE_0_69

        # Automatically set special Hat Machine abilities that are not set explicitly.
        if CAN_WEAR_HAT in abilities and GRAPPLE in abilities:
            abilities |= CAN_WEAR_HAT_AND_GRAPPLE
        if CAN_WEAR_HAT in abilities and CAN_DOUBLE_JUMP in abilities:
            abilities |= CAN_WEAR_HAT_AND_DOUBLE_JUMP

        if self.alignment is Alignment.PASSIVE:
            # Note that Force Ghosts are considered passive.
            abilities &= ~CAN_AGGRAVATE_ENEMIES
        else:
            # Enemies are aggressive against GOOD characters and will fight back against that damage or attack near
            # them, except Force Ghosts who are untargetable.
            if CAN_MELEE in abilities or BLASTER in abilities or self.alignment is Alignment.GOOD:
                abilities |= CAN_AGGRAVATE_ENEMIES
            # All non-passive (non-ghost) Jedi can deflect (and reflect) blaster bolts.
            if JEDI in abilities:
                abilities |= CAN_DEFLECT_BOLTS

        if self.run_speed >= 0.9 and IS_A_VEHICLE not in abilities:
            abilities |= RUN_SPEED_0_9_OR_HIGHER

        if abilities is not self.abilities:
            # print(f"Updated abilities for {self.name}. Added:\n\t{abilities & ~self.abilities!r}")
            object.__setattr__(self, "abilities", abilities)


@dataclass(frozen=True)
class VehicleData(GenericCharacterData):
    item_type: ClassVar[ItemType] = "Vehicle"
    single_jump_height: float = 0.0
    single_jump_distance: float = 0.0

    def __post_init__(self):
        super().__post_init__()

        # Automatically set some implied abilities as a safeguard.
        abilities = self.abilities

        # To have a vehicle ability implies being a vehicle.
        if (VEHICLE_BLASTER | VEHICLE_TOW | VEHICLE_TIE) & abilities != 0:
            abilities |= IS_A_VEHICLE

        if abilities is not self.abilities:
            # print(f"Updated abilities for {self.name}. Added:\n\t{abilities & ~self.abilities!r}")
            object.__setattr__(self, "abilities", abilities)


@dataclass(frozen=True)
class ExtraData(GenericItemData):
    extra_number: int
    level_shortname: str | None
    localization_id: int
    item_type: ClassVar[ItemType] = "Extra"
    shop_slot_byte: int = field(init=False)
    shop_slot_bit_mask: int = field(init=False)

    def __post_init__(self):
        object.__setattr__(self, "shop_slot_byte", self.extra_number // 8)
        object.__setattr__(self, "shop_slot_bit_mask", 1 << (self.extra_number % 8))

    @property
    def purchase_location_name(self) -> str:
        if self.level_shortname:
            return f"Purchase {self.name} ({self.level_shortname})"
        else:
            return f"Purchase {self.name}"


@dataclass(frozen=True)
class NonPowerBrickExtraData(ExtraData):
    studs_cost: int

    def __post_init__(self):
        super().__post_init__()
        if self.level_shortname is not None:
            raise ValueError("NonPowerBrickExtraData should not have a level_shortname set.")


# Purchasable characters and how they are unlocked, in the order they appear in the shop.
# See the order of characters in COLLECTION.TXT that use "buy_in_shop", plus Indiana Jones, who is special.
CHARACTER_SHOP_SLOTS: dict[str, tuple[str | None, int]] = {
    "Gonk Droid": (None, 3000),
    "PK Droid": (None, 1500),

    # Episode 1
    "Battle Droid": ("1-1", 6500),
    "Battle Droid (Security)": ("1-1", 8500),
    "Battle Droid (Commander)": ("1-1", 10_000),
    "Droideka": ("1-1", 40_000),

    "Captain Tarpals": ("1-2", 17_500),
    "Boss Nass": ("1-2", 15_000),

    "Royal Guard": ("1-3", 10_000),
    "Padmé": ("1-3", 20_000),

    "Watto": ("1-4", 16_000),
    "Pit Droid": ("1-4", 4000),

    # No non-vehicle characters for 1-5

    "Darth Maul": ("1-6", 60_000),

    # Episode 2
    "Zam Wesell": ("2-1", 27_500),
    "Dexter Jettster": ("2-1", 10_000),

    "Clone": ("2-2", 13_000),
    "Lama Su": ("2-2", 9000),
    "Taun We": ("2-2", 9000),

    "Geonosian": ("2-3", 20_000),
    "Battle Droid (Geonosis)": ("2-3", 8500),

    "Super Battle Droid": ("2-4", 25_000),
    "Jango Fett": ("2-4", 70_000),
    "Boba Fett (Boy)": ("2-4", 5500),
    "Luminara": ("2-4", 28_000),
    "Ki-Adi Mundi": ("2-4", 30_000),
    "Kit Fisto": ("2-4", 35_000),
    "Shaak Ti": ("2-4", 36_000),
    "Aayla Secura": ("2-4", 37_000),
    "Plo Koon": ("2-4", 39_000),

    # No non-vehicle characters for 2-5 or 2-6

    # Episode 3
    # No non-vehicle characters for 3-1

    "Count Dooku": ("3-2", 100_000),
    "Grievous' Bodyguard": ("3-2", 42_000),

    "General Grievous": ("3-3", 70_000),

    "Wookiee": ("3-4", 16_000),
    "Clone (Episode III)": ("3-4", 10_000),
    "Clone (Episode III, Pilot)": ("3-4", 11_000),
    "Clone (Episode III, Swamp)": ("3-4", 12_000),
    "Clone (Episode III, Walker)": ("3-4", 12_000),

    "Mace Windu (Episode III)": ("3-5", 38_000),
    "Disguised Clone": ("3-5", 12_000),

    # No non-vehicle characters for 3-6

    # Episode 4
    "Rebel Trooper": ("4-1", 10_000),
    "Stormtrooper": ("4-1", 10_000),
    "Imperial Shuttle Pilot": ("4-1", 25_000),

    "Tusken Raider": ("4-2", 23_000),
    "Jawa": ("4-2", 24_000),

    "Sandtrooper": ("4-3", 14_000),
    "Greedo": ("4-3", 60_000),
    "Imperial Spy": ("4-3", 13_500),

    "Beach Trooper": ("4-4", 20_000),
    "Death Star Trooper": ("4-4", 19_000),
    "TIE Fighter Pilot": ("4-4", 21_000),
    "Imperial Officer": ("4-4", 28_000),
    "Grand Moff Tarkin": ("4-4", 38_000),

    # No non-vehicle characters for 4-5 or 4-6

    # Episode 5
    # No non-vehicle characters for 5-1

    "Han Solo (Hood)": ("5-2", 20_000),
    "Rebel Trooper (Hoth)": ("5-2", 16_000),
    "Rebel Pilot": ("5-2", 15_000),
    "Snowtrooper": ("5-2", 16_000),
    "Luke Skywalker (Hoth)": ("5-2", 14_000),

    # No non-vehicle characters for 5-3, 5-4 or 5-5

    "Lobot": ("5-6", 11_000),
    "Ugnaught": ("5-6", 36_000),
    "Bespin Guard": ("5-6", 15_000),
    "Princess Leia (Prisoner)": ("5-6", 22_000),

    # Episode 6
    "Gamorrean Guard": ("6-1", 40_000),
    "Bib Fortuna": ("6-1", 16_000),
    "Palace Guard": ("6-1", 14_000),
    "Bossk": ("6-1", 75_000),

    "Skiff Guard": ("6-2", 12_000),
    "Boba Fett": ("6-2", 100_000),

    # No non-vehicle characters for 6-3

    "Ewok": ("6-4", 34_000),

    "Imperial Guard": ("6-5", 45_000),
    "The Emperor": ("6-5", 275_000),

    "Admiral Ackbar": ("6-6", 33_000),

    # All Episodes complete
    "IG-88": ("ALL_EPISODES", 100_000),
    "Dengar": ("ALL_EPISODES", 70_000),
    "4-LOM": ("ALL_EPISODES", 45_000),
    "Ben Kenobi (Ghost)": ("ALL_EPISODES", 1_100_000),
    "Anakin Skywalker (Ghost)": ("ALL_EPISODES", 1_000_000),
    "Yoda (Ghost)": ("ALL_EPISODES", 1_200_000),
    "R2-Q5": ("ALL_EPISODES", 100_000),

    # Watch Indiana Jones trailer
    "Indiana Jones": ("INDY_TRAILER", 50_000),

    # Episode 1 Vehicles
    "Sebulba's Pod": ("1-4", 20000),

    # Episode 2 Vehicles
    "Zam's Airspeeder": ("2-1", 24000),

    # Episode 3 Vehicles
    "Droid Trifighter": ("3-1", 28000),
    "Vulture Droid": ("3-1", 30000),
    "Clone Arcfighter": ("3-1", 33000),

    # Episode 4 Vehicles
    "TIE Fighter": ("4-6", 35000),
    "TIE Interceptor": ("4-6", 40000),
    "TIE Fighter (Darth Vader)": ("4-6", 50000),

    # Episode 5 Vehicles
    "TIE Bomber": ("5-3", 60000),
    "Imperial Shuttle": ("5-3", 25000),
}


def _make_shop_slot_requirement_to_unlocks() -> Mapping[str | None, Mapping[str, int]]:
    d: dict[str | None, dict[str, int]] = {}
    for character_name, (unlock_requirement, studs_cost) in CHARACTER_SHOP_SLOTS.items():
        if unlock_requirement not in d:
            names: dict[str, int] = {}
            d[unlock_requirement] = names
        else:
            names = d[unlock_requirement]
        names[character_name] = studs_cost

    return d


SHOP_SLOT_REQUIREMENT_TO_UNLOCKS: Mapping[str | None, Mapping[str, int]] = (
    _make_shop_slot_requirement_to_unlocks()
)
del _make_shop_slot_requirement_to_unlocks

CHARACTER_TO_SHOP_SLOT = {name: i for i, name in enumerate(CHARACTER_SHOP_SLOTS.keys())}


_generic = GenericItemData
_char = CharacterData
_vehicle = VehicleData
_extra = ExtraData

COMMON_NORMAL_JUMP_HEIGHT = CAN_BARELY_JUMP | CAN_JUMP_HEIGHT_0_37

COMMON_PACIFIST_NON_DROID = (
        CAN_BUILD_BRICKS
        | CAN_PULL_LEVERS
        | CAN_PUSH_OBJECTS
        | COMMON_NORMAL_JUMP_HEIGHT
        | CAN_JUMP_DISTANCE_0_69
        | CAN_RIDE_VEHICLES
)
COMMON_SHORT_SLOW = (
    CAN_BUILD_BRICKS
    | CAN_PULL_LEVERS
    | CAN_PUSH_OBJECTS
    | COMMON_NORMAL_JUMP_HEIGHT
    | CAN_RIDE_VEHICLES
    | SHORTIE
)

COMMON_NORMAL_SPEED_PACIFIST_NON_DROID = COMMON_PACIFIST_NON_DROID | CAN_JUMP_DISTANCE_0_69
# TODO: Remove explicit marking of jump height, and deduce it from the jump_height attribute instead.
COMMON_CAN_JUMP_SLIGHTLY_HIGHER = COMMON_NORMAL_JUMP_HEIGHT | CAN_JUMP_0_44 | CAN_JUMP_DISTANCE_0_69
COMMON_HIGH_JUMP = CAN_JUMP_0_44 | CAN_DOUBLE_JUMP | HIGH_JUMP
COMMON_HIGH_JUMP_SLAM = COMMON_HIGH_JUMP | CAN_HIGH_JUMP_SLAM | CAN_MELEE | CAN_DEFLECT_BOLTS

COMMON_MELEE_NON_DROID = COMMON_PACIFIST_NON_DROID | CAN_MELEE
COMMON_MELEE_NON_DROID_HIGHER_JUMP = COMMON_MELEE_NON_DROID | CAN_JUMP_0_44
COMMON_BLASTER_NON_DROID = COMMON_PACIFIST_NON_DROID | BLASTER
COMMON_HATLESS_NON_DROID = COMMON_PACIFIST_NON_DROID | CAN_WEAR_HAT
COMMON_HATLESS_MELEE_NON_DROID = COMMON_MELEE_NON_DROID | CAN_WEAR_HAT
COMMON_HATLESS_MELEE_NON_DROID_HIGHER_JUMP = COMMON_HATLESS_MELEE_NON_DROID | CAN_JUMP_0_44
COMMON_HATLES_PACIFIST_NON_DROID = COMMON_PACIFIST_NON_DROID | CAN_WEAR_HAT
COMMON_JEDI = JEDI | COMMON_PACIFIST_NON_DROID | CAN_DOUBLE_JUMP | CAN_TRIPLE_JUMP_GREAT_DISTANCE | IS_NON_GHOST_JEDI
COMMON_SITH = COMMON_JEDI | SITH

COMMON_GRAPPLE = GRAPPLE | BLASTER
COMMON_BOUNTY_HUNTER = BOUNTY_HUNTER | COMMON_GRAPPLE | CAN_MELEE
COMMON_JETPACK = HOVER | JETPACK | CAN_JUMP_0_44
COMMON_NON_DROID_BOUNTY_HUNTER = COMMON_BOUNTY_HUNTER | COMMON_PACIFIST_NON_DROID
COMMON_JETPACK_BOUNTY_HUNTER = COMMON_NON_DROID_BOUNTY_HUNTER | COMMON_JETPACK

MIXIN_FORCE_GHOST = ~(CAN_AGGRAVATE_ENEMIES | IS_NON_GHOST_JEDI | CAN_DEFLECT_BOLTS)


def generic_jedi(ap_id: int, name: str, character_id: int, already_got_hat: bool = False, is_ghost: bool = False):
    abilities = COMMON_JEDI
    if not already_got_hat:
        abilities |= CAN_WEAR_HAT
    if is_ghost:
        abilities &= MIXIN_FORCE_GHOST
        alignment = Alignment.PASSIVE
    else:
        alignment = Alignment.GOOD
    return CharacterData(ap_id, name, character_id, abilities, 1.2, 0.44, 0.92, alignment)


def generic_sith(ap_id: int, name: str, character_id: int, already_got_hat: bool = False, imperial: bool = False):
    abilities = COMMON_SITH
    if imperial:
        abilities |= IMPERIAL
    if not already_got_hat:
        abilities |= CAN_WEAR_HAT
    return CharacterData(ap_id, name, character_id, abilities, 1.2, 0.44, 0.92, Alignment.EVIL)


def generic_astromech(ap_id: int, name: str, character_id: int):
    abilities = ASTROMECH_PANEL | HOVER | ASTROMECH_DROID | CAN_BARELY_JUMP | CAN_SELF_DESTRUCT | WEAPON_ZAPPER
    # todo?: Use hover time to determine jump distance instead of using the calculated value for their barely jump?
    return CharacterData(ap_id, name, character_id, abilities, 1.0, 0.11, 0.41, Alignment.PASSIVE)


def generic_clone(ap_id: int, name: str, character_id: int):
    abilities = IMPERIAL | COMMON_GRAPPLE | COMMON_PACIFIST_NON_DROID
    return CharacterData(ap_id, name, character_id, abilities, 1.0, 0.37, 0.7, Alignment.EVIL)


def generic_officer(ap_id: int, name: str, character_id: int, already_got_hat: bool = False):
    abilities = IMPERIAL | COMMON_GRAPPLE | COMMON_HATLESS_MELEE_NON_DROID
    if not already_got_hat:
        abilities |= CAN_WEAR_HAT
    return CharacterData(ap_id, name, character_id, abilities, 1.2, 0.44, 0.92, Alignment.EVIL)


def generic_lando(ap_id: int, name: str, character_id: int, already_got_hat: bool = False):
    abilities = COMMON_GRAPPLE | COMMON_MELEE_NON_DROID
    if not already_got_hat:
        abilities |= CAN_WEAR_HAT
    return CharacterData(ap_id, name, character_id, abilities, 1.18, 0.44, 0.90413, Alignment.GOOD)


def generic_padme(ap_id: int, name: str, character_id: int):
    abilities = COMMON_GRAPPLE | COMMON_HATLESS_MELEE_NON_DROID
    return CharacterData(ap_id, name, character_id, abilities, 1.2, 0.37, 0.84, Alignment.GOOD)


def generic_solo(ap_id: int, name: str, character_id: int):
    # todo: ViolaGuy's standalone TCS randomizer I think has some logic involving the roll that Han Solo can do.
    abilities = COMMON_GRAPPLE | COMMON_HATLESS_MELEE_NON_DROID
    return CharacterData(ap_id, name, character_id, abilities, 1.2, 0.37, 0.84, Alignment.GOOD)


def generic_leia(ap_id: int, name: str, character_id: int, already_got_hat: bool = False):
    abilities = COMMON_GRAPPLE | COMMON_MELEE_NON_DROID
    if not already_got_hat:
        abilities |= CAN_WEAR_HAT
    return CharacterData(ap_id, name, character_id, abilities, 1.2, 0.44, 0.92, Alignment.GOOD)


def generic_stormtrooper(ap_id: int, name: str, character_id: int):
    abilities = IMPERIAL | COMMON_GRAPPLE | COMMON_PACIFIST_NON_DROID | CAN_FLOP_JUMP
    return CharacterData(ap_id, name, character_id, abilities, 1.2, 0.44, 0.92, Alignment.EVIL)


def generic_rebel(ap_id: int, name: str, character_id: int):
    abilities = COMMON_GRAPPLE | COMMON_MELEE_NON_DROID
    return CharacterData(ap_id, name, character_id, abilities, 1.2, 0.44, 0.92, Alignment.GOOD)


def generic_greedo(ap_id: int, name: str, character_id: int):
    abilities = COMMON_BOUNTY_HUNTER | COMMON_MELEE_NON_DROID
    return CharacterData(ap_id, name, character_id, abilities, 1.2, 0.44, 0.92, Alignment.EVIL)


def generic_kaminoan(ap_id: int, name: str, character_id: int):
    abilities = COMMON_PACIFIST_NON_DROID
    return CharacterData(ap_id, name, character_id, abilities, 1.2, 0.37, 0.84, Alignment.NEUTRAL)


def generic_skiff_guard(ap_id: int, name: str, character_id: int, already_got_hat: bool = False):
    abilities = COMMON_GRAPPLE | COMMON_PACIFIST_NON_DROID
    if not already_got_hat:
        abilities |= CAN_WEAR_HAT
    return CharacterData(ap_id, name, character_id, abilities, 1.2, 0.44, 0.92, Alignment.EVIL)


def generic_battle_droid(ap_id: int, name: str, character_id: int):
    abilities = BLASTER | CAN_SELF_DESTRUCT
    return CharacterData(ap_id, name, character_id, abilities, 1.2, 0.0, 0.0, Alignment.EVIL)


def generic_yoda(ap_id: int, name: str, character_id: int, is_ghost: bool = False):
    # Yoda's low base movement speed greatly reduces his triple jump horizontal distance, so he cannot
    # CAN_TRIPLE_JUMP_GREAT_DISTANCE.
    abilities = JEDI | COMMON_MELEE_NON_DROID | CAN_DOUBLE_JUMP | CAN_DEFLECT_BOLTS | IS_NON_GHOST_JEDI
    if is_ghost:
        abilities &= MIXIN_FORCE_GHOST
        alignment = Alignment.PASSIVE
    else:
        alignment = Alignment.GOOD
    # todo: what is the effective run_speed with the lightsaber out?
    return CharacterData(ap_id, name, character_id, abilities, 0.8, 0.44, 0.6133333, alignment)


def generic_ewok(ap_id: int, name: str, character_id: int):
    abilities = WEAPON_EWOK | COMMON_SHORT_SLOW | CAN_JUMP_0_44
    return CharacterData(ap_id, name, character_id, abilities, 0.9, 0.44, 0.69, Alignment.GOOD)


def generic_protocol_droid(ap_id: int, name: str, character_id: int):
    abilities = PROTOCOL_PANEL | CAN_SELF_DESTRUCT
    return CharacterData(ap_id, name, character_id, abilities, 0.75, 0.0, 0.0, Alignment.PASSIVE)


def generic_wookie(ap_id: int, name: str, character_id: int):
    # Wookies can specially wear hats.
    abilities = COMMON_GRAPPLE | COMMON_HATLESS_MELEE_NON_DROID
    return CharacterData(ap_id, name, character_id, abilities, 1.2, 0.37, 0.84, Alignment.GOOD)


def generic_luke(ap_id: int, name: str, character_id: int, already_got_hat: bool = False):
    """Non-Jedi Luke specifically."""
    abilities = COMMON_GRAPPLE | COMMON_MELEE_NON_DROID
    if not already_got_hat:
        abilities |= CAN_WEAR_HAT
    return CharacterData(ap_id, name, character_id, abilities, 1.2, 0.44, 0.92, Alignment.GOOD)


def generic_geonosian(ap_id: int, name: str, character_id: int, abilities: CharacterAbility, alignment: Alignment):
    # Calculated jump distance is 1.2, but it's more like 0.75 or so.
    # Geonosian gets a jump, and then hovers slightly above the ground, which grants extra height.
    # Jump Distance:
    #  I could get across larger gaps, without elevation changes, than
    #  - run_speed=1.0, jump_speed=2.1, air_gravity=-6.0 -> jump_distance=0.7 (Clone).
    #  I could not get across as large gaps, without elevation changes, as
    #  - run_speed=1.32, jump_speed=2.4, air_gravity=-7.0 -> jump_distance=0.9 (Captain Tarpals)
    #  - run_speed=1.2, jump_speed=2.1, air_gravity=-6.0 -> jump_distance=0.84 (Padmé)
    #  - run_speed=1.0, jump_speed=2.3, air_gravity=-6.0 -> jump_distance=0.77777 (Dexter Jettster)
    #  Without elevation changes, I'm guessing the Geonosian jump_distance is around 0.75.
    #  There is an issue with gaps that have elevation changes however, since the flutter effect can quickly fall
    #  downwards. For example, on 3-6, in the lava platforming section, there is a jump from rib-like platforms to
    #  individual sinking platforms, and while Ewok (jump_distance=0.69) can barely make it to the first platform,
    #  Geonosian cannot. Geonosian does not seem far off from being able to make this jump, however, so I have given
    #  Geonosian a jump_distance of 0.65.
    # Jump Height:
    #  I could not jump as high as 4-LOM (0.37 jump height) and the only other characters that can jump worse are
    #  Astromech Droids.
    #  Geonosian can make it up the first two force steps in 3-3 (spawned by destroying the second explosives),
    #  Astromech Droids are not even close. These steps have about 0.3 y distance between them.
    return CharacterData(ap_id, name, character_id, abilities, 1.5, 0.3, 0.65)


ITEM_DATA: list[GenericItemData] = [
    generic_jedi(177, "Obi-Wan Kenobi", 1),
    # There is a second, incorrect Zam Wesell at 305
    _char(58, "Zam Wesell", 2, COMMON_BOUNTY_HUNTER | COMMON_MELEE_NON_DROID, 1.4, 0.4, 1.112, Alignment.EVIL),
    generic_sith(112, "The Emperor", 6, True, True),
    _char(109, "Boba Fett", 7, COMMON_JETPACK_BOUNTY_HUNTER, 1.2, 0.44, 0.92, Alignment.EVIL),
    generic_astromech(6, "R2-D2", 8),
    _char(87, "Tusken Raider", 9, COMMON_GRAPPLE | COMMON_HATLESS_MELEE_NON_DROID, 1.2, 0.44, 0.92, Alignment.EVIL),
    generic_yoda(15, "Yoda", 10),
    generic_protocol_droid(12, "C-3PO", 12),
    generic_rebel(84, "Rebel Trooper", 13),
    generic_officer(95, "Imperial Officer", 14, True),
    generic_wookie(20, "Chewbacca", 16),
    _char(46, "Gonk Droid", 17, CAN_SELF_DESTRUCT, 0.12, 0.0, 0.0, Alignment.PASSIVE),
    generic_stormtrooper(85, "Stormtrooper", 20),
    _char(88, "Jawa", 22, SHORTIE | COMMON_PACIFIST_NON_DROID | WEAPON_ZAPPER, 0.9, 0.44, 0.69, Alignment.EVIL),
    generic_leia(21, "Princess Leia", 23),
    generic_leia(30, "Princess Leia (Hoth)", 24),
    generic_jedi(33, "Luke Skywalker (Bespin)", 25),
    generic_jedi(39, "Luke Skywalker (Endor)", 26, True),
    generic_jedi(35, "Luke Skywalker (Jedi)", 27),
    generic_luke(24, "Luke Skywalker (Tatooine)", 28),
    generic_luke(27, "Luke Skywalker (Stormtrooper)", 29),
    generic_solo(26, "Han Solo", 33),
    generic_solo(28, "Han Solo (Stormtrooper)", 34),
    generic_lando(44, "Lando Calrissian", 35),
    generic_sith(43, "Darth Vader", 40, True, True),
    generic_stormtrooper(92, "Beach Trooper", 48),
    generic_stormtrooper(100, "Snowtrooper", 45),
    generic_stormtrooper(93, "Death Star Trooper", 49),
    generic_stormtrooper(94, "TIE Fighter Pilot", 50),
    generic_stormtrooper(89, "Sandtrooper", 51),
    generic_officer(86, "Imperial Shuttle Pilot", 53, True),
    generic_jedi(25, "Ben Kenobi", 56),
    # Has special hair that apparently counts as a hat.
    generic_leia(45, "Princess Leia (Bespin)", 57, True),
    generic_rebel(99, "Rebel Pilot", 58),
    _char(66, "Jango Fett", 59, COMMON_JETPACK_BOUNTY_HUNTER, 1.2, 0.44, 0.92, Alignment.EVIL),
    # Can build for some reason???
    _char(76, "General Grievous", 60,
          COMMON_HIGH_JUMP_SLAM | CAN_BUILD_BRICKS | CAN_TRIPLE_JUMP_GREAT_DISTANCE,
          1.2, 0.65, 1.12, Alignment.EVIL),
    generic_sith(57, "Darth Maul", 61, True),
    generic_jedi(13, "Mace Windu", 62),
    generic_jedi(82, "Mace Windu (Episode III)", 63),
    _char(75, "Grievous' Bodyguard", 64, COMMON_HIGH_JUMP_SLAM, 1.4, 1.44, 1.6, Alignment.EVIL),
    _char(51, "Droideka", 65, BLASTER | CAN_SELF_DESTRUCT, 1.8, 0.0, 0.0, Alignment.EVIL),
    generic_astromech(9, "R4-P17", 66),
    generic_battle_droid(48, "Battle Droid", 67),
    generic_battle_droid(50, "Battle Droid (Commander)", 68),
    generic_battle_droid(64, "Battle Droid (Geonosis)", 69),
    generic_battle_droid(49, "Battle Droid (Security)", 70),
    generic_protocol_droid(178, "TC-14", 71),
    generic_wookie(77, "Wookiee", 72),
    _char(18, "Chancellor Palpatine", 73, COMMON_HATLES_PACIFIST_NON_DROID, 1.2, 0.37, 0.84, Alignment.GOOD),
    generic_jedi(16, "Obi-Wan Kenobi (Episode III)", 74),
    generic_jedi(8, "Obi-Wan Kenobi (Jedi Master)", 75),
    generic_padme(120, "Padmé", 76),
    generic_padme(5, "Padmé (Battle)", 77),
    generic_padme(14, "Padmé (Clawed)", 78),
    generic_padme(11, "Padmé (Geonosis)", 79),
    _char(3, "Queen Amidala", 80, COMMON_GRAPPLE | COMMON_MELEE_NON_DROID, 1.2, 0.37, 0.84, Alignment.GOOD),
    _char(65, "Super Battle Droid", 81, BLASTER | CAN_SELF_DESTRUCT, 1.07, 0.0, 0.0, Alignment.EVIL),
    generic_jedi(69, "Ki-Adi Mundi", 82, True),
    generic_jedi(70, "Kit Fisto", 83, True),
    generic_jedi(68, "Luminara", 84, True),
    generic_jedi(71, "Shaak Ti", 85, True),
    generic_clone(60, "Clone", 86),
    generic_clone(78, "Clone (Episode III)", 87),
    generic_clone(79, "Clone (Episode III, Pilot)", 88),
    generic_clone(19, "Commander Cody", 89),
    generic_clone(80, "Clone (Episode III, Swamp)", 90),
    generic_clone(81, "Clone (Episode III, Walker)", 91),
    generic_clone(83, "Disguised Clone", 92),
    _char(7, "Anakin Skywalker (Boy)", 93, SHORTIE | COMMON_HATLES_PACIFIST_NON_DROID, 1.2, 0.37, 0.84, Alignment.GOOD),
    _char(67, "Boba Fett (Boy)", 94, COMMON_SHORT_SLOW, 0.8, 0.37, 0.56, Alignment.EVIL),
    # Cannot build.
    # Like Watto, they cannot jump normally, but fly instead, with similar jump distance to Ewok.
    # TODO: Find something that another 0.4 height user can just barely get onto, or otherwise figure out the effective
    #  jump height for Geonosian.
    generic_geonosian(63, "Geonosian", 95,
                      CAN_PULL_LEVERS | CAN_PUSH_OBJECTS | CAN_RIDE_VEHICLES | BLASTER | CAN_JUMP_HEIGHT_0_37,
                      Alignment.EVIL),
    generic_jedi(17, "Anakin Skywalker (Jedi)", 96),
    generic_jedi(10, "Anakin Skywalker (Padawan)", 97),
    _char(4, "Captain Panaka", 98, COMMON_GRAPPLE | COMMON_MELEE_NON_DROID, 1.2, 0.37, 0.84, Alignment.GOOD),
    # Jar Jar has a vanilla bug where there is a typo in the lever pulling animation, which prevents Jar Jar, and
    # Gungans based on him, from being able to pull levers.
    _char(2, "Jar Jar Binks", 99,
          COMMON_HIGH_JUMP
          | CAN_BUILD_BRICKS
          | CAN_PUSH_OBJECTS
          | CAN_RIDE_VEHICLES
          | CAN_AGGRAVATE_ENEMIES,
          1.32, 0.41, 0.905, Alignment.GOOD),
    _char(47, "PK Droid", 100, CAN_SELF_DESTRUCT, 0.8285375, 0.0, 0.0, Alignment.PASSIVE),
    _char(54, "Royal Guard", 101, COMMON_GRAPPLE | COMMON_PACIFIST_NON_DROID, 1.2, 0.37, 0.84, Alignment.GOOD),
    # Crazy jump height on such an unassuming character!
    _char(104, "Gamorrean Guard", 102, COMMON_MELEE_NON_DROID | CAN_DEFLECT_BOLTS, 0.75, 0.53, 0.69, Alignment.EVIL),
    generic_sith(74, "Count Dooku", 103, False, False),
    generic_jedi(176, "Qui-Gon Jinn", 104),
    generic_rebel(98, "Rebel Trooper (Hoth)", 107),
    generic_leia(34, "Princess Leia (Boushh)", 129),
    generic_officer(96, "Grand Moff Tarkin", 131),
    generic_solo(36, "Han Solo (Skiff)", 141),
    # Can wear hats despite the hood.
    generic_solo(97, "Han Solo (Hood)", 142),
    generic_solo(29, "Han Solo (Hoth)", 143),
    # TODO: From the extracted data, Luke Skywalker (Pilot) does not already have a hat?
    generic_luke(31, "Luke Skywalker (Pilot)", 156, True),
    generic_jedi(32, "Luke Skywalker (Dagobah)", 157),
    _char(102, "Ugnaught", 158, COMMON_SHORT_SLOW | WEAPON_ZAPPER, 0.9, 0.44, 0.69, Alignment.EVIL),
    generic_leia(38, "Princess Leia (Slave)", 161),
    generic_leia(40, "Princess Leia (Endor)", 162, True),
    # Custom characters can only use unlocked character equipment, besides some blasters. They do not get access to
    # lightsabers/force unless Jedi are unlocked.
    _char(188, "STRANGER 1", 168, COMMON_GRAPPLE | COMMON_HATLESS_MELEE_NON_DROID, 1.2, 0.44, 0.92, Alignment.GOOD),
    _char(189, "STRANGER 2", 169, COMMON_GRAPPLE | COMMON_HATLESS_MELEE_NON_DROID, 1.2, 0.44, 0.92, Alignment.GOOD),
    generic_greedo(90, "Greedo", 171),
    # GOOD alignment for some reason.
    _char(91, "Imperial Spy", 172, COMMON_PACIFIST_NON_DROID, 1.2, 0.44, 0.92, Alignment.GOOD),
    # GOOD alignment for some reason.
    _char(105, "Bib Fortuna", 185, COMMON_MELEE_NON_DROID, 1.2, 0.44, 0.92, Alignment.GOOD),
    generic_skiff_guard(108, "Skiff Guard", 186),
    generic_rebel(23, "Rebel Friend", 190),
    _char(101, "Lobot", 192, COMMON_HATLESS_MELEE_NON_DROID, 1.2, 0.44, 0.92, Alignment.GOOD),
    _char(103, "Bespin Guard", 193, COMMON_GRAPPLE | COMMON_MELEE_NON_DROID, 1.2, 0.44, 0.92, Alignment.GOOD),
    _char(111, "Imperial Guard", 194,
          IMPERIAL | COMMON_MELEE_NON_DROID | CAN_DEFLECT_BOLTS,
          1.2, 0.44, 0.92, Alignment.EVIL),
    generic_jedi(117, "Ben Kenobi (Ghost)", 195, False, True),
    # TODO: Check if Palace Guard can actually Melee, I suspect not.
    generic_skiff_guard(106, "Palace Guard", 196, True),
    _char(114, "IG-88", 197,
          COMMON_BOUNTY_HUNTER
          | ASTROMECH_PANEL
          | PROTOCOL_PANEL
          | CAN_PUSH_OBJECTS
          | CAN_JUMP_HEIGHT_0_37
          | CAN_RIDE_VEHICLES
          | CAN_MELEE,
          1.2, 0.44, 0.92, Alignment.EVIL),
    generic_ewok(110, "Ewok", 199),
    generic_lando(37, "Lando (Palace Guard)", 201, True),
    generic_luke(121, "Luke Skywalker (Hoth)", 204, True),
    generic_leia(163, "Princess Leia (Prisoner)", 205),
    generic_solo(41, "Han Solo (Endor)", 206),
    generic_rebel(22, "Captain Antilles", 207),
    _char(113, "Admiral Ackbar", 211, COMMON_GRAPPLE | COMMON_PACIFIST_NON_DROID, 1.2, 0.44, 0.92, Alignment.GOOD),
    generic_greedo(107, "Bossk", 212),
    generic_greedo(115, "Dengar", 213),
    generic_ewok(42, "Wicket", 223),
    # Lower jump height than IG-88.
    _char(116, "4-LOM", 225,
          COMMON_BOUNTY_HUNTER
          | ASTROMECH_PANEL
          | PROTOCOL_PANEL
          | CAN_PUSH_OBJECTS
          | CAN_JUMP_HEIGHT_0_37
          | CAN_RIDE_VEHICLES
          | CAN_MELEE,
          1.2, 0.37, 0.84, Alignment.EVIL),
    generic_jedi(161, "Anakin Skywalker (Ghost)", 226, False, True),
    generic_yoda(118, "Yoda (Ghost)", 227, True),
    _char(53, "Boss Nass", 254, COMMON_PACIFIST_NON_DROID, 1.0, 0.37, 0.7, Alignment.GOOD),
    _char(56, "Pit Droid", 268, CAN_SELF_DESTRUCT, 0.8, 0.0, 0.0, Alignment.PASSIVE),
    # Cannot build.
    generic_geonosian(55, "Watto", 269,
                      CAN_PULL_LEVERS | CAN_PUSH_OBJECTS | CAN_RIDE_VEHICLES | WEAPON_ZAPPER | CAN_JUMP_HEIGHT_0_37,
                      Alignment.GOOD),
    # Due to being based on Jar Jar, he cannot pull levers.
    _char(52, "Captain Tarpals", 276,
          COMMON_HIGH_JUMP
          | CAN_BUILD_BRICKS
          | CAN_PUSH_OBJECTS
          | CAN_RIDE_VEHICLES
          | CAN_MELEE
          | CAN_DEFLECT_BOLTS,
          1.32, 0.41, 0.905, Alignment.GOOD),
    generic_kaminoan(61, "Lama Su", 280),
    generic_kaminoan(62, "Taun We", 281),
    _char(59, "Dexter Jettster", 304, COMMON_PACIFIST_NON_DROID, 1.0, 0.44, 0.76666, Alignment.GOOD),
    generic_astromech(119, "R2-Q5", 314),
    generic_jedi(72, "Aayla Secura", 315, True),
    generic_jedi(73, "Plo Koon", 316, True),
    # TODO: Check he can wear hats.
    generic_solo(162, "Indiana Jones", 317),

    _vehicle(174, "Anakin's Speeder", 3, VEHICLE_BLASTER, 16.0),
    _vehicle(207, "Slave 1", 11, VEHICLE_BLASTER, 24.0),
    _vehicle(173, "Snowspeeder", 32, VEHICLE_TOW | VEHICLE_BLASTER, 18.0),
    _vehicle(169, "X-wing", 36, VEHICLE_BLASTER, 24.0),
    _vehicle(195, "TIE Fighter", 37, VEHICLE_BLASTER | VEHICLE_TIE, 24.0),
    _vehicle(171, "Millennium Falcon", 38, VEHICLE_BLASTER, 24.0),
    _vehicle(170, "Y-wing", 39, VEHICLE_BLASTER, 24.0),
    _vehicle(172, "TIE Interceptor", 128, VEHICLE_TIE | VEHICLE_BLASTER, 24.0),
    _vehicle(196, "TIE Fighter (Darth Vader)", 182, VEHICLE_BLASTER | VEHICLE_TIE, 24.0),
    _vehicle(198, "Imperial Shuttle", 198, VEHICLE_BLASTER, 24.0),
    _vehicle(197, "TIE Bomber", 209, VEHICLE_BLASTER | VEHICLE_TIE, 24.0),
    _vehicle(167, "Jedi Starfighter (Yellow)", 221, VEHICLE_BLASTER, 21.0),
    _vehicle(164, "Anakin's Pod", 259, IS_A_VEHICLE, 30.0),
    _vehicle(190, "Sebulba's Pod", 261, IS_A_VEHICLE, 30.0),
    _vehicle(165, "Naboo Starfighter", 272, VEHICLE_TOW | VEHICLE_BLASTER, 20.0),
    _vehicle(191, "Zam's Airspeeder", 277, VEHICLE_BLASTER, 16.0),
    _vehicle(166, "Republic Gunship", 285, VEHICLE_TOW | VEHICLE_BLASTER, 18.0),
    _vehicle(192, "Droid Trifighter", 292, VEHICLE_BLASTER, 21.0),
    _vehicle(193, "Vulture Droid", 293, VEHICLE_BLASTER, 21.0),
    _vehicle(194, "Clone Arcfighter", 295, VEHICLE_BLASTER, 24.0),
    _vehicle(168, "Jedi Starfighter (Red)", 291, VEHICLE_BLASTER, 21.0),

    _extra(122, "Super Gonk", 0x8, "1-1", 699),
    _extra(123, "Poo Money", 0x9, "1-2", 296),  # "Fertilizer" in manual
    _extra(124, "Walkie Talkie Disable", 0xA, "1-3", 1665),
    _extra(125, "Power Brick Detector", 0xB, "1-4", 1657),
    _extra(126, "Super Slap", 0xC, "1-5", 1658),
    _extra(127, "Force Grapple Leap", 0xD, "1-6", 1660),
    _extra(128, "Stud Magnet", 0xE, "2-1", 297),
    _extra(129, "Disarm Troopers", 0xF, "2-2", 1662),
    _extra(130, "Character Studs", 0x10, "2-3", 1671),
    _extra(131, "Perfect Deflect", 0x11, "2-4", 1666),
    _extra(132, "Exploding Blaster Bolts", 0x12, "2-5", 1663),
    _extra(133, "Force Pull", 0x13, "2-6", 1667),
    _extra(134, "Vehicle Smart Bomb", 0x14, "3-1", 1664),
    _extra(135, "Super Astromech", 0x15, "3-2", 1668),
    _extra(136, "Super Jedi Slam", 0x16, "3-3", 1670),
    _extra(137, "Super Thermal Detonator", 0x17, "3-4", 1661),
    _extra(138, "Deflect Bolts", 0x18, "3-5", 1659),
    _extra(139, "Dark Side", 0x19, "3-6", 1669),
    _extra(140, "Super Blasters", 0x1A, "4-1", 682),
    _extra(141, "Fast Force", 0x1B, "4-2", 685),
    _extra(142, "Super Lightsabers", 0x1C, "4-3", 667),
    _extra(143, "Tractor Beam", 0x1D, "4-4", 687),
    _extra(144, "Invincibility", 0x1E, "4-5", 664),
    _extra(-1, "Score x2", 0x1F, "4-6", 666),
    _extra(146, "Self Destruct", 0x20, "5-1", 681),
    _extra(147, "Fast Build", 0x21, "5-2", 684),
    _extra(-1, "Score x4", 0x22, "5-3" ,670),
    _extra(148, "Regenerate Hearts", 0x23, "5-4", 683),
    _extra(149, "Minikit Detector", 0x24, "5-6", 665),
    _extra(-1, "Score x6", 0x25, "5-5", 676),
    _extra(150, "Super Zapper", 0x26, "6-1", 688),
    _extra(151, "Bounty Hunter Rockets", 0x27, "6-2", 673),
    _extra(-1, "Score x8", 0x28, "6-3", 679),
    _extra(152, "Super Ewok Catapult", 0x29, "6-4", 689),
    _extra(153, "Infinite Torpedos", 0x2A, "6-6", 686),
    _extra(-1, "Score x10", 0x2B, "6-5", 680),
    _extra(-1, "Adaptive Difficulty", 0x2C, None, 690),  # Effectively a difficulty setting, so not randomized.

    NonPowerBrickExtraData(179, "Extra Toggle", 0x0, None, 672, 30000),
    NonPowerBrickExtraData(180, "Fertilizer", 0x1, None, 671, 8000),
    NonPowerBrickExtraData(181, "Disguise", 0x2, None, 668, 10000),
    NonPowerBrickExtraData(182, "Daisy Chains", 0x3, None, 677, 5000),
    NonPowerBrickExtraData(183, "Chewbacca Carrying C-3PO", 0x4, None, 669, 10000),
    NonPowerBrickExtraData(184, "Tow Death Star", 0x5, None, 678, 5000),
    NonPowerBrickExtraData(185, "Silhouettes", 0x6, None, 698, 10000),
    NonPowerBrickExtraData(186, "Beep Beep", 0x7, None, 298, 7500),

    _generic(145, "Progressive Score Multiplier"),

    _generic(154, "Episode Completion Token"),

    _generic(155, "Episode 1 Unlock"),
    _generic(156, "Episode 2 Unlock"),
    _generic(157, "Episode 3 Unlock"),
    _generic(158, "Episode 4 Unlock"),
    _generic(159, "Episode 5 Unlock"),
    _generic(160, "Episode 6 Unlock"),

    MinikitItemData(199, "Minikit", 1),
    MinikitItemData(200, "2 Minikits", 2),
    MinikitItemData(1, "5 Minikits", 5),
    MinikitItemData(201, "10 Minikits", 10),

    _generic(203, "Kyber Brick"),

    _generic(202, "Power Up"),

    _generic(204, "Silver Stud"),
    _generic(205, "Gold Stud"),
    _generic(206, "Blue Stud"),
    _generic(175, "Purple Stud"),

    # "Extra Toggle" characters.
    # Floats above the ground, with hover_height=0.25, which prevents the last safe position from updating.
    # Shoots short range blaster bolts that deal no damage to enemies, but can destroy objects and are affected by
    # Exploding Blaster Bolts (allowing dealing damage to enemies). The 0-damage blaster bolts will also aggro enemies.
    # todo: Find out what height of obstacle it can float over, guessing at least 0.15 for now.
    # TODO: Find out what distance it can 'jump'. Since it cannot actually jump, and instead floats
    _char(-1, "Training Remote", 19, CAN_SELF_DESTRUCT | CAN_AGGRAVATE_ENEMIES, 1.05, 0.25, 0.0, Alignment.NEUTRAL),
    generic_stormtrooper(-1, "Scout Trooper", 52),
    _char(-1, "Han Solo (frozen in carbonite)", 105, CharacterAbility.NONE, 0.75, 0.0, 0.0, Alignment.GOOD),
    _char(-1, "Womp Rat", 165, CharacterAbility.NONE, 1.8, 0.0, 0.0, Alignment.PASSIVE),
    _char(-1, "Droid 1", 174, BLASTER | CAN_SELF_DESTRUCT, 0.6, 0.0, 0.0, Alignment.PASSIVE),
    _char(-1, "Droid 2", 175, BLASTER | CAN_SELF_DESTRUCT, 0.6, 0.0, 0.0, Alignment.PASSIVE),
    _char(-1, "Droid 3", 176, BLASTER | CAN_SELF_DESTRUCT, 0.4, 0.0, 0.0, Alignment.PASSIVE),
    _char(-1, "Droid 4", 177, BLASTER | CAN_SELF_DESTRUCT, 0.6, 0.0, 0.0, Alignment.PASSIVE),
    _char(-1, "Mouse Droid", 44, CAN_SELF_DESTRUCT, 2.4, 0.0, 0.0, Alignment.PASSIVE),
    generic_rebel(-1, "Rebel Engineer", 224),
    generic_stormtrooper(-1, "AT-AT Driver", 228),
    # Explicitly marked as being able to jump with 0.44 height, but cannot actually jump in-game.
    _char(-1, "Skeleton", 231, CAN_MELEE, 1.2, 0.0, 0.0, Alignment.GOOD),
    generic_stormtrooper(-1, "Imperial Engineer", 233),
    # Note: It's melee attack is a regular melee attack, not a combo melee attack.
    _char(-1, "Buzz Droid", 294, CAN_SELF_DESTRUCT | CAN_MELEE, 1.2, 0.0, 0.0, Alignment.EVIL),

    # Miscellaneous vehicles.
    # This is the vehicle present in the outside area of the Cantina. 'map' is the internal name for the Cantina.
    _char(-1, "mapcar", 303, CharacterAbility.NONE, 2.0, 0.0, 0.0, Alignment.GOOD),

    _char(-1, "Super Gonk Droid", -1,
          CAN_SELF_DESTRUCT | COMMON_CAN_JUMP_SLIGHTLY_HIGHER | CAN_JUMP_DISTANCE_0_69,
          1.44, 0.53, 1.325, Alignment.PASSIVE),
]


# Programmatically add Chapter Unlock items, starting from ID 1000 so that they avoid clashing with manually defined
# items.
CHAPTER_UNLOCKS: list[GenericItemData] = [
    _generic(i, f"{episode}-{chapter} Unlock") for i, (episode, chapter)
    in enumerate(itertools.product(range(1, 7), range(1, 7)), start=1000)
]
ITEM_DATA.extend(CHAPTER_UNLOCKS)


USEFUL_NON_PROGRESSION_CHARACTERS: set[str] = {
    # There is currently no Ghost logic for bypassing gas and other hazards, so give the Ghosts at least Useful
    # classification.
    "Ben Kenobi (Ghost)",
    "Anakin Skywalker (Ghost)",
    "Yoda (Ghost)",
    # There is currently no glitch logic for the glitchy mess that is Yoda, so ensure Yoda is never excluded by making
    # him Useful.
    "Yoda",
    # The fastest character (1.8).
    "Droideka",
    # The second-fastest character (1.5).
    "Watto",
    # The third-fastest character when Super Gonk is active (1.44).
    "Gonk Droid",
    # Fastest vehicles.
    "Anakin's Pod",
    "Sebulba's Pod",
}


ITEM_DATA_BY_NAME: Mapping[str, GenericItemData] = {data.name: data for data in ITEM_DATA}
ITEM_DATA_BY_ID: Mapping[int, GenericItemData] = {data.code: data for data in ITEM_DATA if data.is_sendable}
EXTRAS_BY_NAME: Mapping[str, ExtraData] = {data.name: data for data in ITEM_DATA if isinstance(data, ExtraData)}
PURCHASABLE_NON_POWER_BRICK_EXTRAS: tuple[NonPowerBrickExtraData, ...] = tuple(
    [extra for extra in EXTRAS_BY_NAME.values() if isinstance(extra, NonPowerBrickExtraData)]
)
CHARACTERS_AND_VEHICLES_BY_NAME: Mapping[str, GenericCharacterData] = {data.name: data for data in ITEM_DATA
                                                                       if isinstance(data, GenericCharacterData)}
LOGIC_CONSIDERED_CHARACTERS = {
    name: character for name, character in CHARACTERS_AND_VEHICLES_BY_NAME.items()
    # todo: Mark unsendable, but event characters instead of hardcoding Super Gonk Droid like this.
    if character.is_sendable or character.name == "Super Gonk Droid"
}
GENERIC_BY_NAME: Mapping[str, GenericItemData] = {data.name: data for data in ITEM_DATA if data.item_type == "Generic"}
MINIKITS_BY_NAME: Mapping[str, MinikitItemData] = {data.name: data for data in ITEM_DATA
                                                   if isinstance(data, MinikitItemData)}
NON_VEHICLE_CHARACTER_BY_INDEX: Mapping[int, CharacterData] = {char.character_index: char
                                                               for char in CHARACTERS_AND_VEHICLES_BY_NAME.values()
                                                               if isinstance(char, CharacterData)}
AP_NON_VEHICLE_CHARACTER_INDICES: AbstractSet[int] = {char.character_index
                                                      for char in NON_VEHICLE_CHARACTER_BY_INDEX.values()
                                                      if char.is_sendable}

ITEM_NAME_TO_ID: dict[str, int] = {name: item.code for name, item in ITEM_DATA_BY_NAME.items() if item.is_sendable}

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
