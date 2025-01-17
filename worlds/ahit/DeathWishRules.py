from worlds.AutoWorld import World, CollectionState
from .Rules import can_use_hat, can_use_hookshot, can_hit, zipline_logic, get_difficulty, has_paintings
from .Types import HatType, Difficulty, HatInTimeLocation, HatInTimeItem, LocData
from .DeathWishLocations import dw_prereqs, dw_candles
from BaseClasses import Entrance, Location, ItemClassification
from worlds.generic.Rules import add_rule, set_rule
from typing import List, Callable
from .Regions import act_chapters
from .Locations import zero_jumps, zero_jumps_expert, zero_jumps_hard, death_wishes

# Any speedruns expect the player to have Sprint Hat
dw_requirements = {
    "Beat the Heat": LocData(umbrella=True),
    "So You're Back From Outer Space": LocData(hookshot=True),
    "Mafia's Jumps": LocData(required_hats=[HatType.ICE]),
    "Vault Codes in the Wind": LocData(required_hats=[HatType.SPRINT]),

    "Security Breach": LocData(hit_requirement=1),
    "10 Seconds until Self-Destruct": LocData(hookshot=True),
    "Community Rift: Rhythm Jump Studio": LocData(required_hats=[HatType.ICE]),

    "Speedrun Well": LocData(hookshot=True, hit_requirement=1),
    "Boss Rush": LocData(umbrella=True, hookshot=True),
    "Community Rift: Twilight Travels": LocData(hookshot=True, required_hats=[HatType.DWELLER]),

    "Bird Sanctuary": LocData(hookshot=True),
    "Wound-Up Windmill": LocData(hookshot=True),
    "The Illness has Speedrun": LocData(hookshot=True),
    "Community Rift: The Mountain Rift": LocData(hookshot=True, required_hats=[HatType.DWELLER]),
    "Camera Tourist": LocData(misc_required=["Camera Badge"]),

    "The Mustache Gauntlet": LocData(hookshot=True, required_hats=[HatType.DWELLER]),

    "Rift Collapse - Deep Sea": LocData(hookshot=True),
}

# Includes main objective requirements
dw_bonus_requirements = {
    # Some One-Hit Hero requirements need badge pins as well because of Hookshot
    "So You're Back From Outer Space": LocData(required_hats=[HatType.SPRINT]),
    "Encore! Encore!": LocData(misc_required=["One-Hit Hero Badge"]),

    "10 Seconds until Self-Destruct": LocData(misc_required=["One-Hit Hero Badge", "Badge Pin"]),

    "Boss Rush": LocData(misc_required=["One-Hit Hero Badge", "Badge Pin"]),
    "Community Rift: Twilight Travels": LocData(required_hats=[HatType.BREWING]),

    "Bird Sanctuary": LocData(misc_required=["One-Hit Hero Badge", "Badge Pin"], required_hats=[HatType.DWELLER]),
    "Wound-Up Windmill": LocData(misc_required=["One-Hit Hero Badge", "Badge Pin"]),
    "The Illness has Speedrun": LocData(required_hats=[HatType.SPRINT]),

    "The Mustache Gauntlet": LocData(required_hats=[HatType.ICE]),

    "Rift Collapse - Deep Sea": LocData(required_hats=[HatType.DWELLER]),
}

dw_stamp_costs = {
    "So You're Back From Outer Space":  2,
    "Collect-a-thon":                   5,
    "She Speedran from Outer Space":    8,
    "Encore! Encore!":                  10,

    "Security Breach":                  4,
    "The Great Big Hootenanny":         7,
    "10 Seconds until Self-Destruct":   15,
    "Killing Two Birds":                25,
    "Snatcher Coins in Nyakuza Metro":  30,

    "Speedrun Well":                10,
    "Boss Rush":                    15,
    "Quality Time with Snatcher":   20,
    "Breaching the Contract":       40,

    "Bird Sanctuary":           15,
    "Wound-Up Windmill":        30,
    "The Illness has Speedrun": 35,

    "The Mustache Gauntlet":    35,
    "No More Bad Guys":         50,
    "Seal the Deal":            70,
}

