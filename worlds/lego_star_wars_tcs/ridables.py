from .constants import CharacterAbility
from .data.areas import Area
from .data.characters import Character


class Ridable:
    user_facing_name: str
    character: Character
    chapter_areas: tuple[Area, ...]
    bonus_areas: tuple[Area, ...]
    is_in_cantina: bool

    def __init__(self,
                 character: Character,
                 *areas: Area,
                 ):
        self.user_facing_name = character.readable_name
        self.character = character
        chapters = []
        bonuses = []
        unknown_areas = []
        for area in areas:
            if area.is_chapter():
                chapters.append(area)
            elif area.is_bonus_room_bonus():
                bonuses.append(area)
            elif area is Area.MAP:
                self.is_in_cantina = True
            else:
                unknown_areas.append(area)
        if unknown_areas:
            raise ValueError(f"Unknown areas for ridable {character!r}: {unknown_areas}")
        self.chapter_areas = tuple(chapters)
        self.bonus_areas = tuple(bonuses)

    @property
    def location_name(self):
        return f"Ride {self.user_facing_name}"


# There is apparently a resident ATAT in HOTHESCAPE/5-2?
_RIDABLES: tuple[Ridable, ...] = (
    Ridable(Character.STAP2, Area.NEGOTIATIONS),
    Ridable(Character.SPEEDER_LAND, Area.TATOOINE, Area.MOSEISLEY, Area.BONUS, Area.BONUS2),
    # This is in the files for New Town, but does not appear to be present.
    Ridable(Character.WOOKIEFLYER, Area.BONUS2),
    # There is also a Dewback out-of-bounds/unloaded in 4-3 MOSEISLEY_B.
    Ridable(Character.DEWBACK, Area.TATOOINE, Area.MOSEISLEY, Area.BONUS, Area.BONUS2),
    # Orange Car.
    # In 4-1, requires destroying Silver Bricks + (Imperial Panel or Bounty Hunter Panel)
    Ridable(Character.MOONCAR, Area.BLOCKADERUNNER, Area.BONUS, Area.BONUS2),
    Ridable(Character.LIFEBOAT, Area.BONUS),
    Ridable(Character.FIRETRUCK, Area.BONUS),
    Ridable(Character.BASKETCANNON, Area.BONUS),
    Ridable(Character.CLONEWALKER, Area.KASHYYYK, Area.BONUS),
    # Red Car from Cloud City.
    Ridable(Character.CLOUDCAR, Area.CLOUDCITYESCAPE, Area.BONUS, Area.BONUS2),
    Ridable(Character.TAUNTAUN, Area.HOTHESCAPE, Area.BONUS, Area.BONUS2),
    # 'Milk Van'.
    # In New Town, requires destroying a house (melee OK)
    # In 4-1, requires protocol droid + jedi + (Bounty Hunter panel or Imperial Panel) (basically the same as the Power
    #   Brick)
    Ridable(Character.TOWNCAR, Area.BLOCKADERUNNER, Area.BONUS, Area.BONUS2),
    # In 5-4 there is one Tractor used to get the Power Brick, requiring SITH, but there is a later Tractor that only
    # requires JEDI
    Ridable(Character.TRACTOR, Area.DAGOBAH, Area.ENDORBATTLE, Area.BONUS, Area.BONUS2),
    Ridable(Character.BANTHA, Area.TATOOINE, Area.BONUS, Area.BONUS2),
    Ridable(Character.ATST, Area.MOSEISLEY, Area.SPEEDERCHASE, Area.ENDORBATTLE, Area.BONUS2),
    Ridable(Character.SERVICE_CAR, Area.RETAKEPALACE, Area.MAUL, Area.DEATHSTARESCAPE),
    Ridable(Character.FLASHSPEEDER, Area.RETAKEPALACE),
    Ridable(Character.GRABBERCONTROL,
            Area.BLOCKADERUNNER, Area.DEATHSTARRESCUE, Area.DEATHSTARESCAPE, Area.CLOUDCITYTRAP, Area.CLOUDCITYESCAPE),
    Ridable(Character.MOSCANNON, Area.MOSEISLEY),
    # Note: Also in the HOTH NEWBONUS, which is not part of the randomizer currently.
    # This is in the files for 6-3, but if it exists, I don't know where it is.
    Ridable(Character.TROOPERCANNON, Area.HOTHESCAPE, Area.CLOUDCITYTRAP),
    # This is in the files, but I'm not sure this exists?
    # _Ridable("HeavyRepeatingCannon", "Hoth Heavy Repeating Cannon", 0, "5-2"),
    # The one that is used to launch C-3PO.
    Ridable(Character.SNOWMOB, Area.HOTHESCAPE),
    Ridable(Character.CATAPULT, Area.ENDORBATTLE),
    Ridable(Character.CANNON, Area.SARLACCPIT),
    Ridable(Character.BIGGUN, Area.SARLACCPIT),
    # Requires pulling a lever OR destroying barrels and building bricks.
    Ridable(Character.MAPCAR, Area.MAP),
    Ridable(Character.SPEEDERBIKE, Area.SPEEDERCHASE),
    # Apparently there is also one in HOTHESCAPE/5-2?
    Ridable(Character.ATAT, Area.SPEEDERCHASE),
    Ridable(Character.BOMARRMONK, Area.JABBASPALACE),
)

RIDABLES_BY_NAME = {ridable.user_facing_name: ridable for ridable in _RIDABLES}
del _RIDABLES

