from enum import auto, IntFlag


__all__ = [
    "CharacterAbility",
    "ASTROMECH",
    "BLASTER",
    "GRAPPLE",
    "BOUNTY_HUNTER",
    "HOVER",
    "HIGH_JUMP",
    "IMPERIAL",
    "JEDI",
    "PROTOCOL_DROID",
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
    "CAN_JUMP_SLIGHTLY_HIGHER",
    "CAN_DOUBLE_JUMP",
    "CAN_HIGH_JUMP_SLAM",
    "CAN_ATTACK_UP_CLOSE",
    "CAN_DAGOBAH_SWAMP",

    "WEAPON_EWOK",
    "WEAPON_ZAPPER",

    "CAN_SELF_DESTRUCT",

    "IS_A_VEHICLE",
    "VEHICLE_TIE",
    "VEHICLE_TOW",
    "VEHICLE_BLASTER",
]


# todo: These are the abilities from the manual logic, not the real abilities.
class CharacterAbility(IntFlag):
    NONE = 0
    ASTROMECH = auto()
    # todo: This will eventually need to be split into separate Grapple and Blaster.
    BLASTER = auto()
    GRAPPLE = auto()
    BOUNTY_HUNTER = auto()
    HOVER = auto()
    HIGH_JUMP = auto()
    IMPERIAL = auto()
    JEDI = auto()
    PROTOCOL_DROID = auto()
    SHORTIE = auto()
    SITH = auto()

    JETPACK = auto()

    # Relevant for some Imperial access and 6-1 Bounty Hunter access.
    CAN_WEAR_HAT = auto()
    # CAN_WEAR_HAT + BLASTER (grapple) on a single character.
    CAN_WEAR_HAT_AND_GRAPPLE = auto()
    # CAN_WEAR_HAT + JEDI on a single character.
    CAN_WEAR_HAT_AND_DOUBLE_JUMP = auto()
    CAN_RIDE_VEHICLES = auto()
    CAN_PULL_LEVERS = auto()
    CAN_PUSH_OBJECTS = auto()  # Blocks and Spinners
    CAN_BUILD_BRICKS = auto()

    CAN_BARELY_JUMP = auto()
    CAN_JUMP_NORMAL_HEIGHT = auto()  # Has at least a basic jump height.
    CAN_JUMP_SLIGHTLY_HIGHER = auto()
    CAN_DOUBLE_JUMP = auto()  # Jedi or High Jump

    CAN_HIGH_JUMP_SLAM = auto()  # General Grievous or Grievous' Bodyguard. Only used in Moderate+ Logic.

    CAN_ATTACK_UP_CLOSE = auto()

    CAN_DAGOBAH_SWAMP = auto()  # Basically just "this character is an Astromech Droid"
    CAN_SELF_DESTRUCT = auto()  # Most droids, but not 4-LOM and IG-88.
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
ASTROMECH = CharacterAbility.ASTROMECH
BLASTER = CharacterAbility.BLASTER
GRAPPLE = CharacterAbility.GRAPPLE
BOUNTY_HUNTER = CharacterAbility.BOUNTY_HUNTER
HOVER = CharacterAbility.HOVER
HIGH_JUMP = CharacterAbility.HIGH_JUMP
IMPERIAL = CharacterAbility.IMPERIAL
JEDI = CharacterAbility.JEDI
PROTOCOL_DROID = CharacterAbility.PROTOCOL_DROID
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
CAN_DAGOBAH_SWAMP = CharacterAbility.CAN_DAGOBAH_SWAMP
IS_A_VEHICLE = CharacterAbility.IS_A_VEHICLE

# Extremely common ability flags.
CAN_RIDE_VEHICLES = CharacterAbility.CAN_RIDE_VEHICLES
CAN_PULL_LEVERS = CharacterAbility.CAN_PULL_LEVERS
CAN_PUSH_OBJECTS = CharacterAbility.CAN_PUSH_OBJECTS
CAN_BUILD_BRICKS = CharacterAbility.CAN_BUILD_BRICKS

CAN_DOUBLE_JUMP = CharacterAbility.CAN_DOUBLE_JUMP
CAN_JUMP_SLIGHTLY_HIGHER = CharacterAbility.CAN_JUMP_SLIGHTLY_HIGHER
CAN_JUMP_NORMAL_HEIGHT = CharacterAbility.CAN_JUMP_NORMAL_HEIGHT
CAN_BARELY_JUMP = CharacterAbility.CAN_BARELY_JUMP

CAN_HIGH_JUMP_SLAM = CharacterAbility.CAN_HIGH_JUMP_SLAM

CAN_ATTACK_UP_CLOSE = CharacterAbility.CAN_ATTACK_UP_CLOSE

# Weapon type flags.
WEAPON_EWOK = CharacterAbility.WEAPON_EWOK
WEAPON_ZAPPER = CharacterAbility.WEAPON_ZAPPER

# Other flags.
CAN_SELF_DESTRUCT = CharacterAbility.CAN_SELF_DESTRUCT


# Combination flags
#CHARACTER_CAN_JUMP_NORMALLY = CAN_JUMP_NORMAL_HEIGHT | CAN_BARELY_JUMP
#CHARACTER_CAN_JUMP_SLIGHTLY_HIGHER = CAN_JUMP_SLIGHTLY_HIGHER | CHARACTER_CAN_JUMP_NORMALLY
#CHARACTER_JEDI = JEDI | CAN_ATTACK_UP_CLOSE
#CHARACTER_SITH = SITH | CHARACTER_JEDI

CHARACTER_ASTROMECH_DROID = ASTROMECH | CAN_BARELY_JUMP | WEAPON_ZAPPER | CAN_DAGOBAH_SWAMP | HOVER


def update_for_implied_abilities(abilities: CharacterAbility):
    # All Sith are Jedi.
    if SITH in abilities:
        abilities |= JEDI

    # All characters that can Grapple happen to have Blasters.
    if GRAPPLE in abilities:
        abilities |= BLASTER

    # These are all suitable sources of dealing damage up close.
    if (JEDI | BLASTER | BOUNTY_HUNTER | WEAPON_EWOK) & abilities != 0:
        abilities |= CAN_ATTACK_UP_CLOSE

    if (HIGH_JUMP | JEDI) & abilities != 0:
        abilities |= CAN_DOUBLE_JUMP
    if CAN_DOUBLE_JUMP in abilities:
        abilities |= CAN_JUMP_SLIGHTLY_HIGHER
    if CAN_JUMP_SLIGHTLY_HIGHER in abilities:
        abilities |= CAN_JUMP_NORMAL_HEIGHT
    if CAN_JUMP_NORMAL_HEIGHT:
        abilities |= CAN_BARELY_JUMP

    # TODO: Can 4-LOM + IG-88 survive gas and use Self-Destruct?
    if (ASTROMECH | PROTOCOL_DROID) & abilities != 0:
        abilities |= CAN_SELF_DESTRUCT

    # Jetpacks are a superior version of Astromech hovering.
    if JETPACK in abilities:
        abilities |= HOVER

    return abilities
