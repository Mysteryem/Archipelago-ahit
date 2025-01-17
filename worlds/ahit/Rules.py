from worlds.AutoWorld import World, CollectionState
from worlds.generic.Rules import add_rule, set_rule
from .Locations import location_table, zipline_unlocks, is_location_valid, contract_locations, \
    shop_locations, event_locs, snatcher_coins
from .Types import HatType, ChapterIndex, hat_type_to_item, Difficulty, HatDLC
from BaseClasses import Location, Entrance, Region
import typing


act_connections = {
    "Mafia Town - Act 2": ["Mafia Town - Act 1"],
    "Mafia Town - Act 3": ["Mafia Town - Act 1"],
    "Mafia Town - Act 4": ["Mafia Town - Act 2", "Mafia Town - Act 3"],
    "Mafia Town - Act 6": ["Mafia Town - Act 4"],
    "Mafia Town - Act 7": ["Mafia Town - Act 4"],
    "Mafia Town - Act 5": ["Mafia Town - Act 6", "Mafia Town - Act 7"],

    "Battle of the Birds - Act 2": ["Battle of the Birds - Act 1"],
    "Battle of the Birds - Act 3": ["Battle of the Birds - Act 1"],
    "Battle of the Birds - Act 4": ["Battle of the Birds - Act 2", "Battle of the Birds - Act 3"],
    "Battle of the Birds - Act 5": ["Battle of the Birds - Act 2", "Battle of the Birds - Act 3"],
    "Battle of the Birds - Finale A": ["Battle of the Birds - Act 4", "Battle of the Birds - Act 5"],
    "Battle of the Birds - Finale B": ["Battle of the Birds - Finale A"],

    "Subcon Forest - Finale": ["Subcon Forest - Act 1", "Subcon Forest - Act 2",
                               "Subcon Forest - Act 3", "Subcon Forest - Act 4",
                               "Subcon Forest - Act 5"],

    "The Arctic Cruise - Act 2":  ["The Arctic Cruise - Act 1"],
    "The Arctic Cruise - Finale": ["The Arctic Cruise - Act 2"],
}


def can_use_hat(state: CollectionState, world: World, hat: HatType) -> bool:
    if world.options.HatItems.value > 0:
        return state.has(hat_type_to_item[hat], world.player)

    return state.count("Yarn", world.player) >= get_hat_cost(world, hat)


def get_hat_cost(world: World, hat: HatType) -> int:
    cost: int = 0
    costs = world.get_hat_yarn_costs()
    for h in world.get_hat_craft_order():
        cost += costs[h]
        if h == hat:
            break

    return cost


def can_sdj(state: CollectionState, world: World):
    return can_use_hat(state, world, HatType.SPRINT)


def painting_logic(world: World) -> bool:
    return world.options.ShuffleSubconPaintings.value > 0


# -1 = Normal, 0 = Moderate, 1 = Hard, 2 = Expert
def get_difficulty(world: World) -> Difficulty:
    return Difficulty(world.options.LogicDifficulty.value)


def has_paintings(state: CollectionState, world: World, count: int, allow_skip: bool = True) -> bool:
    if not painting_logic(world):
        return True

    if world.options.NoPaintingSkips.value == 0 and allow_skip:
        # In Moderate there is a very easy trick to skip all the walls, except for the one guarding the boss arena
        if get_difficulty(world) >= Difficulty.MODERATE:
            return True

    return state.count("Progressive Painting Unlock", world.player) >= count


def zipline_logic(world: World) -> bool:
    return world.options.ShuffleAlpineZiplines.value > 0


def can_use_hookshot(state: CollectionState, world: World):
    return state.has("Hookshot Badge", world.player)


def can_hit(state: CollectionState, world: World, umbrella_only: bool = False):
    if world.options.UmbrellaLogic.value == 0:
        return True

    return state.has("Umbrella", world.player) or not umbrella_only and can_use_hat(state, world, HatType.BREWING)


def can_surf(state: CollectionState, world: World):
    return state.has("No Bonk Badge", world.player)


def has_relic_combo(state: CollectionState, world: World, relic: str) -> bool:
    return state.has_group(relic, world.player, len(world.item_name_groups[relic]))


def get_relic_count(state: CollectionState, world: World, relic: str) -> int:
    return state.count_group(relic, world.player)


# Only use for rifts
def can_clear_act(state: CollectionState, world: World, act_entrance: str) -> bool:
    entrance: Entrance = world.multiworld.get_entrance(act_entrance, world.player)
    if not state.can_reach(entrance.connected_region, "Region", world.player):
        return False

    if "Free Roam" in entrance.connected_region.name:
        return True

    name: str = f"Act Completion ({entrance.connected_region.name})"
    return world.multiworld.get_location(name, world.player).access_rule(state)


def can_clear_alpine(state: CollectionState, world: World) -> bool:
    return state.has("Birdhouse Cleared", world.player) and state.has("Lava Cake Cleared", world.player) \
            and state.has("Windmill Cleared", world.player) and state.has("Twilight Bell Cleared", world.player)


def can_clear_metro(state: CollectionState, world: World) -> bool:
    return state.has("Nyakuza Intro Cleared", world.player) \
           and state.has("Yellow Overpass Station Cleared", world.player) \
           and state.has("Yellow Overpass Manhole Cleared", world.player) \
           and state.has("Green Clean Station Cleared", world.player) \
           and state.has("Green Clean Manhole Cleared", world.player) \
           and state.has("Bluefin Tunnel Cleared", world.player) \
           and state.has("Pink Paw Station Cleared", world.player) \
           and state.has("Pink Paw Manhole Cleared", world.player)


