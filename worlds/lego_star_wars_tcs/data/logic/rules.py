import dataclasses
from functools import reduce
from operator import or_
from typing import ClassVar, Iterable, TYPE_CHECKING
from typing_extensions import override

from BaseClasses import CollectionState
from rule_builder.field_resolvers import FieldResolver, resolve_field
from rule_builder.options import OptionFilter
from rule_builder.rules import (
    False_,
    Filtered,
    Has,
    HasAll,
    HasAny,
    HasFromListUnique,
    Rule,
    True_,
    TWorld,
    And,
    Or,
)

from ...character_ability import CharacterAbility
from ...constants import GAME_NAME
from ...items import LOGIC_CONSIDERED_CHARACTERS
from ...options import ChapterUnlockRequirement, EpisodeUnlockRequirement


if TYPE_CHECKING:
    from ... import LegoStarWarsTCSWorld
    from .types import Chapter
else:
    LegoStarWarsTCSWorld = TWorld
    Chapter = object


def _caching_enabled(world: LegoStarWarsTCSWorld):
    # Caching support is not implemented currently.
    return False
    # return getattr(world, "rule_caching_enabled", False)


def _common_rule_args(world: LegoStarWarsTCSWorld):
    return dict(player=world.player, caching_enabled=_caching_enabled(world))


@dataclasses.dataclass
class HasAbility(Rule[LegoStarWarsTCSWorld], game=GAME_NAME):
    """A rule that checks if the player has a given character ability."""

    ability: CharacterAbility | FieldResolver
    """The ability to check for."""

    def __post_init__(self):
        super().__post_init__()
        if isinstance(self.ability, CharacterAbility):
            assert self.ability.bit_count() == 1, f"Expected a single bit, but got {self.ability!r}"

    def _instantiate(self, world: LegoStarWarsTCSWorld) -> Rule.Resolved:
        resolved: int = resolve_field(self.ability, world, CharacterAbility).value

        if resolved.bit_count() == 0:
            return True_().resolve(world)

        assert resolved.bit_count() == 1
        return self.Resolved(
            resolved,
            **_common_rule_args(world)
        )

    class Resolved(Rule.Resolved):
        ability_as_int: int
        skip_cache: ClassVar[bool] = True

        @override
        def _evaluate(self, state: CollectionState) -> bool:
            # != 0 is faster than calling bool().
            return state.prog_items[self.player]["COMBINED_ABILITIES"] & self.ability_as_int != 0


@dataclasses.dataclass
class HasAllAbilities(Rule[LegoStarWarsTCSWorld], game=GAME_NAME):
    """A rule that checks if the player has all the given character abilities."""

    abilities: CharacterAbility | FieldResolver
    """The abilities to check for."""

    def _instantiate(self, world: LegoStarWarsTCSWorld) -> Rule.Resolved:
        resolved_abilities = resolve_field(self.abilities, world, CharacterAbility)

        # Simplify within this rule only.
        simplified = resolved_abilities.simplify_and()

        if simplified.bit_count() == 0:
            return True_().resolve(world)
        if simplified.bit_count() == 1:
            return HasAbility(simplified).resolve(world)
        return self.Resolved(
            simplified,
            **_common_rule_args(world)
        )

    class Resolved(Rule.Resolved):
        abilities_as_int: int
        skip_cache: ClassVar[bool] = True

        @override
        def _evaluate(self, state: CollectionState) -> bool:
            return state.prog_items[self.player]["COMBINED_ABILITIES"] & self.abilities_as_int == self.abilities_as_int

    def __and__(self, other: "Rule[Any] | Iterable[OptionFilter] | OptionFilter") -> "Rule[TWorld]":
        if isinstance(other, OptionFilter):
            other = (other,)
        if isinstance(other, Iterable):
            if not other:
                return self
            return Filtered(self, options=other)
        if self.options == other.options:
            if isinstance(other, HasAllAbilities):
                if other.abilities in self.abilities:
                    return self
                elif self.abilities in other.abilities:
                    return other
                else:
                    return HasAllAbilities(other.abilities | self.abilities)
            if isinstance(other, HasAbility):
                if other.ability in self.abilities:
                    return self
                else:
                    return HasAllAbilities(other.ability | self.abilities)
        return super().__and__(other)


