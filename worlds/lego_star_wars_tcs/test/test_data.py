from unittest import TestCase
from typing import Callable, Iterable

from ..data.logic import EPISODES
from ..data.logic.types import Chapter


def chapters_iter() -> Iterable[Chapter]:
    for episode in EPISODES:
        yield from episode


def chapters_test(test_func: Callable[[TestCase, Chapter], None]):
    def test_chapters(self: TestCase):
        for chapter in chapters_iter():
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

    @chapters_test
    def test_chapter_completion_has_unique_status_level(self, chapter: Chapter):
        """Test that the Chapter Completion region is in a level ending with _status, and that no other regions are in
        this level."""
        self.assertIn("Chapter Completion", chapter.region_to_level)
        status_level = chapter.region_to_level["Chapter Completion"]
        self.assertTrue(status_level.endswith("_status"))
        for region, level in chapter.region_to_level.items():
            if region != "Chapter Completion":
                self.assertNotEqual(level, status_level)

    def test_levels_unique_per_chapter(self):
        """Test that levels are unique to a single chapter."""
        seen_levels = set()
        for chapter in chapters_iter():
            chapter_levels = set(chapter.region_to_level.values())
            self.assertTrue(seen_levels.isdisjoint(chapter_levels))
            seen_levels.update(chapter_levels)

    def test_episode_chapter_numbers(self):
        """Test that chapter episode/chapter numbers are unique and within the expected bounds."""
        seen_by_episode = {episode_number: set() for episode_number in range(1, 7)}
        allowed_chapter_numbers = range(1, 7)
        for chapter in chapters_iter():
            self.assertIn(chapter.episode_number, seen_by_episode)
            self.assertIn(chapter.chapter_number, allowed_chapter_numbers)

            seen_chapters = seen_by_episode[chapter.episode_number]
            self.assertNotIn(chapter.chapter_number, seen_chapters)

            seen_chapters.add(chapter.chapter_number)

    @chapters_test
    def test_regions_have_exits_or_locations(self, chapter: Chapter):
        """Test that each region contains at least one exit, or at least one location."""
        unused_region_names = {name for name, exits in chapter.regions.items() if not exits}
        unused_region_names.discard("Chapter Completion")
        if not unused_region_names:
            return
        for location_data in chapter.all_in_level_location_data:
            if location_data.region in unused_region_names:
                unused_region_names.remove(location_data.region)
                if not unused_region_names:
                    return
        self.fail(f"There are unused regions: {sorted(unused_region_names)}")



