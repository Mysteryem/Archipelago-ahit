from enum import IntEnum, IntFlag

from .type_aliases import TCSContext

from ..data.areas import Area
from ..data.levels import Level, SAVE_DATA_MINIKITS_ELEMENT_SIZE

# Comments explaining save data structure assume the following import:
# from ctypes import *

# Every Level that does not have minikits still writes the full 84 bytes of minikits data into the save data.
# class LevelMinikitSavaData(Structure):
#     __fields__ = [
#         ("minikits", (c_char * 8) * 10),
#         # The size of the minikit_count field is not clear to me, but only the first byte is ever used.
#         ("minikit_count", c_byte),
#         ("unknown", c_byte * 3),
#     ]
# There are a limited number of minikits within each Level belonging to an Area that actually has minikits, so the vast
# majority of Levels will never use the full array of 10 minikit names. For simplicity, only Levels belonging to Areas
# without minikits are used currently.


# Every Area writes the same bytes into the save data, even if that area does not use those bytes:
# class AreaSavaData(Structure):
#     __fields__ = [
#         ("is_unlocked", c_bool),
#         ("is_complete", c_bool),
#         # Likely a leftover from earlier development of the game. Both True Jedi bytes are set when completing True
#         # Jedi.
#         ("is_story_true_jedi_complete", c_bool),
#         ("is_free_play_true_jedi_complete", c_bool),
#         ("is_minikit_gold_brick_acquired", c_bool),
#         ("acquired_minikit_count", c_int8),
#         ("is_power_brick_acquired", c_bool),
#         ("is_challenge_mode_complete", c_bool),
#         # For bonus levels, this makes sense, but every chapter in Challenge mode has the same timer, so it is rather
#         # weird that the game reads the Challenge mode timer, for each chapter, from the save data.
#         ("bonus_level_best_time_or_challenge_mode_timer", c_float),
#     ]
# Every 'level' as players would consider it, is a separate Area, so each chapter, each minikit bonus, each character
# bonus, each gold brick door bonus, each 2-player Arcade 'level' and the Cantina itself. Additionally, each Episode
# ending cutscene also is a separate Area, and there is an incomplete Lego Indiana Jones 'level' that has its own Area.
# - Minikit and Character bonuses only use "is_unlocked", "is_complete" and
#   "bonus_level_best_time_or_challenge_mode_timer".
# - Most gold brick bonuses only use "is_complete".
# - LEGO City and New Town additionally use "bonus_level_best_time_or_challenge_mode_timer".
# - Gold Brick bonuses use a separate part of the save data to store which bonuses are unlocked.
# - Episode endings use nothing.


def _make_levels_free_space() -> list[Level]:
    levels_with_minikits = set().union(*(area.get_playable_levels() for area in Area))
    levels_without_minikits = [level for level in Level if level not in levels_with_minikits]
    return levels_without_minikits

_LEVELS_WITHOUT_MINIKITS: list[Level] = _make_levels_free_space()
del _make_levels_free_space

CUSTOM_SAVE_DATA_SECTION_SIZE = SAVE_DATA_MINIKITS_ELEMENT_SIZE

_CUSTOM_SAVE_FLAGS_1_ADDRESS = 0x86e506


class CustomSaveFlags1(IntFlag):
    """
    There are two unused bytes in the save data after the byte that stores whether the Indiana Jones trailer has been
    watched.
    BYTE1_AFTER_INDIANA_JONES_TRAILER = 0x86e506
    BYTE2_AFTER_INDIANA_JONES_TRAILER = 0x86e507

    The client uses these two bytes for storing up to 16 flags.
    """
    MINIKIT_GOAL_COMPLETE = 0x1
    DEATH_LINK_ENABLED = 0x2
    AUTO_COLLECT_PICKUPS_ENABLED = 0x4
    AUTO_COLLECT_PICKUPS_VEHICLES_ONLY = 0x8
    FIELD_5 = 0x10  # Could be DEFEAT_BOSSES_GOAL_COMPLETE to reduce memory reading once the goal is complete.
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
        v: int = self.value
        if v <= 0xFF:
            addr = _CUSTOM_SAVE_FLAGS_1_ADDRESS
        else:
            v = v >> 8
            addr = _CUSTOM_SAVE_FLAGS_1_ADDRESS + 1

        return (ctx.read_uchar(addr) & v) != 0

    def set(self, ctx: TCSContext):
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
        v: int = self.value
        if v <= 0xFF:
            addr = _CUSTOM_SAVE_FLAGS_1_ADDRESS
        else:
            v = v >> 8
            addr = _CUSTOM_SAVE_FLAGS_1_ADDRESS + 1

        b = ctx.read_uchar(addr)
        if b & v:
            ctx.write_byte(_CUSTOM_SAVE_FLAGS_1_ADDRESS, b & ~v)

    def set_bool(self, ctx: TCSContext, b: bool):
        if b:
            self.set(ctx)
        else:
            self.unset(ctx)


class CustomSaveDataSections(IntEnum):
    SLOT_NAME = 0
    MULTIWORLD_SEED_NAME = 1
    # The first 6 bytes are used for storing which Extras were active, so that the player does not have to re-activate
    # them when continuing an in-progress multiworld.
    CUSTOM_SAVE_FLAGS2 = 2

    def get_address(self) -> int:
        return _LEVELS_WITHOUT_MINIKITS[self.value].minikits_save_data_addr

    def read_full(self, ctx: TCSContext) -> bytes:
        return ctx.read_bytes(self.get_address(), CUSTOM_SAVE_DATA_SECTION_SIZE)

    def read_utf8_string(self, ctx: TCSContext) -> str:
        addr = self.get_address()
        length = ctx.read_uchar(addr)
        if length == 0:
            return ""
        else:
            if length > CUSTOM_SAVE_DATA_SECTION_SIZE - 1:
                raise Exception(f"Got unexpected utf-8 bytes length of {length}, which would not fit within the custom"
                                f" save data section.")
            return ctx.read_bytes(addr + 1, length).decode("utf-8")

    def write_utf8_string(self, ctx: TCSContext, value: str) -> None:
        addr = self.get_address()
        encoded = value.encode("utf-8")
        encoded_length = len(encoded)
        # Write the length of the string into the first byte.
        to_write = bytes([encoded_length]) + encoded
        to_write_length = len(to_write)
        if to_write_length > CUSTOM_SAVE_DATA_SECTION_SIZE:
            raise ValueError(f"'{value}' encodes to more bytes than can be stored.")
        ctx.write_bytes(addr, to_write, to_write_length)

    def is_utf8_string_empty(self, ctx: TCSContext):
        return ctx.read_uchar(self.get_address()) == 0

assert max(CustomSaveDataSections) < len(_LEVELS_WITHOUT_MINIKITS)