@dataclasses.dataclass
class HasAnyAbilities(Rule[LegoStarWarsTCSWorld], game=GAME_NAME):
    """A rule that checks if the player has any of the given character abilities."""

    abilities: CharacterAbility | FieldResolver
    """The abilities to check for."""

    def _instantiate(self, world: LegoStarWarsTCSWorld) -> Rule.Resolved:
        resolved_abilities = resolve_field(self.abilities, world, CharacterAbility)

        # Simplify within this rule only.
        simplified = resolved_abilities.simplify_or()

        if simplified.bit_count() == 0:
            return True_().resolve(world)
        if simplified.bit_count() == 1:
            return HasAbility(simplified).resolve(world)
        return self.Resolved(
            simplified,
            **_common_rule_args(world)
        )

    class Resolved(Rule.Resolved):
        abilities_as_int: int
        skip_cache: ClassVar[bool] = True

        @override
        def _evaluate(self, state: CollectionState) -> bool:
            return state.prog_items[self.player]["COMBINED_ABILITIES"] & self.abilities_as_int != 0


@dataclasses.dataclass
class HasAbilityCombination(Rule[LegoStarWarsTCSWorld], game=GAME_NAME):
    """A rule that checks if the player has any character with any of the given combinations of abilities.

    Typically only a single ability combination will be needed, but multiple can be provided.

    This is often an expensive rule, but is rarely used rule for cases where it is not worth defining a new ability just
    for a specific use case."""
    ability_combinations: tuple[CharacterAbility, ...] | FieldResolver

    def __init__(self,
                 *ability_combinations: CharacterAbility | FieldResolver,
                 options: Iterable[OptionFilter] = (),
                 filtered_resolution: bool = False
                 ):
        super().__init__(options=options, filtered_resolution=filtered_resolution)
        found_resolver = False
        found_abilities = False
        for v in ability_combinations:
            if isinstance(v, FieldResolver):
                if found_resolver:
                    raise ValueError("Only specify at most one FieldResolver")
                found_resolver = True
            if isinstance(v, CharacterAbility):
                found_abilities = True
        if found_abilities and found_resolver:
            raise ValueError("Cannot specify abilities and field resolvers simultaneously.")

        if found_resolver:
            self.ability_combinations = ability_combinations[0]
        else:
            self.ability_combinations = ability_combinations

    @override
    def _instantiate(self, world: TWorld) -> Rule.Resolved:
        abilities = resolve_field(self.ability_combinations, world, CharacterAbility)

        return self._make_rule(abilities).resolve(world)

    @staticmethod
    def simplify_contained_combinations(combinations: list[CharacterAbility]):
        """
        HasAbilityCombination(HIGH_JUMP | JEDI, HIGH_JUMP | JEDI | SITH)
        can be reduced to HasAbilityCombination(HIGH_JUMP | JEDI)
        :param combinations:
        :return:
        """
        if len(combinations) <= 1:
            # Nothing to do.
            return combinations
        simplified_combinations = []
        while combinations:
            combination = combinations.pop()
            for other_combinations in (simplified_combinations, combinations):
                for other_combination in other_combinations:
                    if other_combination in combination:
                        break
                else:
                    continue
                # Propagate the inner break.
                break
            else:
                # No inner break, so no other combination is present in `combination`
                simplified_combinations.append(combination)
        return simplified_combinations

    @staticmethod
    def _make_rule(*combinations: CharacterAbility) -> Rule:
        if not combinations:
            return False_()

        simplified_combinations = HasAbilityCombination.simplify_contained_combinations(list(combinations))

        # Remove abilities implied by another ability that is requested in that combination.
        # e.g. (JEDI | CAN_MELEE) can be reduced to just (JEDI)
        simplified_combinations = [combination.simplify_combination() for combination in simplified_combinations]

        # Simplify contained combinations again.
        simplified_combinations = HasAbilityCombination.simplify_contained_combinations(simplified_combinations)

        reduced_to_single_bit = []
        still_multiple_bits = []
        for combination in simplified_combinations:
            if combination.bit_count() > 1:
                still_multiple_bits.append(combination)
            else:
                reduced_to_single_bit.append(combination)

        any_rules = []

        if reduced_to_single_bit:
            if len(reduced_to_single_bit) == 1:
                any_rules.append(HasAbility(reduced_to_single_bit[0]))
            else:
                any_rules.append(HasAnyAbilities(reduce(or_, reduced_to_single_bit)))

        if still_multiple_bits:
            all_matching_characters: set[str] = set()
            common_abilities_for_each_combination: list[CharacterAbility] = []
            for combination in still_multiple_bits:
                common_abilities = ~CharacterAbility.NONE
                # Find all characters with this ability combination.
                for character in LOGIC_CONSIDERED_CHARACTERS.values():
                    if combination in character.abilities:
                        # If there are some single bits to check for, then all characters with those single bits can be
                        # ignored because that single bit would match before needing to check for the character being in
                        # the state.
                        if not reduced_to_single_bit or not any(single_bit for single_bit in reduced_to_single_bit):
                            all_matching_characters.add(character.name)
                            common_abilities &= character.abilities
                if common_abilities is not ~CharacterAbility.NONE:
                    common_abilities_for_each_combination.append(common_abilities)

            characters_rule = HasAny(*all_matching_characters)

            # If there are lots of characters that match this, check for having any of the common abilities of each
            # set of characters that have one of the combinations of abilities.
            # characters
            # because that is a faster check.
            if len(all_matching_characters) >= 8 and common_abilities_for_each_combination:
                abilities_rules = []
                for common_abilities_for_combination in common_abilities_for_each_combination:
                    abilities_rules.append(HasAllAbilities(common_abilities_for_combination))
                if abilities_rules:
                    characters_rule = And(Or(*abilities_rules), characters_rule)

            any_rules.append(characters_rule)
        return Or(*any_rules)


