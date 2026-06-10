from dataclasses import dataclass, field
from random import Random
from typing import cast

from rule_builder.rules import Rule, Or, And, True_, WrapperRule

from .rules import InLevelRule, HasAbility, HasAnyAbilities, HasAllAbilities
from .rule_replacement import RuleReplacer
from ...character_ability import CharacterAbility


class ExtractionRuleReplacer(RuleReplacer):
    def __init__(self):
        super().__init__({})

    def _handle(self, rule: Rule) -> Rule:
        if isinstance(rule, InLevelRule):
            simpler = rule.make_simpler_rule()
            # If the rule cannot be simplified, then it may return itself.
            if simpler is not rule:
                return self.replace(simpler)
            else:
                return rule
        return super()._handle(rule)


# todo: can `required` abilities and `optional` abilities always get combined, and then do `optional &= ~required` at
#  the and?
@dataclass
class AbilityRequirements:
    random: Random
    abilities_memodict: dict[tuple[Rule.Resolved, CharacterAbility], tuple[CharacterAbility, CharacterAbility] | None] \
        = field(default_factory=dict)

    def _memoize(self,
                 key: tuple[Rule.Resolved, CharacterAbility],
                 result: tuple[CharacterAbility, CharacterAbility] | None,
                 ) -> tuple[CharacterAbility, CharacterAbility] | None:
        self.abilities_memodict[key] = result
        return result

    # todo: Is the `optional` argument even necessary? It is only ever combined with currently, so would not be
    #  necessary.
    def extract_ability_requirements(
            self,
            rule: Rule.Resolved,
            required: CharacterAbility = CharacterAbility.NONE,
            optional: CharacterAbility = CharacterAbility.NONE,
    ) -> tuple[CharacterAbility, CharacterAbility] | None:
        # Resolved rules are singletons, so if a resolved rule is used in multiple places, it is the same instance.
        key = rule, required
        if key in self.abilities_memodict:
            return self.abilities_memodict[key]

        if isinstance(rule, Or.Resolved):
            # cast to work around bugs in PyCharm's type checker.
            rule = cast(Or.Resolved, rule)

            # Any one rule must be required.
            # First try to find if there is any rule whose required abilities are already satisfied. If so, then all
            # abilities used by the child rules are optional, besides those that are already in `required`.
            found_requirements: list[tuple[CharacterAbility, CharacterAbility]] = []
            child_iter = iter(rule.children)
            for child in child_iter:
                requirements = self.extract_ability_requirements(child, required, optional)
                if requirements is not None:
                    if requirements[0] in required:
                        # This child is already satisfied by the required abilities, so the whole rule is satisfied by
                        # the abilities.
                        # Mark everything as optional.
                        optional |= requirements[1]
                        # And the requirements from already processed children.
                        for required_for_child_but_optional_for_parent, optional_requirement in found_requirements:
                            optional |= required_for_child_but_optional_for_parent | optional_requirement
                        # And the requirements from the remaining children.
                        for remaining_child in child_iter:
                            # todo: Does it matter that `optional` has already been modified?
                            requirements = self.extract_ability_requirements(remaining_child, required, optional)
                            if requirements is not None:
                                optional |= requirements[0] | requirements[1]
                        # Remove required abilities from optional abilities before returning.
                        return self._memoize(key, (required, optional & ~required))
                    else:
                        found_requirements.append(requirements)
            if not found_requirements:
                return self._memoize(key, None)
            # Find the child with the smallest number of new bits that are required.
            # Shuffle first, so that, if there is a tie, the tie is resolved randomly.
            # todo?: Assign a cost to each ability (rarer abilities have a higher cost) and pick the required abilities
            #  with the lowest cost instead?
            self.random.shuffle(found_requirements)
            found_requirements.sort(key=lambda t: (t[0] & ~required).bit_count())
            first = found_requirements[0]
            required |= first[0]
            optional |= first[1]
            for required_for_child_but_optional_for_parent, optional_requirement in found_requirements[1:]:
                optional |= required_for_child_but_optional_for_parent | optional_requirement
            return self._memoize(key, (required, optional & ~required))

        if isinstance(rule, And.Resolved):
            # cast to work around bugs in PyCharm's type checker.
            rule = cast(And.Resolved, rule)

            found = False
            for child in rule.children:
                requirements = self.extract_ability_requirements(child, required, optional)
                if requirements is not None:
                    found = True
                    # Union the abilities.
                    required |= requirements[0]
                    optional |= requirements[1]
            if not found:
                # No parts of this rule require abilities.
                return self._memoize(key, None)
            # Remove all required abilities from the optional abilities before returning.
            return self._memoize(key, (required, optional & ~required))

        if isinstance(rule, HasAbility.Resolved):
            # cast to work around bugs in PyCharm's type checker.
            rule = cast(HasAbility.Resolved, rule)

            return self._memoize(key, (required | CharacterAbility(rule.ability_as_int), optional))

        if isinstance(rule, HasAnyAbilities.Resolved):
            # cast to work around bugs in PyCharm's type checker.
            rule = cast(HasAnyAbilities.Resolved, rule)

            abilities = CharacterAbility(rule.abilities_as_int)
            intersection = abilities & required
            if intersection is not CharacterAbility.NONE:
                # This rule would already be satisfied by the currently required abilities.
                # Find other abilities present in this rule that are not already required, and mark them as optional.
                other_abilities = abilities & ~required
                return self._memoize(key, (required, optional | other_abilities))
            else:
                # This rule would not already be satisfied by the currently required abilities.
                # todo: Should we prefer picking an ability that is already in `optional` to promote to `required`, or
                #  prefer an ability that is in neither `optional` nor `required`?
                # Pick an ability used by this rule at random.
                picked_ability = self.random.choice(list(abilities))
                # Remove the picked ability from the other abilities.
                other_abilities = abilities & ~picked_ability
                # Remove the picked ability from the optional abilities (if present)
                optional &= ~picked_ability
                return self._memoize(key, (required | picked_ability, optional | other_abilities))

        if isinstance(rule, HasAllAbilities.Resolved):
            # cast to work around bugs in PyCharm's type checker.
            rule = cast(HasAllAbilities.Resolved, rule)

            # All abilities are required.
            return self._memoize(key, (CharacterAbility(required | rule.abilities_as_int), optional))

        if isinstance(rule, True_.Resolved):
            return self._memoize(key, (required, optional))

        if isinstance(rule, WrapperRule.Resolved):
            # cast to work around bugs in PyCharm's type checker.
            rule = cast(WrapperRule.Resolved, rule)

            return self._memoize(key, (self.extract_ability_requirements(rule.child, required, optional)))

        # This rule does not have ability requirements, e.g. it is a Has("Exploding Blaster Bolts"), or a
        # CanReachRegion("region name") or similar.
        return self._memoize(key, None)
