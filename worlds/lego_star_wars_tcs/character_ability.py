from enum import auto, IntFlag


__all__ = [
    "CharacterAbility",
    "ASTROMECH_PANEL",
    "BLASTER",
    "GRAPPLE",
    "BOUNTY_HUNTER",
    "HOVER",
    "HIGH_JUMP",
    "IMPERIAL",
    "JEDI",
    "PROTOCOL_PANEL",
    "SHORTIE",
    "SITH",

    "JETPACK",

    "CAN_WEAR_HAT",
    "CAN_WEAR_HAT_AND_GRAPPLE",
    "CAN_WEAR_HAT_AND_DOUBLE_JUMP",
    "CAN_RIDE_VEHICLES",
    "CAN_PULL_LEVERS",
    "CAN_PUSH_OBJECTS",
    "CAN_BUILD_BRICKS",
    "CAN_BARELY_JUMP",
    "CAN_JUMP_NORMAL_HEIGHT",
    "CAN_JUMP_NORMAL_DISTANCE",
    "RUN_SPEED_0_9_OR_HIGHER",
    "CAN_JUMP_SLIGHTLY_HIGHER",
    "CAN_FLOP_JUMP",
    "CAN_DOUBLE_JUMP",
    "CAN_HIGH_JUMP_SLAM",
    "CAN_TRIPLE_JUMP_GREAT_DISTANCE",
    "CAN_ATTACK_UP_CLOSE",
    "CAN_DEFLECT_BOLTS",
    "ASTROMECH_DROID",

    "WEAPON_EWOK",
    "WEAPON_ZAPPER",

    "CAN_SELF_DESTRUCT",
    "CAN_AGGRAVATE_ENEMIES",
    "IS_NON_GHOST_JEDI",

    "IS_A_VEHICLE",
    "VEHICLE_TIE",
    "VEHICLE_TOW",
    "VEHICLE_BLASTER",

    "IMPLIED_ABILITIES",
    "ABILITY_REDUCTIONS",
]


