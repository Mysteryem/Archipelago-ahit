from BaseClasses import Item, ItemClassification
from worlds.AutoWorld import World
from .Types import HatDLC, HatType, hat_type_to_item, Difficulty, ItemData, HatInTimeItem
from .Locations import get_total_locations
from .Rules import get_difficulty
from typing import Optional, List, Dict


def create_itempool(world: World) -> List[Item]:
    itempool: List[Item] = []
    if not world.is_dw_only() and world.options.HatItems.value == 0:
        calculate_yarn_costs(world)
        yarn_pool: List[Item] = create_multiple_items(world, "Yarn",
                                                      world.options.YarnAvailable.value,
                                                      ItemClassification.progression_skip_balancing)

        for i in range(int(len(yarn_pool) * (0.01 * world.options.YarnBalancePercent.value))):
            yarn_pool[i].classification = ItemClassification.progression

        itempool += yarn_pool

    for name in item_table.keys():
        if name == "Yarn":
            continue

        if not item_dlc_enabled(world, name):
            continue

        if world.options.HatItems.value == 0 and name in hat_type_to_item.values():
            continue

        item_type: ItemClassification = item_table.get(name).classification

        if world.is_dw_only():
            if item_type is ItemClassification.progression \
               or item_type is ItemClassification.progression_skip_balancing:
                continue
        else:
            if name == "Scooter Badge":
                if world.options.CTRLogic.value >= 1 or get_difficulty(world) >= Difficulty.MODERATE:
                    item_type = ItemClassification.progression
            elif name == "No Bonk Badge":
                if get_difficulty(world) >= Difficulty.MODERATE:
                    item_type = ItemClassification.progression

        # some death wish bonuses require one hit hero + hookshot
        if world.is_dw() and name == "Badge Pin" and not world.is_dw_only():
            item_type = ItemClassification.progression

        if item_type is ItemClassification.filler or item_type is ItemClassification.trap:
            continue

        if name in act_contracts.keys() and world.options.ShuffleActContracts.value == 0:
            continue

        if name in alps_hooks.keys() and world.options.ShuffleAlpineZiplines.value == 0:
            continue

        if name == "Progressive Painting Unlock" \
           and world.options.ShuffleSubconPaintings.value == 0:
            continue

        if world.options.StartWithCompassBadge.value > 0 and name == "Compass Badge":
            continue

        if name == "Time Piece":
            tp_count: int = 40
            max_extra: int = 0
            if world.is_dlc1():
                max_extra += 6

            if world.is_dlc2():
                max_extra += 10

            tp_count += min(max_extra, world.options.MaxExtraTimePieces.value)
            tp_list: List[Item] = create_multiple_items(world, name, tp_count, item_type)

            for i in range(int(len(tp_list) * (0.01 * world.options.TimePieceBalancePercent.value))):
                tp_list[i].classification = ItemClassification.progression

            itempool += tp_list
            continue

        itempool += create_multiple_items(world, name, item_frequencies.get(name, 1), item_type)

    itempool += create_junk_items(world, get_total_locations(world) - len(itempool))
    return itempool


def calculate_yarn_costs(world: World):
    mw = world.multiworld
    min_yarn_cost = int(min(world.options.YarnCostMin.value, world.options.YarnCostMax.value))
    max_yarn_cost = int(max(world.options.YarnCostMin.value, world.options.YarnCostMax.value))

    max_cost: int = 0
    for i in range(5):
        cost: int = mw.random.randint(min(min_yarn_cost, max_yarn_cost), max(max_yarn_cost, min_yarn_cost))
        world.get_hat_yarn_costs()[HatType(i)] = cost
        max_cost += cost

    available_yarn: int = world.options.YarnAvailable.value
    if max_cost > available_yarn:
        world.options.YarnAvailable.value = max_cost
        available_yarn = max_cost

    if max_cost + world.options.MinExtraYarn.value > available_yarn:
        world.options.YarnAvailable.value += (max_cost + world.options.MinExtraYarn.value) - available_yarn


def item_dlc_enabled(world: World, name: str) -> bool:
    data = item_table[name]

    if data.dlc_flags == HatDLC.none:
        return True
    elif data.dlc_flags == HatDLC.dlc1 and world.is_dlc1():
        return True
    elif data.dlc_flags == HatDLC.dlc2 and world.is_dlc2():
        return True
    elif data.dlc_flags == HatDLC.death_wish and world.is_dw():
        return True

    return False


