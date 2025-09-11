from enum import IntEnum, IntFlag

from .common import StaticUChar
from .type_aliases import TCSContext


# It looks like AREA IDs tend to use 4 bytes, even though they only need 1 byte.
CURRENT_AREA_ADDRESS = StaticUChar(0x7fd2c1)


CHARACTERS_SHOP_START = 0x86E4A8  # See CHARACTER_SHOP_SLOTS in items.py for the mapping
EXTRAS_SHOP_START = 0x86E4B8

# 0 when a menu is not open, 1 when a menu is open (pause screen, shop, custom character creator, select mode after
# entering a level door). Increases to 2 when opening a submenu in the pause screen.
OPENED_MENU_DEPTH_ADDRESS = 0x800944


# Byte
# 255: Cutscene
# 1: Playing, Indy trailer, loading into Cantina, Title crawl
# 2: In-level 'cutscene' where non-playable characters play an animation and the player has no control
# 6: Bounty Hunter missions select
# 7: In custom character creator
# 8: In Cantina shop
# 9: Minikits display on outside scrapyard
# There is another address at 0x925395
GAME_STATE_ADDRESS = 0x925394


# This is GameState1 because other address have been found that can be used to infer game state, so it is likely that
# there will be a GameState2 in the future.
class GameState1(IntEnum):
    CUTSCENE = 255
    PLAYING_OR_TRAILER_OR_CANTINA_LOAD_OR_CHAPTER_TITLE_CRAWL = 1
    IN_LEVEL_SOFT_CUTSCENE = 2
    UNKNOWN_3 = 3
    UNKNOWN_4 = 4
    UNKNOWN_5 = 5
    IN_BOUNTY_HUNTER_MISSION_SELECT = 6
    IN_CUSTOM_CHARACTER_CREATOR = 7
    IN_CANTINA_SHOP = 8
    IN_JUNKYARD_MINIKITS_DISPLAY = 9

    def is_set(self, ctx: TCSContext) -> bool:
        return ctx.read_uchar(GAME_STATE_ADDRESS) == self.value

    @classmethod
    def is_playing(cls, ctx: TCSContext) -> bool:
        state = ctx.read_uchar(GAME_STATE_ADDRESS)
        return (state == cls.PLAYING_OR_TRAILER_OR_CANTINA_LOAD_OR_CHAPTER_TITLE_CRAWL.value
                or state == cls.IN_LEVEL_SOFT_CUTSCENE.value)


class ShopType(IntEnum):
    NONE = 255  # -1 as a `signed char`
    HINTS = 0
    CHARACTERS = 1
    EXTRAS = 2
    ENTER_CODE = 3
    GOLD_BRICKS = 4
    STORY_CLIPS = 5


class CantinaRoom(IntEnum):
    UNKNOWN = -2
    NOT_IN_CANTINA = -1
    SHOP_ROOM = 0
    EPISODE_1 = 1
    EPISODE_2 = 2
    EPISODE_3 = 3
    EPISODE_4 = 4
    EPISODE_5 = 5
    EPISODE_6 = 6
    JUNKYARD = 7
    BONUSES = 8
    BOUNTY_HUNTER_MISSIONS = 9


_CUSTOM_SAVE_FLAGS_1_ADDRESS = 0x86e4e6  # 0x86e506 (GOG)