def set_rules(world: World):
    # First, chapter access
    starting_chapter = ChapterIndex(world.options.StartingChapter.value)
    world.set_chapter_cost(starting_chapter, 0)

    # Chapter costs increase progressively. Randomly decide the chapter order, except for Finale
    chapter_list: typing.List[ChapterIndex] = [ChapterIndex.MAFIA, ChapterIndex.BIRDS,
                                               ChapterIndex.SUBCON, ChapterIndex.ALPINE]

    final_chapter = ChapterIndex.FINALE
    if world.options.EndGoal.value == 2:
        final_chapter = ChapterIndex.METRO
        chapter_list.append(ChapterIndex.FINALE)
    elif world.options.EndGoal.value == 3:
        final_chapter = None
        chapter_list.append(ChapterIndex.FINALE)

    if world.is_dlc1():
        chapter_list.append(ChapterIndex.CRUISE)

    if world.is_dlc2() and final_chapter is not ChapterIndex.METRO:
        chapter_list.append(ChapterIndex.METRO)

    chapter_list.remove(starting_chapter)
    world.random.shuffle(chapter_list)

    if starting_chapter is not ChapterIndex.ALPINE and (world.is_dlc1() or world.is_dlc2()):
        index1: int = 69
        index2: int = 69
        pos: int
        lowest_index: int
        chapter_list.remove(ChapterIndex.ALPINE)

        if world.is_dlc1():
            index1 = chapter_list.index(ChapterIndex.CRUISE)

        if world.is_dlc2() and final_chapter is not ChapterIndex.METRO:
            index2 = chapter_list.index(ChapterIndex.METRO)

        lowest_index = min(index1, index2)
        if lowest_index == 0:
            pos = 0
        else:
            pos = world.random.randint(0, lowest_index)

        chapter_list.insert(pos, ChapterIndex.ALPINE)

    if world.is_dlc1() and world.is_dlc2() and final_chapter is not ChapterIndex.METRO:
        chapter_list.remove(ChapterIndex.METRO)
        index = chapter_list.index(ChapterIndex.CRUISE)
        if index >= len(chapter_list):
            chapter_list.append(ChapterIndex.METRO)
        else:
            chapter_list.insert(world.random.randint(index+1, len(chapter_list)), ChapterIndex.METRO)

    lowest_cost: int = world.options.LowestChapterCost.value
    highest_cost: int = world.options.HighestChapterCost.value
    cost_increment: int = world.options.ChapterCostIncrement.value
    min_difference: int = world.options.ChapterCostMinDifference.value
    last_cost: int = 0
    cost: int
    loop_count: int = 0

    for chapter in chapter_list:
        min_range: int = lowest_cost + (cost_increment * loop_count)
        if min_range >= highest_cost:
            min_range = highest_cost-1

        value: int = world.random.randint(min_range, min(highest_cost, max(lowest_cost, last_cost + cost_increment)))

        cost = world.random.randint(value, min(value + cost_increment, highest_cost))
        if loop_count >= 1:
            if last_cost + min_difference > cost:
                cost = last_cost + min_difference

        cost = min(cost, highest_cost)
        world.set_chapter_cost(chapter, cost)
        last_cost = cost
        loop_count += 1

    if final_chapter is not None:
        world.set_chapter_cost(final_chapter, world.random.randint(
                                                            world.options.FinalChapterMinCost.value,
                                                            world.options.FinalChapterMaxCost.value))

    add_rule(world.multiworld.get_entrance("Telescope -> Mafia Town", world.player),
             lambda state: state.has("Time Piece", world.player, world.get_chapter_cost(ChapterIndex.MAFIA)))

    add_rule(world.multiworld.get_entrance("Telescope -> Battle of the Birds", world.player),
             lambda state: state.has("Time Piece", world.player, world.get_chapter_cost(ChapterIndex.BIRDS)))

    add_rule(world.multiworld.get_entrance("Telescope -> Subcon Forest", world.player),
             lambda state: state.has("Time Piece", world.player, world.get_chapter_cost(ChapterIndex.SUBCON)))

    add_rule(world.multiworld.get_entrance("Telescope -> Alpine Skyline", world.player),
             lambda state: state.has("Time Piece", world.player, world.get_chapter_cost(ChapterIndex.ALPINE)))

    add_rule(world.multiworld.get_entrance("Telescope -> Time's End", world.player),
             lambda state: state.has("Time Piece", world.player, world.get_chapter_cost(ChapterIndex.FINALE))
             and can_use_hat(state, world, HatType.BREWING) and can_use_hat(state, world, HatType.DWELLER))

    if world.is_dlc1():
        add_rule(world.multiworld.get_entrance("Telescope -> The Arctic Cruise", world.player),
                 lambda state: state.has("Time Piece", world.player, world.get_chapter_cost(ChapterIndex.ALPINE))
                 and state.has("Time Piece", world.player, world.get_chapter_cost(ChapterIndex.CRUISE)))

    if world.is_dlc2():
        add_rule(world.multiworld.get_entrance("Telescope -> Nyakuza Metro", world.player),
                 lambda state: state.has("Time Piece", world.player, world.get_chapter_cost(ChapterIndex.ALPINE))
                 and state.has("Time Piece", world.player, world.get_chapter_cost(ChapterIndex.METRO))
                 and can_use_hat(state, world, HatType.DWELLER) and can_use_hat(state, world, HatType.ICE))

    if world.options.ActRandomizer.value == 0:
        set_default_rift_rules(world)

    table = {**location_table, **event_locs}
    location: Location
    for (key, data) in table.items():
        if not is_location_valid(world, key):
            continue

        if key in contract_locations.keys():
            continue

        if data.dlc_flags & HatDLC.death_wish and key in snatcher_coins.keys():
            key = f"{key} ({data.region})"

        location = world.multiworld.get_location(key, world.player)

        for hat in data.required_hats:
            if hat is not HatType.NONE:
                add_rule(location, lambda state, h=hat: can_use_hat(state, world, h))

        if data.hookshot:
            add_rule(location, lambda state: can_use_hookshot(state, world))

        if data.umbrella and world.options.UmbrellaLogic.value > 0:
            add_rule(location, lambda state: state.has("Umbrella", world.player))

        if data.paintings > 0 and world.options.ShuffleSubconPaintings.value > 0:
            add_rule(location, lambda state, paintings=data.paintings: has_paintings(state, world, paintings))

        if data.hit_requirement > 0:
            if data.hit_requirement == 1:
                add_rule(location, lambda state: can_hit(state, world))
            elif data.hit_requirement == 2:  # Can bypass with Dweller Mask (dweller bells)
                add_rule(location, lambda state: can_hit(state, world) or can_use_hat(state, world, HatType.DWELLER))

        for misc in data.misc_required:
            add_rule(location, lambda state, item=misc: state.has(item, world.player))

    set_specific_rules(world)

    # Putting all of this here, so it doesn't get overridden by anything
    # Illness starts the player past the intro
    alpine_entrance = world.multiworld.get_entrance("AFR -> Alpine Skyline Area", world.player)
    add_rule(alpine_entrance, lambda state: can_use_hookshot(state, world))
    if world.options.UmbrellaLogic.value > 0:
        add_rule(alpine_entrance, lambda state: state.has("Umbrella", world.player))

    if zipline_logic(world):
        add_rule(world.multiworld.get_entrance("-> The Birdhouse", world.player),
                 lambda state: state.has("Zipline Unlock - The Birdhouse Path", world.player))

        add_rule(world.multiworld.get_entrance("-> The Lava Cake", world.player),
                 lambda state: state.has("Zipline Unlock - The Lava Cake Path", world.player))

        add_rule(world.multiworld.get_entrance("-> The Windmill", world.player),
                 lambda state: state.has("Zipline Unlock - The Windmill Path", world.player))

        add_rule(world.multiworld.get_entrance("-> The Twilight Bell", world.player),
                 lambda state: state.has("Zipline Unlock - The Twilight Bell Path", world.player))

        add_rule(world.multiworld.get_location("Act Completion (The Illness has Spread)", world.player),
                 lambda state: state.has("Zipline Unlock - The Birdhouse Path", world.player)
                 and state.has("Zipline Unlock - The Lava Cake Path", world.player)
                 and state.has("Zipline Unlock - The Windmill Path", world.player))

    if zipline_logic(world):
        for (loc, zipline) in zipline_unlocks.items():
            add_rule(world.multiworld.get_location(loc, world.player),
                     lambda state, z=zipline: state.has(z, world.player))

    for loc in world.multiworld.get_region("Alpine Skyline Area (TIHS)", world.player).locations:
        if "Goat Village" in loc.name:
            continue
        # This needs some special handling
        if loc.name == "Alpine Skyline - Goat Refinery":
            add_rule(loc, lambda state: state.has("AFR Access", world.player)
                     and can_use_hookshot(state, world)
                     and can_hit(state, world, True))

            difficulty: Difficulty = Difficulty(world.options.LogicDifficulty.value)
            if difficulty >= Difficulty.MODERATE:
                add_rule(loc, lambda state: state.has("TIHS Access", world.player)
                         and can_use_hat(state, world, HatType.SPRINT), "or")
            elif difficulty >= Difficulty.HARD:
                add_rule(loc, lambda state: state.has("TIHS Access", world.player, "or"))

            continue

        add_rule(loc, lambda state: can_use_hookshot(state, world))

    dummy_entrances: typing.List[Entrance] = []
      
    for (key, acts) in act_connections.items():
        if "Arctic Cruise" in key and not world.is_dlc1():
            continue

        i: int = 1
        entrance: Entrance = world.multiworld.get_entrance(key, world.player)
        region: Region = entrance.connected_region
        access_rules: typing.List[typing.Callable[[CollectionState], bool]] = []
        dummy_entrances.append(entrance)

        # Entrances to this act that we have to set access_rules on
        entrances: typing.List[Entrance] = []

        for act in acts:
            act_entrance: Entrance = world.multiworld.get_entrance(act, world.player)
            access_rules.append(act_entrance.access_rule)
            required_region = act_entrance.connected_region
            name: str = f"{key}: Connection {i}"
            new_entrance: Entrance = connect_regions(required_region, region, name, world.player)
            entrances.append(new_entrance)

            # Copy access rules from act completions
            if "Free Roam" not in required_region.name:
                rule: typing.Callable[[CollectionState], bool]
                name = f"Act Completion ({required_region.name})"
                rule = world.multiworld.get_location(name, world.player).access_rule
                access_rules.append(rule)

            i += 1

        for e in entrances:
            for rules in access_rules:
                add_rule(e, rules)

    for e in dummy_entrances:
        set_rule(e, lambda state: False)

    set_event_rules(world)

    if world.options.EndGoal.value == 1:
        world.multiworld.completion_condition[world.player] = lambda state: state.has("Time Piece Cluster", world.player)
    elif world.options.EndGoal.value == 2:
        world.multiworld.completion_condition[world.player] = lambda state: state.has("Rush Hour Cleared", world.player)