def create_item(world: World, name: str) -> Item:
    data = item_table[name]
    return HatInTimeItem(name, data.classification, data.code, world.player)


def create_multiple_items(world: World, name: str, count: int = 1,
                          item_type: Optional[ItemClassification] = ItemClassification.progression) -> List[Item]:

    data = item_table[name]
    itemlist: List[Item] = []

    for i in range(count):
        itemlist += [HatInTimeItem(name, item_type, data.code, world.player)]

    return itemlist


def create_junk_items(world: World, count: int) -> List[Item]:
    trap_chance = world.options.TrapChance.value
    junk_pool: List[Item] = []
    junk_list: Dict[str, int] = {}
    trap_list: Dict[str, int] = {}
    ic: ItemClassification

    for name in item_table.keys():
        ic = item_table[name].classification
        if ic == ItemClassification.filler:
            if world.is_dw_only() and "Pons" in name:
                continue

            junk_list[name] = junk_weights.get(name)

        elif trap_chance > 0 and ic == ItemClassification.trap:
            if name == "Baby Trap":
                trap_list[name] = world.options.BabyTrapWeight.value
            elif name == "Laser Trap":
                trap_list[name] = world.options.LaserTrapWeight.value
            elif name == "Parade Trap":
                trap_list[name] = world.options.ParadeTrapWeight.value

    for i in range(count):
        if trap_chance > 0 and world.random.randint(1, 100) <= trap_chance:
            junk_pool += [world.create_item(
                world.random.choices(list(trap_list.keys()), weights=list(trap_list.values()), k=1)[0])]
        else:
            junk_pool += [world.create_item(
                world.random.choices(list(junk_list.keys()), weights=list(junk_list.values()), k=1)[0])]

    return junk_pool


ahit_items = {
    "Yarn": ItemData(2000300001, ItemClassification.progression_skip_balancing),
    "Time Piece": ItemData(2000300002, ItemClassification.progression_skip_balancing),

    # for HatItems option
    "Sprint Hat": ItemData(2000300049, ItemClassification.progression),
    "Brewing Hat": ItemData(2000300050, ItemClassification.progression),
    "Ice Hat": ItemData(2000300051, ItemClassification.progression),
    "Dweller Mask": ItemData(2000300052, ItemClassification.progression),
    "Time Stop Hat": ItemData(2000300053, ItemClassification.progression),

    # Relics
    "Relic (Burger Patty)": ItemData(2000300006, ItemClassification.progression),
    "Relic (Burger Cushion)": ItemData(2000300007, ItemClassification.progression),
    "Relic (Mountain Set)": ItemData(2000300008, ItemClassification.progression),
    "Relic (Train)": ItemData(2000300009, ItemClassification.progression),
    "Relic (UFO)": ItemData(2000300010, ItemClassification.progression),
    "Relic (Cow)": ItemData(2000300011, ItemClassification.progression),
    "Relic (Cool Cow)": ItemData(2000300012, ItemClassification.progression),
    "Relic (Tin-foil Hat Cow)": ItemData(2000300013, ItemClassification.progression),
    "Relic (Crayon Box)": ItemData(2000300014, ItemClassification.progression),
    "Relic (Red Crayon)": ItemData(2000300015, ItemClassification.progression),
    "Relic (Blue Crayon)": ItemData(2000300016, ItemClassification.progression),
    "Relic (Green Crayon)": ItemData(2000300017, ItemClassification.progression),

    # Badges
    "Projectile Badge": ItemData(2000300024, ItemClassification.useful),
    "Fast Hatter Badge": ItemData(2000300025, ItemClassification.useful),
    "Hover Badge": ItemData(2000300026, ItemClassification.useful),
    "Hookshot Badge": ItemData(2000300027, ItemClassification.progression),
    "Item Magnet Badge": ItemData(2000300028, ItemClassification.useful),
    "No Bonk Badge": ItemData(2000300029, ItemClassification.useful),
    "Compass Badge": ItemData(2000300030, ItemClassification.useful),
    "Scooter Badge": ItemData(2000300031, ItemClassification.useful),
    "One-Hit Hero Badge": ItemData(2000300038, ItemClassification.progression, HatDLC.death_wish),
    "Camera Badge": ItemData(2000300042, ItemClassification.progression, HatDLC.death_wish),

    # Other
    "Badge Pin": ItemData(2000300043, ItemClassification.useful),
    "Umbrella": ItemData(2000300033, ItemClassification.progression),
    "Progressive Painting Unlock": ItemData(2000300003, ItemClassification.progression),

    # Garbage items
    "25 Pons": ItemData(2000300034, ItemClassification.filler),
    "50 Pons": ItemData(2000300035, ItemClassification.filler),
    "100 Pons": ItemData(2000300036, ItemClassification.filler),
    "Health Pon": ItemData(2000300037, ItemClassification.filler),
    "Random Cosmetic": ItemData(2000300044, ItemClassification.filler),

    # Traps
    "Baby Trap": ItemData(2000300039, ItemClassification.trap),
    "Laser Trap": ItemData(2000300040, ItemClassification.trap),
    "Parade Trap": ItemData(2000300041, ItemClassification.trap),

    # DLC1 items
    "Relic (Cake Stand)": ItemData(2000300018, ItemClassification.progression, HatDLC.dlc1),
    "Relic (Shortcake)": ItemData(2000300019, ItemClassification.progression, HatDLC.dlc1),
    "Relic (Chocolate Cake Slice)": ItemData(2000300020, ItemClassification.progression, HatDLC.dlc1),
    "Relic (Chocolate Cake)": ItemData(2000300021, ItemClassification.progression, HatDLC.dlc1),

    # DLC2 items
    "Relic (Necklace Bust)": ItemData(2000300022, ItemClassification.progression, HatDLC.dlc2),
    "Relic (Necklace)": ItemData(2000300023, ItemClassification.progression, HatDLC.dlc2),
    "Metro Ticket - Yellow": ItemData(2000300045, ItemClassification.progression, HatDLC.dlc2),
    "Metro Ticket - Green": ItemData(2000300046, ItemClassification.progression, HatDLC.dlc2),
    "Metro Ticket - Blue": ItemData(2000300047, ItemClassification.progression, HatDLC.dlc2),
    "Metro Ticket - Pink": ItemData(2000300048, ItemClassification.progression, HatDLC.dlc2),
}