required_snatcher_coins = {
    "Snatcher Coins in Mafia Town": ["Snatcher Coin - Top of HQ", "Snatcher Coin - Top of Tower",
                                     "Snatcher Coin - Under Ruined Tower"],

    "Snatcher Coins in Battle of the Birds": ["Snatcher Coin - Top of Red House", "Snatcher Coin - Train Rush",
                                              "Snatcher Coin - Picture Perfect"],

    "Snatcher Coins in Subcon Forest": ["Snatcher Coin - Swamp Tree", "Snatcher Coin - Manor Roof",
                                        "Snatcher Coin - Giant Time Piece"],

    "Snatcher Coins in Alpine Skyline": ["Snatcher Coin - Goat Village Top", "Snatcher Coin - Lava Cake",
                                         "Snatcher Coin - Windmill"],

    "Snatcher Coins in Nyakuza Metro": ["Snatcher Coin - Green Clean Tower", "Snatcher Coin - Bluefin Cat Train",
                                        "Snatcher Coin - Pink Paw Fence"],
}


def set_dw_rules(world: World):
    if "Snatcher's Hit List" not in world.get_excluded_dws() \
       or "Camera Tourist" not in world.get_excluded_dws():
        set_enemy_rules(world)

    dw_list: List[str] = []
    if world.options.DWShuffle.value > 0:
        dw_list = world.get_dw_shuffle()
    else:
        for name in death_wishes.keys():
            dw_list.append(name)

    for name in dw_list:
        if name == "Snatcher Coins in Nyakuza Metro" and not world.is_dlc2():
            continue

        dw = world.multiworld.get_region(name, world.player)
        temp_list: List[Location] = []
        main_objective = world.multiworld.get_location(f"{name} - Main Objective", world.player)
        full_clear = world.multiworld.get_location(f"{name} - All Clear", world.player)
        main_stamp = world.multiworld.get_location(f"Main Stamp - {name}", world.player)
        bonus_stamps = world.multiworld.get_location(f"Bonus Stamps - {name}", world.player)
        temp_list.append(main_objective)
        temp_list.append(full_clear)

        if world.options.DWShuffle.value == 0:
            if name in dw_stamp_costs.keys():
                for entrance in dw.entrances:
                    add_rule(entrance, lambda state, n=name: get_total_dw_stamps(state, world) >= dw_stamp_costs[n])

        if world.options.DWEnableBonus.value == 0:
            # place nothing, but let the locations exist still, so we can use them for bonus stamp rules
            full_clear.address = None
            full_clear.place_locked_item(HatInTimeItem("Nothing", ItemClassification.filler, None, world.player))
            full_clear.show_in_spoiler = False

        # No need for rules if excluded - stamps will be auto-granted
        if world.is_dw_excluded(name):
            continue

        # Specific Rules
        modify_dw_rules(world, name)

        main_rule: Callable[[CollectionState], bool]
        for i in range(len(temp_list)):
            loc = temp_list[i]
            data: LocData

            if loc.name == main_objective.name:
                data = dw_requirements.get(name)
            else:
                data = dw_bonus_requirements.get(name)

            if data is None:
                continue

            if data.hookshot:
                add_rule(loc, lambda state: can_use_hookshot(state, world))

            for hat in data.required_hats:
                if hat is not HatType.NONE:
                    add_rule(loc, lambda state, h=hat: can_use_hat(state, world, h))

            for misc in data.misc_required:
                add_rule(loc, lambda state, item=misc: state.has(item, world.player))

            if data.umbrella and world.options.UmbrellaLogic.value > 0:
                add_rule(loc, lambda state: state.has("Umbrella", world.player))

            if data.paintings > 0 and world.options.ShuffleSubconPaintings.value > 0:
                add_rule(loc, lambda state, paintings=data.paintings: has_paintings(state, world, paintings))

            if data.hit_requirement > 0:
                if data.hit_requirement == 1:
                    add_rule(loc, lambda state: can_hit(state, world))
                elif data.hit_requirement == 2:  # Can bypass with Dweller Mask (dweller bells)
                    add_rule(loc, lambda state: can_hit(state, world) or can_use_hat(state, world, HatType.DWELLER))

            main_rule = main_objective.access_rule

            if loc.name == main_objective.name:
                add_rule(main_stamp, loc.access_rule)
            elif loc.name == full_clear.name:
                add_rule(loc, main_rule)
                # Only set bonus stamp rules if we don't auto complete bonuses
                if world.options.DWAutoCompleteBonuses.value == 0 \
                   and not world.is_bonus_excluded(loc.name):
                    add_rule(bonus_stamps, loc.access_rule)

    if world.options.DWShuffle.value > 0:
        dw_shuffle = world.get_dw_shuffle()
        for i in range(len(dw_shuffle)):
            if i == 0:
                continue

            name = dw_shuffle[i]
            prev_dw = world.multiworld.get_region(dw_shuffle[i-1], world.player)
            entrance = world.multiworld.get_entrance(f"{prev_dw.name} -> {name}", world.player)
            add_rule(entrance, lambda state, n=prev_dw.name: state.has(f"1 Stamp - {n}", world.player))
    else:
        for key, reqs in dw_prereqs.items():
            if key == "Snatcher Coins in Nyakuza Metro" and not world.is_dlc2():
                continue

            access_rules: List[Callable[[CollectionState], bool]] = []
            entrances: List[Entrance] = []

            for parent in reqs:
                entrance = world.multiworld.get_entrance(f"{parent} -> {key}", world.player)
                entrances.append(entrance)

                if not world.is_dw_excluded(parent):
                    access_rules.append(lambda state, n=parent: state.has(f"1 Stamp - {n}", world.player))

            for entrance in entrances:
                for rule in access_rules:
                    add_rule(entrance, rule)

    if world.options.EndGoal.value == 3:
        world.multiworld.completion_condition[world.player] = lambda state: state.has("1 Stamp - Seal the Deal",
                                                                                      world.player)