def set_specific_rules(world: World):
    add_rule(world.multiworld.get_location("Mafia Boss Shop Item", world.player),
             lambda state: state.has("Time Piece", world.player, 12)
             and state.has("Time Piece", world.player, world.get_chapter_cost(ChapterIndex.BIRDS)))

    add_rule(world.multiworld.get_location("Spaceship - Rumbi Abuse", world.player),
             lambda state: state.has("Time Piece", world.player, 4))

    set_mafia_town_rules(world)
    set_botb_rules(world)
    set_subcon_rules(world)
    set_alps_rules(world)

    if world.is_dlc1():
        set_dlc1_rules(world)

    if world.is_dlc2():
        set_dlc2_rules(world)

    difficulty: Difficulty = get_difficulty(world)

    if difficulty >= Difficulty.MODERATE:
        set_moderate_rules(world)

    if difficulty >= Difficulty.HARD:
        set_hard_rules(world)

    if difficulty >= 2:
        set_expert_rules(world)


def set_moderate_rules(world: World):
    # Moderate: Gallery without Brewing Hat
    set_rule(world.multiworld.get_location("Act Completion (Time Rift - Gallery)", world.player), lambda state: True)

    # Moderate: Above Boats via Ice Hat Sliding
    add_rule(world.multiworld.get_location("Mafia Town - Above Boats", world.player),
             lambda state: can_use_hat(state, world, HatType.ICE), "or")

    # Moderate: Clock Tower Chest + Ruined Tower with nothing
    add_rule(world.multiworld.get_location("Mafia Town - Clock Tower Chest", world.player), lambda state: True)
    add_rule(world.multiworld.get_location("Mafia Town - Top of Ruined Tower", world.player), lambda state: True)

    # Moderate: enter and clear The Subcon Well without Hookshot and without hitting the bell
    for loc in world.multiworld.get_region("The Subcon Well", world.player).locations:
        set_rule(loc, lambda state: has_paintings(state, world, 1))

    # Moderate: Vanessa Manor with nothing
    for loc in world.multiworld.get_region("Queen Vanessa's Manor", world.player).locations:
        set_rule(loc, lambda state: True)

    set_rule(world.multiworld.get_location("Subcon Forest - Manor Rooftop", world.player), lambda state: True)

    # Moderate: get to Birdhouse/Yellow Band Hills without Brewing Hat
    set_rule(world.multiworld.get_entrance("-> The Birdhouse", world.player),
             lambda state: can_use_hookshot(state, world))
    set_rule(world.multiworld.get_location("Alpine Skyline - Yellow Band Hills", world.player),
             lambda state: can_use_hookshot(state, world))

    # Moderate: The Birdhouse - Dweller Platforms Relic with only Birdhouse access
    set_rule(world.multiworld.get_location("Alpine Skyline - The Birdhouse: Dweller Platforms Relic", world.player),
             lambda state: True)

    # Moderate: Twilight Path without Dweller Mask
    set_rule(world.multiworld.get_location("Alpine Skyline - The Twilight Path", world.player), lambda state: True)

    # Moderate: Mystifying Time Mesa time trial without hats
    set_rule(world.multiworld.get_location("Alpine Skyline - Mystifying Time Mesa: Zipline", world.player),
             lambda state: can_use_hookshot(state, world))

    # Moderate: Finale without Hookshot
    set_rule(world.multiworld.get_location("Act Completion (The Finale)", world.player),
             lambda state: can_use_hat(state, world, HatType.DWELLER))

    if world.is_dlc1():
        # Moderate: clear Rock the Boat without Ice Hat
        add_rule(world.multiworld.get_location("Rock the Boat - Post Captain Rescue", world.player), lambda state: True)
        add_rule(world.multiworld.get_location("Act Completion (Rock the Boat)", world.player), lambda state: True)

        # Moderate: clear Deep Sea without Ice Hat
        set_rule(world.multiworld.get_location("Act Completion (Time Rift - Deep Sea)", world.player),
                 lambda state: can_use_hookshot(state, world) and can_use_hat(state, world, HatType.DWELLER))

    # There is a glitched fall damage volume near the Yellow Overpass time piece that warps the player to Pink Paw.
    # Yellow Overpass time piece can also be reached without Hookshot quite easily.
    if world.is_dlc2():
        # No Hookshot
        set_rule(world.multiworld.get_location("Act Completion (Yellow Overpass Station)", world.player),
                 lambda state: True)

        # No Dweller, Hookshot, or Time Stop for these
        set_rule(world.multiworld.get_location("Pink Paw Station - Cat Vacuum", world.player), lambda state: True)
        set_rule(world.multiworld.get_location("Pink Paw Station - Behind Fan", world.player), lambda state: True)

        # Moderate: clear Rush Hour without Hookshot
        set_rule(world.multiworld.get_location("Act Completion (Rush Hour)", world.player),
                 lambda state: state.has("Metro Ticket - Pink", world.player)
                 and state.has("Metro Ticket - Yellow", world.player)
                 and state.has("Metro Ticket - Blue", world.player)
                 and can_use_hat(state, world, HatType.ICE)
                 and can_use_hat(state, world, HatType.BREWING))

        # Moderate: Bluefin Tunnel + Pink Paw Station without tickets
        if world.options.NoTicketSkips.value == 0:
            set_rule(world.multiworld.get_entrance("-> Pink Paw Station", world.player), lambda state: True)
            set_rule(world.multiworld.get_entrance("-> Bluefin Tunnel", world.player), lambda state: True)