act_contracts = {
    "Snatcher's Contract - The Subcon Well": ItemData(2000300200, ItemClassification.progression),
    "Snatcher's Contract - Toilet of Doom": ItemData(2000300201, ItemClassification.progression),
    "Snatcher's Contract - Queen Vanessa's Manor": ItemData(2000300202, ItemClassification.progression),
    "Snatcher's Contract - Mail Delivery Service": ItemData(2000300203, ItemClassification.progression),
}

alps_hooks = {
    "Zipline Unlock - The Birdhouse Path": ItemData(2000300204, ItemClassification.progression),
    "Zipline Unlock - The Lava Cake Path": ItemData(2000300205, ItemClassification.progression),
    "Zipline Unlock - The Windmill Path": ItemData(2000300206, ItemClassification.progression),
    "Zipline Unlock - The Twilight Bell Path": ItemData(2000300207, ItemClassification.progression),
}

relic_groups = {
    "Burger": {"Relic (Burger Patty)", "Relic (Burger Cushion)"},
    "Train": {"Relic (Mountain Set)", "Relic (Train)"},
    "UFO": {"Relic (UFO)", "Relic (Cow)", "Relic (Cool Cow)", "Relic (Tin-foil Hat Cow)"},
    "Crayon": {"Relic (Crayon Box)", "Relic (Red Crayon)", "Relic (Blue Crayon)", "Relic (Green Crayon)"},
    "Cake": {"Relic (Cake Stand)", "Relic (Chocolate Cake)", "Relic (Chocolate Cake Slice)", "Relic (Shortcake)"},
    "Necklace": {"Relic (Necklace Bust)", "Relic (Necklace)"},
}

item_frequencies = {
    "Badge Pin": 2,
    "Progressive Painting Unlock": 3,
}

junk_weights = {
    "25 Pons": 50,
    "50 Pons": 25,
    "100 Pons": 10,
    "Health Pon": 35,
    "Random Cosmetic": 35,
}

item_table = {
    **ahit_items,
    **act_contracts,
    **alps_hooks,
}