# todo: These are the abilities from the manual logic, not the real abilities.
class CharacterAbility(IntFlag):
    NONE = 0
    ASTROMECH_PANEL = auto()
    # todo: This will eventually need to be split into separate Grapple and Blaster.
    BLASTER = auto()
    GRAPPLE = auto()
    BOUNTY_HUNTER = auto()
    HOVER = auto()
    HIGH_JUMP = auto()
    IMPERIAL = auto()
    JEDI = auto()
    PROTOCOL_PANEL = auto()
    SHORTIE = auto()
    SITH = auto()

    JETPACK = auto()

    # Relevant for some Imperial access and 6-1 Bounty Hunter access.
    CAN_WEAR_HAT = auto()
    # CAN_WEAR_HAT + BLASTER (grapple) on a single character.
    CAN_WEAR_HAT_AND_GRAPPLE = auto()
    # CAN_WEAR_HAT + JEDI on a single character.
    CAN_WEAR_HAT_AND_DOUBLE_JUMP = auto()
    CAN_PULL_LEVERS = auto()
    # All characters that can push objects also can ride vehicles, and vice-versa, so these use the same flag for better
    # performance.
    CAN_RIDE_VEHICLES_AND_PUSH_OBJECTS = auto()
    CAN_RIDE_VEHICLES = CAN_RIDE_VEHICLES_AND_PUSH_OBJECTS
    CAN_PUSH_OBJECTS = CAN_RIDE_VEHICLES_AND_PUSH_OBJECTS  # Blocks and Spinners
    CAN_BUILD_BRICKS = auto()

    CAN_BARELY_JUMP = auto()
    CAN_JUMP_NORMAL_HEIGHT = auto()  # Has at least a basic jump height.
    # Has at least a basic jump height and basic movement speed.
    # Most characters except Ewoks and Ugnaught.
    CAN_JUMP_NORMAL_DISTANCE = auto()
    # If a character is too slow, they cannot get past the 2-3 conveyor crushers without jumping around them or using
    # the thin edge of collision along the front edge of the conveyor.
    # run_speed=0.9 is fast enough, run_speed=0.8285375 is too slow and there are no runs speeds inbetween.
    RUN_SPEED_0_9_OR_HIGHER = auto()
    CAN_JUMP_SLIGHTLY_HIGHER = auto()
    CAN_FLOP_JUMP = auto()  # Stormtroopers can flop instead dive-rolling, which gets ever so slightly more height.
    CAN_DOUBLE_JUMP = auto()  # Jedi or High Jump

    CAN_HIGH_JUMP_SLAM = auto()  # General Grievous or Grievous' Bodyguard. Only used in Moderate+ Logic.
    CAN_TRIPLE_JUMP_GREAT_DISTANCE = auto()  # General Grievous and Jedi (except Yoda/Yoda(Ghost))

    CAN_ATTACK_UP_CLOSE = auto()
    # Not to be confused with being able to reflect bolts, which only Jedi can do.
    CAN_DEFLECT_BOLTS = auto()  # All Jedi, except ghosts, + Captain Tarpals + Grievous' Bodyguard + General Grievous.

    ASTROMECH_DROID = auto()  # This character is an Astromech Droid, relevant to Dagobah and sometimes P2's AI.
    CAN_SELF_DESTRUCT = auto()  # Most droids, but not 4-LOM and IG-88.
    # Can this character cause enemy AI to attack them? Passive characters, ghost characters, and neutral characters
    # without weapons cannot cause enemy AI to attack them. This is relevant for the Deflect Bolts extra.
    # Ugnaught and Jawa cannot aggravate enemies, unless they have Super Zapper, but this only works on Droids is only
    # relevant in 3-4 where there are both Droids and Clones
    CAN_AGGRAVATE_ENEMIES = auto()
    # Ghost Jedi on their cannot be used to reflect blaster bolts, such as at the start of 1-6 because enemies will not
    # shoot at them in the first place to allow reflecting blaster bolts.
    IS_NON_GHOST_JEDI = auto()
    # IMMUNE_TO_GAS = auto()  # Droids and ghosts.
    # todo: Lots more abilities to add to split up and replace the basic existing ones...
    # GHOST = auto()
    # DROID = auto()
    # UNTARGETABLE = auto()  # Are there any characters other than Ghosts?

    WEAPON_EWOK = auto()
    WEAPON_ZAPPER = auto()

    IS_A_VEHICLE = auto()
    VEHICLE_TIE = auto()
    VEHICLE_TOW = auto()
    VEHICLE_BLASTER = auto()

    # def __matmul__(self, other):
    #     """(A | B | C) @ D -> (A in D) or (B in D) or (C in D)"""
    #     if isinstance(other, CharacterAbility):
    #         return self & other != 0
    #     else:
    #         return NotImplemented

    def simplify_and(self) -> "CharacterAbility":
        if self.value.bit_count() < 2:
            return self
        simplified = self
        for ability in self:
            if ability in IMPLIED_BY_ABILITIES and IMPLIED_BY_ABILITIES[ability] & simplified:
                simplified &= ~ability
        return simplified

    def simplify_or(self) -> "CharacterAbility":
        if self.value.bit_count() < 2:
            return self
        simplified = self

        for ability in self:
            if ability in IMPLIED_ABILITIES and IMPLIED_ABILITIES[ability] & simplified:
                simplified &= ~ability

        if simplified.value.bit_count() < 2:
            return simplified

        for combination, reducable_to in ABILITY_REDUCTIONS.items():
            if combination in simplified:
                # Remove the combination bits.
                simplified &= ~combination
                # Add the reduced bit.
                simplified |= reducable_to
        return simplified


# Workaround for Python 3.10 support. Iterating Flag instances was only added in Python 3.11.
# There is probably a better way to do this, but it will get the job done.
if getattr(CharacterAbility.NONE, "__iter__", None) is None:
    def __iter__(self: CharacterAbility):
        none_flag = CharacterAbility.NONE
        for flag in CharacterAbility:
            if flag is not none_flag and flag in self:
                yield flag
    CharacterAbility.__iter__ = __iter__  # type: ignore
    del __iter__


# Humanoid Special Abilities. These are rather more obvious to players.
ASTROMECH_PANEL = CharacterAbility.ASTROMECH_PANEL
BLASTER = CharacterAbility.BLASTER
GRAPPLE = CharacterAbility.GRAPPLE
BOUNTY_HUNTER = CharacterAbility.BOUNTY_HUNTER
HOVER = CharacterAbility.HOVER
HIGH_JUMP = CharacterAbility.HIGH_JUMP
IMPERIAL = CharacterAbility.IMPERIAL
JEDI = CharacterAbility.JEDI
PROTOCOL_PANEL = CharacterAbility.PROTOCOL_PANEL
SHORTIE = CharacterAbility.SHORTIE
SITH = CharacterAbility.SITH
JETPACK = CharacterAbility.JETPACK