def modify_dw_rules(world: World, name: str):
    difficulty: Difficulty = get_difficulty(world)
    main_objective = world.multiworld.get_location(f"{name} - Main Objective", world.player)
    full_clear = world.multiworld.get_location(f"{name} - All Clear", world.player)

    if name == "The Illness has Speedrun":
        # All stamps with hookshot only in Expert
        if difficulty >= Difficulty.EXPERT:
            set_rule(full_clear, lambda state: True)
        else:
            add_rule(main_objective, lambda state: state.has("Umbrella", world.player))

    elif name == "The Mustache Gauntlet":
        add_rule(main_objective, lambda state: state.has("Umbrella", world.player)
                 or can_use_hat(state, world, HatType.ICE) or can_use_hat(state, world, HatType.BREWING))

    elif name == "Vault Codes in the Wind":
        # Sprint is normally expected here
        if difficulty >= Difficulty.HARD:
            set_rule(main_objective, lambda state: True)

    elif name == "Speedrun Well":
        # All stamps with nothing :)
        if difficulty >= Difficulty.EXPERT:
            set_rule(main_objective, lambda state: True)

    elif name == "Mafia's Jumps":
        if difficulty >= Difficulty.HARD:
            set_rule(main_objective, lambda state: True)
            set_rule(full_clear, lambda state: True)

    elif name == "So You're Back from Outer Space":
        # Without Hookshot
        if difficulty >= Difficulty.HARD:
            set_rule(main_objective, lambda state: True)

    elif name == "Wound-Up Windmill":
        # No badge pin required. Player can switch to One Hit Hero after the checkpoint and do level without it.
        if difficulty >= Difficulty.MODERATE:
            set_rule(full_clear, lambda state: can_use_hookshot(state, world)
                     and state.has("One-Hit Hero Badge", world.player))

    if name in dw_candles:
        set_candle_dw_rules(name, world)


def get_total_dw_stamps(state: CollectionState, world: World) -> int:
    if world.options.DWShuffle.value > 0:
        return 999  # no stamp costs in death wish shuffle

    count: int = 0

    for name in death_wishes:
        if name == "Snatcher Coins in Nyakuza Metro" and not world.is_dlc2():
            continue

        if state.has(f"1 Stamp - {name}", world.player):
            count += 1
        else:
            continue

        if state.has(f"2 Stamps - {name}", world.player):
            count += 2
        elif name not in dw_candles:
            count += 1

    return count


def set_candle_dw_rules(name: str, world: World):
    main_objective = world.multiworld.get_location(f"{name} - Main Objective", world.player)
    full_clear = world.multiworld.get_location(f"{name} - All Clear", world.player)

    if name == "Zero Jumps":
        add_rule(main_objective, lambda state: get_zero_jump_clear_count(state, world) >= 1)
        add_rule(full_clear, lambda state: get_zero_jump_clear_count(state, world) >= 4
                 and state.has("Train Rush (Zero Jumps)", world.player) and can_use_hat(state, world, HatType.ICE))

        # No Ice Hat/painting required in Expert for Toilet Zero Jumps
        # This painting wall can only be skipped via cherry hover.
        if get_difficulty(world) < Difficulty.EXPERT or world.options.NoPaintingSkips.value == 1:
            set_rule(world.multiworld.get_location("Toilet of Doom (Zero Jumps)", world.player),
                     lambda state: can_use_hookshot(state, world) and can_hit(state, world)
                     and has_paintings(state, world, 1, False))
        else:
            set_rule(world.multiworld.get_location("Toilet of Doom (Zero Jumps)", world.player),
                     lambda state: can_use_hookshot(state, world) and can_hit(state, world))

        set_rule(world.multiworld.get_location("Contractual Obligations (Zero Jumps)", world.player),
                 lambda state: has_paintings(state, world, 1, False))

    elif name == "Snatcher's Hit List":
        add_rule(main_objective, lambda state: state.has("Mafia Goon", world.player))
        add_rule(full_clear, lambda state: get_reachable_enemy_count(state, world) >= 12)

    elif name == "Camera Tourist":
        add_rule(main_objective, lambda state: get_reachable_enemy_count(state, world) >= 8)
        add_rule(full_clear, lambda state: can_reach_all_bosses(state, world)
                 and state.has("Triple Enemy Picture", world.player))

    elif "Snatcher Coins" in name:
        for coin in required_snatcher_coins[name]:
            add_rule(main_objective, lambda state: state.has(coin, world.player), "or")
            add_rule(full_clear, lambda state: state.has(coin, world.player))


