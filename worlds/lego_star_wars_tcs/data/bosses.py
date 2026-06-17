from enum import IntEnum, auto
from typing import TypedDict, NotRequired

from .areas import Area
from .characters import Character
from .levels import Level

class DefeatMethod(IntEnum):
    KILL = auto()
    """The character is defeated by killing them, spawning parts etc."""
    COMPLETE_CHAPTER = auto()
    """No character exists, or the chapter ends as soon as the boss is defeated"""
    DESPAWN = auto()
    """The character despawns when defeated, rather than dying"""


class _BossInitializer(TypedDict):
    area: Area
    character: NotRequired[Character]
    readable_name: NotRequired[str]
    defeat_method: DefeatMethod
    level: NotRequired[Level]
    """The level in which a boss character is killed, or despawns, upon being defeated"""


class Boss(IntEnum):
    area: Area
    character: Character | None
    readable_name: str
    defeat_method: DefeatMethod
    level: Level | None

    def __new__(cls, *args, **kwargs):
        obj = int.__new__(cls, args[0])
        obj._value_ = args[0]
        return obj

    def __init__(self, _id, boss_initializer: _BossInitializer):
        self.area = boss_initializer["area"]
        self.character = boss_initializer.get("character")
        self.defeat_method = boss_initializer["defeat_method"]
        if "readable_name" in boss_initializer:
            self.readable_name = boss_initializer["readable_name"]
        else:
            character = self.character
            if character is None:
                raise ValueError("No name or character specified.")
            self.readable_name = character.readable_name
        self.level = boss_initializer.get("level")
        if self.level is not None and self.level not in self.area.levels:
            raise ValueError(f"Level {self.level!r} is not found in area {self.area!r}")
        if self.defeat_method in (DefeatMethod.KILL, DefeatMethod.DESPAWN) and self.level is None:
            raise ValueError("A Level must be specified when the DefeatMethod is KILL or DESPAWN")
    
    @staticmethod
    def from_area(area: Area) -> "Boss | None":
        return _AREA_TO_BOSS.get(area)

    DARTH_MAUL = auto(), dict(area=Area.MAUL,
                              character=Character.DARTH_MAUL,
                              defeat_method=DefeatMethod.COMPLETE_CHAPTER)
    ZAM_WESELL = auto(), dict(area=Area.PURSUIT,
                              readable_name=Character.ZAM_WESELL.readable_name,
                              character=Character.ZAMS_AIRSPEEDER,
                              defeat_method=DefeatMethod.COMPLETE_CHAPTER)
    JANGO_FETT_KAMINO = auto(), dict(area=Area.KAMINO,
                                     character=Character.JANGO_FETT,
                                     defeat_method=DefeatMethod.COMPLETE_CHAPTER)
    JANGO_FETT_JEDI = auto(), dict(area=Area.JEDI,
                                   character=Character.JANGO_FETT,
                                   defeat_method=DefeatMethod.COMPLETE_CHAPTER)
    DOOKU_DOOKU = auto(), dict(area=Area.DOOKU,
                               character=Character.COUNT_DOOKU,
                               defeat_method=DefeatMethod.COMPLETE_CHAPTER)
    DOOKU_CRUISER = auto(), dict(area=Area.CRUISER,
                                 character=Character.COUNT_DOOKU,
                                 defeat_method=DefeatMethod.KILL,
                                 level=Level.CRUISER_C)
    GRIEVOUS = auto(), dict(area=Area.GRIEVOUS,
                            character=Character.GENERAL_GRIEVOUS,
                            defeat_method=DefeatMethod.COMPLETE_CHAPTER)
    ANAKIN = auto(), dict(area=Area.VADER,
                          readable_name="Anakin Skywalker",
                          character=Character.ANAKIN_SKYWALKER_JEDI,
                          defeat_method=DefeatMethod.COMPLETE_CHAPTER)
    SPY = auto(), dict(area=Area.MOSEISLEY,
                       character=Character.IMPERIAL_SPY,
                       defeat_method=DefeatMethod.KILL,
                       level=Level.MOSEISLEY_D)
    DEATH_STAR = auto(), dict(area=Area.DEATHSTARBATTLE,
                              readable_name="Death Star",
                              defeat_method=DefeatMethod.COMPLETE_CHAPTER)
    VADER_DAGOBAH = auto(), dict(area=Area.DAGOBAH,
                                 character=Character.DARTH_VADER,
                                 defeat_method=DefeatMethod.DESPAWN,
                                 level=Level.DAGOBAH_D)
    VADER_TRAP = auto(), dict(area=Area.CLOUDCITYTRAP,
                              character=Character.DARTH_VADER,
                              defeat_method=DefeatMethod.COMPLETE_CHAPTER)
    BOBA_FETT_ESCAPE = auto(), dict(area=Area.CLOUDCITYESCAPE,
                                    character=Character.BOBA_FETT,
                                    defeat_method=DefeatMethod.DESPAWN,
                                    level=Level.CLOUDCITYESCAPE_A)
    RANCOR = auto(), dict(area=Area.JABBASPALACE,
                          character=Character.RANCOR,
                          defeat_method=DefeatMethod.COMPLETE_CHAPTER)
    BOBA_FETT_SARLACC = auto(), dict(area=Area.SARLACCPIT,
                                     character=Character.BOBA_FETT,
                                     defeat_method=DefeatMethod.KILL,
                                     level=Level.SARLACCPIT_A)
    EMPEROR = auto(), dict(area=Area.EMPERORFIGHT,
                           character=Character.THE_EMPEROR,
                           defeat_method=DefeatMethod.COMPLETE_CHAPTER)
    DEATH_STAR_2 = auto(), dict(area=Area.DEATHSTAR2BATTLE,
                                readable_name="Death Star II",
                                defeat_method=DefeatMethod.COMPLETE_CHAPTER)


assert len([boss.area for boss in Boss]) == len({boss.area for boss in Boss}), "Each area can only have one boss."

_AREA_TO_BOSS = {
    boss.area: boss for boss in Boss
}