from dataclasses import dataclass
from typing import ClassVar

from . import VEHICLE_ITEMS_BASE, GenericCharacterData, ItemType
from ..characters import Character
from ...character_ability import *


@dataclass(frozen=True)
class VehicleData(GenericCharacterData):
    run_speed: float
    item_type: ClassVar[ItemType] = "Vehicle"

    def __post_init__(self):

        # Automatically set some implied abilities as a safeguard.
        abilities = self.abilities

        abilities |= IS_A_VEHICLE

        if abilities & ~CharacterAbility.ALL_VEHICLE_ABILITIES != 0:
            raise Exception(f"Vehicles can only use vehicle abilities, but got {abilities}")

        if abilities is not self.abilities:
            # print(f"Updated abilities for {self.name}. Added:\n\t{abilities & ~self.abilities!r}")
            object.__setattr__(self, "abilities", abilities)

    @classmethod
    def ap_item(
            cls,
            character: Character,
            abilities: CharacterAbility,
            run_speed: float,
    ):
        return cls(
            code=character + VEHICLE_ITEMS_BASE,
            name=character.readable_name,
            character=character,
            abilities=abilities,
            run_speed=run_speed,
        )

_vehicle = VehicleData.ap_item

VEHICLE_DATA: list[VehicleData] = [
    _vehicle(Character.ANAKINS_SPEEDER, VEHICLE_BLASTER, 16.0),
    _vehicle(Character.SLAVE_1, VEHICLE_BLASTER, 24.0),
    _vehicle(Character.SNOWSPEEDER, VEHICLE_TOW | VEHICLE_BLASTER, 18.0),
    _vehicle(Character.X_WING, VEHICLE_BLASTER, 24.0),
    _vehicle(Character.TIE_FIGHTER, VEHICLE_BLASTER | VEHICLE_TIE, 24.0),
    _vehicle(Character.MILLENNIUM_FALCON, VEHICLE_BLASTER, 24.0),
    _vehicle(Character.Y_WING, VEHICLE_BLASTER, 24.0),
    _vehicle(Character.TIE_INTERCEPTOR, VEHICLE_TIE | VEHICLE_BLASTER, 24.0),
    _vehicle(Character.TIE_FIGHTER_DARTH_VADER, VEHICLE_BLASTER | VEHICLE_TIE, 24.0),
    _vehicle(Character.IMPERIAL_SHUTTLE, VEHICLE_BLASTER, 24.0),
    _vehicle(Character.TIE_BOMBER, VEHICLE_BLASTER | VEHICLE_TIE, 24.0),
    _vehicle(Character.JEDI_STARFIGHTER_YELLOW, VEHICLE_BLASTER, 21.0),
    _vehicle(Character.ANAKINS_POD, IS_A_VEHICLE, 30.0),
    _vehicle(Character.SEBULBAS_POD, IS_A_VEHICLE, 30.0),
    _vehicle(Character.NABOO_STARFIGHTER, VEHICLE_TOW | VEHICLE_BLASTER, 20.0),
    _vehicle(Character.ZAMS_AIRSPEEDER, VEHICLE_BLASTER, 16.0),
    _vehicle(Character.REPUBLIC_GUNSHIP, VEHICLE_TOW | VEHICLE_BLASTER, 18.0),
    _vehicle(Character.DROID_TRIFIGHTER, VEHICLE_BLASTER, 21.0),
    _vehicle(Character.VULTURE_DROID, VEHICLE_BLASTER, 21.0),
    _vehicle(Character.CLONE_ARCFIGHTER, VEHICLE_BLASTER, 24.0),
    _vehicle(Character.JEDI_STARFIGHTER_RED, VEHICLE_BLASTER, 21.0),
]

VEHICLE_CHARACTER_TO_ITEM_DATA = {
    data.character: data for data in VEHICLE_DATA
}