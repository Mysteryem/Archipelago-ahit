# The game does not initialize the True Jedi requirements until you enter the area, so the extractor cannot read them
# unless the player has entered every single area in the current session. So the true jedi values are reproduced here.
KNOWN_TRUE_JEDI = {
    # area index: (story, free_play),
    0: (31000, 64000),
    1: (44000, 52000),
    2: (48000, 60000),
    3: (45000, 45000),
    5: (60000, 100000),
    6: (31000, 64000),
    10: (35000, 45000),
    11: (50000, 65000),
    12: (40000, 55000),
    13: (8000, 16000),
    14: (30000, 40000),
    16: (10000, 22000),
    20: (75000, 75000),
    21: (60000, 80000),
    22: (3300, 5000),
    23: (65000, 90000),
    24: (35000, 75000),
    25: (25000, 45000),
    30: (28000, 40000),
    31: (60000, 90000),
    32: (60000, 100000),
    33: (60000, 80000),
    34: (45000, 65000),
    35: (30000, 45000),
    39: (25000, 35000),
    40: (40000, 80000),
    41: (30000, 48000),
    42: (52000, 72000),
    43: (14000, 22000),
    44: (34000, 60000),
    48: (43000, 60000),
    49: (50000, 65000),
    50: (55000, 70000),
    51: (90000, 110000),
    52: (35000, 80000),
    53: (35000, 40000),

    # Non-chapter areas that don't have True Jedi, but still have values set.
    # All other non-chapter areas do not have values set, or are not playable levels, so I did not check them.
    4: (45000, 45000),  # Pod Race (Original)
    15: (50000, 100000),  # Gunship Cavalry (Original)
    29: (40000, 70000),  # A New Hope
    58: (20000, 30000),  # Anakin's Flight
}


def _extract():
    import pymem
    from ctypes import Structure, c_ushort, c_ubyte, c_uint, c_char, sizeof, c_byte, c_short

    class AreaData(Structure):
        _fields_ = [
            ("area_file_path", c_char * 64),
            ("area_name", c_char * 32),
            ("level_ids", c_ushort * 12),
            ("localized_text_id", c_ushort),
            ("area_flags", c_ushort),
            ("id", c_ubyte),
            ("level_id_count", c_ubyte),
            ("red_brick_cheat_id", c_byte),
            ("unknown_byte", c_ubyte),
            ("unknown_4_bytes", c_uint),
            ("time_trial_time", c_ushort),
            ("episode_index", c_byte),
            ("area_index", c_byte),
            ("area_music_id", c_short),
            ("minikit_character_id", c_short),
            ("story_true_jedi_requirement", c_uint),
            ("free_play_true_jedi_requirement", c_uint),
            # we don't care about anything else, and I don't know exactly what the remaining fields are anyway.
        ]
    from ..levels import Level
    from ..extras import Extra

    process = pymem.Pymem("LegoStarWarsSaga")
    p_a_data_start = 0x00951374
    a_data_start = process.read_uint(p_a_data_start)
    a_data_size = 0x9c

    p_t_tab_addr = 0x00926c40
    t_tab_addr = process.read_uint(p_t_tab_addr)

    longest_extra = "Extra.EXPLODING_BLASTER_BOLTS"
    longest_name = len("Through The Jundland Wastes")

    i = 0
    while True:
        area_data_bytes = process.read_bytes(a_data_start + a_data_size * i, sizeof(AreaData))
        area_data = AreaData.from_buffer_copy(area_data_bytes)
        name = area_data.area_name.rstrip(b"\x00").decode("utf-8")
        level_ids = area_data.level_ids[:area_data.level_id_count]

        # char **
        if area_data.area_index == 6:
            human_readable_name = f"Episode {area_data.episode_index+1} Ending"
        # The Character and Minikit Bonuses actually have names based on where they are, e.g. "Tatooine" or "Endor".
        elif area_data.area_index == 7:
            human_readable_name = f"Episode {area_data.episode_index+1} Character Bonus"
        elif area_data.area_index == 8:
            human_readable_name = f"Episode {area_data.episode_index+1} Minikit Bonus"
        elif area_data.localized_text_id > 0:
            p_human_readable_name_addr = t_tab_addr + area_data.localized_text_id * 4
            human_readable_name_addr = process.read_uint(p_human_readable_name_addr)
            if human_readable_name_addr:
                human_readable_name = process.read_bytes(
                    human_readable_name_addr, 64
                ).partition(b"\x00")[0].decode("utf-8)").title().replace("'S", "'s")
            else:
                human_readable_name = "?"
        else:
            human_readable_name = "??"

        space = " " * (16 - len(name))
        story_true_jedi, free_play_true_jedi = KNOWN_TRUE_JEDI.get(
            i, (area_data.story_true_jedi_requirement, area_data.free_play_true_jedi_requirement)
        )

        name_spaces = " " * (longest_name - len(human_readable_name))

        level_names = [f"Level.{Level(level).name}" for level in level_ids]
        level_ids_str = ", ".join(level_names)

        if area_data.red_brick_cheat_id != -1:
            extra = Extra(area_data.red_brick_cheat_id)
            extra_str = f"Extra.{extra.name}"
        else:
            extra_str = "None"
        extra_str = " " * (len(longest_extra) - len(extra_str)) + extra_str

        print(f"    {name.upper()} = {space}{i:2}"
              f", dict(episode_index={area_data.episode_index:2}"
              f", area_index={area_data.area_index:2}"
              f", readable_name={name_spaces}\"{human_readable_name}\""
              f", flags=AreaFlag(0x{area_data.area_flags:04x})"
              f", story_true_jedi={story_true_jedi:5}"
              f", free_play_true_jedi={free_play_true_jedi:6}"
              f", extra={extra_str}"
              f", levels=[{level_ids_str}])"
              )

        if name == "LostTemple":
            break
        i += 1

if __name__ == "__main__":
    _extract()