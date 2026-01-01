import logging
import re

import unicodedata

from random import Random
from typing import NamedTuple

from BaseClasses import ItemClassification
from Utils import async_start

from . import ClientComponent
from ..common import StaticUint
from ..events import (
    subscribe_event,
    OnReceiveSlotDataEvent,
    OnLevelChangeEvent,
    OnGameWatcherTickEvent,
)
from ..type_aliases import ApLocationId, TCSContext
from ...constants import GAME_NAME
from ...items import CHARACTERS_AND_VEHICLES_BY_NAME, EXTRAS_BY_NAME, ExtraData
from ...levels import SHORT_NAME_TO_CHAPTER_AREA
from ...locations import LOCATION_NAME_TO_ID
from ...options import TextColorChoice


try:
    # Copy SA2B's fake item names for replacing traps, if it is available.
    # noinspection PyUnresolvedReferences
    from worlds.sa2b.AestheticData import totally_real_item_names as _sa2b_fake_items_dict

    # noinspection PyBroadException
    try:
        FAKE_TRAP_NAMES = {str(k): tuple(v) for k, v in _sa2b_fake_items_dict.items() if v}
    except Exception:
        FAKE_TRAP_NAMES = {}
    del _sa2b_fake_items_dict
except ImportError:
    FAKE_TRAP_NAMES = {}


SHOP_SLOT_NAME_MAX_BYTES = 64
"""64 bytes, including the null-terminator."""

P_CHARACTER_SHOP_SLOTS = StaticUint(0x880478)
P_EXTRAS_SHOP_SLOTS = StaticUint(0x880480)
SHOP_SLOT_SIZE_BYTES = 0x74


debug_logger = logging.getLogger("TCS Debug")


# If a game does not have any fake item names defined, then one of these could be picked as the fake item name.
VERY_FAKE_TCS_ITEM_NAMES = (
    # Misspellings.
    # "Gank Droid",
    # "DK Droid",
    # "Captain Tadpoles",
    "Darth Mall",
    "Django Fett",
    "Ki-Adi Mandi",
    "Shaaak Ti",
    "Count Douku",
    "R2-Q6",
    "Milenium Falcon",
    # Other.
    "Greedo Shot First",
    # Fake characters.
    "Anakin Skywalker (Jedi Master)",
    "Qui-Gon Jinn (Episode 3)",
)


# todo: TCS doesn't actually have any traps currently, so these won't be used.
# Some of these names could be real names in other Star Wars games, so the client won't use them if the other game
# doesn't have any fake item names defined.
FAKE_TRAP_NAMES[GAME_NAME] = VERY_FAKE_TCS_ITEM_NAMES + (
    # Fake characters.
    "Battle Droid (Sergeant)",
    "Clone (Episode 3, Commander)",
    "Rebel Guard",
    "Rebel Spy",
    "Bothan Spy",
    "Bath Trooper",
    "Luke Skywalker (Yavin)",
    "Zuckuss",
    "TIE Defender",
    "B-Wing",
    "V-Wing",
    "IG-86",
    "Darth Plagueis",
    # "Royal Trooper",
    # Characters that go by a different name in-game.
    "Destroyer Droid",
    "Padme",
    "Boba Fett (Child)",
    "Darth Sidious",
    "Obi-Wan Kenobi (Ghost)",
    "Darth Vader (Ghost)",
)


LEVEL_ID_CANTINA = 325


USABLE_CHARACTERS = set(
    # No ".
    # No $ because it becomes a checkmark/tick like would be seen in a checkbox.
    " !#%&'()*+,-./"
    "0123456789"
    ":;<=>?@"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "[\\]^_`"
    "abcdefghijklmnopqrstuvwxyz"
    # No | because it becomes the R1 Button.
    # No ~ because it is used for color formatting and symbol replacement.
    "{}"
    # These both display as "'" for some reason. Ignoring them for now.
    # "\x91\x92"
    "¡©®²´º¿"
    "ÀÁÃÄÅÆÈÉÍÏÑÓØÙÚÜßàáâãäåæçèéêëìíîïñòóôöøùúüĄąĆćĘęŁłńœŚśźŻż"
    "’“”…™"
    # No Ъ. я seems to become a special - sometimes, I'm not sure how it works.
    "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЫЬЭЮЯабвгдежзийклмнопрстуфхцчшщъыьэюя"
)

