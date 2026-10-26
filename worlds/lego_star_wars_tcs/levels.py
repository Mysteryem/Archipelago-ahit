from dataclasses import dataclass, field

from .character_ability import (
    CharacterAbility,
    SITH,
    BOUNTY_HUNTER,
    BLASTER,
    JEDI,
    CAN_WEAR_HAT,
    CAN_BUILD_BRICKS,
    CAN_PULL_LEVERS,
    CAN_MELEE,
    CAN_PUSH_OBJECTS,
    CAN_RIDE_VEHICLES,
    IS_A_VEHICLE,
)
from .data.areas import Area
from .data.characters import Character


@dataclass(frozen=True)
class BonusArea:
    name: str
    address: int
    # Playable level IDs within this area.
    playable_level_ids: tuple[int, ...]
    completion_offset: int
    """
    The cheat table listing the addresses listed a base address with unknown purpose for the bonus levels, and then an
    offset from that address for the completion byte, so that is why there is an offset separate from the address.
    """
    status_level_id: int
    area_id: int
    item_requirements: tuple[str, ...] = ()
    completion_ability_requirements: CharacterAbility = CharacterAbility.NONE
    gold_bricks_required: int = 0
    gold_brick: bool = True
    story_characters: frozenset[Character] = field(init=False)

    def __post_init__(self):
        object.__setattr__(self, "story_characters", BONUS_AREA_STORY_CHARACTERS.get(self.name, frozenset()))

    @property
    def completion_location_name(self) -> str:
        if self.gold_brick:
            return self.name + " Completion"
        else:
            # The only Bonus Area without a Gold Brick is not a level to complete, but watching the Indy Trailer.
            return self.name


BONUS_AREA_STORY_CHARACTERS: dict[str, frozenset[Character]] = {
    k: frozenset(v) for k, v in {
        "Mos Espa Pod Race (Original)": {
            Character.ANAKINS_POD,
        },
        "Anakin's Flight": {
            Character.NABOO_STARFIGHTER,
        },
        "Gunship Cavalry (Original)": {
            Character.REPUBLIC_GUNSHIP,
        },
        "A New Hope (Bonus Level)": {
            Character.DARTH_VADER,
            Character.C_3PO,
        }
    }.items()
}


# True Jedi that is difficult if not impossible in Free Play with just the Story characters for a level.
DIFFICULT_OR_IMPOSSIBLE_TRUE_JEDI: set[Area] = {
    # I don't think this is possible, I tried before, even with maximum usage of Power Ups. Higher logic could probably
    # get this because they can jump to the top of the cylindrical area with all the Battle Droids, which has a bunch of
    # Blue Studs.
    Area.MAUL,
    Area.DOOKU,  # I only managed 14180/22000
    Area.GRIEVOUS,  # Barely possible by re-entering and getting studs that replace minikits
    Area.TEMPLE,  # I managed only 40700/45000, even with 3 double jump slams to get 3 Blue Studs that were just too high.
    # Dying is easy in multiple areas, where even without deaths, it is barely possible.
    Area.VADER,
    # It's pretty slow, but possible to overshoot by 20K studs while mostly wasting the two Power Ups. If it is possible
    # to get 9/10 TIE Fighters in the Turbolaser control area towards the very end, then return to the previous room via
    # the elevator, go back to the Turbolasers and destroy the last TIE Fighter before the Power Up runs out, then
    # doubling the studs that spawn (around 20K) would be a huge benefit.
    # Area.DEATHSTARRESCUE,
    # Possible to overshoot by 95K Studs, even without taking advantage of Power Ups, though it is slow, and a vehicle,
    # level, so dying a lot is expected. Vehicle chapters also just kind of suck for picking up studs. 4-6 could be
    # included in the difficult True Jedi if there are complaints.
    # Area.DEATHSTARBATTLE,
    # Apparently barely possible by re-entering and getting studs that replace minikits. I find this vehicle chapter
    # especially difficult to actually pick studs up off the ground, and dying is also easy in this chapter.
    Area.HOTHBATTLE,
    # I only managed 53K/80K without deaths, but while wasting Power Ups. Even with Power Ups, 5-2 is looking clearly
    # impossible.
    Area.HOTHESCAPE,
    # If no studs are lost from dying and Power Ups are used to their fullest, then 5-6 is just barely possible
    # without getting Minikit Blue Studs, but by only around 100-200 Studs.
    Area.CLOUDCITYESCAPE,
    # I am assuming that the extra room where the door needs to be blown up is required to get True Jedi in 6-5.
    Area.EMPERORFIGHT,
}