# Vehicle Special Abilities.
VEHICLE_TIE = CharacterAbility.VEHICLE_TIE
VEHICLE_TOW = CharacterAbility.VEHICLE_TOW
VEHICLE_BLASTER = CharacterAbility.VEHICLE_BLASTER

# Chapter-specific flags.
CAN_WEAR_HAT = CharacterAbility.CAN_WEAR_HAT
CAN_WEAR_HAT_AND_GRAPPLE = CharacterAbility.CAN_WEAR_HAT_AND_GRAPPLE
CAN_WEAR_HAT_AND_DOUBLE_JUMP = CharacterAbility.CAN_WEAR_HAT_AND_DOUBLE_JUMP
ASTROMECH_DROID = CharacterAbility.ASTROMECH_DROID
IS_A_VEHICLE = CharacterAbility.IS_A_VEHICLE

# Extremely common ability flags.
CAN_RIDE_VEHICLES = CharacterAbility.CAN_RIDE_VEHICLES
CAN_PULL_LEVERS = CharacterAbility.CAN_PULL_LEVERS
CAN_PUSH_OBJECTS = CharacterAbility.CAN_PUSH_OBJECTS
CAN_BUILD_BRICKS = CharacterAbility.CAN_BUILD_BRICKS
CAN_RIDE_VEHICLES_AND_PUSH_OBJECTS = CharacterAbility.CAN_RIDE_VEHICLES_AND_PUSH_OBJECTS

CAN_DOUBLE_JUMP = CharacterAbility.CAN_DOUBLE_JUMP
CAN_JUMP_SLIGHTLY_HIGHER = CharacterAbility.CAN_JUMP_SLIGHTLY_HIGHER
CAN_FLOP_JUMP = CharacterAbility.CAN_FLOP_JUMP
CAN_JUMP_NORMAL_HEIGHT = CharacterAbility.CAN_JUMP_NORMAL_HEIGHT
CAN_JUMP_NORMAL_DISTANCE = CharacterAbility.CAN_JUMP_NORMAL_DISTANCE
RUN_SPEED_0_9_OR_HIGHER = CharacterAbility.RUN_SPEED_0_9_OR_HIGHER
CAN_BARELY_JUMP = CharacterAbility.CAN_BARELY_JUMP

CAN_HIGH_JUMP_SLAM = CharacterAbility.CAN_HIGH_JUMP_SLAM
CAN_TRIPLE_JUMP_GREAT_DISTANCE = CharacterAbility.CAN_TRIPLE_JUMP_GREAT_DISTANCE

CAN_ATTACK_UP_CLOSE = CharacterAbility.CAN_ATTACK_UP_CLOSE
CAN_DEFLECT_BOLTS = CharacterAbility.CAN_DEFLECT_BOLTS

# Weapon type flags.
WEAPON_EWOK = CharacterAbility.WEAPON_EWOK
WEAPON_ZAPPER = CharacterAbility.WEAPON_ZAPPER

# Other flags.
CAN_SELF_DESTRUCT = CharacterAbility.CAN_SELF_DESTRUCT
CAN_AGGRAVATE_ENEMIES = CharacterAbility.CAN_AGGRAVATE_ENEMIES
IS_NON_GHOST_JEDI = CharacterAbility.IS_NON_GHOST_JEDI


# Combination flags
#CHARACTER_CAN_JUMP_NORMALLY = CAN_JUMP_NORMAL_HEIGHT | CAN_BARELY_JUMP
#CHARACTER_CAN_JUMP_SLIGHTLY_HIGHER = CAN_JUMP_SLIGHTLY_HIGHER | CHARACTER_CAN_JUMP_NORMALLY
#CHARACTER_JEDI = JEDI | CAN_ATTACK_UP_CLOSE
#CHARACTER_SITH = SITH | CHARACTER_JEDI

# CHARACTER_ASTROMECH_DROID = ASTROMECH_PANEL | CAN_BARELY_JUMP | WEAPON_ZAPPER | ASTROMECH_DROID | HOVER


