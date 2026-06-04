def _extract():
    import pymem
    from ..levels import LevelFlag

    process = pymem.Pymem("LegoStarWarsSaga")
    p_l_data_start = 0x00951b98
    l_data_start = process.read_uint(p_l_data_start)
    l_data_size = 0x130
    level_name_offset = 0x40
    level_name_max_size = 32

    flags_offset = 0x64

    id_to_data: dict[int, tuple[str, LevelFlag]] = {}

    i = 0
    while True:
        level_data_addr = l_data_start + l_data_size * i
        name_b = process.read_bytes(level_data_addr + level_name_offset, level_name_max_size)
        name_b = name_b.rstrip(b"\x00")
        name_s = name_b.decode('utf-8')

        flag = process.read_uint(level_data_addr + flags_offset)
        id_to_data[i] = name_s, LevelFlag(flag)
        if name_b.startswith(b"LostTemple"):
            break
        i += 1

    for level_id, (name, flag) in id_to_data.items():
        print(f"    {name.upper()} = {level_id}, LevelFlag(0x{flag.value:x})")

if __name__ == "__main__":
    _extract()