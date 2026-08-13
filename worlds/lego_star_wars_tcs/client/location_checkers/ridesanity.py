from . import ClientComponent
from ..common_addresses import CURRENT_AREA_ADDRESS
from ..events import subscribe_event, OnReceiveSlotDataEvent, OnAreaChangeEvent, OnPlayerCharacterIdChangeEvent
from ..type_aliases import ApLocationId, TCSContext
from ...ridables import BONUS_TO_RIDABLES

from ...options import GoalChapterLocationsMode, Ridesanity

from ...data.areas import Area, BONUS_ROOM_BONUSES
from ...data.characters import Character
from ...data.locations import LOCATION_NAME_TO_ID
from ...data.logic import CHAPTERS_BY_SHORT_NAME


class RidesanityChecker(ClientComponent):
    ridables_by_area: dict[Area, dict[Character, ApLocationId]]
    current_area: Area | None = None
    locations_to_send: set[ApLocationId]

    def __init__(self):
        self.ridables_by_area = {}
        self.locations_to_send = set()

    @subscribe_event
    def init_from_slot_data(self, event: OnReceiveSlotDataEvent):
        slot_data = event.slot_data
        # Initialise
        ridesanity_enabled = bool(slot_data.ridesanity)

        self.ridables_by_area = {}

        if not ridesanity_enabled:
            return

        goal_chapter_locations_mode = slot_data.goal_chapter_locations_mode
        goal_locations_removed = goal_chapter_locations_mode == GoalChapterLocationsMode.option_removed
        goal_chapter_option = slot_data.goal_chapter
        if goal_chapter_option is not None:
            goal_chapter = Area.from_short_name(goal_chapter_option.value)
        else:
            goal_chapter = None

        for bonus_name in slot_data.enabled_bonuses.value:
            area = next(area for area in BONUS_ROOM_BONUSES if area.readable_name == bonus_name)
            if area not in BONUS_TO_RIDABLES:
                # No ridables in this bonus.
                continue
            self.ridables_by_area[area] = {
                ridable.character: LOCATION_NAME_TO_ID[ridable.character.get_ridesanity_location_name()]
                for ridable in BONUS_TO_RIDABLES[area]
            }
        for short_name in slot_data.enabled_chapters.value:
            chapter = CHAPTERS_BY_SHORT_NAME[short_name]
            ridables = chapter.ridables
            if not ridables:
                # No ridables in this chapter.
                continue
            area = chapter.area
            if area is goal_chapter and goal_locations_removed:
                # The Goal Chapter, with locations removed, should not send Ridesanity checks.
                continue
            self.ridables_by_area[area] = {
                character: LOCATION_NAME_TO_ID[character.get_ridesanity_location_name()]
                for character in ridables.keys()
            }

        self.ridables_by_area[Area.MAP] = {
            Character.MAPCAR: LOCATION_NAME_TO_ID[Character.MAPCAR.get_ridesanity_location_name()],
        }

        current_area_id = CURRENT_AREA_ADDRESS.get(event.context)
        if current_area_id in Area:
            self.current_area = Area(current_area_id)
        else:
            self.current_area = None

        # If the player is currently riding a character that should send a check, they can just stop riding and then
        # start riding again for the check to send, so don't bother checking the current character IDs of the players.

    @subscribe_event
    async def on_area_change(self, event: OnAreaChangeEvent):
        # Update which ids we are currently checking for. (or just update a `self` attribute that stores the area ID.
        if event.new_area_data_id in Area:
            self.current_area = Area(event.new_area_data_id)
        else:
            self.current_area = None

    @subscribe_event
    async def on_player_character_id_change(self, event: OnPlayerCharacterIdChangeEvent):
        # Check for the player being one of the ridable characters that should send a check and update a `self`
        # attribute of locations to send.
        current_area = self.current_area
        if current_area is None:
            return

        ridables: dict[Character, ApLocationId] = self.ridables_by_area.get(current_area, {})

        if not ridables:
            return

        for character_id in (event.new_p1_character_id, event.new_p2_character_id):
            if character_id in ridables:
                ap_location_id = ridables[character_id]
                if event.context.is_location_unchecked(ap_location_id):
                    self.locations_to_send.add(ap_location_id)
                else:
                    del ridables[character_id]

    async def check_ridesanity(self, ctx: TCSContext, new_location_checks: list[int]):
        if self.locations_to_send:
            # Remove any completed location checks.
            self.locations_to_send.difference_update(ctx.checked_locations)
            # Add in new location checks.
            new_location_checks.extend(self.locations_to_send)