def get_zero_jump_clear_count(state: CollectionState, world: World) -> int:
    total: int = 0

    for name in act_chapters.keys():
        n = f"{name} (Zero Jumps)"
        if n not in zero_jumps:
            continue

        if get_difficulty(world) < Difficulty.HARD and n in zero_jumps_hard:
            continue

        if get_difficulty(world) < Difficulty.EXPERT and n in zero_jumps_expert:
            continue

        if not state.has(n, world.player):
            continue

        total += 1

    return total


def get_reachable_enemy_count(state: CollectionState, world: World) -> int:
    count: int = 0
    for enemy in hit_list.keys():
        if enemy in bosses:
            continue

        if state.has(enemy, world.player):
            count += 1

    return count


def can_reach_all_bosses(state: CollectionState, world: World) -> bool:
    for boss in bosses:
        if not state.has(boss, world.player):
            return False

    return True


def create_enemy_events(world: World):
    no_tourist = "Camera Tourist" in world.get_excluded_dws() or "Camera Tourist" in world.get_excluded_bonuses()

    for enemy, regions in hit_list.items():
        if no_tourist and enemy in bosses:
            continue

        for area in regions:
            if (area == "Bon Voyage!" or area == "Time Rift - Deep Sea") and not world.is_dlc1():
                continue

            if area == "Time Rift - Tour" and (not world.is_dlc1()
               or world.options.ExcludeTour.value > 0):
                continue

            if area == "Bluefin Tunnel" and not world.is_dlc2():
                continue
            if world.options.DWShuffle.value > 0 and area in death_wishes.keys() \
               and area not in world.get_dw_shuffle():
                continue

            region = world.multiworld.get_region(area, world.player)
            event = HatInTimeLocation(world.player, f"{enemy} - {area}", None, region)
            event.place_locked_item(HatInTimeItem(enemy, ItemClassification.progression, None, world.player))
            region.locations.append(event)
            event.show_in_spoiler = False

    for name in triple_enemy_locations:
        if name == "Time Rift - Tour" and (not world.is_dlc1() or world.options.ExcludeTour.value > 0):
            continue

        if world.options.DWShuffle.value > 0 and name in death_wishes.keys() \
           and name not in world.get_dw_shuffle():
            continue

        region = world.multiworld.get_region(name, world.player)
        event = HatInTimeLocation(world.player, f"Triple Enemy Picture - {name}", None, region)
        event.place_locked_item(HatInTimeItem("Triple Enemy Picture", ItemClassification.progression, None, world.player))
        region.locations.append(event)
        event.show_in_spoiler = False
        if name == "The Mustache Gauntlet":
            add_rule(event, lambda state: can_use_hookshot(state, world) and can_use_hat(state, world, HatType.DWELLER))