# This dictionary is generated by test.test_abilities.TestAbilities.test_implied_abilities when the test fails.
# By listing out the dict contents, it provides a visual aid into understanding possible optimisations in rules, rather
# than there just being a dictionary with unknown contents.
# If A => B (A implies B), then A | B is B, and A & B is A.
# This dict maps A to all B that are implied.
# noinspection LongLine
IMPLIED_ABILITIES: dict[CharacterAbility, CharacterAbility] = {
    # All characters with this ability: Also have these abilities,
    # HasAllAbilities(left | right) -> HasAbility(left)
    ASTROMECH_PANEL: CAN_BARELY_JUMP | RUN_SPEED_0_9_OR_HIGHER,
    BLASTER: RUN_SPEED_0_9_OR_HIGHER | CAN_ATTACK_UP_CLOSE | CAN_AGGRAVATE_ENEMIES,
    GRAPPLE: BLASTER | CAN_RIDE_VEHICLES_AND_PUSH_OBJECTS | CAN_BARELY_JUMP | CAN_JUMP_NORMAL_HEIGHT | RUN_SPEED_0_9_OR_HIGHER | CAN_ATTACK_UP_CLOSE | CAN_AGGRAVATE_ENEMIES,
    BOUNTY_HUNTER: BLASTER | GRAPPLE | CAN_RIDE_VEHICLES_AND_PUSH_OBJECTS | CAN_BARELY_JUMP | CAN_JUMP_NORMAL_HEIGHT | RUN_SPEED_0_9_OR_HIGHER | CAN_ATTACK_UP_CLOSE | CAN_AGGRAVATE_ENEMIES,
    HOVER: CAN_BARELY_JUMP | CAN_JUMP_NORMAL_DISTANCE | RUN_SPEED_0_9_OR_HIGHER,
    HIGH_JUMP: CAN_BARELY_JUMP | CAN_JUMP_NORMAL_HEIGHT | CAN_JUMP_NORMAL_DISTANCE | RUN_SPEED_0_9_OR_HIGHER | CAN_JUMP_SLIGHTLY_HIGHER | CAN_FLOP_JUMP | CAN_DOUBLE_JUMP | CAN_AGGRAVATE_ENEMIES,
    IMPERIAL: CAN_PULL_LEVERS | CAN_RIDE_VEHICLES_AND_PUSH_OBJECTS | CAN_BUILD_BRICKS | CAN_BARELY_JUMP | CAN_JUMP_NORMAL_HEIGHT | CAN_JUMP_NORMAL_DISTANCE | RUN_SPEED_0_9_OR_HIGHER | CAN_ATTACK_UP_CLOSE | CAN_AGGRAVATE_ENEMIES,
    JEDI: CAN_PULL_LEVERS | CAN_RIDE_VEHICLES_AND_PUSH_OBJECTS | CAN_BUILD_BRICKS | CAN_BARELY_JUMP | CAN_JUMP_NORMAL_HEIGHT | CAN_JUMP_NORMAL_DISTANCE | CAN_JUMP_SLIGHTLY_HIGHER | CAN_FLOP_JUMP | CAN_DOUBLE_JUMP | CAN_ATTACK_UP_CLOSE,
    PROTOCOL_PANEL: CharacterAbility.NONE,
    SHORTIE: CAN_PULL_LEVERS | CAN_RIDE_VEHICLES_AND_PUSH_OBJECTS | CAN_BUILD_BRICKS | CAN_BARELY_JUMP | CAN_JUMP_NORMAL_HEIGHT,
    SITH: JEDI | CAN_PULL_LEVERS | CAN_RIDE_VEHICLES_AND_PUSH_OBJECTS | CAN_BUILD_BRICKS | CAN_BARELY_JUMP | CAN_JUMP_NORMAL_HEIGHT | CAN_JUMP_NORMAL_DISTANCE | RUN_SPEED_0_9_OR_HIGHER | CAN_JUMP_SLIGHTLY_HIGHER | CAN_FLOP_JUMP | CAN_DOUBLE_JUMP | CAN_TRIPLE_JUMP_GREAT_DISTANCE | CAN_ATTACK_UP_CLOSE | CAN_DEFLECT_BOLTS | CAN_AGGRAVATE_ENEMIES | IS_NON_GHOST_JEDI,
    JETPACK: BLASTER | GRAPPLE | BOUNTY_HUNTER | HOVER | CAN_PULL_LEVERS | CAN_RIDE_VEHICLES_AND_PUSH_OBJECTS | CAN_BUILD_BRICKS | CAN_BARELY_JUMP | CAN_JUMP_NORMAL_HEIGHT | CAN_JUMP_NORMAL_DISTANCE | RUN_SPEED_0_9_OR_HIGHER | CAN_ATTACK_UP_CLOSE | CAN_AGGRAVATE_ENEMIES,
    CAN_WEAR_HAT: CAN_PULL_LEVERS | CAN_RIDE_VEHICLES_AND_PUSH_OBJECTS | CAN_BUILD_BRICKS | CAN_BARELY_JUMP | CAN_JUMP_NORMAL_HEIGHT | CAN_JUMP_NORMAL_DISTANCE | RUN_SPEED_0_9_OR_HIGHER,
    CAN_WEAR_HAT_AND_GRAPPLE: BLASTER | GRAPPLE | CAN_WEAR_HAT | CAN_PULL_LEVERS | CAN_RIDE_VEHICLES_AND_PUSH_OBJECTS | CAN_BUILD_BRICKS | CAN_BARELY_JUMP | CAN_JUMP_NORMAL_HEIGHT | CAN_JUMP_NORMAL_DISTANCE | RUN_SPEED_0_9_OR_HIGHER | CAN_ATTACK_UP_CLOSE | CAN_AGGRAVATE_ENEMIES,
    CAN_WEAR_HAT_AND_DOUBLE_JUMP: JEDI | CAN_WEAR_HAT | CAN_PULL_LEVERS | CAN_RIDE_VEHICLES_AND_PUSH_OBJECTS | CAN_BUILD_BRICKS | CAN_BARELY_JUMP | CAN_JUMP_NORMAL_HEIGHT | CAN_JUMP_NORMAL_DISTANCE | RUN_SPEED_0_9_OR_HIGHER | CAN_JUMP_SLIGHTLY_HIGHER | CAN_FLOP_JUMP | CAN_DOUBLE_JUMP | CAN_TRIPLE_JUMP_GREAT_DISTANCE | CAN_ATTACK_UP_CLOSE,
    CAN_PULL_LEVERS: CAN_RIDE_VEHICLES_AND_PUSH_OBJECTS | CAN_BARELY_JUMP | CAN_JUMP_NORMAL_HEIGHT,
    CAN_RIDE_VEHICLES_AND_PUSH_OBJECTS: CAN_BARELY_JUMP | CAN_JUMP_NORMAL_HEIGHT,
    CAN_BUILD_BRICKS: CAN_BARELY_JUMP | CAN_JUMP_NORMAL_HEIGHT,
    CAN_BARELY_JUMP: CharacterAbility.NONE,
    CAN_JUMP_NORMAL_HEIGHT: CAN_BARELY_JUMP,
    CAN_JUMP_NORMAL_DISTANCE: CAN_BARELY_JUMP,
    RUN_SPEED_0_9_OR_HIGHER: CharacterAbility.NONE,
    CAN_JUMP_SLIGHTLY_HIGHER: CAN_BARELY_JUMP | CAN_JUMP_NORMAL_HEIGHT | CAN_JUMP_NORMAL_DISTANCE | CAN_FLOP_JUMP,
    CAN_FLOP_JUMP: CAN_BARELY_JUMP | CAN_JUMP_NORMAL_HEIGHT | CAN_JUMP_NORMAL_DISTANCE,
    CAN_DOUBLE_JUMP: CAN_BARELY_JUMP | CAN_JUMP_NORMAL_HEIGHT | CAN_JUMP_NORMAL_DISTANCE | CAN_JUMP_SLIGHTLY_HIGHER | CAN_FLOP_JUMP,
    CAN_HIGH_JUMP_SLAM: HIGH_JUMP | CAN_BARELY_JUMP | CAN_JUMP_NORMAL_HEIGHT | CAN_JUMP_NORMAL_DISTANCE | RUN_SPEED_0_9_OR_HIGHER | CAN_JUMP_SLIGHTLY_HIGHER | CAN_FLOP_JUMP | CAN_DOUBLE_JUMP | CAN_ATTACK_UP_CLOSE | CAN_DEFLECT_BOLTS | CAN_AGGRAVATE_ENEMIES,
    CAN_TRIPLE_JUMP_GREAT_DISTANCE: CAN_BUILD_BRICKS | CAN_BARELY_JUMP | CAN_JUMP_NORMAL_HEIGHT | CAN_JUMP_NORMAL_DISTANCE | RUN_SPEED_0_9_OR_HIGHER | CAN_JUMP_SLIGHTLY_HIGHER | CAN_FLOP_JUMP | CAN_DOUBLE_JUMP | CAN_ATTACK_UP_CLOSE,
    CAN_ATTACK_UP_CLOSE: CharacterAbility.NONE,
    CAN_DEFLECT_BOLTS: CAN_BARELY_JUMP | CAN_JUMP_NORMAL_HEIGHT | CAN_JUMP_NORMAL_DISTANCE | CAN_ATTACK_UP_CLOSE | CAN_AGGRAVATE_ENEMIES,
    ASTROMECH_DROID: ASTROMECH_PANEL | HOVER | CAN_BARELY_JUMP | CAN_JUMP_NORMAL_DISTANCE | RUN_SPEED_0_9_OR_HIGHER | CAN_SELF_DESTRUCT | WEAPON_ZAPPER,
    CAN_SELF_DESTRUCT: CharacterAbility.NONE,
    CAN_AGGRAVATE_ENEMIES: CharacterAbility.NONE,
    IS_NON_GHOST_JEDI: JEDI | CAN_PULL_LEVERS | CAN_RIDE_VEHICLES_AND_PUSH_OBJECTS | CAN_BUILD_BRICKS | CAN_BARELY_JUMP | CAN_JUMP_NORMAL_HEIGHT | CAN_JUMP_NORMAL_DISTANCE | RUN_SPEED_0_9_OR_HIGHER | CAN_JUMP_SLIGHTLY_HIGHER | CAN_FLOP_JUMP | CAN_DOUBLE_JUMP | CAN_TRIPLE_JUMP_GREAT_DISTANCE | CAN_ATTACK_UP_CLOSE | CAN_DEFLECT_BOLTS | CAN_AGGRAVATE_ENEMIES,
    WEAPON_EWOK: SHORTIE | CAN_PULL_LEVERS | CAN_RIDE_VEHICLES_AND_PUSH_OBJECTS | CAN_BUILD_BRICKS | CAN_BARELY_JUMP | CAN_JUMP_NORMAL_HEIGHT | RUN_SPEED_0_9_OR_HIGHER | CAN_ATTACK_UP_CLOSE | CAN_AGGRAVATE_ENEMIES,
    WEAPON_ZAPPER: CAN_BARELY_JUMP | RUN_SPEED_0_9_OR_HIGHER,
    IS_A_VEHICLE: CharacterAbility.NONE,
    VEHICLE_TIE: IS_A_VEHICLE | VEHICLE_BLASTER,
    VEHICLE_TOW: IS_A_VEHICLE | VEHICLE_BLASTER,
    VEHICLE_BLASTER: IS_A_VEHICLE,
}


