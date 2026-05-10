from ...common import UintField
from ...common_types import CharacterDataFlag3, CharacterEntryFlag2
from ...type_aliases import TCSContext
from ....items import CHARACTERS_AND_VEHICLES_BY_NAME
from ....constants import CharacterAbility


# UnknownLoadedCharacterData.data_flag3
CHARACTER_DATA_FLAG_3 = UintField(0x4c)

# CharacterEntry.UnknownFlag2
CHARACTER_ENTRY_FLAG_2 = UintField(0x90)


def set_ig88_and_4lom_as_protocol_droids(ctx: TCSContext):
    # Give 4-LOM and IG-88 the Protocol flag so that if the player has no Protocol Droid, but does have 4-LOM or
    # IG-88, the game will pick 4-LOM or IG-88 for the Free Play character selection.
    # While 4-LOM and IG-88 can also use Astromech panels, the Astromech flag (0x40) also tells the game that
    # the characters can hover, and can traverse Dagobah's swamps, which neither 4-LOM nor IG-88 can do, so they
    # should not be given the Astromech flag.
    # Character data is loaded once when the game starts, so the changes made here are permanent until the game
    # is restarted.
    # UnknownLoadedCharacterData* _CDataList
    addr_p_c_data_list = 0x93b294
    addr_c_data_list = ctx.read_uint(addr_p_c_data_list)
    # sizeof(UnknownLoadedCharacterData)
    unknown_loaded_character_data_size = 0x4c
    for character in ("IG-88", "4-LOM"):
        character_index = CHARACTERS_AND_VEHICLES_BY_NAME[character].character_index
        addr_character_data = addr_c_data_list + unknown_loaded_character_data_size * character_index
        character_data_flag_3 = CHARACTER_DATA_FLAG_3.get(ctx, addr_character_data)
        new_flag = character_data_flag_3 | CharacterDataFlag3.PROTOCOL.value
        CHARACTER_DATA_FLAG_3.set(ctx, addr_character_data, new_flag)


def set_astromech_panel_users_as_tightrope_walk(ctx: TCSContext):
    # Give astromech panel users the TIGHTROPE_WALK flag, which a custom category is added for, so that a character that
    # can use astromech panels is always picked, if one is unlocked.
    addr_p_gc_data_list = 0x93b2a4
    addr_gc_data_list = ctx.read_uint(addr_p_gc_data_list)
    # sizeof(CharacterEntry)
    character_entry_size = 0x120
    for character in CHARACTERS_AND_VEHICLES_BY_NAME.values():
        if CharacterAbility.ASTROMECH in character.abilities:
            addr_character_entry = addr_gc_data_list + character_entry_size * character.character_index
            character_entry_flag = CHARACTER_ENTRY_FLAG_2.get(ctx, addr_character_entry)
            new_flag = character_entry_flag | CharacterEntryFlag2.TIGHTROPE_WALK.value
            CHARACTER_ENTRY_FLAG_2.set(ctx, addr_character_entry, new_flag)
