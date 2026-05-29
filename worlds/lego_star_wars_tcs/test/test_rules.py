from unittest import TestCase

from rule_builder.rules import Has, Rule, And, Or, HasAny

from ..data.logic.option_filters import logic_options
from ..data.logic.macros import can_jump_distance_rule
from ..data.logic.rules import HasAbility
from ..character_ability import CharacterAbility

BASE_ITEM = "BASE_ITEM"
NORMAL_ITEM = "NORMAL_ITEM"
MODERATE_ITEM = "MODERATE_ITEM"
HARD_ITEM = "HARD_ITEM"

BASIC_OPTIONS = logic_options(
    base=Has(BASE_ITEM),
    normal=Has(NORMAL_ITEM),
    moderate=Has(MODERATE_ITEM),
    hard=Has(HARD_ITEM),
)


class TestLogicOptionsRules(TestCase):
    def items_from_simple_rule(self, rule: Rule) -> list[str]:
        items = []
        self.assertIsInstance(rule, (Has, And))
        if isinstance(rule, Has):
            items.append(rule.item_name)
        elif isinstance(rule, And):
            for child_rule in rule.children:
                self.assertIsInstance(child_rule, Has)
                items.append(child_rule.item_name)
        return items

    def test_logic_options_recursive_replacement(self):
        options = logic_options(
            base=Has("base item 2") & BASIC_OPTIONS,
            hard=Has("hard item 2"),
        )

        self.assertEqual(self.items_from_simple_rule(options.base), ["base item 2", BASE_ITEM])
        self.assertEqual(self.items_from_simple_rule(options.normal), ["base item 2", NORMAL_ITEM])
        self.assertEqual(self.items_from_simple_rule(options.moderate), ["base item 2", MODERATE_ITEM])
        self.assertEqual(self.items_from_simple_rule(options.hard), ["hard item 2"])

    def test_logic_options_and_full_spread(self):
        options = logic_options(
            base=Has("base item 2"),
            hard=Has("hard item 2"),
        ).and_rule(BASIC_OPTIONS)

        self.assertEqual(self.items_from_simple_rule(options.base), ["base item 2", BASE_ITEM])
        self.assertEqual(self.items_from_simple_rule(options.normal), ["base item 2", NORMAL_ITEM])
        self.assertEqual(self.items_from_simple_rule(options.moderate), ["base item 2", MODERATE_ITEM])
        self.assertEqual(self.items_from_simple_rule(options.hard), ["hard item 2", HARD_ITEM])

    def test_logic_options_and_full_spread_reverse(self):
        options = BASIC_OPTIONS.and_rule(
            logic_options(
                base=Has("base item 2"),
                hard=Has("hard item 2"),
            )
        )

        self.assertEqual(self.items_from_simple_rule(options.base), [BASE_ITEM, "base item 2"])
        self.assertEqual(self.items_from_simple_rule(options.normal), [NORMAL_ITEM, "base item 2"])
        self.assertEqual(self.items_from_simple_rule(options.moderate), [MODERATE_ITEM, "base item 2"])
        self.assertEqual(self.items_from_simple_rule(options.hard), [HARD_ITEM, "hard item 2"])

    def test_logic_option_single_rule_full_spread(self):
        options = BASIC_OPTIONS.and_rule(Has("spread rule"))

        self.assertEqual(self.items_from_simple_rule(options.base), [BASE_ITEM, "spread rule"])
        self.assertEqual(self.items_from_simple_rule(options.normal), [NORMAL_ITEM, "spread rule"])
        self.assertEqual(self.items_from_simple_rule(options.moderate), [MODERATE_ITEM, "spread rule"])
        self.assertEqual(self.items_from_simple_rule(options.hard), [HARD_ITEM, "spread rule"])

    def test_logic_options_partial_spread(self):
        options = logic_options(
            base=Has("base item 2"),
            hard=Has("hard item 2"),
        ).and_rule(BASIC_OPTIONS, apply_to="moderate+")

        self.assertEqual(self.items_from_simple_rule(options.base), ["base item 2"])
        self.assertEqual(self.items_from_simple_rule(options.normal), ["base item 2"])
        self.assertEqual(self.items_from_simple_rule(options.moderate), ["base item 2", MODERATE_ITEM])
        self.assertEqual(self.items_from_simple_rule(options.hard), ["hard item 2", HARD_ITEM])

    def test_logic_options_single_rule_partial_spread(self):
        options = logic_options(
            base=Has("base item 2"),
            hard=Has("hard item 2"),
        ).and_rule(BASIC_OPTIONS.normal, apply_to="moderate+")

        self.assertEqual(self.items_from_simple_rule(options.base), ["base item 2"])
        self.assertEqual(self.items_from_simple_rule(options.normal), ["base item 2"])
        self.assertEqual(self.items_from_simple_rule(options.moderate), ["base item 2", NORMAL_ITEM])
        self.assertEqual(self.items_from_simple_rule(options.hard), ["hard item 2", NORMAL_ITEM])


class TestJumpDistanceMacros(TestCase):
    def _test(self, distance: float, expected_ability: CharacterAbility, *expected_characters: str):
        rule = can_jump_distance_rule(distance)
        if expected_characters:
            self.assertIsInstance(rule, Or)
            for child in rule.children:
                self.assertIsInstance(child, (HasAbility, HasAny))
                if isinstance(child, HasAbility):
                    self.assertIs(child.ability, expected_ability)
                elif isinstance(child, HasAny):
                    self.assertEqual(set(expected_characters), set(child.item_names))
        else:
            self.assertIsInstance(rule, HasAbility)
            self.assertIs(rule.ability, expected_ability)

    def test_0_5(self):
        self._test(0.5, CharacterAbility.CAN_BARELY_JUMP)

    def test_0_56(self):
        self._test(0.56, CharacterAbility.CAN_BARELY_JUMP)

    def test_0_6(self):
        self._test(0.6, CharacterAbility.CAN_JUMP_DISTANCE_0_69)

    def test_0_65(self):
        self._test(0.65, CharacterAbility.CAN_JUMP_DISTANCE_0_69)

    def test_0_7(self):
        self._test(0.7, CharacterAbility.CAN_JUMP_DISTANCE_0_84,
                   # 0.7
                   "Clone",
                   "Clone (Episode III)",
                   "Clone (Episode III, Pilot)",
                   "Commander Cody",
                   "Clone (Episode III, Swamp)",
                   "Clone (Episode III, Walker)",
                   "Disguised Clone",
                   "Boss Nass",
                   # 0.75
                   "Geonosian",
                   "Watto",
                   # 0.766...
                   "Dexter Jettster",
                   )

    def test_0_8(self):
        self._test(0.8, CharacterAbility.CAN_JUMP_DISTANCE_0_84)

    def test_0_9(self):
        self._test(0.9, CharacterAbility.CAN_JUMP_DISTANCE_0_92, "Lando Calrissian", "Lando (Palace Guard)")

    def test_1_0(self):
        with self.assertRaises(ValueError):
            can_jump_distance_rule(1.0)
