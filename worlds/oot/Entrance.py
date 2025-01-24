from typing import Any, Literal

from BaseClasses import Entrance, Region, MultiWorld

from worlds.generic.Rules import set_rule, CollectionRule


class OOTProxyEntrance:
    """Used to simplify connecting regions by updating child and adult entrances simultaneously"""
    def __init__(self, player: int, multiworld: MultiWorld, name='', parent=None):
        self.child_entrance = OOTEntrance(player, multiworld, f"({name}), as Child", parent.child_region, proxy=self)
        self.adult_entrance = OOTEntrance(player, multiworld, f"({name}), as Adult", parent.adult_region, proxy=self)
        self.child_entrance.age = "child"
        self.adult_entrance.age = "adult"
        self.player = player
        self.name = name
        self.multiworld = multiworld
        self.access_rules = []
        self.reverse = None
        self.replaces = None
        self.assumed = None
        self.type = None
        self.shuffled = False
        self.data = None
        self.primary = False
        self.always = False
        self.never = False
        self.connected_region = None
        self.parent_region = parent
        # Nasty, but how core does it.
        proxy_cache = multiworld.worlds[player].entrance_proxy_cache
        assert name not in proxy_cache
        proxy_cache[name] = self

    @property
    def vanilla_connected_region(self):
        return self._vanilla_connected_region

    @vanilla_connected_region.setter
    def vanilla_connected_region(self, region: str):
        self._vanilla_connected_region = region
        self.child_entrance.vanilla_connected_region = region
        self.adult_entrance.vanilla_connected_region = region

    @property
    def rule_string(self):
        return self._rule_string

    @rule_string.setter
    def rule_string(self, rule: str):
        self._rule_string = rule
        self.child_entrance.rule_string = rule
        self.adult_entrance.rule_string = rule

    def set_rule(self, rule: CollectionRule):
        world = self.multiworld.worlds[self.player]
        if world.starting_age == "child":
            set_rule(self.child_entrance, rule)
            set_rule(self.adult_entrance, rule)
        else:
            set_rule(self.child_entrance, rule)
            set_rule(self.adult_entrance, rule)

    def bind_two_way(self, other_entrance):
        self.reverse = other_entrance
        other_entrance.reverse = self

    def connect(self, region: Region, addresses: Any = None, target: Any = None) -> None:
        self.child_entrance.connect(region.multiworld.get_region(region.name + " as Child", region.player))
        self.adult_entrance.connect(region.multiworld.get_region(region.name + " as Adult", region.player))
        # self.child_entrance.target = target.child_region
        # self.adult_entrance.target = target.adult_region
        self.connected_region = region
        self.target = target
        # region.child_region.entrances.append(self.child_entrance)
        # region.adult_region.entrances.append(self.adult_entrance)

    def disconnect(self) -> Region | None:
        self.child_entrance.disconnect()
        self.adult_entrance.disconnect()
        # self.connected_region.child_region.entrances.remove(self.child_entrance)
        # self.connected_region.adult_region.entrances.remove(self.adult_entrance)
        previously_connected = self.connected_region
        self.connected_region = None
        return previously_connected

    def get_new_target(self, pool_type) -> "OOTProxyEntrance":
        root = self.multiworld.get_region('Root Exits', self.player)
        target_entrance = OOTProxyEntrance(self.player, self.multiworld, f'Root -> ({self.name}) ({pool_type})', root)
        target_entrance.connect(self.connected_region)
        target_entrance.replaces = self
        root.exits.append(target_entrance)
        return target_entrance

    def assume_reachable(self, pool_type) -> "OOTProxyEntrance | None":
        if self.assumed is None:
            self.assumed = self.get_new_target(pool_type)
            self.disconnect()
        return self.assumed

    def __repr__(self):
        multiworld = self.parent_region.multiworld if self.parent_region else None
        return multiworld.get_name_string_for_object(self) if multiworld else f'{self.name} (Player {self.player})'


class OOTEntrance(Entrance): 
    game: str = 'Ocarina of Time'

    age: Literal["adult", "child", None] = None

    def __init__(self, player, multiworld, name='', parent=None, proxy=None):
        super(OOTEntrance, self).__init__(player, name, parent)
        self.multiworld = multiworld
        self.access_rules = []
        self.proxy: OOTProxyEntrance | None = proxy
        # self.reverse = None
        # self.replaces = None
        # self.assumed = None
        # self.type = None
        # self.shuffled = False
        # self.data = None
        # self.primary = False
        # self.always = False
        # self.never = False

    # def bind_two_way(self, other_entrance):
    #     self.reverse = other_entrance
    #     other_entrance.reverse = self

    def disconnect(self) -> Region | None:
        self.connected_region.entrances.remove(self)
        previously_connected = self.connected_region
        self.connected_region = None
        return previously_connected

    # def get_new_target(self, pool_type) -> "OOTEntrance":
    #     root = self.multiworld.get_region('Root Exits', self.player)
    #     target_entrance = OOTEntrance(self.player, self.multiworld, f'Root -> ({self.name}) ({pool_type})', root)
    #     target_entrance.connect(self.connected_region)
    #     target_entrance.replaces = self
    #     root.exits.append(target_entrance)
    #     return target_entrance

    # def assume_reachable(self, pool_type) -> "OOTEntrance | None":
    #     if self.assumed is None:
    #         self.assumed = self.get_new_target(pool_type)
    #         self.disconnect()
    #     return self.assumed
