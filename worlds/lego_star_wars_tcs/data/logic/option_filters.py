from dataclasses import dataclass
from operator import and_, or_
from typing import TYPE_CHECKING, Literal

from Options import CommonOptions
from rule_builder.field_resolvers import FromWorldAttr
from rule_builder.rules import Rule, TWorld, True_, Has, Or, And, NestedRule
from rule_builder.options import OptionFilter

from ...constants import GAME_NAME
from ...options import LogicDifficulty, EntranceRandomizer


if TYPE_CHECKING:
    from ... import LegoStarWarsTCSWorld
else:
    LegoStarWarsTCSWorld = TWorld


normal_logic = (OptionFilter(LogicDifficulty, LogicDifficulty.option_normal, "ge"),)
moderate_logic = (OptionFilter(LogicDifficulty, LogicDifficulty.option_moderate, "ge"),)
hard_logic = (OptionFilter(LogicDifficulty, LogicDifficulty.option_hard, "ge"),)

base_logic_only = (OptionFilter(LogicDifficulty, LogicDifficulty.option_none),)
normal_logic_only = (OptionFilter(LogicDifficulty, LogicDifficulty.option_normal),)
moderate_logic_only = (OptionFilter(LogicDifficulty, LogicDifficulty.option_moderate),)
hard_logic_only = (OptionFilter(LogicDifficulty, LogicDifficulty.option_hard),)

base_and_normal_logic_only = (
    OptionFilter(LogicDifficulty, LogicDifficulty.option_normal, "le"),
)

logic_expects_fighting_all_enemies = base_logic_only
extras_in_logic = normal_logic

# Entrance Rando does not exist currently, but this can be used to mark rules as only being relevant to entrance rando,
# and then filtering them out (replacing them with False_()).
entrance_rando = (OptionFilter(LogicDifficulty, float("nan"), "eq"),)


DifficultySpecifier = Literal[
    "base",
    "base+",
    "normal",
    "normal+",
    "moderate",
    "moderate+",
    "hard",
    "hard+",
]

_DIFFICULTIES = (
    "base",
    "normal",
    "moderate",
    "hard",
)

_PLUS_DIFFICULTY_TO_SLICE = {
    "base+": slice(0, None),
    "normal+": slice(1, None),
    "moderate+": slice(2, None),
    "hard+": slice(3, None),
}


@dataclass
class LogicOptions(Rule[LegoStarWarsTCSWorld], game=GAME_NAME):
    base: Rule[TWorld]
    normal: Rule[TWorld]
    moderate: Rule[TWorld]
    hard: Rule[TWorld]

    def _instantiate(self, world: LegoStarWarsTCSWorld) -> Rule.Resolved:
        logic_difficulty = world.options.logic_difficulty
        if logic_difficulty == LogicDifficulty.option_none:
            rule = self.base
        elif logic_difficulty == LogicDifficulty.option_normal:
            rule = self.normal
        elif logic_difficulty == LogicDifficulty.option_moderate:
            rule = self.moderate
        elif logic_difficulty == LogicDifficulty.option_hard:
            rule = self.hard
        else:
            raise Exception(f"Unrecognised logic difficulty {logic_difficulty}")
        return rule.resolve(world)

    def _apply_rule_op(self,
                       rule: Rule,
                       op: Literal[and_, or_],
                       apply_to: DifficultySpecifier | None = None) -> "LogicOptions":
        if apply_to is None:
            # Not a necessary optimisation, but saves having to create extra intermediary LogicOptions instances.
            if isinstance(rule, LogicOptions):
                return LogicOptions(
                    op(self.base, rule.base),
                    op(self.normal, rule.normal),
                    op(self.moderate, rule.moderate),
                    op(self.hard, rule.hard),
                )
            else:
                # Apply to all.
                apply_to = "base+"

        if apply_to.endswith("+"):
            slice_to_use = _PLUS_DIFFICULTY_TO_SLICE[apply_to]
            difficulty_names = _DIFFICULTIES[slice_to_use]
            logic = self
            for difficulty_name in difficulty_names:
                logic = logic._apply_rule_op(rule, op, difficulty_name)
            return logic

        if isinstance(rule, LogicOptions):
            rule = getattr(rule, apply_to)

        if apply_to == "base":
            return LogicOptions(
                op(self.base, rule),
                self.normal,
                self.moderate,
                self.hard,
            )
        elif apply_to == "normal":
            return LogicOptions(
                self.base,
                op(self.normal, rule),
                self.moderate,
                self.hard,
            )
        elif apply_to == "moderate":
            return LogicOptions(
                self.base,
                self.normal,
                op(self.moderate, rule),
                self.hard,
            )
        elif apply_to == "hard":
            return LogicOptions(
                self.base,
                self.normal,
                self.moderate,
                op(self.hard, rule),
            )
        raise ValueError(f"Unexpected apply_to {apply_to}")

    def and_rule(self,
                 rule: Rule,
                 apply_to: DifficultySpecifier | None = None) -> "LogicOptions":
        return self._apply_rule_op(rule, and_, apply_to)

    def or_rule(self,
                rule: Rule,
                apply_to: DifficultySpecifier | None = None) -> "LogicOptions":
        return self._apply_rule_op(rule, or_, apply_to)