def set_hard_rules(world: World):
    # Hard: clear Time Rift - The Twilight Bell with Sprint+Scooter only
    add_rule(world.multiworld.get_location("Act Completion (Time Rift - The Twilight Bell)", world.player),
             lambda state: can_use_hat(state, world, HatType.SPRINT)
             and state.has("Scooter Badge", world.player), "or")

    # No Dweller Mask required
    set_rule(world.multiworld.get_location("Subcon Forest - Dweller Floating Rocks", world.player),
             lambda state: has_paintings(state, world, 3))

    # Cherry bridge over boss arena gap (painting still expected)
    set_rule(world.multiworld.get_location("Subcon Forest - Boss Arena Chest", world.player),
             lambda state: has_paintings(state, world, 1, False) or state.has("YCHE Access", world.player))

    set_rule(world.multiworld.get_location("Subcon Forest - Noose Treehouse", world.player),
             lambda state: has_paintings(state, world, 2, True))
    set_rule(world.multiworld.get_location("Subcon Forest - Long Tree Climb Chest", world.player),
             lambda state: has_paintings(state, world, 2, True))
    set_rule(world.multiworld.get_location("Subcon Forest - Tall Tree Hookshot Swing", world.player),
             lambda state: has_paintings(state, world, 3, True))

    # SDJ
    add_rule(world.multiworld.get_location("Subcon Forest - Long Tree Climb Chest", world.player),
             lambda state: can_sdj(state, world) and has_paintings(state, world, 2), "or")

    add_rule(world.multiworld.get_location("Subcon Forest - Dweller Platforming Tree B", world.player),
             lambda state: has_paintings(state, world, 3) and can_sdj(state, world), "or")

    add_rule(world.multiworld.get_location("Act Completion (Time Rift - Curly Tail Trail)", world.player),
             lambda state: can_sdj(state, world), "or")

    # Finale Telescope with only Ice Hat
    add_rule(world.multiworld.get_entrance("Telescope -> Time's End", world.player),
             lambda state: can_use_hat(state, world, HatType.ICE), "or")

    if world.is_dlc1():
        # Hard: clear Deep Sea without Dweller Mask
        set_rule(world.multiworld.get_location("Act Completion (Time Rift - Deep Sea)", world.player),
                 lambda state: can_use_hookshot(state, world))

    if world.is_dlc2():
        # Hard: clear Green Clean Manhole without Dweller Mask
        set_rule(world.multiworld.get_location("Act Completion (Green Clean Manhole)", world.player),
                 lambda state: can_use_hat(state, world, HatType.ICE))

        # Hard: clear Rush Hour with Brewing Hat only
        if world.options.NoTicketSkips.value != 1:
            set_rule(world.multiworld.get_location("Act Completion (Rush Hour)", world.player),
                     lambda state: can_use_hat(state, world, HatType.BREWING))
        else:
            set_rule(world.multiworld.get_location("Act Completion (Rush Hour)", world.player),
                     lambda state: can_use_hat(state, world, HatType.BREWING)
                     and state.has("Metro Ticket - Yellow", world.player)
                     and state.has("Metro Ticket - Blue", world.player)
                     and state.has("Metro Ticket - Pink", world.player))


