from unittest import TestCase
from typing import Callable

from ..data.logic import EPISODES
from ..data.logic.types import Chapter


def chapters_test(test_func: Callable[[TestCase, Chapter], None]):
    def test_chapters(self: TestCase):
        for episode in EPISODES:
            for chapter in episode:
                with self.subTest(chapter=(chapter.episode_number, chapter.chapter_number), chapter_name=chapter.name):
                    test_func(self, chapter)
    return test_chapters


class TestEpisodes(TestCase):
    @chapters_test
    def test_minikit_count(self, chapter: Chapter):
        """Test that each chapter has exactly 10 minikits defined."""
        self.assertEqual(len(chapter.minikits), 10)

    @chapters_test
    def test_unique_minikit_pickup_names_per_level(self, chapter: Chapter):
        """Test that within each level in a chapter, the minikit pickup names are unique."""
        for level, minikits in chapter.level_minikits.items():
            with self.subTest(level=level):
                found_pickup_names = set()
                for minikit_data in minikits.values():
                    for pickup_name in minikit_data.pickup_names:
                        self.assertNotIn(pickup_name, found_pickup_names)
                        found_pickup_names.add(pickup_name)

    @chapters_test
    def test_location_regions_exist(self, chapter: Chapter):
        for location_data in chapter.all_in_level_location_data:
            self.assertIn(location_data.region, chapter.regions)