def _make_implied_by_abilities() -> dict[CharacterAbility, CharacterAbility]:
    implied_by_dict: dict[CharacterAbility, CharacterAbility] = {
        ability: CharacterAbility.NONE for ability in CharacterAbility
    }
    for ability, implies in IMPLIED_ABILITIES.items():
        for implied in implies:
            implied_by_dict[implied] |= ability
    return implied_by_dict


# If A => B (A implies B), then A | B is B, and A & B is A.
# This dict maps B to all A that imply it.
IMPLIED_BY_ABILITIES = _make_implied_by_abilities()


ABILITY_REDUCTIONS: dict[CharacterAbility, CharacterAbility] = {
    # 2) Are at least one of these: 1) All of these.
    # 1) All of these: 2) Are these.
    # HasAnyAbilities(A | B) can be reduced to HasAbility(C).
    # Combinations with more bits need to be first.
    HIGH_JUMP | JEDI | CAN_TRIPLE_JUMP_GREAT_DISTANCE: CAN_DOUBLE_JUMP,
    HIGH_JUMP | JEDI: CAN_DOUBLE_JUMP,
    ASTROMECH_PANEL | CAN_JUMP_NORMAL_HEIGHT: CAN_BARELY_JUMP,
    HOVER | CAN_JUMP_NORMAL_HEIGHT: CAN_BARELY_JUMP,
    CAN_RIDE_VEHICLES_AND_PUSH_OBJECTS | CAN_JUMP_NORMAL_DISTANCE: CAN_BARELY_JUMP,
    CAN_JUMP_NORMAL_HEIGHT | CAN_JUMP_NORMAL_DISTANCE: CAN_BARELY_JUMP,
    CAN_RIDE_VEHICLES_AND_PUSH_OBJECTS | CAN_JUMP_SLIGHTLY_HIGHER: CAN_JUMP_NORMAL_HEIGHT,
    CAN_RIDE_VEHICLES_AND_PUSH_OBJECTS | CAN_FLOP_JUMP: CAN_JUMP_NORMAL_HEIGHT,
    JETPACK | ASTROMECH_DROID: HOVER,
    CAN_JUMP_NORMAL_HEIGHT | ASTROMECH_DROID: CAN_BARELY_JUMP,
    CAN_JUMP_NORMAL_HEIGHT | WEAPON_ZAPPER: CAN_BARELY_JUMP,
}
