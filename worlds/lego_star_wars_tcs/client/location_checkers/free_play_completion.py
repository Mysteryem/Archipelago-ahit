import logging
from enum import IntFlag
from typing import Iterable

from ..events import subscribe_event, OnReceiveSlotDataEvent
from ..type_aliases import ApLocationId, TCSContext
from ..common import ClientComponent, StaticUint
from ..common_addresses import ChallengeMode

from ...options import GoalChapterLocationsMode

from ...data.areas import Area, ALL_CHAPTER_AREAS
from ...data.levels import Level
from ...data.locations import LOCATION_NAME_TO_ID


_DEBUG_LOGGER = logging.getLogger("TCS Debug")


# Flags set when on the Status screen.
_STATUS_LEVEL_FLAGS_ADDRESS = StaticUint(0x87a6f8)


# The value is usually just 0b0 for incomplete, or 0b1 for complete. The client uses the custom value 0b11 to mark
# chapters as being completed in Free Play because the game does not specifically store whether a chapter has been
# completed in Free Play, and the game happily write to the save data whatever the client writes into the save data
# loaded into memory.
_CUSTOM_COMPLETED_IN_FREE_PLAY = 0b11


class _StatusLevelFlags(IntFlag):
    UNKNOWN_1 = 0x1
    UNKNOWN_2 = 0x2
    # todo: See if completing Story True Jedi vs Free Play True Jedi have different flags.
    TRUE_JEDI_COMPLETED = 0x4  # Upon getting the True Jedi Gold Brick
    STORY_MODE = 0x8
    MINIKITS_COMPLETED = 0x10  # Upon getting the 10/10 Minikits Gold Brick
    UNKNOWN_20 = 0x20
    CHARACTER_SWAP_ENABLED = 0x40  # Free Play/Challenge/Character Bonus/Minikit Bonus
    VEHICLE_LEVEL = 0x80  # Minikit Bonus also counts as a vehicle level
    CHARACTER_OR_MINIKIT_BONUS = 0x100
    UNKNOWN_200 = 0x200  # todo: This appears to be set for 'collect all studs' bonus levels, (LEGO City + New Town)
    SUPERSTORY = 0x400
    SAVE_AND_QUIT = 0x800
    # Story related. This bit gets set when exiting back to the cantina from Story mode, but only after a delay.
    UNKNOWN_1000 = 0x1000


# Free Play level completion therefore requires:
_STATUS_LEVEL_FREE_PLAY_COMPLETION_REQUIREMENTS = int(_StatusLevelFlags.CHARACTER_SWAP_ENABLED)
# Does not care about:
# _STATUS_LEVEL_FREE_PLAY_COMPLETION_IGNORES = int(
#         _StatusLevelFlags.TRUE_JEDI_COMPLETED
#         | _StatusLevelFlags.MINIKITS_COMPLETED
#         | _StatusLevelFlags.VEHICLE_LEVEL
# )
# Must not have:
_STATUS_LEVEL_FREE_PLAY_COMPLETION_NEGATIVE_REQUIREMENTS = int(
    _StatusLevelFlags.STORY_MODE
    | _StatusLevelFlags.CHARACTER_OR_MINIKIT_BONUS
    | _StatusLevelFlags.SUPERSTORY
    | _StatusLevelFlags.SAVE_AND_QUIT
)
# # Unknown:
# _STATUS_LEVEL_FREE_PLAY_COMPLETION_UNKNOWN = int(
#     _StatusLevelFlags.UNKNOWN_1
#     | _StatusLevelFlags.UNKNOWN_2
#     | _StatusLevelFlags.UNKNOWN_20
#     | _StatusLevelFlags.UNKNOWN_200
#     | _StatusLevelFlags.UNKNOWN_1000
# )
# These status level flags are not enough to tell apart Free Play and Challenge mode, so an additional explicit check
# for Challenge mode needs to be performed.


_STATUS_LEVEL_TO_AREA: dict[Level, Area] = {
    area.get_status_level(): area for area in ALL_CHAPTER_AREAS
}
_STATUS_LEVEL_TO_AP_ID: dict[Level, ApLocationId] = {
    status_level: LOCATION_NAME_TO_ID[area.get_completion_name()]
    for status_level, area in _STATUS_LEVEL_TO_AREA.items()
}


def _is_status_level_free_play_completion(ctx: TCSContext) -> bool:
    """
    Return whether the current status Level is being shown as part of chapter completion in Free Play.

    The status Level for each chapter Area is used when tallying up Studs/Minikits etc. when returning to the
    Cantina, both for chapter completion and for 'Save and Exit'.

    The result is undefined if the player is not currently in a status Level.
    """
    status_flags = _STATUS_LEVEL_FLAGS_ADDRESS.get(ctx)
    return (status_flags & _STATUS_LEVEL_FREE_PLAY_COMPLETION_REQUIREMENTS != 0
            and status_flags & _STATUS_LEVEL_FREE_PLAY_COMPLETION_NEGATIVE_REQUIREMENTS == 0
            # The status_flags cannot be used to tell apart Free Play and Challenge, so an explicit check for Challenge
            # mode not being enabled is needed.
            and ChallengeMode.NO_CHALLENGE.is_set(ctx))


