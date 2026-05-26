from unittest import TestCase

from rule_builder.rules import Has, Rule, And

from ..data.logic.option_filters import logic_options

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


class TestRules(TestCase):
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

