from rule_builder.rules import Rule, And, Or, False_, True_

from .rules import InLevelRule
from .rule_replacement import RuleReplacer, Difficulty


class ExtractionRuleReplacer(RuleReplacer):
    def __init__(self):
        super().__init__({})

    def _handle(self, rule: Rule, difficulty: Difficulty) -> Rule:
        if isinstance(rule, InLevelRule):
            simpler = rule.make_simpler_rule()
            # If the rule cannot be simplified, then it may return itself.
            if simpler is not rule:
                return self.replace(simpler, difficulty)
            else:
                return rule
        return super()._handle(rule, difficulty)