def set_expert_rules(world: World):
    # Finale Telescope with no hats
    set_rule(world.multiworld.get_entrance("Telescope -> Time's End", world.player),
             lambda state: state.has("Time Piece", world.player, world.get_chapter_cost(ChapterIndex.FINALE)))

    # Expert: Mafia Town - Above Boats, Top of Lighthouse, and Hot Air Balloon with nothing
    set_rule(world.multiworld.get_location("Mafia Town - Above Boats", world.player), lambda state: True)
    set_rule(world.multiworld.get_location("Mafia Town - Top of Lighthouse", world.player), lambda state: True)
    set_rule(world.multiworld.get_location("Mafia Town - Hot Air Balloon", world.player), lambda state: True)

    # Expert: Clear Dead Bird Studio with nothing
    for loc in world.multiworld.get_region("Dead Bird Studio - Post Elevator Area", world.player).locations:
        set_rule(loc, lambda state: True)

    set_rule(world.multiworld.get_location("Act Completion (Dead Bird Studio)", world.player), lambda state: True)

    # Expert: Clear Dead Bird Studio Basement without Hookshot
    for loc in world.multiworld.get_region("Dead Bird Studio Basement", world.player).locations:
        set_rule(loc, lambda state: True)

    # Expert: get to and clear Twilight Bell without Dweller Mask.
    # Dweller Mask OR Sprint Hat OR Brewing Hat OR Time Stop + Umbrella required to complete act.
    add_rule(world.multiworld.get_entrance("-> The Twilight Bell", world.player),
             lambda state: can_use_hookshot(state, world), "or")

    add_rule(world.multiworld.get_location("Act Completion (The Twilight Bell)", world.player),
             lambda state: can_use_hat(state, world, HatType.BREWING)
             or can_use_hat(state, world, HatType.DWELLER)
             or can_use_hat(state, world, HatType.SPRINT)
             or (can_use_hat(state, world, HatType.TIME_STOP) and state.has("Umbrella", world.player)))

    # Expert: Time Rift - Curly Tail Trail with nothing
    # Time Rift - Twilight Bell and Time Rift - Village with nothing
    set_rule(world.multiworld.get_location("Act Completion (Time Rift - Curly Tail Trail)", world.player),
             lambda state: True)

    set_rule(world.multiworld.get_location("Act Completion (Time Rift - Village)", world.player), lambda state: True)
    set_rule(world.multiworld.get_location("Act Completion (Time Rift - The Twilight Bell)", world.player),
             lambda state: True)

    # Expert: Cherry Hovering
    entrance = connect_regions(world.multiworld.get_region("Your Contract has Expired", world.player),
                               world.multiworld.get_region("Subcon Forest Area", world.player),
                               "Subcon Forest Entrance YCHE", world.player)

    if world.options.NoPaintingSkips.value > 0:
        add_rule(entrance, lambda state: has_paintings(state, world, 1))

    set_rule(world.multiworld.get_location("Act Completion (Toilet of Doom)", world.player),
             lambda state: can_use_hookshot(state, world) and can_hit(state, world)
             and has_paintings(state, world, 1, True))

    # Set painting rules only. Skipping paintings is determined in has_paintings
    set_rule(world.multiworld.get_location("Subcon Forest - Boss Arena Chest", world.player),
             lambda state: has_paintings(state, world, 1, True))
    set_rule(world.multiworld.get_location("Subcon Forest - Dweller Platforming Tree B", world.player),
             lambda state: has_paintings(state, world, 3, True))
    set_rule(world.multiworld.get_location("Subcon Forest - Magnet Badge Bush", world.player),
             lambda state: has_paintings(state, world, 3, True))

    # You can cherry hover to Snatcher's post-fight cutscene, which completes the level without having to fight him
    connect_regions(world.multiworld.get_region("Subcon Forest Area", world.player),
                    world.multiworld.get_region("Your Contract has Expired", world.player),
                    "Snatcher Hover", world.player)
    set_rule(world.multiworld.get_location("Act Completion (Your Contract has Expired)", world.player),
             lambda state: True)

    if world.is_dlc2():
        # Expert: clear Rush Hour with nothing
        if world.options.NoTicketSkips.value == 0:
            set_rule(world.multiworld.get_location("Act Completion (Rush Hour)", world.player), lambda state: True)
        else:
            set_rule(world.multiworld.get_location("Act Completion (Rush Hour)", world.player),
                     lambda state: state.has("Metro Ticket - Yellow", world.player)
                     and state.has("Metro Ticket - Blue", world.player)
                     and state.has("Metro Ticket - Pink", world.player))