class CustomSaveFlags1(IntFlag):
    """
    There are two unused bytes in the save data after the byte that stores whether the Indiana Jones trailer has been
    watched.
    BYTE1_AFTER_INDIANA_JONES_TRAILER = 0x86e506
    BYTE2_AFTER_INDIANA_JONES_TRAILER = 0x86e507

    The client uses these two bytes for storing up to 16 flags.
    """
    MINIKIT_GOAL_COMPLETE = 0x1
    FIELD_2 = 0x2  # DEFEAT_BOSSES_GOAL_COMPLETE
    FIELD_3 = 0x4  # DEATH_LINK_ENABLED
    FIELD_4 = 0x8
    FIELD_5 = 0x10
    FIELD_6 = 0x20
    FIELD_7 = 0x40
    FIELD_8 = 0x80
    FIELD_9 = 0x100
    FIELD_10 = 0x200
    FIELD_11 = 0x400
    FIELD_12 = 0x800
    FIELD_13 = 0x1000
    FIELD_14 = 0x2000
    FIELD_15 = 0x4000
    FIELD_16 = 0x8000

    def is_set(self, ctx: TCSContext) -> bool:
        # noinspection PyTypeChecker
        v: int = self.value
        if v <= 0xFF:
            addr = _CUSTOM_SAVE_FLAGS_1_ADDRESS
        else:
            v = v >> 8
            addr = _CUSTOM_SAVE_FLAGS_1_ADDRESS + 1

        return (ctx.read_uchar(addr) & v) != 0

    def set(self, ctx: TCSContext):
        # noinspection PyTypeChecker
        v: int = self.value
        if v <= 0xFF:
            addr = _CUSTOM_SAVE_FLAGS_1_ADDRESS
        else:
            v = v >> 8
            addr = _CUSTOM_SAVE_FLAGS_1_ADDRESS + 1

        b = ctx.read_uchar(addr)
        if not (b & v):
            ctx.write_byte(_CUSTOM_SAVE_FLAGS_1_ADDRESS, b | v)

    def unset(self, ctx: TCSContext):
        # noinspection PyTypeChecker
        v: int = self.value
        if v <= 0xFF:
            addr = _CUSTOM_SAVE_FLAGS_1_ADDRESS
        else:
            v = v >> 8
            addr = _CUSTOM_SAVE_FLAGS_1_ADDRESS + 1

        b = ctx.read_uchar(addr)
        if b & v:
            ctx.write_byte(_CUSTOM_SAVE_FLAGS_1_ADDRESS, b & ~v)

# Other potential unused sava-data bytes
# Some (most?) (all?) bonus levels have enough space reserved for all the Minikits/True Jedi/Power Brick bytes, which
# they don't use.
# The Extras shop uses 6 bytes, but appears to have 16 bytes allocated.
# The Hints shop uses 2 bytes, but appears to have 12 bytes allocated.
# The Characters shop uses 13 bytes, but appears to have 16 bytes allocated.


# -- Game state addresses.

# This value is slightly unstable and occasionally changes to 0 while playing. It is also set to 2 in Mos Espa Pod Race
# for some reason.
# Importantly, this value is *not* 0 when watching a Story cutscene, and is instead 1.
PAUSED_OR_STATUS_WHEN_0_ADDRESS = 0x9737D8
# This address is usually -1/255 while playing or paused, 1 while tabbed out and 0 while both paused and tabbed out.
# It is a more unstable than the previous value, while playing, however.
TABBED_OUT_WHEN_1_ADDRESS = 0x9868C4

# 0 when playing, 1 when in a cutscene, same-level door transition, Indy trailer and title crawl.
# Rarely unstable and seen as -1 briefly while playing
IS_PLAYING_WHEN_0_ADDRESS = 0x297C0AC


def is_actively_playing(ctx: TCSContext):
    """
    Return True if the player is actively playing the game.

    Returns False in cases like having a menu open, having the game paused, or having the game tabbed out.
    """
    return (
            # Handles pause and status screens.
            ctx.read_uchar(PAUSED_OR_STATUS_WHEN_0_ADDRESS) != 0
            # Handles tabbing out.
            and ctx.read_uchar(TABBED_OUT_WHEN_1_ADDRESS) != 1
            # Handles pause menu and other menus.
            and ctx.read_uchar(OPENED_MENU_DEPTH_ADDRESS) == 0
            # Handles same-level screen transitions.
            and ctx.read_uchar(IS_PLAYING_WHEN_0_ADDRESS) == 0
            and GameState1.is_playing(ctx)
    )
