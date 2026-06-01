from typing import Literal, cast

from rule_builder.rules import Rule, NestedRule, And, Or, WrapperRule, Filtered, TWorld, False_, True_

from .option_filters import LogicOptions


def _recursively_replace_logic_options(rule: Rule, difficulty_attribute: Literal["base", "normal", "moderate", "hard"]):
    rule_class = type(rule)
    if rule_class is LogicOptions:
        if rule.options:
            # OptionFilters would probably be annoying to combine correctly, especially if filtered_resolution
            # differs between the LogicOptions and the rule being getattr-ed.
            raise Exception("LogicOptions should not use OptionFilters, filter the individual rules instead.")
        return _recursively_replace_logic_options(getattr(rule, difficulty_attribute), difficulty_attribute)
    if isinstance(rule, NestedRule):
        if len(rule.children) == 1:
            return _recursively_replace_logic_options(rule.children[0], difficulty_attribute)
        if len(rule.children) == 0:
            if rule_class is Or:
                return False_()
            elif rule_class is And:
                # Note: Rule Builder is currently bugged, and will resolve And(*[]) to False_()!
                return True_()
            else:
                raise Exception(f"Cannot handle unknown type NestedRule: {rule}")
        # Recursively iterate through children and replace rules as necessary.
        # Scan for a rule that could need replacement.
        for child in rule.children:
            if isinstance(child, (LogicOptions, NestedRule)):
                # A rule that could need replacing has been found.

                # Find which NestedRule type we are.
                if rule_class is And:
                    cls = And
                elif rule_class is Or:
                    cls = Or
                else:
                    raise Exception(f"Cannot handle unknown type NestedRule: {rule}")

                new_children = []
                changed = False
                for child2 in rule.children:
                    replacement_child = _recursively_replace_logic_options(child2, difficulty_attribute)
                    # If no changes are made, then the input rule is returned.
                    if replacement_child is not child2:
                        changed = True
                    new_children.append(replacement_child)
                if changed:
                    return cls(
                        *new_children,
                        options=rule.options,
                        filtered_resolution=rule.filtered_resolution
                    )
                # No rules have changed, so fall through to returning the input rule.
        # No rules could need replacement, so fall through to returning the input rule.
    if isinstance(rule, WrapperRule):
        if rule_class is Filtered or rule_class is WrapperRule:
            replacement_child = _recursively_replace_logic_options(rule.child, difficulty_attribute)
            if replacement_child is not rule.child:
                return cast(type[Filtered] | type[WrapperRule], rule_class)(
                    replacement_child,
                    options=rule.options,
                    filtered_resolution=rule.filtered_resolution
                )
    return rule


def logic_options_un_nested(
        base: Rule[TWorld],
        normal: Rule[TWorld],
        moderate: Rule[TWorld],
        hard: Rule[TWorld],
) -> Rule | None:
    # If any of base/normal/moderate/hard contain a LogicOptions rule, replace that with the base/normal/moderate/hard
    # rule.
    base_rule = _recursively_replace_logic_options(base, "base")
    normal_rule = _recursively_replace_logic_options(normal, "normal")
    moderate_rule = _recursively_replace_logic_options(moderate, "moderate")
    hard_rule = _recursively_replace_logic_options(hard, "hard")

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


def un_nest_logic_options(rule: Rule) -> Rule:
    if isinstance(rule, LogicOptions):
        un_nested = logic_options_un_nested(
            base=rule.base,
            normal=rule.normal,
            moderate=rule.moderate,
            hard=rule.hard,
        )
    else:
        un_nested = logic_options_un_nested(
            base=rule,
            normal=rule,
            moderate=rule,
            hard=rule,
        )
    if un_nested is not None:
        return un_nested
    else:
        return rule
