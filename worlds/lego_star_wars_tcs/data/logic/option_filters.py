from dataclasses import dataclass
from operator import and_, or_
from typing import TYPE_CHECKING, Literal, Any
from typing_extensions import override

from rule_builder.rules import Rule, TWorld, Has, Or, And
from rule_builder.options import OptionFilter

from ...constants import GAME_NAME
from ...options import LogicDifficulty, UncapOriginalTrilogyHighJump


if TYPE_CHECKING:
    from ... import LegoStarWarsTCSWorld
else:
    LegoStarWarsTCSWorld = TWorld


OT_HIGH_JUMP_ENABLED = OptionFilter(UncapOriginalTrilogyHighJump, True)
OT_HIGH_JUMP_DISABLED = OptionFilter(UncapOriginalTrilogyHighJump, False)


def ot_high_jump_ternary(uncapped: Rule, capped: Rule) -> Rule:
    return Or(
        uncapped & OT_HIGH_JUMP_ENABLED,
        capped & OT_HIGH_JUMP_DISABLED,
    )


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

    @override
    def _instantiate(self, world: LegoStarWarsTCSWorld) -> Rule.Resolved:
        logic_difficulty = world.options.logic_difficulty
        if logic_difficulty == LogicDifficulty.option_none:
            if world.is_universal_tracker():
                rule = Or(
                    self.base,
                    And(
                        Has(world.glitches_item_name),
                        Or(
                            self.normal,
                            Has(world.glitches_all_item_name) & (self.moderate | self.hard),
                        ),
                    ),
                )
            else:
                rule = self.base
        elif logic_difficulty == LogicDifficulty.option_normal:
            if world.is_universal_tracker():
                rule = Or(
                    self.normal,
                    And(
                        Has(world.glitches_item_name),
                        Or(
                            self.moderate,
                            Has(world.glitches_all_item_name) & self.hard,
                        ),
                    ),
                )
            else:
                rule = self.normal
        elif logic_difficulty == LogicDifficulty.option_moderate:
            if world.is_universal_tracker():
                rule = Or(
                    self.moderate,
                    Has(world.glitches_item_name) & self.hard,
                )
            else:
                rule = self.moderate
        elif logic_difficulty == LogicDifficulty.option_hard:
            rule = self.hard
        else:
            raise Exception(f"Unrecognised logic difficulty {logic_difficulty}")
        return rule.resolve(world)

    @override
    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        del data["args"]
        data["base"] = self.base.to_dict()
        data["normal"] = self.normal.to_dict()
        data["moderate"] = self.moderate.to_dict()
        data["hard"] = self.hard.to_dict()
        return data

    def _apply_rule_op(self,
                       rule: Rule,
                       op: Literal[and_, or_],
                       apply_to: DifficultySpecifier | None = None,
                       reverse_order: bool = False) -> "LogicOptions":
        if apply_to is None:
            # Not a necessary optimisation, but saves having to create extra intermediary LogicOptions instances.
            if isinstance(rule, LogicOptions):
                if reverse_order:
                    first_args = (rule.base, rule.normal, rule.moderate, rule.hard)
                    second_args = (self.base, self.normal, self.moderate, self.hard)
                else:
                    first_args = (self.base, self.normal, self.moderate, self.hard)
                    second_args = (rule.base, rule.normal, rule.moderate, rule.hard)
                applied = []
                last_first_arg = None
                last_second_arg = None
                last_applied = None
                for first_arg, second_arg in zip(first_args, second_args):
                    # If the arguments have not changed, use the previous result.
                    if first_arg is not last_first_arg or second_arg is not last_second_arg:
                        last_applied = op(first_arg, second_arg)
                    applied.append(last_applied)
                    last_first_arg = first_arg
                    last_second_arg = second_arg
                return LogicOptions(*applied)
            else:
                # Apply to all.
                apply_to = "base+"

        if apply_to.endswith("+"):
            slice_to_use = _PLUS_DIFFICULTY_TO_SLICE[apply_to]
            difficulty_names = _DIFFICULTIES[slice_to_use]
            logic = self
            for difficulty_name in difficulty_names:
                logic = logic._apply_rule_op(rule, op, difficulty_name, reverse_order)
            return logic

        if isinstance(rule, LogicOptions):
            rule = getattr(rule, apply_to)

        if apply_to == "base":
            return LogicOptions(
                op(rule, self.base) if reverse_order else op(self.base, rule),
                self.normal,
                self.moderate,
                self.hard,
            )
        elif apply_to == "normal":
            return LogicOptions(
                self.base,
                op(rule, self.normal) if reverse_order else op(self.normal, rule),
                self.moderate,
                self.hard,
            )
        elif apply_to == "moderate":
            return LogicOptions(
                self.base,
                self.normal,
                op(rule, self.moderate) if reverse_order else op(self.moderate, rule),
                self.hard,
            )
        elif apply_to == "hard":
            return LogicOptions(
                self.base,
                self.normal,
                self.moderate,
                op(rule, self.hard) if reverse_order else op(self.hard, rule),
            )
        raise ValueError(f"Unexpected apply_to {apply_to}")

    def and_rule(self,
                 rule: Rule,
                 apply_to: DifficultySpecifier | None = None) -> "LogicOptions":
        return self._apply_rule_op(rule, and_, apply_to)

    def rand_rule(self,
                  rule: Rule,
                  apply_to: DifficultySpecifier | None = None) -> "LogicOptions":
        return self._apply_rule_op(rule, and_, apply_to, reverse_order=True)

    def or_rule(self,
                rule: Rule,
                apply_to: DifficultySpecifier | None = None) -> "LogicOptions":
        return self._apply_rule_op(rule, or_, apply_to)

    def ror_rule(self,
                 rule: Rule,
                 apply_to: DifficultySpecifier | None = None) -> "LogicOptions":
        return self._apply_rule_op(rule, or_, apply_to, reverse_order=True)

    # I'm not sure if pre-applying __and__/__or__ like this helps with performance when initialising rules.
    # def __and__(self, other):
    #     return self.and_rule(other)
    #
    # def __or__(self, other):
    #     return self.or_rule(other)


def logic_options(
        base: Rule[TWorld],
        normal: Rule[TWorld] | None = None,
        moderate: Rule[TWorld] | None = None,
        hard: Rule[TWorld] | None = None,
        *, strict: bool = True,
) -> LogicOptions[TWorld]:
    base_rule = base

    if normal is None:
        normal = base
        normal_rule = base
    else:
        normal_rule = normal

    if moderate is None:
        moderate = normal
        moderate_rule = normal
    else:
        moderate_rule = moderate

    if hard is None:
        # hard = moderate
        hard_rule = moderate
    else:
        hard_rule = hard

    if strict and hard_rule is moderate_rule and hard_rule is normal_rule and hard_rule is base_rule:
        # This is not really a problem, but it could indicate an issue elsewhere if all the provided rules are the same.
        raise Exception("All rules are the same. Maybe don't use logic_options.")

    assert isinstance(base_rule, Rule)
    assert isinstance(normal_rule, Rule)
    assert isinstance(moderate_rule, Rule)
    assert isinstance(hard_rule, Rule)

    return LogicOptions(base_rule, normal_rule, moderate_rule, hard_rule)