def set_mafia_town_rules(world: World):
    add_rule(world.multiworld.get_location("Mafia Town - Behind HQ Chest", world.player),
             lambda state: state.can_reach("Act Completion (Heating Up Mafia Town)", "Location", world.player)
             or state.can_reach("Down with the Mafia!", "Region", world.player)
             or state.can_reach("Cheating the Race", "Region", world.player)
             or state.can_reach("The Golden Vault", "Region", world.player))

    # Old guys don't appear in SCFOS
    add_rule(world.multiworld.get_location("Mafia Town - Old Man (Steel Beams)", world.player),
             lambda state: state.can_reach("Welcome to Mafia Town", "Region", world.player)
             or state.can_reach("Barrel Battle", "Region", world.player)
             or state.can_reach("Cheating the Race", "Region", world.player)
             or state.can_reach("The Golden Vault", "Region", world.player)
             or state.can_reach("Down with the Mafia!", "Region", world.player))

    add_rule(world.multiworld.get_location("Mafia Town - Old Man (Seaside Spaghetti)", world.player),
             lambda state: state.can_reach("Welcome to Mafia Town", "Region", world.player)
             or state.can_reach("Barrel Battle", "Region", world.player)
             or state.can_reach("Cheating the Race", "Region", world.player)
             or state.can_reach("The Golden Vault", "Region", world.player)
             or state.can_reach("Down with the Mafia!", "Region", world.player))

    # Only available outside She Came from Outer Space
    add_rule(world.multiworld.get_location("Mafia Town - Mafia Geek Platform", world.player),
             lambda state: state.can_reach("Welcome to Mafia Town", "Region", world.player)
             or state.can_reach("Barrel Battle", "Region", world.player)
             or state.can_reach("Down with the Mafia!", "Region", world.player)
             or state.can_reach("Cheating the Race", "Region", world.player)
             or state.can_reach("Heating Up Mafia Town", "Region", world.player)
             or state.can_reach("The Golden Vault", "Region", world.player))

    # Only available outside Down with the Mafia! (for some reason)
    add_rule(world.multiworld.get_location("Mafia Town - On Scaffolding", world.player),
             lambda state: state.can_reach("Welcome to Mafia Town", "Region", world.player)
             or state.can_reach("Barrel Battle", "Region", world.player)
             or state.can_reach("She Came from Outer Space", "Region", world.player)
             or state.can_reach("Cheating the Race", "Region", world.player)
             or state.can_reach("Heating Up Mafia Town", "Region", world.player)
             or state.can_reach("The Golden Vault", "Region", world.player))

    # For some reason, the brewing crate is removed in HUMT
    add_rule(world.multiworld.get_location("Mafia Town - Secret Cave", world.player),
             lambda state: state.has("HUMT Access", world.player), "or")

    # Can bounce across the lava to get this without Hookshot (need to die though)
    add_rule(world.multiworld.get_location("Mafia Town - Above Boats", world.player),
             lambda state: state.has("HUMT Access", world.player), "or")

    ctr_logic: int = world.options.CTRLogic.value
    if ctr_logic == 3:
        set_rule(world.multiworld.get_location("Act Completion (Cheating the Race)", world.player), lambda state: True)
    elif ctr_logic == 2:
        add_rule(world.multiworld.get_location("Act Completion (Cheating the Race)", world.player),
                 lambda state: can_use_hat(state, world, HatType.SPRINT), "or")
    elif ctr_logic == 1:
        add_rule(world.multiworld.get_location("Act Completion (Cheating the Race)", world.player),
                 lambda state: can_use_hat(state, world, HatType.SPRINT)
                 and state.has("Scooter Badge", world.player), "or")


def set_botb_rules(world: World):
    if world.options.UmbrellaLogic.value == 0 and get_difficulty(world) < Difficulty.MODERATE:
        set_rule(world.multiworld.get_location("Dead Bird Studio - DJ Grooves Sign Chest", world.player),
                 lambda state: state.has("Umbrella", world.player) or can_use_hat(state, world, HatType.BREWING))
        set_rule(world.multiworld.get_location("Dead Bird Studio - Tepee Chest", world.player),
                 lambda state: state.has("Umbrella", world.player) or can_use_hat(state, world, HatType.BREWING))
        set_rule(world.multiworld.get_location("Dead Bird Studio - Conductor Chest", world.player),
                 lambda state: state.has("Umbrella", world.player) or can_use_hat(state, world, HatType.BREWING))
        set_rule(world.multiworld.get_location("Act Completion (Dead Bird Studio)", world.player),
                 lambda state: state.has("Umbrella", world.player) or can_use_hat(state, world, HatType.BREWING))


def set_subcon_rules(world: World):
    set_rule(world.multiworld.get_location("Act Completion (Time Rift - Village)", world.player),
             lambda state: can_use_hat(state, world, HatType.BREWING) or state.has("Umbrella", world.player)
             or can_use_hat(state, world, HatType.DWELLER))

    # You can't skip over the boss arena wall without cherry hover, so these two need to be set this way
    set_rule(world.multiworld.get_location("Subcon Forest - Boss Arena Chest", world.player),
             lambda state: state.has("TOD Access", world.player) and can_use_hookshot(state, world)
             and has_paintings(state, world, 1, False) or state.has("YCHE Access", world.player))

    # The painting wall can't be skipped without cherry hover, which is Expert
    set_rule(world.multiworld.get_location("Act Completion (Toilet of Doom)", world.player),
             lambda state: can_use_hookshot(state, world) and can_hit(state, world)
             and has_paintings(state, world, 1, False))

    add_rule(world.multiworld.get_entrance("Subcon Forest - Act 2", world.player),
             lambda state: state.has("Snatcher's Contract - The Subcon Well", world.player))

    add_rule(world.multiworld.get_entrance("Subcon Forest - Act 3", world.player),
             lambda state: state.has("Snatcher's Contract - Toilet of Doom", world.player))

    add_rule(world.multiworld.get_entrance("Subcon Forest - Act 4", world.player),
             lambda state: state.has("Snatcher's Contract - Queen Vanessa's Manor", world.player))

    add_rule(world.multiworld.get_entrance("Subcon Forest - Act 5", world.player),
             lambda state: state.has("Snatcher's Contract - Mail Delivery Service", world.player))

    if painting_logic(world):
        add_rule(world.multiworld.get_location("Act Completion (Contractual Obligations)", world.player),
                 lambda state: has_paintings(state, world, 1, False))

        for key in contract_locations:
            if key == "Snatcher's Contract - The Subcon Well":
                continue

            add_rule(world.multiworld.get_location(key, world.player), lambda state: has_paintings(state, world, 1))


def set_alps_rules(world: World):
    add_rule(world.multiworld.get_entrance("-> The Birdhouse", world.player),
             lambda state: can_use_hookshot(state, world) and can_use_hat(state, world, HatType.BREWING))

    add_rule(world.multiworld.get_entrance("-> The Lava Cake", world.player),
             lambda state: can_use_hookshot(state, world))

    add_rule(world.multiworld.get_entrance("-> The Windmill", world.player),
             lambda state: can_use_hookshot(state, world))

    add_rule(world.multiworld.get_entrance("-> The Twilight Bell", world.player),
             lambda state: can_use_hookshot(state, world) and can_use_hat(state, world, HatType.DWELLER))

    add_rule(world.multiworld.get_location("Alpine Skyline - Mystifying Time Mesa: Zipline", world.player),
             lambda state: can_use_hat(state, world, HatType.SPRINT) or can_use_hat(state, world, HatType.TIME_STOP))

    add_rule(world.multiworld.get_entrance("Alpine Skyline - Finale", world.player),
             lambda state: can_clear_alpine(state, world))