def _recursively_replace_logic_options(rule: Rule, difficulty_attribute: Literal["base", "normal", "moderate", "hard"]):
    if isinstance(rule, LogicOptions):
        if rule.options:
            # OptionFilters would probably be annoying to combine correctly, especially if filtered_resolution
            # differs between the LogicOptions and the rule being getattr-ed.
            raise Exception("LogicOptions should not use OptionFilters, filter the individual rules instead.")
        return _recursively_replace_logic_options(getattr(rule, difficulty_attribute), difficulty_attribute)
    if isinstance(rule, NestedRule):
        # Recursively iterate through children and replace rules as necessary.
        # Scan for a rule that could need replacement.
        for child in rule.children:
            if isinstance(child, (LogicOptions, NestedRule)):
                # A rule that could need replacing has been found.

                # Find which NestedRule type we are.
                if isinstance(rule, And):
                    cls = And
                elif isinstance(rule, Or):
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
    return rule


def logic_options(
        base: Rule[TWorld],
        normal: Rule[TWorld] | None = None,
        moderate: Rule[TWorld] | None = None,
        hard: Rule[TWorld] | None = None,
) -> LogicOptions[TWorld]:
    # If any of base/normal/moderate/hard contain a LogicOptions rule, replace that with the base/normal/moderate/hard
    # rule.
    base_rule = _recursively_replace_logic_options(base, "base")

    if normal is None:
        normal = base
        if base_rule is base:
            # No replacement occurred.
            normal_rule = base
        else:
            normal_rule = _recursively_replace_logic_options(base, "normal")
    else:
        normal_rule = _recursively_replace_logic_options(normal, "normal")

    if moderate is None:
        moderate = normal
        if normal_rule is normal:
            # No replacement occurred.
            moderate_rule = normal
        else:
            moderate_rule = _recursively_replace_logic_options(normal, "moderate")
    else:
        moderate_rule = _recursively_replace_logic_options(moderate, "moderate")

    if hard is None:
        # hard = moderate
        if moderate_rule is moderate:
            # No replacement occurred.
            hard_rule = moderate
        else:
            hard_rule = _recursively_replace_logic_options(moderate, "hard")
    else:
        hard_rule = _recursively_replace_logic_options(hard, "hard")

    if hard_rule is moderate_rule and hard_rule is normal_rule and hard_rule is base_rule:
        # This is not really a problem, but it could indicate an issue elsewhere if all the provided rules are the same.
        raise Exception("All rules are the same. Maybe don't use logic_options.")

    return LogicOptions(base_rule, normal_rule, moderate_rule, hard_rule)





