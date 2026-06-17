from . import ClientComponent
from ..common import StaticUint
from ..common_addresses import IS_CHARACTER_SWAPPING_ENABLED
from ..events import subscribe_event, OnLevelChangeEvent

from ...data.characters import Character
from ...data.levels import Level

_A_VEHICLE_CHARACTER = Character.SEBULBAS_POD
_LUKE_DAGOBAH_ID_ADDR = StaticUint(0x7f198c)


# todo: This could be removed once new logic for Dagobah is implemented, but it could cause problems with how
#  starting chapter ability requirements are determined.
def _fix_luke_skywalker_dagobah(event: OnLevelChangeEvent):
    """
    'Fixes' `Luke Skywalker (Dagobah)` being hardcoded to be unable to lift the X-wing at the end of Dagobah, which is
    required to complete the chapter.

    The 'fix' is performed by overwriting the character ID that the game checks for when in the final level in Dagobah.
    """
    if event.new_level_id == Level.DAGOBAH_C and IS_CHARACTER_SWAPPING_ENABLED.get(event.context):
        _LUKE_DAGOBAH_ID_ADDR.set(event.context, _A_VEHICLE_CHARACTER)
    else:
        _LUKE_DAGOBAH_ID_ADDR.set(event.context, Character.LUKE_SKYWALKER_DAGOBAH)


class LevelSpecificFixes(ClientComponent):
    """
    Various level-specific fixes.
    """
    @subscribe_event
    def on_level_change(self, event: OnLevelChangeEvent):
        _fix_luke_skywalker_dagobah(event)
