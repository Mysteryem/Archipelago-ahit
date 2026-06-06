from unittest import TestCase

from ..data.characters import UnlockMethod
from ..data.items import GenericCharacterData
from ..data.shop import CHARACTER_SHOP_SLOTS
from ..items import ITEM_DATA, CHARACTERS_AND_VEHICLES_BY_NAME


class TestItems(TestCase):
    def test_item_code_uniqueness(self):
        found_codes = set()
        for item in ITEM_DATA:
            if item.code == -1:
                continue
            self.assertGreater(item.code, 0)
            self.assertNotIn(item.code, found_codes)
            found_codes.add(item.code)

    def test_item_name_uniqueness(self):
        found_names = set()
        for item in ITEM_DATA:
            self.assertNotIn(item.name, found_names)
            found_names.add(item.name)

    def test_character_number_uniqueness(self):
        found_characters = set()
        for item in ITEM_DATA:
            if not isinstance(item, GenericCharacterData):
                continue
            self.assertNotIn(item.character, found_characters)
            if item.character.is_event():
                self.assertIsNone(item.code)
                self.assertTrue(item.is_sendable)
            else:
                self.assertIsNotNone(item.code)
                self.assertFalse(item.is_sendable)
            found_characters.add(item.character)

    def test_shop_slots_count(self):
        """Test that there are the correct number of Character shop slots."""
        # The slots are from 0 to 88.
        self.assertEqual(len(CHARACTER_SHOP_SLOTS), 89)

    def test_shop_slots_characters(self):
        for character in CHARACTER_SHOP_SLOTS:
            self.assertIn(character.readable_name, CHARACTERS_AND_VEHICLES_BY_NAME)

    def test_shop_slots_unlocks(self):
        possible_unlocks = {
            UnlockMethod.AREA_COMPLETE,
            UnlockMethod.INDY_TRAILER,
            UnlockMethod.ALL_EPISODES_COMPLETE,
        }
        for character in CHARACTER_SHOP_SLOTS:
            self.assertIn(character.unlock_method, possible_unlocks)
            if character.unlock_method is UnlockMethod.AREA_COMPLETE:
                areas = character.areas
                self.assertIsNotNone(areas)
                self.assertTrue(len(areas) == 1)
                self.assertTrue(next(iter(areas)).is_chapter())

