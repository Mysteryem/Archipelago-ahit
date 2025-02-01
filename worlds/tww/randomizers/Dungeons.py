from typing import TYPE_CHECKING, Any, Optional

from BaseClasses import CollectionState, Item, Location, MultiWorld
from Fill import fill_restrictive, remaining_fill, FillError

from ..Items import item_factory

if TYPE_CHECKING:
    from .. import TWWWorld


class Dungeon:
    """
    This class represents a dungeon in The Wind Waker, including its dungeon items.

    :param name: The name of the dungeon.
    :param big_key: The big key item for the dungeon.
    :param small_keys: A list of small key items for the dungeon.
    :param dungeon_items: A list of other items specific to the dungeon.
    :param player: The ID of the player associated with the dungeon.
    """

    def __init__(
        self,
        name: str,
        big_key: Optional[Item],
        small_keys: list[Item],
        dungeon_items: list[Item],
        player: int,
    ):
        self.name = name
        self.big_key = big_key
        self.small_keys = small_keys
        self.dungeon_items = dungeon_items
        self.player = player

    @property
    def keys(self) -> list[Item]:
        """
        Retrieve all the keys for the dungeon.

        :return: A list of Small Keys and the Big Key (if it exists).
        """
        return self.small_keys + ([self.big_key] if self.big_key else [])

    @property
    def all_items(self) -> list[Item]:
        """
        Retrieve all items associated with the dungeon.

        :return: A list of all items associated with the dungeon.
        """
        return self.dungeon_items + self.keys

    def __eq__(self, other: Any) -> bool:
        """
        Check equality between this dungeon and another object.

        :param other: The object to compare.
        :return: `True` if the other object is a Dungeon with the same name and player, `False` otherwise.
        """
        if isinstance(other, Dungeon):
            return self.name == other.name and self.player == other.player
        return False

    def __repr__(self) -> str:
        """
        Provide a string representation of the dungeon.

        :return: A string representing the dungeon.
        """
        return self.__str__()

    def __str__(self) -> str:
        """
        Convert the dungeon to a human-readable string.

        :return: A string in the format "<name> (Player <player>)".
        """
        return f"{self.name} (Player {self.player})"


def create_dungeons(world: "TWWWorld") -> None:
    """
    Create and assign dungeons to the given world based on game options.

    :param world: The Wind Waker game world.
    """
    player = world.player
    options = world.options

    def make_dungeon(name: str, big_key: Optional[Item], small_keys: list[Item], dungeon_items: list[Item]) -> Dungeon:
        dungeon = Dungeon(name, big_key, small_keys, dungeon_items, player)
        for item in dungeon.all_items:
            item.dungeon = dungeon
        return dungeon

    if options.progression_dungeons:
        if not options.required_bosses or "Dragon Roost Cavern" in world.boss_reqs.required_dungeons:
            world.dungeons["Dragon Roost Cavern"] = make_dungeon(
                "Dragon Roost Cavern",
                item_factory("DRC Big Key", world),
                item_factory(["DRC Small Key"] * 4, world),
                item_factory(["DRC Dungeon Map", "DRC Compass"], world),
            )

        if not options.required_bosses or "Forbidden Woods" in world.boss_reqs.required_dungeons:
            world.dungeons["Forbidden Woods"] = make_dungeon(
                "Forbidden Woods",
                item_factory("FW Big Key", world),
                item_factory(["FW Small Key"] * 1, world),
                item_factory(["FW Dungeon Map", "FW Compass"], world),
            )

        if not options.required_bosses or "Tower of the Gods" in world.boss_reqs.required_dungeons:
            world.dungeons["Tower of the Gods"] = make_dungeon(
                "Tower of the Gods",
                item_factory("TotG Big Key", world),
                item_factory(["TotG Small Key"] * 2, world),
                item_factory(["TotG Dungeon Map", "TotG Compass"], world),
            )

        if not options.required_bosses or "Forsaken Fortress" in world.boss_reqs.required_dungeons:
            world.dungeons["Forsaken Fortress"] = make_dungeon(
                "Forsaken Fortress",
                None,
                [],
                item_factory(["FF Dungeon Map", "FF Compass"], world),
            )

        if not options.required_bosses or "Earth Temple" in world.boss_reqs.required_dungeons:
            world.dungeons["Earth Temple"] = make_dungeon(
                "Earth Temple",
                item_factory("ET Big Key", world),
                item_factory(["ET Small Key"] * 3, world),
                item_factory(["ET Dungeon Map", "ET Compass"], world),
            )

        if not options.required_bosses or "Wind Temple" in world.boss_reqs.required_dungeons:
            world.dungeons["Wind Temple"] = make_dungeon(
                "Wind Temple",
                item_factory("WT Big Key", world),
                item_factory(["WT Small Key"] * 2, world),
                item_factory(["WT Dungeon Map", "WT Compass"], world),
            )


