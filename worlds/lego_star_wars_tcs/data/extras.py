from enum import IntEnum
from typing import TypedDict

__all__ = [
    "Extra",
]


class ExtraInitializer(TypedDict):
    readable_name: str
    localization_id: int
    purchase_cost: int | None



class Extra(IntEnum):
    readable_name: str
    localization_id: int
    purchase_cost: int | None

    def __new__(cls, *args, **kwargs):
        obj = int.__new__(cls, args[0])
        obj._value_ = args[0]
        return obj

    def __init__(self, _id, initializer: ExtraInitializer):
        self.readable_name = initializer["readable_name"]
        self.localization_id = initializer["localization_id"]
        self.purchase_cost = initializer["purchase_cost"]

    EXTRA_TOGGLE =             0, dict(localization_id= 672, purchase_cost=   30000, readable_name="Extra Toggle")
    FERTILIZER =               1, dict(localization_id= 671, purchase_cost=    8000, readable_name="Fertilizer")
    DISGUISE =                 2, dict(localization_id= 668, purchase_cost=   10000, readable_name="Disguise")
    DAISY_CHAINS =             3, dict(localization_id= 677, purchase_cost=    5000, readable_name="Daisy Chains")
    CHEWBACCA_CARRYING_C_3PO = 4, dict(localization_id= 669, purchase_cost=   10000, readable_name="Chewbacca Carrying C-3PO")
    TOW_DEATH_STAR =           5, dict(localization_id= 678, purchase_cost=    5000, readable_name="Tow Death Star")
    SILHOUETTES =              6, dict(localization_id= 698, purchase_cost=   10000, readable_name="Silhouettes")
    BEEP_BEEP =                7, dict(localization_id= 298, purchase_cost=    7500, readable_name="Beep Beep")
    SUPER_GONK =               8, dict(localization_id= 699, purchase_cost=  100000, readable_name="Super Gonk")
    POO_MONEY =                9, dict(localization_id= 296, purchase_cost=  100000, readable_name="Poo Money")
    WALKIE_TALKIE_DISABLE =   10, dict(localization_id=1665, purchase_cost=    5000, readable_name="Walkie Talkie Disable")
    POWER_BRICK_DETECTOR =    11, dict(localization_id=1657, purchase_cost=  125000, readable_name="Power Brick Detector")
    SUPER_SLAP =              12, dict(localization_id=1658, purchase_cost=    5000, readable_name="Super Slap")
    FORCE_GRAPPLE_LEAP =      13, dict(localization_id=1660, purchase_cost=   15000, readable_name="Force Grapple Leap")
    STUD_MAGNET =             14, dict(localization_id= 297, purchase_cost=  100000, readable_name="Stud Magnet")
    DISARM_TROOPERS =         15, dict(localization_id=1662, purchase_cost=  100000, readable_name="Disarm Troopers")
    CHARACTER_STUDS =         16, dict(localization_id=1671, purchase_cost=  100000, readable_name="Character Studs")
    PERFECT_DEFLECT =         17, dict(localization_id=1666, purchase_cost=   20000, readable_name="Perfect Deflect")
    EXPLODING_BLASTER_BOLTS = 18, dict(localization_id=1663, purchase_cost=   20000, readable_name="Exploding Blaster Bolts")
    FORCE_PULL =              19, dict(localization_id=1667, purchase_cost=   12000, readable_name="Force Pull")
    VEHICLE_SMART_BOMB =      20, dict(localization_id=1664, purchase_cost=   15000, readable_name="Vehicle Smart Bomb")
    SUPER_ASTROMECH =         21, dict(localization_id=1668, purchase_cost=   10000, readable_name="Super Astromech")
    SUPER_JEDI_SLAM =         22, dict(localization_id=1670, purchase_cost=   11000, readable_name="Super Jedi Slam")
    SUPER_THERMAL_DETONATOR = 23, dict(localization_id=1661, purchase_cost=   25000, readable_name="Super Thermal Detonator")
    DEFLECT_BOLTS =           24, dict(localization_id=1659, purchase_cost=  150000, readable_name="Deflect Bolts")
    DARK_SIDE =               25, dict(localization_id=1669, purchase_cost=   25000, readable_name="Dark Side")
    SUPER_BLASTERS =          26, dict(localization_id= 682, purchase_cost=   15000, readable_name="Super Blasters")
    FAST_FORCE =              27, dict(localization_id= 685, purchase_cost=   40000, readable_name="Fast Force")
    SUPER_LIGHTSABERS =       28, dict(localization_id= 667, purchase_cost=   40000, readable_name="Super Lightsabers")
    TRACTOR_BEAM =            29, dict(localization_id= 687, purchase_cost=   15000, readable_name="Tractor Beam")
    INVINCIBILITY =           30, dict(localization_id= 664, purchase_cost= 1000000, readable_name="Invincibility")
    SCORE_X2 =                31, dict(localization_id= 666, purchase_cost= 1250000, readable_name="Score x2")
    SELF_DESTRUCT =           32, dict(localization_id= 681, purchase_cost=   25000, readable_name="Self Destruct")
    FAST_BUILD =              33, dict(localization_id= 684, purchase_cost=   30000, readable_name="Fast Build")
    SCORE_X4 =                34, dict(localization_id= 670, purchase_cost= 2500000, readable_name="Score x4")
    REGENERATE_HEARTS =       35, dict(localization_id= 683, purchase_cost=  150000, readable_name="Regenerate Hearts")
    MINIKIT_DETECTOR =        36, dict(localization_id= 665, purchase_cost=  250000, readable_name="Minikit Detector")
    SCORE_X6 =                37, dict(localization_id= 676, purchase_cost= 5000000, readable_name="Score x6")
    SUPER_ZAPPER =            38, dict(localization_id= 688, purchase_cost=   14000, readable_name="Super Zapper")
    BOUNTY_HUNTER_ROCKETS =   39, dict(localization_id= 673, purchase_cost=   20000, readable_name="Bounty Hunter Rockets")
    SCORE_X8 =                40, dict(localization_id= 679, purchase_cost=10000000, readable_name="Score x8")
    SUPER_EWOK_CATAPULT =     41, dict(localization_id= 689, purchase_cost=   25000, readable_name="Super Ewok Catapult")
    INFINITE_TORPEDOS =       42, dict(localization_id= 686, purchase_cost=   25000, readable_name="Infinite Torpedos")
    SCORE_X10 =               43, dict(localization_id= 680, purchase_cost=20000000, readable_name="Score x10")
    ADAPTIVE_DIFFICULTY =     44, dict(localization_id= 690, purchase_cost=None,     readable_name="Adaptive Difficulty")
