import dataclasses

from typing import TYPE_CHECKING, Any, Protocol, TypeVar

from rule_builder.rules import (
    And,
    Or,
    NestedRule,
    Filtered,
    WrapperRule,
    Rule,
    Has,
    HasAll,
    HasAny,
    HasFromListUnique,
    HasGroup,
    HasAnyCount,
    HasFromList,
    HasAllCounts,
    HasGroupUnique,
    CanReachRegion,
    CanReachEntrance,
    CanReachLocation,
    True_,
    False_,
)
from rule_builder.field_resolvers import FieldResolver

from .rules import (
    InLevelRule,
    HasAbility,
    HasAbilityCombination,
    HasAnyAbilities,
    HasAllAbilities,
    HasAbilityExceptCharacters,
    HasSingleJumpDistance,
)
from .option_filters import LogicOptions
from ..extras import Extra
from ...character_ability import CharacterAbility
from ...constants import GAME_NAME
from ...data.items.character_items import NON_VEHICLE_EXTRA_CHARACTER_TO_ITEM_DATA


if TYPE_CHECKING:
    from .types import Chapter
    from worlds.AutoWorld import World
else:
    Chapter = object


CHILD_RULES_TO_CHECK = (
    NestedRule,
    WrapperRule,
    HasAbility,
    HasAbilityCombination,
    HasAnyAbilities,
    HasAllAbilities,
    HasAbilityExceptCharacters,
    LogicOptions,
)
ALLOWED_OTHER_RULES = (
    True_,
    False_,
    Has,
    HasAll,
    HasAny,
    HasFromListUnique,
    HasGroup,
    HasAnyCount,
    HasFromList,
    HasAllCounts,
    HasGroupUnique,
    CanReachRegion,
    CanReachEntrance,
    CanReachLocation,
)


@dataclasses.dataclass
class RuleData(Protocol):
    @property
    def rule(self) -> Rule:
        return ...

    @property
    def er_rule(self) -> Rule | None:
        return ...


TRuleData = TypeVar("TRuleData", bound=RuleData)


# WIP idea for handling rules using FieldResolvers.
@dataclasses.dataclass(frozen=True)
class HasAbilityFieldResolver(FieldResolver, game=GAME_NAME):
    child: FieldResolver
    extra_toggle_abilities_union: CharacterAbility

    def resolve(self, world: "World") -> Any:
        ability_required: CharacterAbility = self.child.resolve(world)
        if ability_required in self.extra_toggle_abilities_union:
            return 1
        else:
            return 0


# Alternatives:

# @dataclasses.dataclass
# class HasAbilityWrapper(WrapperRule):
#     extra_toggle_abilities_union: CharacterAbility
#     extra_toggle_abilities_combinations: frozenset[CharacterAbility]
#
#     def _instantiate(self, world: TWorld) -> Rule.Resolved:
#         resolved_child = self.child.resolve(world)
#         if isinstance(resolved_child, HasAbility.Resolved)


# @dataclasses.dataclass
# class HasAbilityOrExtraToggle(HasAbility):
#     extra_toggle_abilities: CharacterAbility | FieldResolver
#     """The abilities provided by Extra Toggle characters."""
#
#     def _instantiate(self, world: TWorld) -> "Resolved":
#         resolved: int = resolve_field(self.ability, world, CharacterAbility).value
#
#         if resolved.bit_count() == 0:
#             return True_().resolve(world)
#
#         assert resolved.bit_count() == 1
#         provided_resolved: int = resolve_field(self.extra_toggle_abilities, world, CharacterAbility).value
#         if resolved & provided_resolved == resolved:
#             return self.Resolved(
#                 resolved,
#                 **common_rule_args(world)
#             )
#         else:
#             return super().Resolved(
#                 resolved,
#                 **common_rule_args(world)
#             )
#
#     class Resolved(HasAbility.Resolved):
#
#         @override
#         def _evaluate(self, state: CollectionState) -> bool:
#             return (state.prog_items[self.player]["COMBINED_ABILITIES"] & self.ability_as_int != 0
#                     or state.prog_items[self.player][Extra.EXTRA_TOGGLE.readable_name] >= 1)