@dataclasses.dataclass
class HasAbilityExceptCharacters(Rule[LegoStarWarsTCSWorld], game=GAME_NAME):
    """A rule that checks if the player has any character with the given ability, except the given characters.

    This is an expensive, but rarely used rule for cases where specific characters cannot use their abilities in
    specific cases, where adding a new CharacterAbility to represent this difference in ability is not worth it.
    """
    ability: CharacterAbility | FieldResolver
    """The ability to check for."""

    except_characters: Iterable[str] | FieldResolver
    """The characters excluded from this rule."""

    def __init__(
            self,
            ability: CharacterAbility | FieldResolver,
            *except_characters: str,
            options: Iterable[OptionFilter] = (),
            filtered_resolution: bool = False,
    ):
        super().__init__(options=options, filtered_resolution=filtered_resolution)
        self.ability = ability
        for character_name in except_characters:
            if character_name not in LOGIC_CONSIDERED_CHARACTERS:
                raise Exception(f"Character '{character_name}' does not exist.")
        self.except_characters = set(except_characters)

    @override
    def _instantiate(self, world: TWorld) -> Rule.Resolved:
        required_ability = resolve_field(self.ability, world, CharacterAbility)
        if required_ability.bit_count() == 0:
            # This would otherwise mean any character except certain characters.
            raise Exception("An ability must be required.")
        if required_ability.bit_count() > 1:
            raise Exception(f"Only a single ability should be required, but got {self.ability.name}")

        except_characters = set(resolve_field(self.except_characters, world, Iterable))

        return self._make_rule(required_ability, except_characters).resolve(world)

    @staticmethod
    def _make_rule(required_ability: CharacterAbility, except_characters: set[str]) -> Rule:
        if not except_characters:
            return HasAbility(required_ability)

        except_characters_abilities = CharacterAbility.NONE
        for character_name in except_characters:
            except_characters_abilities |= LOGIC_CONSIDERED_CHARACTERS[character_name].abilities

        include_characters_abilities = ~CharacterAbility.NONE
        include_characters = []
        for character in LOGIC_CONSIDERED_CHARACTERS.values():
            if required_ability in character.abilities and character.name not in except_characters:
                include_characters_abilities &= character.abilities
                include_characters.append(character.name)

        if not include_characters:
            return False_()

        abilities_included_characters_all_have_but_except_characters_do_not = (
                include_characters_abilities & ~include_characters_abilities
        )

        if abilities_included_characters_all_have_but_except_characters_do_not is not CharacterAbility.NONE:
            all_shared_unique = abilities_included_characters_all_have_but_except_characters_do_not | required_ability
            simplified = all_shared_unique.simplify_combination()
            if simplified.bit_count() == 1:
                return HasAbility(simplified)

            if abilities_included_characters_all_have_but_except_characters_do_not.bit_count() > 1:
                # Try simplifying pairs of abilities.
                for included_ability in abilities_included_characters_all_have_but_except_characters_do_not:
                    pair = included_ability | required_ability
                    simplified = pair.simplify_combination()
                    if simplified.bit_count() == 1:
                        return HasAbility(simplified)

        if len(include_characters) >= 8:
            # If there are lots of characters that match this, check for having all the required abilities first
            # because that is a faster check.
            return HasAbility(required_ability) & HasAny(*include_characters)
        else:
            return HasAny(*include_characters)
