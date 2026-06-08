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

    def _handle_or(self, rule: Or, difficulty: Difficulty) -> Rule:
        if not rule.children:
            return False_()

        if len(rule.children) == 1:
            return self.replace(rule.children[0], difficulty)

        changed = False
        new_children = []
        children_stack = list(reversed(rule.children))
        while children_stack:
            child = children_stack.pop()
            if isinstance(child, Or) and child.options == rule.options:
                children_stack.extend(reversed(child.children))
                changed = True
            else:
                replaced = self.replace(child, difficulty)
                if replaced is not child:
                    changed = True
                    if isinstance(replaced, Or) and replaced.options == rule.options:
                        new_children.extend(replaced.children)
                    else:
                        new_children.append(replaced)
                else:
                    new_children.append(replaced)
        if changed:
            return Or(*new_children, options=rule.options, filtered_resolution=rule.filtered_resolution)
        else:
            return rule

    def _handle_and(self, rule: And, difficulty: Difficulty) -> Rule:
        if not rule.children:
            return True_()

        if len(rule.children) == 1:
            return self.replace(rule.children[0], difficulty)

        changed = False
        new_children = []
        children_stack = list(reversed(rule.children))
        while children_stack:
            child = children_stack.pop()
            if isinstance(child, And) and child.options == rule.options:
                children_stack.extend(reversed(child.children))
                changed = True
            else:
                replaced = self.replace(child, difficulty)
                if replaced is not child:
                    changed = True
                    if isinstance(replaced, And) and replaced.options == rule.options:
                        new_children.extend(replaced.children)
                    else:
                        new_children.append(replaced)
                else:
                    new_children.append(replaced)
        if changed:
            return And(*new_children, options=rule.options, filtered_resolution=rule.filtered_resolution)
        else:
            return rule