_REPLACEMENTS = {
    "Đ": "D",
    "Ħ": "H",
    "Ŀ": "L",
    "Ŋ": "N",
    "Œ": "OE",
    "Ŧ": "T",
    "Ð": "TH",
    "¢": "c",
    "đ": "d",
    "ħ": "h",
    "ı": "i",
    "ĸ": "k",
    "ŀ": "l",
    "ŋŉ": "n",
    "Þðþ": "th",
    "×χ˟": "x",
    # " does not exist for some reason, so replace it with "“".
    '"': "“",
    # $ becomes a checkmark/tick like would be seen in a checkbox.
    # £ becomes a down arrow, like how < and > become left and right arrows.
    # € is not supported.
    # | becomes an R1 Button.
    # ~ is used as a special character for formatting.
    # ¤ becomes a down arrow with a tail, like ↓.
    # ¬ becomes an up arrow with a tail.
    # ¶ becomes an L1 Button.
    # ѐ becomes a "-"
    "$£€|~¤ѐ": "?",
    "‘": "'",
    "‚": ",",
    "Ω": "?",
    "˂": "<",
    "˃": ">",
    "˄": "^",
    "˅": "¤",
    "Ъ": "Ь",
    "♥": "<3",
}
REPLACEMENTS = {c: v for k, v in _REPLACEMENTS.items() for c in k}


# Development helper to check if any explicit replacements would get replaced automatically using `unicodedata`.
# for k, expected_v in REPLACEMENTS.items():
#     normalized_nfkd = unicodedata.normalize("NFKD", k)
#     normalized_no_combining_characters = "".join(c2 for c2 in normalized_nfkd
#                                                  if unicodedata.category(c2) != "Mn")
#     if normalized_no_combining_characters == expected_v:
#         print(f"Do not need to handle: '{k}'")


# ~{color}{text to color}~~
COLOR_FORMATTING = {
    "white": "0",
    "red": "1",  # May be associated with use of the B XBox controller button which is red.
    "green": "2",  # May be associated with use of the A XBox controller button which is green.
    "blue": "3",
    "cyan": "4",
    "pink": "5",
    "yellow": "6",
    "orange": "7",  # Orange is a commonly used color by the game for general text.
    "black": "8",  # Almost unreadable if the text has black outlines.
    # "black2": "9",
    # "cyan2": "a",  # Cyan text and cyan outline?
    # "cyan3": "\\",  # Cyan text and cyan outline?
}


FILLER_COLOR = COLOR_FORMATTING["cyan"]
USEFUL_COLOR = COLOR_FORMATTING["blue"]
PROGRESSION_COLOR = COLOR_FORMATTING["pink"]
PROGRESSION_USEFUL_COLOR = COLOR_FORMATTING["yellow"]
TRAP_COLOR = COLOR_FORMATTING["red"]


# These characters become special symbols.
_SYMBOLS = {
    "R1 Button": "|",  # 124
    "L1 Button": "¶",  # 182
    "Square Button": "û",  # 251
    "X Button": "ý",  # 253
    "Circle Button": "þ",  # 254
    "Triangle Button": "ÿ",  # 255
}


# TODO: This should be part of text_replacer, or a common module shared between text_replacer and shop_names_replacer.
def clean_string(s: str) -> str:
    """Clean up a string to be displayed in-game."""
    # Double [[<special value>]] gets replaced with an icon or similar through _TextDecodeCodeword(). e.g. "[[start]]"
    # becomes a 'start button'.
    s = re.sub(r"\[\[+", "[", s)
    s = re.sub(r"]]+", "]", s)
    if any(unicodedata.category(c) == "Mn" for c in s):
        # Combine combining characters with their base character if possible, e.g. "e"+"́" ("é") -> "é".
        # This can mess with other characters in ways we don't want, so it is only run when a combining character is
        # found, which should be very rare.
        s = unicodedata.normalize("NFKC", s)
    to_convert = list(reversed(s))
    initial_length = len(s)
    characters = []
    while to_convert:
        c = to_convert.pop()
        if c in USABLE_CHARACTERS:
            # The character can be used as-is.
            characters.append(c)
        elif c in REPLACEMENTS:
            # The character has a hardcoded replacement, which could be more than one character.
            characters.extend(REPLACEMENTS[c])
        else:
            # Turn characters with diacritics into the base character plus a combining diacritic character(s).
            normalized_nfkd = unicodedata.normalize("NFKD", c)
            if len(normalized_nfkd) == 1:
                # If the single character did not become more than one character, then there were no combining
                # characters.
                characters.append("?")
            else:
                # Remove all combining characters.
                normalized_no_combining_characters = "".join(c2 for c2 in normalized_nfkd
                                                             if unicodedata.category(c2) != "Mn")
                # Warning: If there is a character that repeatedly produces the same extra character over and over, then
                # this could loop infinitely.
                to_convert.extend(reversed(normalized_no_combining_characters))
                if len(characters) > (2 * initial_length):
                    # Abort to prevent infinite loops.
                    return s
    return "".join(characters)