def get_dungeon_item_pool(multiworld: MultiWorld) -> list[Item]:
    """
    Retrieve the item pool for all The Wind Waker dungeons in the multiworld.

    :param multiworld: The MultiWorld instance.
    :return: List of dungeon items across all The Wind Waker dungeons.
    """
    return [
        item for world in multiworld.get_game_worlds("The Wind Waker") for item in get_dungeon_item_pool_player(world)
    ]


def get_dungeon_item_pool_player(world: "TWWWorld") -> list[Item]:
    """
    Retrieve the item pool for all dungeons specific to a player.

    :param world: The Wind Waker game world.
    :return: List of items in the player's dungeons.
    """
    return [item for dungeon in world.dungeons.values() for item in dungeon.all_items]


def get_unfilled_dungeon_locations(multiworld: MultiWorld) -> list[Location]:
    """
    Retrieve all unfilled The Wind Waker dungeon locations in the multiworld.

    :param multiworld: The MultiWorld instance.
    :return: List of unfilled The Wind Waker dungeon locations.
    """
    return [
        location
        for world in multiworld.get_game_worlds("The Wind Waker")
        for location in multiworld.get_locations(world.player)
        if location.dungeon and not location.item
    ]


def modify_dungeon_location_rules(locations: list[Location], dungeon_specific: set[tuple[int, str]]) -> None:
    """
    Modify the rules for The Wind Waker dungeon locations based on specific player-requested constraints.

    :param locations: List of dungeon locations to modify.
    :param dungeon_specific: Set of dungeon-specific item constraints.
    """
    for location in locations:
        if dungeon_specific:
            dungeon = location.dungeon
            orig_rule = location.item_rule
            location.item_rule = lambda item, dungeon=dungeon, orig_rule=orig_rule: (
                not (item.player, item.name) in dungeon_specific or item.dungeon is dungeon
            ) and orig_rule(item)


