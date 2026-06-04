from typing import TypedDict
from enum import IntEnum, IntFlag

from .levels import Level

__all__ = [
    "Area",
    "AreaFlag",
]

class AreaFlag(IntFlag):
    VEHICLE_AREA = 0x1
    ENDING_AREA = 0x2
    BONUS_AREA = 0x4
    VEHICLE_BONUS = VEHICLE_AREA | BONUS_AREA
    SINGLE_BUFFER = 0x8
    CHAPTER = 0x10
    TEST_AREA = 0x20
    HUB_AREA = 0x40
    NO_CHARACTER_COLLISION = 0x80
    COLLECT_ALL_STUDS_BONUS = 0x100
    NO_PICKUP_GRAVITY = 0x200
    OVERRIDE_THINGS_SCENE = 0x400
    NO_GOLD_BRICK = 0x800
    NO_FREEPLAY = 0x1000
    NO_COMPLETION_POINTS = 0x2000
    UNKNOWN_0x4000 = 0x4000
    UNKNOWN_0x8000 = 0x8000


class AreaInitializer(TypedDict):
    episode_index: int
    area_index: int
    flags: AreaFlag
    story_true_jedi: int
    free_play_true_jedi: int
    cheat_id: int
    levels: list[Level]


# noinspection LongLine
class Area(IntEnum):
    episode_index: int
    area_index: int
    flags: AreaFlag
    story_true_jedi: int
    free_play_true_jedi: int
    cheat_id: int
    levels: tuple[Level, ...]

    def __new__(cls, *args, **kwargs):
        obj = int.__new__(cls)
        obj._value_ = args[0]
        return obj

    def __init__(self,
                 _id,
                 area_initializer: AreaInitializer,
                 ):
        self.episode_index = area_initializer["episode_index"]
        self.area_index = area_initializer["area_index"]
        self.flags = area_initializer["flags"]
        self.story_true_jedi = area_initializer["story_true_jedi"]
        self.free_play_true_jedi = area_initializer["free_play_true_jedi"]
        self.cheat_id = area_initializer["cheat_id"]
        self.levels = tuple(area_initializer["levels"])
    NEGOTIATIONS =      0, dict(episode_index= 0, area_index= 0, flags=AreaFlag(0x0010), story_true_jedi=31000, free_play_true_jedi= 64000, cheat_id= 8, levels=[Level.EP1_FAILEDNEG_INTRO1, Level.EP1_FAILEDNEG_INTRO2, Level.NEGOTIATIONS_A, Level.NEGOTIATIONS_B, Level.NEGOTIATIONS_C, Level.FAILEDNEG_OUTRO, Level.NEGOTIATIONS_STATUS])
    GUNGAN =            1, dict(episode_index= 0, area_index= 1, flags=AreaFlag(0x0010), story_true_jedi=44000, free_play_true_jedi= 52000, cheat_id= 9, levels=[Level.GUNGAN_INTRO1, Level.GUNGAN_INTRO2, Level.GUNGAN_A, Level.GUNGAN_B, Level.GUNGAN_C, Level.GUNGAN_E, Level.GUNGAN_OUTRO2, Level.GUNGAN_STATUS])
    PALACERESCUE =      2, dict(episode_index= 0, area_index= 2, flags=AreaFlag(0x0010), story_true_jedi=48000, free_play_true_jedi= 60000, cheat_id=10, levels=[Level.RESCUE_INTRO1, Level.RESCUE_INTRO2, Level.RESCUE_INTRO4, Level.RESCUE_A, Level.RESCUE_B, Level.RESCUE_C, Level.RESCUE_E, Level.RESCUE_OUTRO, Level.RESCUE_STATUS])
    PODSPRINT =         3, dict(episode_index= 0, area_index= 3, flags=AreaFlag(0x0019), story_true_jedi=45000, free_play_true_jedi= 45000, cheat_id=11, levels=[Level.PODSPRINT_A, Level.PODSPRINT_STATUS])
    PODRACE =           4, dict(episode_index=-1, area_index=-1, flags=AreaFlag(0x1001), story_true_jedi=45000, free_play_true_jedi= 45000, cheat_id=-1, levels=[Level.PODRACE_ARRIVAL1, Level.PODRACE_ARRIVAL2, Level.PODRACE_ARRIVAL3, Level.PODRACE_ARRIVAL4, Level.PODRACE_INTRO, Level.PODRACE_B, Level.PODRACE_C, Level.PODRACE_A, Level.PODRACE_OUTRO1, Level.PODRACE_OUTRO2, Level.PODRACE_STATUS])
    RETAKEPALACE =      5, dict(episode_index= 0, area_index= 4, flags=AreaFlag(0x0010), story_true_jedi=60000, free_play_true_jedi=100000, cheat_id=12, levels=[Level.RETAKE_INTRO1, Level.RETAKE_INTRO2, Level.RETAKE_INTRO3, Level.RETAKE_A, Level.RETAKE_B, Level.RETAKE_D, Level.RETAKE_E, Level.RETAKE_F, Level.RETAKE_G, Level.RETAKE_OUTRO, Level.RETAKE_STATUS])
    MAUL =              6, dict(episode_index= 0, area_index= 5, flags=AreaFlag(0x0010), story_true_jedi=31000, free_play_true_jedi= 64000, cheat_id=13, levels=[Level.DARTHMAUL_INTRO, Level.MAUL_A, Level.MAUL_B, Level.MAUL_D, Level.MAUL_E, Level.MAUL_F, Level.MAUL_STATUS])
    E1ENDING =          7, dict(episode_index= 0, area_index= 6, flags=AreaFlag(0x0002), story_true_jedi=    0, free_play_true_jedi=     0, cheat_id=-1, levels=[Level.EPISODE1ENDING_A])
    E1CHARACTERBONUS =  8, dict(episode_index= 0, area_index= 7, flags=AreaFlag(0x0004), story_true_jedi=    0, free_play_true_jedi=     0, cheat_id=-1, levels=[Level.E1CHARACTERBONUS_A, Level.E1CHARACTERBONUS_STATUS])
    E1VEHICLEBONUS =    9, dict(episode_index= 0, area_index= 8, flags=AreaFlag(0x0005), story_true_jedi=    0, free_play_true_jedi=     0, cheat_id=-1, levels=[Level.E1VEHICLEBONUS_A, Level.E1VEHICLEBONUS_STATUS])
    PURSUIT =          10, dict(episode_index= 1, area_index= 0, flags=AreaFlag(0x0211), story_true_jedi=35000, free_play_true_jedi= 45000, cheat_id=14, levels=[Level.PURSUIT_INTRO, Level.PURSUIT_A, Level.PURSUIT_B, Level.PURSUIT_C, Level.PURSUIT_D, Level.PURSUIT_E, Level.PURSUIT_OUTRO, Level.PURSUIT_STATUS])
    KAMINO =           11, dict(episode_index= 1, area_index= 1, flags=AreaFlag(0x0010), story_true_jedi=50000, free_play_true_jedi= 65000, cheat_id=15, levels=[Level.KAMINO_INTRO1, Level.KAMINO_INTRO2, Level.KAMINO_A, Level.KAMINO_C, Level.KAMINO_D, Level.KAMINO_E, Level.KAMINO_F, Level.KAMINO_OUTRO1, Level.KAMINO_OUTRO2, Level.KAMINO_STATUS])
    FACTORY =          12, dict(episode_index= 1, area_index= 2, flags=AreaFlag(0x0010), story_true_jedi=40000, free_play_true_jedi= 55000, cheat_id=16, levels=[Level.FACTORY_INTRO1, Level.FACTORY_INTRO2, Level.FACTORY_INTRO3, Level.FACTORY_A, Level.FACTORY_B, Level.FACTORY_D, Level.FACTORY_E, Level.FACTORY_F, Level.FACTORY_G, Level.FACTORY_STATUS])
    JEDI =             13, dict(episode_index= 1, area_index= 3, flags=AreaFlag(0x0010), story_true_jedi= 8000, free_play_true_jedi= 16000, cheat_id=17, levels=[Level.JEDI_INTRO, Level.JEDI_B, Level.JEDI_OUTRO, Level.JEDI_STATUS])
    GUNSHIP =          14, dict(episode_index= 1, area_index= 4, flags=AreaFlag(0x0011), story_true_jedi=30000, free_play_true_jedi= 40000, cheat_id=18, levels=[Level.GUNSHIP_A, Level.GUNSHIP_B, Level.GUNSHIP_STATUS])
    BONUS_GUNSHIP =    15, dict(episode_index=-1, area_index=-1, flags=AreaFlag(0x1081), story_true_jedi=50000, free_play_true_jedi=100000, cheat_id=-1, levels=[Level.BONUS_GUNSHIP_A, Level.BONUS_GUNSHIP_B, Level.BONUS_GUNSHIP_STATUS])
    DOOKU =            16, dict(episode_index= 1, area_index= 5, flags=AreaFlag(0x0010), story_true_jedi=10000, free_play_true_jedi= 22000, cheat_id=19, levels=[Level.DOOKU_INTRO, Level.DOOKU_B, Level.DOOKU_C, Level.DOOKU_OUTRO, Level.DOOKU_STATUS])
    E2ENDING =         17, dict(episode_index= 1, area_index= 6, flags=AreaFlag(0x0002), story_true_jedi=    0, free_play_true_jedi=     0, cheat_id=-1, levels=[Level.EP2_ENDING1, Level.EP2_ENDING2])
    E2CHARACTERBONUS = 18, dict(episode_index= 1, area_index= 7, flags=AreaFlag(0x0004), story_true_jedi=    0, free_play_true_jedi=     0, cheat_id=-1, levels=[Level.E2CHARACTERBONUS_A, Level.E2CHARACTERBONUS_STATUS])
    E2VEHICLEBONUS =   19, dict(episode_index= 1, area_index= 8, flags=AreaFlag(0x0205), story_true_jedi=    0, free_play_true_jedi=     0, cheat_id=-1, levels=[Level.E2VEHICLEBONUS_A, Level.E2VEHICLEBONUS_STATUS])
    DOGFIGHT =         20, dict(episode_index= 2, area_index= 0, flags=AreaFlag(0x0019), story_true_jedi=75000, free_play_true_jedi= 75000, cheat_id=20, levels=[Level.DOGFIGHT_A, Level.DOGFIGHT_STATUS])
    CRUISER =          21, dict(episode_index= 2, area_index= 1, flags=AreaFlag(0x0010), story_true_jedi=60000, free_play_true_jedi= 80000, cheat_id=21, levels=[Level.CRUISER_A, Level.CRUISER_B, Level.CRUISER_C, Level.CRUISER_D, Level.CRUISER_E, Level.CRUISER_F, Level.CRUISER_G, Level.CRUISER_OUTRO1, Level.CRUISER_OUTRO2, Level.CRUISER_STATUS])
    GRIEVOUS =         22, dict(episode_index= 2, area_index= 2, flags=AreaFlag(0x0018), story_true_jedi= 3300, free_play_true_jedi=  5000, cheat_id=22, levels=[Level.GRIEVOUS_A, Level.GRIEVOUS_STATUS])
    KASHYYYK =         23, dict(episode_index= 2, area_index= 3, flags=AreaFlag(0x0010), story_true_jedi=65000, free_play_true_jedi= 90000, cheat_id=23, levels=[Level.KASHYYYK_A, Level.KASHYYYK_B, Level.KASHYYYK_C, Level.KASHYYYK_D, Level.KASHYYYK_STATUS])
    TEMPLE =           24, dict(episode_index= 2, area_index= 4, flags=AreaFlag(0x0010), story_true_jedi=35000, free_play_true_jedi= 75000, cheat_id=24, levels=[Level.TEMPLE_INTRO, Level.TEMPLE_INTRO2, Level.TEMPLE_A, Level.TEMPLE_B, Level.TEMPLE_C, Level.TEMPLE_STATUS])
    VADER =            25, dict(episode_index= 2, area_index= 5, flags=AreaFlag(0x0010), story_true_jedi=25000, free_play_true_jedi= 45000, cheat_id=25, levels=[Level.VADER_INTRO, Level.VADER_A, Level.VADER_B, Level.VADER_C, Level.VADER_STATUS])
    E3ENDING =         26, dict(episode_index= 2, area_index= 6, flags=AreaFlag(0x0002), story_true_jedi=    0, free_play_true_jedi=     0, cheat_id=-1, levels=[Level.EP3_ENDING_MEDICROOM, Level.EP3_ENDING_MUSTAFAR, Level.EP3_ENDING_VADER])
    E3CHARACTERBONUS = 27, dict(episode_index= 2, area_index= 7, flags=AreaFlag(0x0004), story_true_jedi=    0, free_play_true_jedi=     0, cheat_id=-1, levels=[Level.E3CHARACTERBONUS_A, Level.E3CHARACTERBONUS_STATUS])
    E3VEHICLEBONUS =   28, dict(episode_index= 2, area_index= 8, flags=AreaFlag(0x0005), story_true_jedi=    0, free_play_true_jedi=     0, cheat_id=-1, levels=[Level.E3VEHICLEBONUS_A, Level.E3VEHICLEBONUS_STATUS])
    ANEWHOPE =         29, dict(episode_index=-1, area_index=-1, flags=AreaFlag(0x0000), story_true_jedi=40000, free_play_true_jedi= 70000, cheat_id=-1, levels=[Level.ANEWHOPE_INTRO, Level.ANEWHOPE_A, Level.ANEWHOPE_B, Level.ANEWHOPE_STATUS])
    BLOCKADERUNNER =   30, dict(episode_index= 3, area_index= 0, flags=AreaFlag(0x0010), story_true_jedi=28000, free_play_true_jedi= 40000, cheat_id=26, levels=[Level.BLOCKADERUNNER_INTRO1, Level.BLOCKADERUNNER_INTRO2, Level.BLOCKADERUNNER_A, Level.BLOCKADERUNNER_B, Level.BLOCKADERUNNER_C, Level.BLOCKADERUNNER_D, Level.BLOCKADERUNNER_OUTRO1, Level.BLOCKADERUNNER_OUTRO2, Level.BLOCKADERUNNER_STATUS])
    TATOOINE =         31, dict(episode_index= 3, area_index= 1, flags=AreaFlag(0x0010), story_true_jedi=60000, free_play_true_jedi= 90000, cheat_id=27, levels=[Level.TATOOINE_INTRO, Level.TATOOINE_A, Level.TATOOINE_B, Level.TATOOINE_C, Level.TATOOINE_D, Level.TATOOINE_E, Level.TATOOINE_OUTRO, Level.TATOOINE_STATUS])
    MOSEISLEY =        32, dict(episode_index= 3, area_index= 2, flags=AreaFlag(0x0010), story_true_jedi=60000, free_play_true_jedi=100000, cheat_id=28, levels=[Level.MOSEISLEY_INTRO, Level.MOSEISLEY_A, Level.MOSEISLEY_B, Level.MOSEISLEY_C, Level.MOSEISLEY_D, Level.MOSEISLEY_E, Level.MOSEISLEY_OUTRO1, Level.MOSEISLEY_OUTRO2, Level.MOSEISLEY_OUTRO3, Level.MOSEISLEY_STATUS])
    DEATHSTARRESCUE =  33, dict(episode_index= 3, area_index= 3, flags=AreaFlag(0x0010), story_true_jedi=60000, free_play_true_jedi= 80000, cheat_id=29, levels=[Level.DEATHSTARRESCUE_INTRO1, Level.DEATHSTARRESCUE_INTRO2, Level.DEATHSTARRESCUE_A, Level.DEATHSTARRESCUE_B, Level.DEATHSTARRESCUE_C, Level.DEATHSTARRESCUE_D, Level.DEATHSTARRESCUE_E, Level.DEATHSTARRESCUE_STATUS])
    DEATHSTARESCAPE =  34, dict(episode_index= 3, area_index= 4, flags=AreaFlag(0x0010), story_true_jedi=45000, free_play_true_jedi= 65000, cheat_id=30, levels=[Level.DEATHSTARESCAPE_INTRO, Level.DEATHSTARESCAPE_A, Level.DEATHSTARESCAPE_B, Level.DEATHSTARESCAPE_C, Level.DEATHSTARESCAPE_D, Level.DEATHSTARESCAPE_OUTRO, Level.DEATHSTARESCAPE_STATUS])
    DEATHSTARBATTLE =  35, dict(episode_index= 3, area_index= 5, flags=AreaFlag(0x0091), story_true_jedi=30000, free_play_true_jedi= 45000, cheat_id=31, levels=[Level.DEATHSTARBATTLE_INTRO1, Level.DEATHSTARBATTLE_INTRO2, Level.DEATHSTARBATTLE_INTRO3, Level.DEATHSTARBATTLE_INTRO4, Level.DEATHSTARBATTLE_A, Level.DEATHSTARBATTLE_B, Level.DEATHSTARBATTLE_C, Level.DEATHSTARBATTLE_D, Level.DEATHSTARBATTLE_MIDTRO, Level.DEATHSTARBATTLE_OUTRO, Level.DEATHSTARBATTLE_STATUS])
    E4ENDING =         36, dict(episode_index= 3, area_index= 6, flags=AreaFlag(0x0002), story_true_jedi=    0, free_play_true_jedi=     0, cheat_id=-1, levels=[Level.EPISODE4ENDING_A])
    E4CHARACTERBONUS = 37, dict(episode_index= 3, area_index= 7, flags=AreaFlag(0x0004), story_true_jedi=    0, free_play_true_jedi=     0, cheat_id=-1, levels=[Level.E4CHARACTERBONUS_A, Level.E4CHARACTERBONUS_STATUS])
    E4VEHICLEBONUS =   38, dict(episode_index= 3, area_index= 8, flags=AreaFlag(0x000d), story_true_jedi=    0, free_play_true_jedi=     0, cheat_id=-1, levels=[Level.E4VEHICLEBONUS_A, Level.E4VEHICLEBONUS_STATUS])
    HOTHBATTLE =       39, dict(episode_index= 4, area_index= 0, flags=AreaFlag(0x0011), story_true_jedi=25000, free_play_true_jedi= 35000, cheat_id=32, levels=[Level.HOTHBATTLE_INTRO1, Level.HOTHBATTLE_INTRO2, Level.HOTHBATTLE_INTRO3, Level.HOTHBATTLE_INTRO4, Level.HOTHBATTLE_A, Level.HOTHBATTLE_B, Level.HOTHBATTLE_C, Level.HOTHBATTLE_D, Level.HOTHBATTLE_E, Level.HOTHBATTLE_OUTRO, Level.HOTHBATTLE_STATUS])
    HOTHESCAPE =       40, dict(episode_index= 4, area_index= 1, flags=AreaFlag(0x0010), story_true_jedi=40000, free_play_true_jedi= 80000, cheat_id=33, levels=[Level.HOTHESCAPE_INTRO, Level.HOTHESCAPE_A, Level.HOTHESCAPE_B, Level.HOTHESCAPE_C, Level.HOTHESCAPE_D, Level.HOTHESCAPE_OUTRO1, Level.HOTHESCAPE_OUTRO2, Level.HOTHESCAPE_STATUS])
    ASTEROIDCHASE =    41, dict(episode_index= 4, area_index= 2, flags=AreaFlag(0x0291), story_true_jedi=30000, free_play_true_jedi= 48000, cheat_id=34, levels=[Level.ASTEROIDCHASE_INTRO, Level.ASTEROIDCHASE_D, Level.ASTEROIDCHASE_A, Level.ASTEROIDCHASE_B, Level.ASTEROIDCHASE_C, Level.ASTEROIDCHASE_MIDTRO, Level.ASTEROIDCHASE_OUTRO, Level.ASTEROIDCHASE_STATUS])
    DAGOBAH =          42, dict(episode_index= 4, area_index= 3, flags=AreaFlag(0x0010), story_true_jedi=52000, free_play_true_jedi= 72000, cheat_id=35, levels=[Level.DAGOBAH_INTRO, Level.DAGOBAH_A, Level.DAGOBAH_B, Level.DAGOBAH_C, Level.DAGOBAH_D, Level.DAGOBAH_E, Level.DAGOBAH_OUTRO2, Level.DAGOBAH_STATUS])
    CLOUDCITYTRAP =    43, dict(episode_index= 4, area_index= 4, flags=AreaFlag(0x0010), story_true_jedi=14000, free_play_true_jedi= 22000, cheat_id=37, levels=[Level.CLOUDCITYTRAP_INTRO, Level.CLOUDCITYTRAP_A, Level.CLOUDCITYTRAP_B, Level.CLOUDCITYTRAP_C, Level.CLOUDCITYTRAP_OUTRO, Level.CLOUDCITYTRAP_STATUS])
    CLOUDCITYESCAPE =  44, dict(episode_index= 4, area_index= 5, flags=AreaFlag(0x0010), story_true_jedi=34000, free_play_true_jedi= 60000, cheat_id=36, levels=[Level.CLOUDCITYESCAPE_INTRO1, Level.CLOUDCITYESCAPE_INTRO2, Level.CLOUDCITYESCAPE_A, Level.CLOUDCITYESCAPE_B, Level.CLOUDCITYESCAPE_C, Level.CLOUDCITYESCAPE_OUTRO, Level.CLOUDCITYESCAPE_STATUS])
    E5ENDING =         45, dict(episode_index= 4, area_index= 6, flags=AreaFlag(0x0002), story_true_jedi=    0, free_play_true_jedi=     0, cheat_id=-1, levels=[Level.EPISODE5ENDING_A])
    E5CHARACTERBONUS = 46, dict(episode_index= 4, area_index= 7, flags=AreaFlag(0x0004), story_true_jedi=    0, free_play_true_jedi=     0, cheat_id=-1, levels=[Level.E5CHARACTERBONUS_A, Level.E5CHARACTERBONUS_STATUS])
    E5VEHICLEBONUS =   47, dict(episode_index= 4, area_index= 8, flags=AreaFlag(0x000d), story_true_jedi=    0, free_play_true_jedi=     0, cheat_id=-1, levels=[Level.E5VEHICLEBONUS_A, Level.E5VEHICLEBONUS_STATUS])
    JABBASPALACE =     48, dict(episode_index= 5, area_index= 0, flags=AreaFlag(0x0010), story_true_jedi=43000, free_play_true_jedi= 60000, cheat_id=38, levels=[Level.JABBASPALACE_INTRO1, Level.JABBASPALACE_INTRO2, Level.JABBASPALACE_A, Level.JABBASPALACE_B, Level.JABBASPALACE_D, Level.JABBASPALACE_E, Level.JABBASPALACE_MIDTRO2, Level.JABBASPALACE_OUTRO, Level.JABBASPALACE_STATUS])
    SARLACCPIT =       49, dict(episode_index= 5, area_index= 1, flags=AreaFlag(0x0010), story_true_jedi=50000, free_play_true_jedi= 65000, cheat_id=39, levels=[Level.SARLACCPIT_INTRO, Level.SARLACCPIT_A, Level.SARLACCPIT_B, Level.SARLACCPIT_C, Level.SARLACCPIT_OUTRO, Level.SARLACCPIT_STATUS])
    SPEEDERCHASE =     50, dict(episode_index= 5, area_index= 2, flags=AreaFlag(0x0018), story_true_jedi=55000, free_play_true_jedi= 70000, cheat_id=40, levels=[Level.SPEEDERCHASE_A, Level.SPEEDERCHASE_STATUS])
    ENDORBATTLE =      51, dict(episode_index= 5, area_index= 3, flags=AreaFlag(0x0010), story_true_jedi=90000, free_play_true_jedi=110000, cheat_id=41, levels=[Level.ENDORBATTLE_INTRO, Level.ENDORBATTLE_A, Level.ENDORBATTLE_B, Level.ENDORBATTLE_C, Level.ENDORBATTLE_D, Level.ENDORBATTLE_OUTRO, Level.ENDORBATTLE_STATUS])
    EMPERORFIGHT =     52, dict(episode_index= 5, area_index= 4, flags=AreaFlag(0x0010), story_true_jedi=35000, free_play_true_jedi= 80000, cheat_id=43, levels=[Level.EMPERORFIGHT_INTRO, Level.EMPERORFIGHT_A, Level.EMPERORFIGHT_B, Level.EMPERORFIGHT_STATUS])
    DEATHSTAR2BATTLE = 53, dict(episode_index= 5, area_index= 5, flags=AreaFlag(0x0291), story_true_jedi=35000, free_play_true_jedi= 40000, cheat_id=42, levels=[Level.DEATHSTAR2BATTLE_INTRO, Level.DEATHSTAR2BATTLE_A, Level.DEATHSTAR2BATTLE_B, Level.DEATHSTAR2BATTLE_C, Level.DEATHSTAR2BATTLE_D, Level.DEATHSTAR2BATTLE_E, Level.DEATHSTAR2BATTLE_F, Level.DEATHSTAR2BATTLE_G, Level.DEATHSTAR2BATTLE_MIDTRO, Level.DEATHSTAR2BATTLE_OUTRO, Level.DEATHSTAR2BATTLE_STATUS])
    E6ENDING =         54, dict(episode_index= 5, area_index= 6, flags=AreaFlag(0x0002), story_true_jedi=    0, free_play_true_jedi=     0, cheat_id=-1, levels=[Level.EPISODE6ENDING_A, Level.EPISODE6ENDING_B])
    E6CHARACTERBONUS = 55, dict(episode_index= 5, area_index= 7, flags=AreaFlag(0x0004), story_true_jedi=    0, free_play_true_jedi=     0, cheat_id=-1, levels=[Level.E6CHARACTERBONUS_A, Level.E6CHARACTERBONUS_STATUS])
    E6VEHICLEBONUS =   56, dict(episode_index= 5, area_index= 8, flags=AreaFlag(0x000d), story_true_jedi=    0, free_play_true_jedi=     0, cheat_id=-1, levels=[Level.E6VEHICLEBONUS_A, Level.E6VEHICLEBONUS_STATUS])
    BONUS =            57, dict(episode_index=-1, area_index=-1, flags=AreaFlag(0x010c), story_true_jedi=    0, free_play_true_jedi=     0, cheat_id=-1, levels=[Level.NEW_TOWN, Level.NEW_TOWN_STATUS])
    ANAKINSFLIGHT =    58, dict(episode_index=-1, area_index=-1, flags=AreaFlag(0x0281), story_true_jedi=20000, free_play_true_jedi= 30000, cheat_id=-1, levels=[Level.ANAKINSFLIGHT_INTRO, Level.ANAKINSFLIGHT_A, Level.ANAKINSFLIGHT_B, Level.ANAKINSFLIGHT_C, Level.ANAKINSFLIGHT_OUTRO1, Level.ANAKINSFLIGHT_OUTRO2, Level.ANAKINSFLIGHT_STATUS])
    BONUS2 =           59, dict(episode_index=-1, area_index=-1, flags=AreaFlag(0x010c), story_true_jedi=    0, free_play_true_jedi=     0, cheat_id=-1, levels=[Level.LEGO_CITY, Level.LEGO_CITY_STATUS])
    SENATE =           60, dict(episode_index=-1, area_index=-1, flags=AreaFlag(0x2804), story_true_jedi=    0, free_play_true_jedi=     0, cheat_id=-1, levels=[Level.SENATE_A, Level.SENATE_STATUS])
    UTAPAU =           61, dict(episode_index=-1, area_index=-1, flags=AreaFlag(0x2804), story_true_jedi=    0, free_play_true_jedi=     0, cheat_id=-1, levels=[Level.UTAPAU_A, Level.UTAPAU_STATUS])
    HOTH =             62, dict(episode_index=-1, area_index=-1, flags=AreaFlag(0x2804), story_true_jedi=    0, free_play_true_jedi=     0, cheat_id=-1, levels=[Level.HOTH_A, Level.HOTH_STATUS])
    NB_KAMINO =        63, dict(episode_index=-1, area_index=-1, flags=AreaFlag(0x2804), story_true_jedi=    0, free_play_true_jedi=     0, cheat_id=-1, levels=[Level.NB_KAMINO_A, Level.NB_KAMINO_STATUS])
    NB_KASHYYYK =      64, dict(episode_index=-1, area_index=-1, flags=AreaFlag(0x2804), story_true_jedi=    0, free_play_true_jedi=     0, cheat_id=-1, levels=[Level.NB_KASHYYYK_A, Level.NB_KASHYYYK_STATUS])
    NB_DAGOBAH =       65, dict(episode_index=-1, area_index=-1, flags=AreaFlag(0x2804), story_true_jedi=    0, free_play_true_jedi=     0, cheat_id=-1, levels=[Level.NB_DAGOBAH_A, Level.NB_DAGOBAH_STATUS])
    MAP =              66, dict(episode_index=-1, area_index=-1, flags=AreaFlag(0x0048), story_true_jedi=    0, free_play_true_jedi=     0, cheat_id=-1, levels=[Level.MAP])
    LOSTTEMPLE =       67, dict(episode_index=-1, area_index=-1, flags=AreaFlag(0x2c00), story_true_jedi=    0, free_play_true_jedi=     0, cheat_id=-1, levels=[Level.LOSTTEMPLE_A])