ShopSlotNumber = int
LocalizationId = int


def _make_character_shop_slot_mapping() -> dict[ShopSlotNumber, ApLocationId]:
    mapping = {}
    for character in CHARACTERS_AND_VEHICLES_BY_NAME.values():
        if character.shop_slot == -1:
            # Not present in the shop.
            continue
        if character.code == -1:
            # Not implemented yet.
            continue
        location_name = character.purchase_location_name
        mapping[character.shop_slot] = LOCATION_NAME_TO_ID[location_name]
    return mapping


def _make_extra_localization_id_mapping() -> dict[ExtraData, ApLocationId]:
    # The score modifiers are not Archipelago items currently, but there are still locations for purchasing them from
    # the shop.
    score_modifiers = {
        EXTRAS_BY_NAME["Score x2"],
        EXTRAS_BY_NAME["Score x4"],
        EXTRAS_BY_NAME["Score x6"],
        EXTRAS_BY_NAME["Score x8"],
        EXTRAS_BY_NAME["Score x10"],
    }

    mapping = {}
    for extra in EXTRAS_BY_NAME.values():
        if extra.name == "Adaptive Difficulty":
            continue
        if extra.code == -1 and extra not in score_modifiers:
            continue
        location_name = extra.purchase_location_name
        mapping[extra] = LOCATION_NAME_TO_ID[location_name]
    return mapping


CHARACTER_SLOTS_MAPPING = _make_character_shop_slot_mapping()
EXTRA_LOCALIZATION_ID_MAPPING = _make_extra_localization_id_mapping()


class ShopSlotData(NamedTuple):
    color_code: str
    name: bytes
    player: int