def fill_dungeons_restrictive(multiworld: MultiWorld) -> None:
    """
    Correctly fill The Wind Waker dungeons in the multiworld.

    :param multiworld: The MultiWorld instance.
    """
    dungeon_specific: set[tuple[int, str]] = set()
    subworld: "TWWWorld"
    in_dungeon_items_per_player: dict[int, list[Item]] = {}
    for subworld in multiworld.get_game_worlds("The Wind Waker"):
        player = subworld.player
        if player not in multiworld.groups:
            dungeon_specific |= {(player, item_name) for item_name in subworld.dungeon_specific_item_names}

            dungeon_local_item_names = subworld.dungeon_local_item_names
            dungeon_items = [item for item in get_dungeon_item_pool_player(subworld) if item.name in dungeon_local_item_names]
            if dungeon_items:
                in_dungeon_items_per_player[player] = dungeon_items

    if in_dungeon_items_per_player:
        dungeon_locations = [location for location in get_unfilled_dungeon_locations(multiworld)]
        modify_dungeon_location_rules(dungeon_locations, dungeon_specific)

        all_state_base = CollectionState(multiworld)
        for item in multiworld.itempool:
            multiworld.worlds[item.player].collect(all_state_base, item)
        for player in multiworld.player_ids:
            player_pre_fill_items = multiworld.worlds[player].get_pre_fill_items()
            if player not in in_dungeon_items_per_player:
                # Collect pre_fill items belonging to other players.
                for item in player_pre_fill_items:
                    if item.advancement:
                        all_state_base.collect(item, True)
            else:
                dungeon_items = in_dungeon_items_per_player[player]
                # Remove dungeon items, so they do not get collected twice.
                player_pre_fill_items = player_pre_fill_items.copy()
                for item in dungeon_items:
                    player_pre_fill_items.remove(item)
                # Collect whatever pre_fill items are left that are not dungeon items.
                for item in player_pre_fill_items:
                    if item.advancement:
                        all_state_base.collect(item, True)


        all_state_base.sweep_for_advancements()
        # Get the remaining filled advancement locations for faster sweeps.
        remaining_filled_advancements = [loc for loc in multiworld.get_locations()
                                         if loc.advancement and loc not in all_state_base.advancements]

        # Remove the completion condition so that minimal-accessibility words place keys correctly.
        for player in in_dungeon_items_per_player.keys():
            if all_state_base.has("Victory", player):
                all_state_base.remove(multiworld.worlds[player].create_item("Victory"))

        # Items sorted last are placed first. Place the most difficult to place items first.
        sort_order = {"Big Key": 3, "Small Key": 2}

        def sort_item_for_placement(item: Item):
            value = sort_order.get(item.type, 1)
            if (item.player, item.name) in dungeon_specific:
                value += 5
            return value

        # We can skip a sweep on the last player.
        last_player = next(reversed(in_dungeon_items_per_player.keys()))

        for player, items_to_place in in_dungeon_items_per_player.items():
            placing_all_state = all_state_base.copy()
            # Collect the pre_fill items belonging to other players that we're going to place after this player.
            for other_player, other_player_items in in_dungeon_items_per_player.items():
                if other_player != player:
                    for item in other_player_items:
                        if item.advancement:
                            placing_all_state.collect(item, True)

            # Get the unfilled dungeon locations for this player.
            dungeon_locations = [loc for loc in multiworld.get_locations(player) if loc.dungeon and loc.item is None]

            # Check that excessive item plando (or rarely pre_fill from other worlds) has not filled too many dungeon
            # locations.
            if len(items_to_place) > len(dungeon_locations):
                raise FillError(f"{len(items_to_place)} in-dungeon items to place for"
                                f" {multiworld.get_player_name(player)}, but only {len(dungeon_locations)} empty"
                                f"dungeon locations.")

            multiworld.random.shuffle(dungeon_locations)

            # Dungeon-locked items have to be placed first so as not to run out of space for dungeon-locked items.
            # Subsort in the order Big Key, Small Key, Other before placing dungeon items.
            items_to_place.sort(key=sort_item_for_placement)

            if any(item.advancement for item in items_to_place):
                # fill_restrictive removes the items placed from `items_to_place`, so the next player's
                # `placing_all_state` will find it empty when it goes to collect the items.
                fill_restrictive(multiworld, placing_all_state, dungeon_locations.copy(), items_to_place,
                                 single_player_placement=True,
                                 name=f"TWW Dungeon Items for {multiworld.get_player_name(player)}")
            else:
                # Faster fill if we're not placing any progression items.
                # remaining_fill removes the items placed from `items_to_place`, so the next player's
                # `placing_all_state` will find it empty when it goes to collect the items.
                remaining_fill(multiworld, dungeon_locations.copy(), items_to_place,
                               check_location_can_fill=not all(item.excludable for item in items_to_place),
                               name=f"TWW Dungeon Items for {multiworld.get_player_name(player)}")

            if player != last_player:
                # Add the advancement locations we just filled
                placed_advancements = [loc for loc in dungeon_locations if loc.advancement]
                if placed_advancements:
                    remaining_filled_advancements.extend(placed_advancements)
                    # Sweep to pick up placed keys into the all state, and any items that were locked behind them.
                    all_state_base.sweep_for_advancements(remaining_filled_advancements)

