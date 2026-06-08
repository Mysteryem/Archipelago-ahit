import dataclasses
from typing import Literal, TypeVar, Protocol

from rule_builder.rules import Rule, And, Or, WrapperRule, Filtered

from .option_filters import LogicOptions


Difficulty = Literal["base", "normal", "moderate", "hard"]


class RuleData(Protocol):
    @property
    def rule(self) -> Rule:
        return ...

    @property
    def er_rule(self) -> Rule | None:
        return ...


TRuleData = TypeVar("TRuleData", bound=RuleData)


class RuleReplacer:
    def __init__(self, dispatch_overrides: dict | None = None) -> None:
        self._handlers = {
            Filtered: self._handle_filtered,
            WrapperRule: self._handle_wrapper_rule,
            LogicOptions: self._handle_logic_options,
            Or: self._handle_or,
            And: self._handle_and,
        }
        if dispatch_overrides:
            self._handlers |= dispatch_overrides
        self.replaced_rules_memodict: dict[tuple[int, Difficulty], Rule] = {}

    def replace_each_difficulty(
            self,
            base: Rule,
            normal: Rule,
            moderate: Rule,
            hard: Rule,
    ) -> Rule | None:
        # If any of base/normal/moderate/hard contain a LogicOptions rule, replace that with the
        # base/normal/moderate/hard rule.
        base_rule = self.replace(base, "base")
        normal_rule = self.replace(normal, "normal")
        moderate_rule = self.replace(moderate, "moderate")
        hard_rule = self.replace(hard, "hard")

        assert isinstance(base_rule, Rule)
        if hard_rule is moderate_rule and hard_rule is normal_rule and hard_rule is base_rule:
            # All the rules are the same.
            return base_rule
        else:
            assert isinstance(normal_rule, Rule)
            assert isinstance(moderate_rule, Rule)
            assert isinstance(hard_rule, Rule)

            if base_rule is base and normal_rule is normal and moderate_rule is moderate and hard_rule is hard:
                # No changes.
                return None

            return LogicOptions(base_rule, normal_rule, moderate_rule, hard_rule)

    def replace_top_level_rule(self, rule: Rule) -> Rule:
        if isinstance(rule, LogicOptions):
            un_nested = self.replace_each_difficulty(
                base=rule.base,
                normal=rule.normal,
                moderate=rule.moderate,
                hard=rule.hard,
            )
        else:
            un_nested = self.replace_each_difficulty(
                base=rule,
                normal=rule,
                moderate=rule,
                hard=rule,
            )
        if un_nested is not None:
            return un_nested
        else:
            return rule

    def replace_rule_data(self, rule_data: TRuleData) -> TRuleData:
        rule = self.replace_top_level_rule(rule_data.rule)
        er_rule = None if rule_data.er_rule is None else self.replace_top_level_rule(rule_data.er_rule)
        if rule is not rule_data.rule or er_rule is not rule_data.er_rule:
            return dataclasses.replace(rule_data, rule=rule, er_rule=er_rule)
        else:
            return rule_data


    def replace(self, rule: Rule, difficulty: Difficulty) -> Rule:
        key = (id(rule), difficulty)
        already_handled = self.replaced_rules_memodict.get(key)
        if already_handled is not None:
            return already_handled
        else:
            replaced = self._handle(rule, difficulty)
            self.replaced_rules_memodict[key] = replaced
            return replaced

    def _handle(self, rule: Rule, difficulty: Difficulty) -> Rule:
        rule_class = type(rule)
        if rule_class in self._handlers:
            return self._handlers[rule_class](rule, difficulty)
        else:
            return rule

    def _handle_filtered(self, rule: Filtered, difficulty: Difficulty) -> Rule:
        replaced = self.replace(rule.child, difficulty)
        if replaced is not rule.child:
            return Filtered(replaced, options=rule.options, filtered_resolution=rule.filtered_resolution)
        else:
            return rule

    def _handle_wrapper_rule(self, rule: WrapperRule, difficulty: Difficulty) -> Rule:
        replaced = self.replace(rule.child, difficulty)
        if replaced is not rule.child:
            return WrapperRule(replaced, options=rule.options, filtered_resolution=rule.filtered_resolution)
        else:
            return rule

    def _handle_logic_options(self, rule: LogicOptions, difficulty: Difficulty) -> Rule:
        if rule.options:
            # OptionFilters would probably be annoying to combine correctly, especially if filtered_resolution
            # differs between the LogicOptions and the rule being getattr-ed.
            raise Exception("LogicOptions should not use OptionFilters, filter the individual rules instead.")
        return self.replace(getattr(rule, difficulty), difficulty)

    def _handle_or(self, rule: Or, difficulty: Difficulty) -> Rule:
        changed = False
        new_children = []
        for child in rule.children:
            replaced = self.replace(child, difficulty)
            if replaced is not child:
                changed = True
            if isinstance(replaced, Or) and replaced.options == rule.options:
                new_children.extend(replaced.children)
            else:
                new_children.append(replaced)
        if changed:
            return Or(*new_children, options=rule.options, filtered_resolution=rule.filtered_resolution)
        else:
            return rule

    def _handle_and(self, rule: And, difficulty: Difficulty) -> Rule:
        changed = False
        new_children = []
        for child in rule.children:
            replaced = self.replace(child, difficulty)
            if replaced is not child:
                changed = True
            if isinstance(replaced, And) and replaced.options == rule.options:
                new_children.extend(replaced.children)
            else:
                new_children.append(replaced)
        if changed:
            return And(*new_children, options=rule.options, filtered_resolution=rule.filtered_resolution)
        else:
            return rule