class ShopNamesReplacer(ClientComponent):
    _scout_locations: set[int]
    _enabled_character_slots: dict[ShopSlotNumber, ApLocationId]
    _enabled_extra_slots: dict[ExtraData, ApLocationId]

    _player_names_as_bytes: dict[int, bytes]
    _cached_ctx_player_names: dict[int, str]
    _cached_character_shop_slot_item_names: dict[ShopSlotNumber, ShopSlotData]
    _cached_character_shop_slot_names: dict[ShopSlotNumber, bytes]
    _cached_extras_shop_slot_item_names: dict[ExtraData, ShopSlotData]
    _cached_extras_shop_slot_names: dict[ExtraData, bytes]

    _got_scouts: bool = False
    _calculated_player_names: bool = False
    _calculated_item_names: bool = False
    _character_shop_slot_names_replaced: bool = False
    _calculated_shop_slot_names: bool = False

    _is_in_cantina: bool = False
    _is_in_shop: bool = False

    prog_useful_color = COLOR_FORMATTING["yellow"]
    progression_color = COLOR_FORMATTING["pink"]
    useful_color = COLOR_FORMATTING["blue"]
    filler_color = COLOR_FORMATTING["cyan"]
    trap_color = COLOR_FORMATTING["red"]

    def __init__(self):
        super().__init__()
        self._scout_locations = set()
        self._enabled_character_slots = {}
        self._enabled_extra_slots = {}
        self._player_names_as_bytes = {-1: b"Unknown"}  # 0 is reserved for Archipelago, so use -1.
        self._cached_ctx_player_names = {}
        self._cached_character_shop_slot_item_names = {}
        self._cached_character_shop_slot_names = {}
        self._cached_extras_shop_slot_item_names = {}
        self._cached_extras_shop_slot_names = {}

    def _set_enabled_locations(self, enabled_locations: set[int]):
        self._enabled_character_slots = {k: v for k, v in CHARACTER_SLOTS_MAPPING.items() if v in enabled_locations}
        self._enabled_extra_slots = {k: v for k, v in EXTRA_LOCALIZATION_ID_MAPPING.items() if v in enabled_locations}

    def update_player_names(self, ctx: TCSContext):
        changed = False
        for player_number, aliased_name in ctx.player_names.items():
            if aliased_name == self._cached_ctx_player_names.get(player_number):
                continue
            self._cached_ctx_player_names[player_number] = aliased_name
            changed = True
            cleaned_name = clean_string(aliased_name)
            self._player_names_as_bytes[player_number] = cleaned_name.encode("utf-8", errors="replace")
        self._calculated_player_names = True
        if changed:
            self._calculated_shop_slot_names = False
            if self._got_scouts:
                self._calculate_shop_slot_names(ctx)

    def _calculate_shop_slot_item_names(self, ctx: TCSContext):
        # Copy for safety.
        locations_info = ctx.locations_info.copy()

        # Create a deterministic Random instance by hashing the NetworkItem instances.
        shop_seed = hash(tuple([locations_info.get(scout_id) for scout_id in sorted(self._scout_locations)]))
        shop_random = Random(shop_seed)

        characters_shop_names = {}
        extras_shop_names = {}
        for slots_dict, names_dict in (
                (self._enabled_character_slots, characters_shop_names),
                (self._enabled_extra_slots, extras_shop_names),
        ):
            for slot_or_extra_data, location_id in slots_dict.items():
                info = locations_info.get(location_id)
                if info is None:
                    debug_logger.error("Missing location info for location ID %i", location_id)
                    names_dict[slot_or_extra_data] = ShopSlotData(FILLER_COLOR, b"Unknown", -1)
                else:
                    classification = ItemClassification(info.flags)
                    # Fake the names for items that are purely traps, and don't have any other classification(s).
                    if classification == ItemClassification.trap and shop_random.random() < 0.5:
                        slot_info = ctx.slot_info.get(info.player)
                        color_code = PROGRESSION_COLOR
                        game = slot_info.game if slot_info else "unknown"
                        if game not in FAKE_TRAP_NAMES:
                            games = list(FAKE_TRAP_NAMES)
                            random_game = shop_random.choice(games)
                            if random_game == GAME_NAME:
                                # The item won't match the game it is for, so avoid any similar sounding item names, and
                                # only use more obviously fake item names.
                                items_to_pick_from = VERY_FAKE_TCS_ITEM_NAMES
                            else:
                                items_to_pick_from = FAKE_TRAP_NAMES[random_game]
                        else:
                            items_to_pick_from = FAKE_TRAP_NAMES[game]

                        fake_item_name = shop_random.choice(items_to_pick_from)
                        cleaned_item_name = clean_string(fake_item_name)
                    else:
                        # Get the name of the item.
                        item_name = ctx.item_names.lookup_in_slot(info.item, info.player)
                        cleaned_item_name = clean_string(item_name)
                        # Determine the color code to use when displaying this item.
                        color_code = self.classification_to_colour_code(classification)
                    names_dict[slot_or_extra_data] = ShopSlotData(
                        color_code, cleaned_item_name.encode("utf-8", errors="replace"), info.player)
        self._cached_character_shop_slot_item_names = characters_shop_names
        self._cached_extras_shop_slot_item_names = extras_shop_names
        self._calculated_item_names = True

    def _calculate_shop_slot_names(self, ctx: TCSContext):
        """Calculate the custom shop slot names by combining the item name and player name."""
        if not self._calculated_item_names:
            self._calculate_shop_slot_item_names(ctx)
        if not self._calculated_player_names:
            debug_logger.error("Player names are not calculated in _calculate_shop_slot_names")
            return

        player_name_parentheses_count = len(b"()")
        spaces_between_item_and_player = len(b" ")
        characters_for_item_color = len("~0~~".encode("utf-8"))  # example colour code.
        null_terminator_count = len(b"\x00")
        max_custom_bytes = (
                SHOP_SLOT_NAME_MAX_BYTES
                - player_name_parentheses_count
                - spaces_between_item_and_player
                - characters_for_item_color
                - null_terminator_count
        )
        for output_dict, input_dict in (
                (self._cached_character_shop_slot_names, self._cached_character_shop_slot_item_names),
                (self._cached_extras_shop_slot_names, self._cached_extras_shop_slot_item_names),
        ):
            for slot_or_localization_id, data in input_dict.items():
                player_name = self._player_names_as_bytes.get(data.player)
                if player_name is None:
                    player_name = b"Unknown player " + f"{data.player}".encode()
                player_name_length = len(player_name)

                item_name = data.name
                item_name_length = len(item_name)

                if (player_name_length + item_name_length) > max_custom_bytes:
                    character_count_to_drop = (player_name_length + item_name_length) - max_custom_bytes
                    dropped_count = 0
                    # todo: This can be more efficient because we know the minimum bytes per character is 1, so more
                    #  can be chopped off at the start, which would avoid performance issues with very long item
                    #  names.
                    # Convert back to strings so there isn't a need to constantly decode and then encode again just to
                    # remove a character from the end.
                    item_name_str = item_name.decode("utf-8")
                    player_name_str = player_name.decode("utf-8")
                    while dropped_count < character_count_to_drop:
                        if item_name_length > player_name_length:
                            assert item_name_length > 0
                            # Chop the last character off the item name.
                            item_name_str = item_name_str[:-1]
                            item_name = item_name_str.encode("utf-8")
                            dropped_count += item_name_length - len(item_name)
                            item_name_length = len(item_name)
                        else:
                            assert player_name_length > 0
                            # Chop the last character off the player name.
                            player_name_str = player_name_str[:-1]
                            player_name = player_name_str.encode("utf-8")
                            dropped_count += player_name_length - len(player_name)
                            player_name_length = len(player_name)
                full_shop_slot_name = (
                        f"~{data.color_code}".encode("utf-8")
                        + item_name
                        + b"~~ ("
                        + player_name
                        + b")\x00"
                )
                output_dict[slot_or_localization_id] = full_shop_slot_name
        self._calculated_shop_slot_names = True

    def update_character_shop_slot_names(self, ctx: TCSContext):
        """Update the Shop with the already calculated custom shop slot names."""
        if not self._calculated_shop_slot_names:
            debug_logger.warning("Tried to update shop slot names without ")
            raise RuntimeError("...")

        shop_slots_start = P_CHARACTER_SHOP_SLOTS.get(ctx)
        if shop_slots_start == 0:
            # Null pointer...
            return
        for slot_index, new_name in self._cached_character_shop_slot_names.items():
            ctx.write_bytes(shop_slots_start + slot_index * SHOP_SLOT_SIZE_BYTES, new_name, len(new_name), raw=True)
        self._character_shop_slot_names_replaced = True

    @subscribe_event
    def init_from_slot_data(self, event: OnReceiveSlotDataEvent):
        self._set_enabled_locations(event.context.server_locations)
        self._scout_locations = set().union(self._enabled_character_slots.values(), self._enabled_extra_slots.values())
        if not self._scout_locations:
            self._got_scouts = True
            self._calculated_shop_slot_names = True
            self._character_shop_slot_names_replaced = True
        else:
            self._got_scouts = False
            self._calculated_shop_slot_names = False
            self._character_shop_slot_names_replaced = False
            # Fire and forget.
            async_start(event.context.send_msgs([{"cmd": "LocationScouts", "locations": list(self._scout_locations)}]))
        self.update_player_names(event.context)
        if "item_colors" in event.slot_data:
            item_colors = event.slot_data["item_colors"]
            self.prog_useful_color, self.progression_color, self.useful_color, self.filler_color, self.trap_color = (
                COLOR_FORMATTING[v.current_key] for v in TextColorChoice.colors_from_slot_data(item_colors)
            )

    def classification_to_colour_code(self, classification: ItemClassification) -> str:
        if (ItemClassification.progression | ItemClassification.useful) in classification:
            return self.prog_useful_color
        elif ItemClassification.progression in classification:
            return self.progression_color
        # Whether a Useful + Trap item should show up as Useful or Trap color is questionable.
        elif ItemClassification.trap in classification:
            return self.trap_color
        elif ItemClassification.useful in classification:
            return self.useful_color
        else:
            return self.filler_color

    def _are_scouts_received(self, ctx: TCSContext) -> bool:
        scouted_location_ids = set(ctx.locations_info.keys())
        return (
                set(self._enabled_character_slots.values()) <= scouted_location_ids
                and set(self._enabled_extra_slots.values()) <= scouted_location_ids
        )

    def _replace_extras_names_with_shop_checks(self, ctx: TCSContext):
        # Replace Extras names with what they unlock.
        text_replacer = ctx.text_replacer
        power_brick_checker = ctx.true_jedi_and_power_brick_and_minikit_checker
        unfound_power_bricks_by_area_id = power_brick_checker.remaining_power_bricks_by_area_id
        for extra_data, data in self._cached_extras_shop_slot_names.items():
            shortname = extra_data.level_shortname
            if shortname is not None:
                chapter_area = SHORT_NAME_TO_CHAPTER_AREA[shortname]
                area_id = chapter_area.area_id
                if area_id in unfound_power_bricks_by_area_id:
                    # The shop slot for this Extra is not unlocked yet, so skip replacing the name of the Extra in the
                    # shop. The shop says "Locked" for locked Extra purchases, but other parts of the game also display
                    # the names of the Extras, so only changing the names of the unlocked slots means that information
                    # about the locked slots cannot be leaked.
                    continue
            text_replacer.write_raw_custom_string(extra_data.localization_id, data)

    def _restore_extras_names(self, ctx: TCSContext):
        # Restore Extras names to their defaults.
        text_replacer = ctx.text_replacer
        for extra_data in self._cached_extras_shop_slot_names.keys():
            text_replacer.write_raw_vanilla_string(extra_data.localization_id)

    @subscribe_event
    def on_tick(self, event: OnGameWatcherTickEvent):
        if not self._got_scouts:
            if event.tick_count % 10 != 0:
                # The scouts could take a bit to be received from the server, so there's no need to check super
                # frequently.
                return
            if self._are_scouts_received(event.context):
                self._got_scouts = True
                self._calculate_shop_slot_names(event.context)

        if self._got_scouts and self._is_in_cantina and self._calculated_shop_slot_names:
            if self._cached_extras_shop_slot_names:
                # Extras shop slots always show the name of the Extra itself, so the names of the Extras themselves have
                # to be changed.
                is_in_shop = event.context.is_in_shop()
                if is_in_shop != self._is_in_shop:
                    text_replacer = event.context.text_replacer
                    if is_in_shop:
                        self._replace_extras_names_with_shop_checks(event.context)
                    else:
                        self._restore_extras_names(event.context)
                    self._is_in_shop = is_in_shop

            # Character shop slots do not need to update with a high frequency.
            if event.tick_count % 10 == 0:
                if not self._character_shop_slot_names_replaced:
                    # The names have not been replaced, so replace them.
                    self.update_character_shop_slot_names(event.context)
                elif event.tick_count % 20 == 0:
                    # Check that the shop slots still have their names replaced.
                    # After loading into the Cantina, the game seems to reset the Shop a second time after loading it,
                    # which can reset the replaced names.
                    if self._cached_character_shop_slot_names:
                        character_shop_start = P_CHARACTER_SHOP_SLOTS.get(event.context)
                        if character_shop_start != 0:
                            index, expected_bytes = next(iter(self._cached_character_shop_slot_names.items()))
                            read_bytes = event.context.read_bytes(character_shop_start + index * SHOP_SLOT_SIZE_BYTES,
                                                                  len(expected_bytes),
                                                                  raw=True)
                            if read_bytes != expected_bytes:
                                # debug_logger.info("Character Shop names were overwritten by the game...")
                                self._character_shop_slot_names_replaced = False

    @subscribe_event
    def on_level_change(self, event: OnLevelChangeEvent):
        self._is_in_cantina = event.new_level_id == LEVEL_ID_CANTINA
        self._is_in_shop = False
        self._character_shop_slot_names_replaced = False

    def reset_persisted_client_data(self, ctx: TCSContext):
        # Restore Extras names to their defaults.
        # This is just some extra cleanup in-case the user disconnects
        text_replacer = ctx.text_replacer
        for extra_data in self._cached_extras_shop_slot_names.keys():
            text_replacer.write_raw_vanilla_string(extra_data.localization_id)