def set_dlc1_rules(world: World):
    add_rule(world.multiworld.get_entrance("Cruise Ship Entrance BV", world.player),
             lambda state: can_use_hookshot(state, world))

    # This particular item isn't present in Act 3 for some reason, yes in vanilla too
    add_rule(world.multiworld.get_location("The Arctic Cruise - Toilet", world.player),
             lambda state: state.can_reach("Bon Voyage!", "Region", world.player)
             or state.can_reach("Ship Shape", "Region", world.player))


def set_dlc2_rules(world: World):
    add_rule(world.multiworld.get_entrance("-> Bluefin Tunnel", world.player),
             lambda state: state.has("Metro Ticket - Green", world.player)
             or state.has("Metro Ticket - Blue", world.player))

    add_rule(world.multiworld.get_entrance("-> Pink Paw Station", world.player),
             lambda state: state.has("Metro Ticket - Pink", world.player)
             or state.has("Metro Ticket - Yellow", world.player) and state.has("Metro Ticket - Blue", world.player))

    add_rule(world.multiworld.get_entrance("Nyakuza Metro - Finale", world.player),
             lambda state: can_clear_metro(state, world))

    add_rule(world.multiworld.get_location("Act Completion (Rush Hour)", world.player),
             lambda state: state.has("Metro Ticket - Yellow", world.player)
             and state.has("Metro Ticket - Blue", world.player)
             and state.has("Metro Ticket - Pink", world.player))

    for key in shop_locations.keys():
        if "Green Clean Station Thug B" in key and is_location_valid(world, key):
            add_rule(world.multiworld.get_location(key, world.player),
                     lambda state: state.has("Metro Ticket - Yellow", world.player), "or")


def reg_act_connection(world: World, region: typing.Union[str, Region], unlocked_entrance: typing.Union[str, Entrance]):
    reg: Region
    entrance: Entrance
    if isinstance(region, str):
        reg = world.multiworld.get_region(region, world.player)
    else:
        reg = region

    if isinstance(unlocked_entrance, str):
        entrance = world.multiworld.get_entrance(unlocked_entrance, world.player)
    else:
        entrance = unlocked_entrance

    world.multiworld.register_indirect_condition(reg, entrance)


# See randomize_act_entrances in Regions.py
# Called before set_rules
def set_rift_rules(world: World, regions: typing.Dict[str, Region]):

    # This is accessing the regions in place of these time rifts, so we can set the rules on all the entrances.
    for entrance in regions["Time Rift - Gallery"].entrances:
        add_rule(entrance, lambda state: can_use_hat(state, world, HatType.BREWING)
                 and state.has("Time Piece", world.player, world.get_chapter_cost(ChapterIndex.BIRDS)))

    for entrance in regions["Time Rift - The Lab"].entrances:
        add_rule(entrance, lambda state: can_use_hat(state, world, HatType.DWELLER)
                 and state.has("Time Piece", world.player, world.get_chapter_cost(ChapterIndex.ALPINE)))

    for entrance in regions["Time Rift - Sewers"].entrances:
        add_rule(entrance, lambda state: can_clear_act(state, world, "Mafia Town - Act 4"))
        reg_act_connection(world, world.multiworld.get_entrance("Mafia Town - Act 4",
                                                                world.player).connected_region, entrance)

    for entrance in regions["Time Rift - Bazaar"].entrances:
        add_rule(entrance, lambda state: can_clear_act(state, world, "Mafia Town - Act 6"))
        reg_act_connection(world, world.multiworld.get_entrance("Mafia Town - Act 6",
                                                                world.player).connected_region, entrance)

    for entrance in regions["Time Rift - Mafia of Cooks"].entrances:
        add_rule(entrance, lambda state: has_relic_combo(state, world, "Burger"))

    for entrance in regions["Time Rift - The Owl Express"].entrances:
        add_rule(entrance, lambda state: can_clear_act(state, world, "Battle of the Birds - Act 2"))
        add_rule(entrance, lambda state: can_clear_act(state, world, "Battle of the Birds - Act 3"))
        reg_act_connection(world, world.multiworld.get_entrance("Battle of the Birds - Act 2",
                                                                world.player).connected_region, entrance)
        reg_act_connection(world, world.multiworld.get_entrance("Battle of the Birds - Act 3",
                                                                world.player).connected_region, entrance)

    for entrance in regions["Time Rift - The Moon"].entrances:
        add_rule(entrance, lambda state: can_clear_act(state, world, "Battle of the Birds - Act 4"))
        add_rule(entrance, lambda state: can_clear_act(state, world, "Battle of the Birds - Act 5"))
        reg_act_connection(world, world.multiworld.get_entrance("Battle of the Birds - Act 4",
                                                                world.player).connected_region, entrance)
        reg_act_connection(world, world.multiworld.get_entrance("Battle of the Birds - Act 5",
                                                                world.player).connected_region, entrance)

    for entrance in regions["Time Rift - Dead Bird Studio"].entrances:
        add_rule(entrance, lambda state: has_relic_combo(state, world, "Train"))

    for entrance in regions["Time Rift - Pipe"].entrances:
        add_rule(entrance, lambda state: can_clear_act(state, world, "Subcon Forest - Act 2"))
        reg_act_connection(world, world.multiworld.get_entrance("Subcon Forest - Act 2",
                                                                world.player).connected_region, entrance)
        if painting_logic(world):
            add_rule(entrance, lambda state: has_paintings(state, world, 2))

    for entrance in regions["Time Rift - Village"].entrances:
        add_rule(entrance, lambda state: can_clear_act(state, world, "Subcon Forest - Act 4"))
        reg_act_connection(world, world.multiworld.get_entrance("Subcon Forest - Act 4",
                                                                world.player).connected_region, entrance)

        if painting_logic(world):
            add_rule(entrance, lambda state: has_paintings(state, world, 2))

    for entrance in regions["Time Rift - Sleepy Subcon"].entrances:
        add_rule(entrance, lambda state: has_relic_combo(state, world, "UFO"))
        if painting_logic(world):
            add_rule(entrance, lambda state: has_paintings(state, world, 3))

    for entrance in regions["Time Rift - Curly Tail Trail"].entrances:
        add_rule(entrance, lambda state: state.has("Windmill Cleared", world.player))

    for entrance in regions["Time Rift - The Twilight Bell"].entrances:
        add_rule(entrance, lambda state: state.has("Twilight Bell Cleared", world.player))

    for entrance in regions["Time Rift - Alpine Skyline"].entrances:
        add_rule(entrance, lambda state: has_relic_combo(state, world, "Crayon"))

    if world.is_dlc1() > 0:
        for entrance in regions["Time Rift - Balcony"].entrances:
            add_rule(entrance, lambda state: can_clear_act(state, world, "The Arctic Cruise - Finale"))

        for entrance in regions["Time Rift - Deep Sea"].entrances:
            add_rule(entrance, lambda state: has_relic_combo(state, world, "Cake"))

    if world.is_dlc2() > 0:
        for entrance in regions["Time Rift - Rumbi Factory"].entrances:
            add_rule(entrance, lambda state: has_relic_combo(state, world, "Necklace"))