def set_enemy_rules(world: World):
    no_tourist = "Camera Tourist" in world.get_excluded_dws() or "Camera Tourist" in world.get_excluded_bonuses()

    for enemy, regions in hit_list.items():
        if no_tourist and enemy in bosses:
            continue

        for area in regions:
            if (area == "Bon Voyage!" or area == "Time Rift - Deep Sea") and not world.is_dlc1():
                continue

            if area == "Time Rift - Tour" and (not world.is_dlc1()
               or world.options.ExcludeTour.value > 0):
                continue

            if area == "Bluefin Tunnel" and not world.is_dlc2():
                continue

            if world.options.DWShuffle.value > 0 and area in death_wishes \
               and area not in world.get_dw_shuffle():
                continue

            event = world.multiworld.get_location(f"{enemy} - {area}", world.player)

            if enemy == "Toxic Flower":
                add_rule(event, lambda state: can_use_hookshot(state, world))

                if area == "The Illness has Spread":
                    add_rule(event, lambda state: not zipline_logic(world) or
                             state.has("Zipline Unlock - The Birdhouse Path", world.player)
                             or state.has("Zipline Unlock - The Lava Cake Path", world.player)
                             or state.has("Zipline Unlock - The Windmill Path", world.player))

            elif enemy == "Director":
                if area == "Dead Bird Studio Basement":
                    add_rule(event, lambda state: can_use_hookshot(state, world))

            elif enemy == "Snatcher" or enemy == "Mustache Girl":
                if area == "Boss Rush":
                    # need to be able to kill toilet and snatcher
                    add_rule(event, lambda state: can_hit(state, world) and can_use_hookshot(state, world))
                    if enemy == "Mustache Girl":
                        add_rule(event, lambda state: can_hit(state, world, True) and can_use_hookshot(state, world))

                elif area == "The Finale" and enemy == "Mustache Girl":
                    add_rule(event, lambda state: can_use_hookshot(state, world)
                             and can_use_hat(state, world, HatType.DWELLER))

            elif enemy == "Shock Squid" or enemy == "Ninja Cat":
                if area == "Time Rift - Deep Sea":
                    add_rule(event, lambda state: can_use_hookshot(state, world))


# Enemies for Snatcher's Hit List/Camera Tourist, and where to find them
hit_list = {
    "Mafia Goon":       ["Mafia Town Area", "Time Rift - Mafia of Cooks", "Time Rift - Tour",
                         "Bon Voyage!", "The Mustache Gauntlet", "Rift Collapse: Mafia of Cooks",
                         "So You're Back From Outer Space"],

    "Sleepy Raccoon":   ["She Came from Outer Space", "Down with the Mafia!", "The Twilight Bell",
                         "She Speedran from Outer Space", "Mafia's Jumps", "The Mustache Gauntlet",
                         "Time Rift - Sleepy Subcon", "Rift Collapse: Sleepy Subcon"],

    "UFO":              ["Picture Perfect", "So You're Back From Outer Space", "Community Rift: Rhythm Jump Studio"],

    "Rat":              ["Down with the Mafia!", "Bluefin Tunnel"],

    "Shock Squid":      ["Bon Voyage!", "Time Rift - Sleepy Subcon", "Time Rift - Deep Sea",
                         "Rift Collapse: Sleepy Subcon"],

    "Shromb Egg":       ["The Birdhouse", "Bird Sanctuary"],

    "Spider":           ["Subcon Forest Area", "The Mustache Gauntlet", "Speedrun Well",
                         "The Lava Cake", "The Windmill"],

    "Crow":             ["Mafia Town Area", "The Birdhouse", "Time Rift - Tour", "Bird Sanctuary",
                         "Time Rift - Alpine Skyline", "Rift Collapse: Alpine Skyline"],

    "Pompous Crow":     ["The Birdhouse", "Time Rift - The Lab", "Bird Sanctuary", "The Mustache Gauntlet"],

    "Fiery Crow":       ["The Finale", "The Lava Cake", "The Mustache Gauntlet"],

    "Express Owl":      ["The Finale", "Time Rift - The Owl Express", "Time Rift - Deep Sea"],

    "Ninja Cat":        ["The Birdhouse", "The Windmill", "Bluefin Tunnel", "The Mustache Gauntlet",
                         "Time Rift - Curly Tail Trail", "Time Rift - Alpine Skyline", "Time Rift - Deep Sea",
                         "Rift Collapse: Alpine Skyline"],

    # Bosses
    "Mafia Boss":       ["Down with the Mafia!", "Encore! Encore!", "Boss Rush"],

    "Conductor":        ["Dead Bird Studio Basement", "Killing Two Birds", "Boss Rush"],
    "Toilet":           ["Toilet of Doom", "Boss Rush"],

    "Snatcher":         ["Your Contract has Expired", "Breaching the Contract", "Boss Rush",
                         "Quality Time with Snatcher"],

    "Toxic Flower":     ["The Illness has Spread", "The Illness has Speedrun"],

    "Mustache Girl":    ["The Finale", "Boss Rush", "No More Bad Guys"],
}

# Camera Tourist has a bonus that requires getting three different types of enemies in one picture.
triple_enemy_locations = [
    "She Came from Outer Space",
    "She Speedran from Outer Space",
    "Mafia's Jumps",
    "The Mustache Gauntlet",
    "The Birdhouse",
    "Bird Sanctuary",
    "Time Rift - Tour",
]

bosses = [
    "Mafia Boss",
    "Conductor",
    "Toilet",
    "Snatcher",
    "Toxic Flower",
    "Mustache Girl",
]
