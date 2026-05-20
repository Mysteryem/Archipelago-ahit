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
    "CAN_JUMP_SLIGHTLY_HIGHER",
    "CAN_FLOP_JUMP",
    "CAN_DOUBLE_JUMP",
    "CAN_HIGH_JUMP_SLAM",
    "CAN_TRIPLE_JUMP_GREAT_DISTANCE",
    "CAN_ATTACK_UP_CLOSE",
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
    CAN_RIDE_VEHICLES = auto()
    CAN_PULL_LEVERS = auto()
    CAN_PUSH_OBJECTS = auto()  # Blocks and Spinners
    CAN_BUILD_BRICKS = auto()

    CAN_BARELY_JUMP = auto()
    CAN_JUMP_NORMAL_HEIGHT = auto()  # Has at least a basic jump height.
    # Has at least a basic jump height and basic movement speed.
    # Most characters except Ewoks and Ugnaught.
    CAN_JUMP_NORMAL_DISTANCE = auto()
    CAN_JUMP_SLIGHTLY_HIGHER = auto()
    CAN_FLOP_JUMP = auto()  # Stormtroopers can flop instead dive-rolling, which gets ever so slightly more height.
    CAN_DOUBLE_JUMP = auto()  # Jedi or High Jump

    CAN_HIGH_JUMP_SLAM = auto()  # General Grievous or Grievous' Bodyguard. Only used in Moderate+ Logic.
    CAN_TRIPLE_JUMP_GREAT_DISTANCE = auto()  # General Grievous and Jedi (except Yoda/Yoda(Ghost))

    CAN_ATTACK_UP_CLOSE = auto()

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

CAN_DOUBLE_JUMP = CharacterAbility.CAN_DOUBLE_JUMP
CAN_JUMP_SLIGHTLY_HIGHER = CharacterAbility.CAN_JUMP_SLIGHTLY_HIGHER
CAN_FLOP_JUMP = CharacterAbility.CAN_FLOP_JUMP
CAN_JUMP_NORMAL_HEIGHT = CharacterAbility.CAN_JUMP_NORMAL_HEIGHT
CAN_JUMP_NORMAL_DISTANCE = CharacterAbility.CAN_JUMP_NORMAL_DISTANCE
CAN_BARELY_JUMP = CharacterAbility.CAN_BARELY_JUMP

CAN_HIGH_JUMP_SLAM = CharacterAbility.CAN_HIGH_JUMP_SLAM
CAN_TRIPLE_JUMP_GREAT_DISTANCE = CharacterAbility.CAN_TRIPLE_JUMP_GREAT_DISTANCE

CAN_ATTACK_UP_CLOSE = CharacterAbility.CAN_ATTACK_UP_CLOSE

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