class ExtraToggleRuleReplacer:
    chapter: Chapter
    extra_toggle_abilities_union: CharacterAbility
    extra_toggle_abilities_unique_combinations: set[CharacterAbility]
    extra_toggle_name_to_abilities: dict[str, CharacterAbility]
    replaced_rules_memodict: dict[int, Rule]

    def __init__(self, chapter: Chapter):
        extra_toggle_abilities_union = CharacterAbility.NONE
        extra_toggle_abilities_unique_combinations: set[CharacterAbility] = set()
        extra_toggle_name_to_abilities: dict[str, CharacterAbility] = {}
        if chapter.extra_toggle_characters:
            for character in chapter.extra_toggle_characters:
                character_data = NON_VEHICLE_EXTRA_CHARACTER_TO_ITEM_DATA[character]
                extra_toggle_abilities_union |= character_data.abilities
                extra_toggle_abilities_unique_combinations.add(character_data.abilities)
                extra_toggle_name_to_abilities[character_data.name] = character_data.abilities
        self.extra_toggle_abilities_union = extra_toggle_abilities_union
        self.extra_toggle_abilities_unique_combinations = extra_toggle_abilities_unique_combinations
        self.replaced_rules_memodict = {}
        self.extra_toggle_name_to_abilities = extra_toggle_name_to_abilities

    @staticmethod
    def or_extra_toggle(rule: Rule, extra_and_rule: Rule | None = None) -> Or:
        if isinstance(rule, InLevelRule):
            replacement = rule.prepare_for_or_extra_toggle()
        else:
            replacement = dataclasses.replace(rule, options=(), filtered_resolution=False)
        if extra_and_rule is None:
            return Or(
                replacement,
                Extra.EXTRA_TOGGLE.has(),
                options=rule.options, filtered_resolution=rule.filtered_resolution
            )
            # return Or(
            #     rule,
            #     Has(Extra.EXTRA_TOGGLE.readable_name, options=rule.options, filtered_resolution=rule.filtered_resolution)
            # )
        else:
            return Or(
                replacement,
                extra_and_rule & Extra.EXTRA_TOGGLE.has(),
                options=rule.options, filtered_resolution=rule.filtered_resolution)
            # return Or(
            #     rule,
            #     And(
            #         extra_and_rule,
            #         Has(Extra.EXTRA_TOGGLE.readable_name),
            #         options=rule.options,
            #         filtered_resolution=rule.filtered_resolution
            #     )
            # )

    def add_extra_toggle_rules(self, rule_data: TRuleData) -> TRuleData:
        assert dataclasses.is_dataclass(rule_data)
        rule = self._recursively_replace_data_rule(rule_data.rule)
        er_rule = None if rule_data.er_rule is None else self._recursively_replace_data_rule(rule_data.rule)
        if rule is not rule_data.rule or er_rule is not rule_data.er_rule:
            return dataclasses.replace(rule_data, rule=rule, er_rule=er_rule)
        else:
            return rule_data

    def _recursively_replace_data_rule(self, rule: Rule) -> Rule:
        if isinstance(rule, LogicOptions):
            potential_replacement = LogicOptions(
                base=rule.base,  # Base rules never consider Extras.
                normal=self._recursively_replace_rules(rule.normal),
                moderate=self._recursively_replace_rules(rule.moderate),
                hard=self._recursively_replace_rules(rule.hard),
                options=rule.options,
                filtered_resolution=rule.filtered_resolution,
            )
            if (rule.normal is not potential_replacement.normal
                    or rule.moderate is not potential_replacement.moderate
                    or rule.hard is not potential_replacement.hard):
                replacement = potential_replacement
            else:
                replacement = rule
            self.replaced_rules_memodict[id(rule)] = replacement
            return replacement
        else:
            return self._recursively_replace_rules(rule)

    def _recursively_replace_rules(self, rule: Rule) -> Rule:
        rule_id = id(rule)
        if (replacement := self.replaced_rules_memodict.get(rule_id)) is not None:
            return replacement

        rule_class = type(rule)

        if rule_class is LogicOptions:
            assert isinstance(rule, LogicOptions)
            potential_replacement = LogicOptions(
                base=rule.base,  # Base rules never consider Extras.
                normal=self._recursively_replace_rules(rule.normal),
                moderate=self._recursively_replace_rules(rule.moderate),
                hard=self._recursively_replace_rules(rule.hard),
                options=rule.options,
                filtered_resolution=rule.filtered_resolution,
            )
            if (rule.normal is not potential_replacement.normal
                    or rule.moderate is not potential_replacement.moderate
                    or rule.hard is not potential_replacement.hard):
                replacement = potential_replacement
            else:
                replacement = rule
        elif isinstance(rule, NestedRule):
            new_children = []
            changed = False
            for child in rule.children:
                if not isinstance(child, CHILD_RULES_TO_CHECK):
                    assert isinstance(child, ALLOWED_OTHER_RULES), \
                        f"Unexpected child rule of type {type(child)}: {child}"
                    new_children.append(child)
                else:
                    new_child = self._recursively_replace_rules(child)
                    if new_child is not child:
                        changed = True
                    new_children.append(new_child)
            if not changed:
                replacement = rule
            else:
                if rule_class is And:
                    replacement = And(*new_children,
                                      options=rule.options, filtered_resolution=rule.filtered_resolution)
                elif rule_class is Or:
                    replacement = Or(*new_children,
                                     options=rule.options, filtered_resolution=rule.filtered_resolution)
                else:
                    raise Exception(f"Cannot handle unknown type NestedRule: {rule}")
        elif isinstance(rule, WrapperRule):
            if rule_class is Filtered:
                replacement = Filtered(self._recursively_replace_rules(rule.child),
                                       options=rule.options, filtered_resolution=rule.filtered_resolution)
            elif rule_class is WrapperRule:
                replacement = WrapperRule(self._recursively_replace_rules(rule.child),
                                          options=rule.options, filtered_resolution=rule.filtered_resolution)
            else:
                raise Exception(f"Cannot handle unknown type WrapperRule: {rule}")
        elif isinstance(rule, HasAbility):
            if isinstance(rule.ability, CharacterAbility):
                if rule.ability not in self.extra_toggle_abilities_union:
                    replacement = rule
                else:
                    replacement = self.or_extra_toggle(rule)
            else:
                # FieldResolver support for HasAbility is provided as an example. FieldResolver support is not
                # currently implemented for other Ability rule types.
                replacement = rule | Has(Extra.EXTRA_TOGGLE.readable_name,
                                         count=HasAbilityFieldResolver(
                                             rule.ability, self.extra_toggle_abilities_union
                                         ),
                                         options=rule.options,
                                         filtered_resolution=rule.filtered_resolution)
        elif isinstance(rule, HasAnyAbilities):
            if isinstance(rule.abilities, CharacterAbility):
                if (rule.abilities & self.extra_toggle_abilities_union) != 0:
                    # There is an Extra Toggle character that provides one of the abilities.
                    replacement = self.or_extra_toggle(rule)
                else:
                    replacement = rule
            else:
                raise Exception("FieldResolver support is not implemented.")
        elif isinstance(rule, HasAllAbilities):
            if isinstance(rule.abilities, CharacterAbility):
                if rule.abilities in self.extra_toggle_abilities_union:
                    # There is an Extra Toggle character that provides all the abilities.
                    replacement = self.or_extra_toggle(rule)
                elif (rule.abilities & self.extra_toggle_abilities_union) != 0:
                    # There is an Extra Toggle character that provides *some* of the abilities.
                    # Find the abilities that are not provided by Extra Toggle characters, but still need to be
                    # provided for the rule to return True.
                    missing_abilities = rule.abilities & ~self.extra_toggle_abilities_union
                    replacement = self.or_extra_toggle(rule, HasAllAbilities(missing_abilities))
                    pass
                else:
                    replacement = rule
            else:
                raise Exception("FieldResolver support is not implemented.")
        elif isinstance(rule, HasAbilityCombination):
            if isinstance(rule.ability_combinations, tuple):
                for combination in rule.ability_combinations:
                    if any(combination in extra_toggle_combination for extra_toggle_combination in
                           self.extra_toggle_abilities_unique_combinations):
                        # There is an Extra Toggle character that provides one of the ability combinations the rule
                        # is checking for.
                        replacement = self.or_extra_toggle(rule)
                        break
                else:
                    replacement = rule
            else:
                raise Exception("FieldResolver support is not implemented.")
        elif isinstance(rule, HasAbilityExceptCharacters):
            if isinstance(rule.ability, CharacterAbility) and not isinstance(rule.except_characters, FieldResolver):
                for extra_toggle_character, character_abilities in self.extra_toggle_name_to_abilities.items():
                    if (
                            (rule.ability is CharacterAbility.NONE or rule.ability in character_abilities)
                            and extra_toggle_character not in rule.except_characters
                    ):
                        # There is a character with the required ability that is not excluded.
                        replacement = self.or_extra_toggle(rule)
                        break
                else:
                    # No break, so no extra toggle character could satisfy the rule.
                    replacement = rule
            else:
                raise Exception("FieldResolver support is not implemented.")
        elif isinstance(rule, HasSingleJumpDistance):
            if (CharacterAbility.HOVER | CharacterAbility.CAN_DOUBLE_JUMP) & self.extra_toggle_abilities_union != 0:
                # A character that can hover or double jump can jump further than the best single-jump distance.
                replacement = self.or_extra_toggle(rule)
            else:
                required_distance = rule.distance
                for character in self.chapter.extra_toggle_characters:
                    character_data = NON_VEHICLE_EXTRA_CHARACTER_TO_ITEM_DATA[character]
                    if character_data.single_jump_distance >= required_distance:
                        # Found a character that can jump the required distance.
                        replacement = self.or_extra_toggle(rule)
                        break
                else:
                    # No extra toggle character was found that could satisfy the rule.
                    replacement = rule
        else:
            assert isinstance(rule, ALLOWED_OTHER_RULES), f"Unexpected rule {rule}"
            replacement = rule

        self.replaced_rules_memodict[rule_id] = replacement
        return replacement