# Basically the same as above, but without the need of the dict since we are just setting defaults
# Called if Act Rando is disabled
def set_default_rift_rules(world: World):

    for entrance in world.multiworld.get_region("Time Rift - Gallery", world.player).entrances:
        add_rule(entrance, lambda state: can_use_hat(state, world, HatType.BREWING)
                 and state.has("Time Piece", world.player, world.get_chapter_cost(ChapterIndex.BIRDS)))

    for entrance in world.multiworld.get_region("Time Rift - The Lab", world.player).entrances:
        add_rule(entrance, lambda state: can_use_hat(state, world, HatType.DWELLER)
                 and state.has("Time Piece", world.player, world.get_chapter_cost(ChapterIndex.ALPINE)))

    for entrance in world.multiworld.get_region("Time Rift - Sewers", world.player).entrances:
        add_rule(entrance, lambda state: can_clear_act(state, world, "Mafia Town - Act 4"))
        reg_act_connection(world, "Down with the Mafia!", entrance.name)

    for entrance in world.multiworld.get_region("Time Rift - Bazaar", world.player).entrances:
        add_rule(entrance, lambda state: can_clear_act(state, world, "Mafia Town - Act 6"))
        reg_act_connection(world, "Heating Up Mafia Town", entrance.name)

    for entrance in world.multiworld.get_region("Time Rift - Mafia of Cooks", world.player).entrances:
        add_rule(entrance, lambda state: has_relic_combo(state, world, "Burger"))

    for entrance in world.multiworld.get_region("Time Rift - The Owl Express", world.player).entrances:
        add_rule(entrance, lambda state: can_clear_act(state, world, "Battle of the Birds - Act 2"))
        add_rule(entrance, lambda state: can_clear_act(state, world, "Battle of the Birds - Act 3"))
        reg_act_connection(world, "Murder on the Owl Express", entrance.name)
        reg_act_connection(world, "Picture Perfect", entrance.name)

    for entrance in world.multiworld.get_region("Time Rift - The Moon", world.player).entrances:
        add_rule(entrance, lambda state: can_clear_act(state, world, "Battle of the Birds - Act 4"))
        add_rule(entrance, lambda state: can_clear_act(state, world, "Battle of the Birds - Act 5"))
        reg_act_connection(world, "Train Rush", entrance.name)
        reg_act_connection(world, "The Big Parade", entrance.name)

    for entrance in world.multiworld.get_region("Time Rift - Dead Bird Studio", world.player).entrances:
        add_rule(entrance, lambda state: has_relic_combo(state, world, "Train"))

    for entrance in world.multiworld.get_region("Time Rift - Pipe", world.player).entrances:
        add_rule(entrance, lambda state: can_clear_act(state, world, "Subcon Forest - Act 2"))
        reg_act_connection(world, "The Subcon Well", entrance.name)
        if painting_logic(world):
            add_rule(entrance, lambda state: has_paintings(state, world, 2))

    for entrance in world.multiworld.get_region("Time Rift - Village", world.player).entrances:
        add_rule(entrance, lambda state: can_clear_act(state, world, "Subcon Forest - Act 4"))
        reg_act_connection(world, "Queen Vanessa's Manor", entrance.name)
        if painting_logic(world):
            add_rule(entrance, lambda state: has_paintings(state, world, 2))

    for entrance in world.multiworld.get_region("Time Rift - Sleepy Subcon", world.player).entrances:
        add_rule(entrance, lambda state: has_relic_combo(state, world, "UFO"))
        if painting_logic(world):
            add_rule(entrance, lambda state: has_paintings(state, world, 3))

    for entrance in world.multiworld.get_region("Time Rift - Curly Tail Trail", world.player).entrances:
        add_rule(entrance, lambda state: state.has("Windmill Cleared", world.player))

    for entrance in world.multiworld.get_region("Time Rift - The Twilight Bell", world.player).entrances:
        add_rule(entrance, lambda state: state.has("Twilight Bell Cleared", world.player))

    for entrance in world.multiworld.get_region("Time Rift - Alpine Skyline", world.player).entrances:
        add_rule(entrance, lambda state: has_relic_combo(state, world, "Crayon"))

    if world.is_dlc1():
        for entrance in world.multiworld.get_region("Time Rift - Balcony", world.player).entrances:
            add_rule(entrance, lambda state: can_clear_act(state, world, "The Arctic Cruise - Finale"))

        for entrance in world.multiworld.get_region("Time Rift - Deep Sea", world.player).entrances:
            add_rule(entrance, lambda state: has_relic_combo(state, world, "Cake"))

    if world.is_dlc2():
        for entrance in world.multiworld.get_region("Time Rift - Rumbi Factory", world.player).entrances:
            add_rule(entrance, lambda state: has_relic_combo(state, world, "Necklace"))


def set_event_rules(world: World):
    for (name, data) in event_locs.items():
        if not is_location_valid(world, name):
            continue

        if data.dlc_flags & HatDLC.death_wish and name in snatcher_coins.keys():
            name = f"{name} ({data.region})"

        event: Location = world.multiworld.get_location(name, world.player)

        if data.act_event:
            add_rule(event, world.multiworld.get_location(f"Act Completion ({data.region})", world.player).access_rule)


def connect_regions(start_region: Region, exit_region: Region, entrancename: str, player: int) -> Entrance:
    entrance = Entrance(player, entrancename, start_region)
    start_region.exits.append(entrance)
    entrance.connect(exit_region)
    return entrance