# TODO: How quickly can a player reasonably skip through the chapter completion screen? Do we need to check for chapter
#  completion with a higher frequency than how often the game watcher is checking?
class FreePlayChapterCompletionChecker(ClientComponent):
    """
    Check if the player has completed a free play chapter by looking for the ending screen that tallies up new
    studs/minikits.

    There appears to be no persistent storage in the game's memory or save data for whether a chapter has been completed
    in Free Play, so the client must poll the game state and track completions itself in the case of disconnecting from
    the server.
    """

    sent_locations: set[ApLocationId]
    completed_free_play: set[Area]
    enabled_chapter_areas: set[Area]
    chapter_completion_locations: dict[Area, list[ApLocationId]]

    def __init__(self):
        self.sent_locations = set()
        self.completed_free_play = set()
        self.enabled_chapter_areas = set()
        self.chapter_completion_locations = {}

    @subscribe_event
    def init_from_slot_data(self, event: OnReceiveSlotDataEvent) -> None:
        ctx = event.context

        goal_chapter_locations_mode = event.slot_data.get("goal_chapter_locations_mode",
                                                          GoalChapterLocationsMode.option_normal)
        goal_locations_removed = goal_chapter_locations_mode == GoalChapterLocationsMode.option_removed
        goal_chapter_short_name: str | None = event.slot_data.get("goal_chapter")
        if goal_chapter_short_name:
            goal_chapter = Area.from_short_name(goal_chapter_short_name)
        else:
            goal_chapter = None
        enabled_chapter_areas: set[Area] = set()
        for area in ALL_CHAPTER_AREAS:
            chapter_locations = [LOCATION_NAME_TO_ID[area.get_completion_name()]]
            # If the Goal Chapter had its locations removed, it should not send Level Completion Character Unlock
            # checks when completing the chapter.
            if not (area is goal_chapter and goal_locations_removed):
                for story_character in area.get_story_characters():
                    loc_name = story_character.get_level_completion_unlock_location_name()
                    chapter_locations.append(LOCATION_NAME_TO_ID[loc_name])
            enabled_chapter_locations = [loc_id for loc_id in chapter_locations if loc_id in ctx.server_locations]
            # Determine if a chapter is enabled by whether any of the chapter locations exist.
            # This is more robust against world bugs than relying on slot data.
            if enabled_chapter_locations:
                enabled_chapter_areas.add(area)
                self.chapter_completion_locations[area] = enabled_chapter_locations
            else:
                # There shouldn't be any present, but ensure that no data from disable chapters is present.
                self.completed_free_play.discard(area)
                self.sent_locations.difference_update(chapter_locations)
        self.enabled_chapter_areas = enabled_chapter_areas

        # Read any completions from save data. This should catch cases where the player has temporarily lost connection
        # to the server, completed a chapter, and then automatically reconnected to the server. The save data will be
        # read and should update datastorage.
        self.read_completed_free_play_from_save_data(ctx)

    def read_completed_free_play_from_save_data(self, ctx: TCSContext):
        enabled_chapter_areas = self.enabled_chapter_areas
        completed_areas: list[Area] = []
        for area in ALL_CHAPTER_AREAS:
            if enabled_chapter_areas is not None and area not in enabled_chapter_areas:
                continue
            # Either the chapter is enabled, or the player has not connected yet, so it is not known if the chapter is
            # enabled.
            # The first byte is whether the area has been completed.
            unlocked_byte = ctx.read_uchar(area.save_data_address)
            if unlocked_byte == _CUSTOM_COMPLETED_IN_FREE_PLAY:
                self.completed_free_play.add(area)
                _DEBUG_LOGGER.info("Read from save file that %r has been completed in Free Play", area)
                self.sent_locations.add(_STATUS_LEVEL_TO_AP_ID[area.get_status_level()])
                completed_areas.append(area)
                # Tell the goal manager it should update for newly completed chapters.
                ctx.goal_manager.tag_for_update("area")
        ctx.update_datastorage_free_play_completion(completed_areas)
        ctx.goal_manager.tag_for_update("boss")

    def update_from_datastorage(self, ctx: TCSContext, area_ids: Iterable[int]):
        _DEBUG_LOGGER.info("Updating Free Play Completion area_ids from datastorage: %s", area_ids)
        for area_id in area_ids:
            area = Area(area_id)
            self.completed_free_play.add(area)
            ctx.goal_manager.tag_for_update("boss")
            # The locations should have been sent already, but try sending again just in-case.
            self.sent_locations.update(self.chapter_completion_locations.get(area, ()))
            # Tell the goal manager it should update for newly completed chapters.
            ctx.goal_manager.tag_for_update("area")

    async def check_completion(self, ctx: TCSContext, new_location_checks: list[ApLocationId]):
        # Level ID should be checked first because _STATUS_LEVEL_FLAGS_ADDRESS only gets set when entering a Status
        # level, and its value will persist in memory until it is set again.
        current_level_id = ctx.read_current_level_id()
        if current_level_id in Level:
            current_level = Level(current_level_id)
            completion_location_id = _STATUS_LEVEL_TO_AP_ID.get(current_level)
            if completion_location_id is not None:
                area = _STATUS_LEVEL_TO_AREA[current_level]
                if area not in self.completed_free_play and _is_status_level_free_play_completion(ctx):
                    completion_locations = self.chapter_completion_locations.get(area, ())
                    self.sent_locations.update(completion_locations)
                    ctx.update_datastorage_free_play_completion([area])
                    self.completed_free_play.add(area)
                    ctx.write_byte(area.save_data_address, _CUSTOM_COMPLETED_IN_FREE_PLAY)
                    ctx.goal_manager.tag_for_update("boss")

        # Not required because only the intersection of ctx.missing_locations will be sent to the server, but removing
        # checked locations (server state) here helps with debugging by reducing self.sent_locations to only new checks.
        self.sent_locations.difference_update(ctx.checked_locations)

        # Locations to send to the server will be filtered to only those in ctx.missing_locations, so include everything
        # up to this point in-case one was missed in a disconnect.
        new_location_checks.extend(self.sent_locations)
