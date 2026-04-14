from . import ClientComponent
from ..common import StaticUint
from ..common_addresses import IS_CHARACTER_SWAPPING_ENABLED
from ..events import subscribe_event, OnLevelChangeEvent

from ...items import CHARACTERS_AND_VEHICLES_BY_NAME

LUKE_DAGOBAH_ID = CHARACTERS_AND_VEHICLES_BY_NAME["Luke Skywalker (Dagobah)"].character_index
A_VEHICLE_CHARACTER_ID = CHARACTERS_AND_VEHICLES_BY_NAME["Sebulba's Pod"].character_index

LEVEL_ID_DAGOBAH_H = 240

LUKE_DAGOBAH_ID_ADDR = StaticUint(0x7f198c)


class LukeDagobahFix(ClientComponent):
    """
    'Fixes' `Luke Skywalker (Dagobah)` being hardcoded to be unable to lift the X-Wing at the end of Dagobah, which is
    required to complete the chapter.

    The 'fix' is performed by overwriting the character ID that the game checks for when in the final level in Dagobah.
    """
    @subscribe_event
    def on_level_change(self, event: OnLevelChangeEvent):
        if event.new_level_id == LEVEL_ID_DAGOBAH_H and IS_CHARACTER_SWAPPING_ENABLED.get(event.context):
            LUKE_DAGOBAH_ID_ADDR.set(event.context, A_VEHICLE_CHARACTER_ID)
        else:
            LUKE_DAGOBAH_ID_ADDR.set(event.context, LUKE_DAGOBAH_ID)
