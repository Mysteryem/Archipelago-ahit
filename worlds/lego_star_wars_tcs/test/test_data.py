import json
from unittest import TestCase
from typing import Callable, Iterable

from rule_builder.rules import Rule, NestedRule, WrapperRule, And
from test.general import setup_multiworld
from worlds import AutoWorldRegister

from ..data.levels import Level
from ..data.logic import EPISODES
from ..data.logic.extraction import un_nest_logic_options
from ..data.logic.option_filters import LogicOptions
from ..data.logic.types import Chapter

from ..constants import GAME_NAME
from ..items import CHARACTERS_AND_VEHICLES_BY_NAME
from ..options import LogicDifficulty


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
    def assertCharacterExists(self, character: str):
        self.assertIn(character, CHARACTERS_AND_VEHICLES_BY_NAME, f"Character '{character}' not found.")

    def assertCharacterIsSendable(self, character: str):
        self.assertTrue(CHARACTERS_AND_VEHICLES_BY_NAME[character].is_sendable,
                        f"Character '{character}' is not sendable")

    def assertCharacterUsableInChapterRequirements(self, character):
        self.assertCharacterExists(character)
        self.assertCharacterIsSendable(character)

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
        self.assertTrue(status_level.name.endswith("_STATUS"))
        for region, level in chapter.region_to_level.items():
            if region != "Chapter Completion":
                self.assertNotEqual(level, status_level)

    def test_levels_unique_per_chapter(self):
        """Test that levels are unique to a single chapter."""
        seen_levels: set[Level] = set()
        for chapter in chapters_iter():
            chapter_levels = set(chapter.region_to_level.values())
            self.assertTrue(seen_levels.isdisjoint(chapter_levels))
            seen_levels.update(chapter_levels)

    @chapters_test
    def test_levels_exist_in_area(self, chapter: Chapter):
        for level in set(chapter.region_to_level.values()):
            self.assertIn(level, chapter.area.levels)

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
    def test_regions_are_used(self, chapter: Chapter):
        """Test that each region contains at least one exit, or at least one location, or is used in a
        CanReachRegion rule."""
        unused_region_names = {name for name, exits in chapter.regions.items() if not exits}
        unused_region_names.discard("Chapter Completion")
        unused_region_names.difference_update(chapter.regions_in_can_reach)
        if not unused_region_names:
            return
        for location_data in chapter.all_in_level_location_data:
            if location_data.region in unused_region_names:
                unused_region_names.remove(location_data.region)
                if not unused_region_names:
                    return
        self.fail(f"There are unused regions: {sorted(unused_region_names)}")

    @chapters_test
    def test_story_characters(self, chapter: Chapter):
        for character in chapter.purchase_characters:
            self.assertCharacterUsableInChapterRequirements(character)

    @chapters_test
    def test_purchase_characters(self, chapter: Chapter):
        for character, purchase_cost in chapter.purchase_characters.items():
            self.assertCharacterUsableInChapterRequirements(character)
            self.assertGreater(purchase_cost, 0)

    def test_purchase_characters_unique_per_chapter(self):
        seen_characters = set()
        for chapter in chapters_iter():
            for character in chapter.purchase_characters:
                self.assertNotIn(character, seen_characters, f"{character} from {chapter.short_name} already found.")
            seen_characters.update(chapter.purchase_characters)

    @staticmethod
    def chapter_rule_gen(chapter: Chapter) -> Iterable[tuple[str, Rule]]:
        for region_name, exits in chapter.regions.items():
            for exit_ in exits:
                exit_name = exit_.name
                if not exit_name:
                    exit_name = f"{region_name} -> {exit_.to_region}"
                yield exit_name, exit_.rule
                if exit_.er_rule is not None:
                    yield exit_name, exit_.er_rule

        for minikit_name, minikit_data in chapter.minikits.items():
            yield minikit_name, minikit_data.rule
            if minikit_data.er_rule is not None:
                yield minikit_name, minikit_data.er_rule

        for ridable_name, ridable_data in chapter.ridables.items():
            yield ridable_name, ridable_data.rule
            if ridable_data.er_rule is not None:
                yield ridable_name, ridable_data.er_rule

        yield "Power Brick", chapter.power_brick.rule
        if chapter.power_brick.er_rule is not None:
            yield "Power Brick", chapter.power_brick.er_rule

        yield "Extra Chapter Entrance Rules", chapter.extra_chapter_entrance_rules

    def _check_top_level_rule(self, rule: Rule, logic_options_allowed: bool = True):
        if isinstance(rule, LogicOptions):
            self.assertTrue(logic_options_allowed,
                            "Found a LogicOptions not nested within another LogicOptions or at the top level")
        if isinstance(rule, WrapperRule):
            self._check_top_level_rule(rule.child, False)
        elif isinstance(rule, NestedRule):
            for child in rule.children:
                self._check_top_level_rule(child, False)

    @chapters_test
    def test_extraction_un_nesting(self, chapter: Chapter):
        for owner_name, rule in self.chapter_rule_gen(chapter):
            with self.subTest(name=owner_name):
                un_nested = un_nest_logic_options(rule)
                self._check_top_level_rule(un_nested)

    @chapters_test
    def test_rules_json_serializable(self, chapter: Chapter):
        for owner_name, rule in self.chapter_rule_gen(chapter):
            with self.subTest(name=owner_name):
                un_nested = un_nest_logic_options(rule)

                with self.subTest(un_nested=False):
                    json.dumps(rule.to_dict())
                if un_nested is not rule:
                    with self.subTest(un_nested=True):
                        json.dumps(un_nested.to_dict())

    @chapters_test
    def test_no_empty_and_in_rules(self, chapter: Chapter):
        def scan_for_empty_and(rule: Rule):
            if isinstance(rule, NestedRule):
                if not rule.children and isinstance(rule, And):
                    self.fail("Found an empty And() rule, this will incorrectly resolve to False_() due to a Rule"
                              " Builder bug")
                for child in rule.children:
                    scan_for_empty_and(child)
            elif isinstance(rule, WrapperRule):
                scan_for_empty_and(rule.child)
            elif isinstance(rule, LogicOptions):
                scan_for_empty_and(rule.base)
                scan_for_empty_and(rule.normal)
                scan_for_empty_and(rule.moderate)
                scan_for_empty_and(rule.hard)
        for owner_name, rule in self.chapter_rule_gen(chapter):
            with self.subTest(name=owner_name):
                scan_for_empty_and(rule)

    def test_rules_resolve(self):
        logic_difficulties = [
            LogicDifficulty(v) for v in LogicDifficulty.name_lookup.keys()
        ]
        world_types = [AutoWorldRegister.world_types[GAME_NAME]] * len(logic_difficulties)
        options = [
            {
                "logic_difficulty": difficulty.value
            } for difficulty in logic_difficulties
        ]

        # There is no region creation code currently, so CanReachRegion rules will fail with a KeyError.
        ignore_key_errors = True

        mw = setup_multiworld(world_types, steps=("generate_early",), seed=None, options=options)
        for world, logic_difficulty in zip(mw.worlds.values(), logic_difficulties):
            def test_function(_self, chapter: Chapter):
                for owner_name, rule in self.chapter_rule_gen(chapter):
                    with self.subTest(rule=owner_name):
                        if ignore_key_errors:
                            try:
                                rule.resolve(world)
                            except KeyError as ex:
                                self.skipTest(f"Missing region: {ex}")
                        else:
                            rule.resolve(world)

            with self.subTest(difficulty=logic_difficulty.current_option_name):
                chapters_test(test_function)(self)