# Most ridables can be reached with only the characters that are needed to complete the chapter in Story.
RIDABLES_REQUIREMENTS: dict[str, dict[str, tuple[CharacterAbility, ...]]] = {
    "4-1": {
        # The car is hidden within Silver Bricks.
        "Moon Car": (CharacterAbility.BOUNTY_HUNTER,),
        # The car is at the end of a hallway that needs a Bounty Hunter or Imperial to access.
        # A Protocol Droid Panel must be used to remove a force field, and a Jedi must be used to spawn the plants that
        # spawn the Town Car bricks when destroyed.
        "Town Car": (
            CharacterAbility.JEDI | CharacterAbility.BOUNTY_HUNTER,
            CharacterAbility.JEDI | CharacterAbility.IMPERIAL,
        ),
    },
    "LEGO City": {
        # The car is hidden within Silver Bricks, and then needs to be built.
        "Moon Car": (CharacterAbility.BOUNTY_HUNTER | CharacterAbility.CAN_BUILD_BRICKS,),
        # To access the first part, levers need to be pulled, then force is needed to move a part into place, and build
        # bricks is needed to build the final part.
        "Wookie Flyer": (CharacterAbility.JEDI | CharacterAbility.CAN_BUILD_BRICKS | CharacterAbility.CAN_PULL_LEVERS,),
        # A house needs to be destroyed to reveal the parts and then a Jedi is needed to assemble the AT-ST.
        "AT-ST": (
            CharacterAbility.JEDI | CharacterAbility.CAN_MELEE,
            CharacterAbility.JEDI | CharacterAbility.BLASTER,
        ),
        # A house needs to be destroyed to reveal the parts and then the Tractor needs to be built.
        "Tractor": (
            CharacterAbility.CAN_MELEE | CharacterAbility.CAN_BUILD_BRICKS,
            CharacterAbility.BLASTER | CharacterAbility.CAN_BUILD_BRICKS,
        ),
        # Either The AT-ST or a Bounty Hunter can destroy the obstacles in the way of getting to the Landspeeder.
        "Landspeeder": (
            CharacterAbility.JEDI | CharacterAbility.CAN_MELEE,
            CharacterAbility.JEDI | CharacterAbility.BLASTER,
            CharacterAbility.BOUNTY_HUNTER,
        ),
        # There are Dewbacks and Banthas close enough to the fences that there is no requirement to destroy or jump over
        # the fences. The CharacterAbility.CAN_RIDE_VEHICLES that is added to every Ridable location is enough to
        # guarantee that the player has at least one character that can enter LEGO City.
    },
    "New Town": {
        # The car is hidden within Silver Bricks and then must be built.
        "Moon Car": (CharacterAbility.BOUNTY_HUNTER | CharacterAbility.CAN_BUILD_BRICKS,),
        # The boat needs fixing.
        "Lifeboat": (CharacterAbility.CAN_BUILD_BRICKS,),
        # The house and bins need destroying, and then the car needs to be built.
        "Town Car": (
            CharacterAbility.CAN_MELEE | CharacterAbility.CAN_BUILD_BRICKS,
            CharacterAbility.BLASTER | CharacterAbility.CAN_BUILD_BRICKS,
        ),
        # A small building needs to be destroyed, and then the tractor needs to be built.
        "Tractor": (
            CharacterAbility.CAN_MELEE | CharacterAbility.CAN_BUILD_BRICKS,
            CharacterAbility.BLASTER | CharacterAbility.CAN_BUILD_BRICKS,
        ),
        # There is a Tauntaun just barely close enough to the fence that there is no need for a character that can jump
        # or destroy the fences, though all characters that can ride vehicles can also jump.
    },
    "cantina": {
        # There are two cars, one is accessed by destroying garbage cans and then building it, and the other is accessed
        # by pulling a lever.
        "Cantina Car": (
            CharacterAbility.CAN_MELEE | CharacterAbility.CAN_BUILD_BRICKS,
            CharacterAbility.BLASTER | CharacterAbility.CAN_BUILD_BRICKS,
            CharacterAbility.CAN_PULL_LEVERS,
        )
    }
}
assert all(ridable in RIDABLES_BY_NAME
           for chapter_ridables in RIDABLES_REQUIREMENTS.values()
           for ridable in chapter_ridables)


def get_ridable_requirements(area: Area, ridable_name: str) -> tuple[CharacterAbility, ...]:
    # todo: Requiring CAN_RIDE_VEHICLES is not strictly necessary currently because the player is always forced to start
    #  with a Jedi.
    requirements = RIDABLES_REQUIREMENTS.get(area, {}).get(ridable_name, ())
    if not requirements:
        return (CharacterAbility.CAN_RIDE_VEHICLES,)
    else:
        return tuple(CharacterAbility.CAN_RIDE_VEHICLES | ability for ability in requirements)


def _make_lookups() -> tuple[dict[Area, list[Ridable]], dict[Area, list[Ridable]]]:
    from collections import defaultdict
    chapter_to_ridable = defaultdict(list)
    bonus_to_ridable = defaultdict(list)
    for ridable in RIDABLES_BY_NAME.values():
        for chapter in ridable.chapter_areas:
            chapter_to_ridable[chapter].append(ridable)
        for bonus in ridable.bonus_areas:
            bonus_to_ridable[bonus].append(ridable)
    return dict(chapter_to_ridable), dict(bonus_to_ridable)


CHAPTER_TO_RIDABLES: dict[Area, list[Ridable]]
BONUS_TO_RIDABLES: dict[Area, list[Ridable]]
CHAPTER_TO_RIDABLES, BONUS_TO_RIDABLES = _make_lookups()
del _make_lookups