CHAPTER_SPECIFIC_REQUIREMENTS: dict[Area, tuple[CharacterAbility, CharacterAbility | None]] = {
    # Mos Espa Pod Race does not require any Vehicle abilities, but does require having at least one vehicle character
    # unlocked, so extra logic is needed to ensure the player actually has a vehicle character.
    Area.PODSPRINT: (IS_A_VEHICLE, None),
    # There is a Hat Machine in Level D, which you can take all the way back to behind spawn to the Imperial Panel with
    # a Minikit behind.
    # All the characters that can wear hats can jump and can make it back to the panel.
    # todo: Maybe the most basic logic level should use (CAN_WEAR_HAT_AND_GRAPPLE or CAN_WEAR_HAT_AND_DOUBLE_JUMP)
    #  because CAN_WEAR_HAT on its own requires either a tight jump, or jumping off a small garbage bin than can be
    #  destroyed by accident.
    Area.MOSEISLEY: (CAN_WEAR_HAT, CharacterAbility.IMPERIAL),
    # There is a section where a Stormtrooper helmet needs to be taken across a gap that requires grappling if you want
    # to keep the hat.
    Area.DEATHSTARRESCUE: (CharacterAbility.CAN_WEAR_HAT_AND_GRAPPLE, CharacterAbility.IMPERIAL),
    # In 4-5, there is an Imperial Hat Machine with an Imperial panel that requires grappling across a gap to reach
    # (Level A), so, if the player has no Imperial character, they need a BLASTER character that can wear hats.
    # This additionally covers a later use of an Imperial Hat Machine where the panel is at the top of an elevator
    # (level B), and another later use of an Imperial Hat Machine where the panel is at the end of a Zipup, across a gap
    # (level C).
    Area.DEATHSTARESCAPE: (CharacterAbility.CAN_WEAR_HAT_AND_GRAPPLE, CharacterAbility.IMPERIAL),
    Area.DAGOBAH: (CharacterAbility.ASTROMECH_DROID, None),
    # In 5-5, there is an Imperial Hat Machine with an Imperial panel that requires double-jumping across a gap to
    # reach, so, if the player has no Imperial character, they need a Jedi/Sith that can wear hats.
    # This gets its own flag, instead of being JEDI | CAN_WEAR_HAT, for logic performance reasons. The complexity comes
    # from the fact that characters may have additional flags, but the logic system prefers to store only the combined
    # flag of all currently usable abilities.
    Area.CLOUDCITYTRAP: (CharacterAbility.CAN_WEAR_HAT_AND_DOUBLE_JUMP, CharacterAbility.IMPERIAL),
    # Level A has a Hat Machine where you need to walk to an elevator with the hat.
    Area.CLOUDCITYESCAPE: (CAN_WEAR_HAT, CharacterAbility.IMPERIAL),
    # The level is played in Story with a character than can wear hats instead of needing a bounty hunter.
    Area.JABBASPALACE: (CAN_WEAR_HAT, CharacterAbility.BOUNTY_HUNTER),
}
"""
Chapter completions that require logic that is specific to that chapter.

The first element of each value are the abilities that would normally be used in Story mode.

The second element of each value is an optional alternative ability that can be used instead, but often requires a rarer
ability. 
"""


# todo: Need to consider the Gold Brick shop eventually. Also Bounty Hunter missions. Also Challenges. Also
#  Character/Minikit bonuses.
BONUS_AREAS = [
    # Could require: "Anakin's Pod"
    BonusArea(Area.PODRACE.readable_name, 0x86e144, (30, 31, 32), 0x1, 35, 4, gold_bricks_required=10),
    # There are a number of test levels in LEVELS.TXT that seem to not be counted, so the level IDs for Anakin's Flight
    # do not match what is expected:
    # Intro = 327
    # A = 328
    # B = 329
    # C = 330
    # Outro1 = 331
    # Outro2 = 332
    # Status = 333
    # Could require: "Naboo Starfighter"
    BonusArea(Area.ANAKINSFLIGHT.readable_name, 0x86e3cc, (328, 329, 330), 0x1, 333, 58, gold_bricks_required=30),
    # Could require: "Republic Gunship"
    BonusArea(Area.BONUS_GUNSHIP.readable_name, 0x86e1c8, (96, 97), 0x1, 98, 15, gold_bricks_required=10),
    # Note: The base address may be incorrect/I do not know what the base address is supposed to be.
    # Could require: "Darth Vader" + "Stormtrooper" + "C-3PO"
    BonusArea(Area.ANEWHOPE.readable_name, 0x86e269, (148, 149), 0x8, 150, 29, gold_bricks_required=20),
    BonusArea(Area.BONUS2.readable_name, 0x86e3d8, (310,), 0x1, 311, 59,
              gold_bricks_required=10,
              completion_ability_requirements=(
                      JEDI
                      | BLASTER
                      | BOUNTY_HUNTER
                      | CAN_BUILD_BRICKS
                      | CAN_PULL_LEVERS
                      | CAN_MELEE
                      | CAN_RIDE_VEHICLES
              )),
    BonusArea(Area.BONUS.readable_name, 0x86e3c0, (308,), 0x1, 309, 57,
              gold_bricks_required=50,
              completion_ability_requirements=(
                      JEDI
                      | SITH
                      | BLASTER
                      | BOUNTY_HUNTER
                      | CAN_BUILD_BRICKS
                      | CAN_PULL_LEVERS
                      | CAN_MELEE
                      | CAN_PUSH_OBJECTS
                      | CAN_RIDE_VEHICLES
              )),
    # The bonus level was never completed, so there is just the trailer to watch (which can be skipped immediately).
    # No gold brick for watching the trailer, but it does unlock the shop slot for purchasing Indiana Jones in vanilla
    # It looks like the unfinished Indiana Jones level would have been Area 67, though this is inaccessible.
    BonusArea(Area.LOSTTEMPLE.readable_name, 0x86e505, (), 0x0, -1, 67, gold_brick=False)
]

AREA_ID_TO_BONUS_AREA = {area.area_id: area for area in BONUS_AREAS}
