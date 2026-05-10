import ctypes

from ...common import TCSContext
from ...common_addresses import StaticUint
from ...common_types import CharacterDataFlag3, CharacterEntryFlag2

p_CharCategoryAddr = StaticUint(0x93b2a0)
p_CHARCATEGORYCOUNT = StaticUint(0x93b28c)


class CharCategory(ctypes.Structure):
    _fields_ = [
        ("name", ctypes.c_uint),  # This is a pointer to the game's memory (char*).
        ("data_flag_3", ctypes.c_uint),
        ("character_entry_flag_2", ctypes.c_uint),
    ]


# Vanilla categories are reproduced with pointers to their original names because there are game functions for looking
# up categories by name.
_CUSTOM_CHAR_CATEGORIES_GOG = [
    CharCategory(
        0x00751edc,  # "JediBaddie" (Sith)
        # This is how Sith are coded...
        CharacterDataFlag3.BADDIE | CharacterDataFlag3.JEDI,
        0,
    ),
    # Custom category to pick a ghost if available.
    CharCategory(
        0x00762e0c,  # "ghost"
        0,
        CharacterEntryFlag2.IS_GHOST,
    ),
    # Custom category to pick a jetpack character (Boba/Jango Fett).
    CharCategory(
        0x007628cc,  # "jetpack"
        CharacterDataFlag3.JETPACK,
        0
    ),
    CharCategory(
        0x00751ee8,  # "Jedi"
        CharacterDataFlag3.JEDI,
        0,
    ),
    CharCategory(
        0x00751ecc,  # "BountyHunter"
        # Vanilla specifies all 3 despite all Bounty Hunters all being able to use Blasters/Zipup.
        CharacterDataFlag3.BLASTER | CharacterDataFlag3.ZIPUP | CharacterDataFlag3.BOUNTY_HUNTER,
        0,
    ),
    CharCategory(
        0x00751ec0,  # "Teleport" (shortie)
        CharacterDataFlag3.TELEPORT,
        0,
    ),
    CharCategory(
        0x00751eb4,  # "HighJump"
        0,
        CharacterEntryFlag2.CAN_HIGH_JUMP,
    ),
    CharCategory(
        0x00751ea8,  # "Astromech"
        CharacterDataFlag3.ASTROMECH,
        0,
    ),
    CharCategory(
        0x00751e9c,  # "Protocol"
        CharacterDataFlag3.PROTOCOL,
        0,
    ),
    CharCategory(
        0x00751e94,  # "ZipUp"
        # Vanilla specifies both.
        CharacterDataFlag3.BLASTER | CharacterDataFlag3.ZIPUP,
        0,
    ),
    CharCategory(
        0x007518cc,  # "Blaster"
        CharacterDataFlag3.BLASTER,
        0,
    ),
    # A category with NULL name at the end signifies the end of the array.
    CharCategory(0, 0, 0)
]


def set_custom_character_categories(ctx: TCSContext):
    custom_categories = [
        # The name is a pointer to a string in the game's memory, so it needs to be adjusted.
        CharCategory(ctx.adjust_gog_address(c.name), c.data_flag_3, c.character_entry_flag_2)
        for c in _CUSTOM_CHAR_CATEGORIES_GOG
    ]
    array_class = CharCategory * len(_CUSTOM_CHAR_CATEGORIES_GOG)
    array_instance = array_class(*custom_categories)
    bytes_to_write = bytes(array_instance)

    allocated_addr = ctx.allocate(len(bytes_to_write))
    ctx.write_bytes(allocated_addr, bytes_to_write, len(bytes_to_write), raw=True)

    ctx.write_uint(p_CharCategoryAddr, allocated_addr)
    # The last element in the array is empty, signifying the end of the array.
    ctx.write_uint(p_CHARCATEGORYCOUNT, len(custom_categories) - 1)
