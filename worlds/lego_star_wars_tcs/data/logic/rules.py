import dataclasses
from typing import ClassVar, Iterable, TYPE_CHECKING
from typing_extensions import override

from BaseClasses import CollectionState
from rule_builder.rules import Rule, TWorld, True_, OptionFilter, Filtered, HasAny, Has, HasFromListUnique, HasAll
from rule_builder.field_resolvers import FieldResolver, resolve_field

from ...character_ability import CharacterAbility
from ...constants import GAME_NAME
from ...items import CHARACTERS_AND_VEHICLES_BY_NAME
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
    """A rule that checks if the player has any character with all the given abilities.

    This is an expensive, but rarely used rule for cases where it is not worth defining a new ability just for this
    case."""
    abilities: CharacterAbility | FieldResolver

    @override
    def _instantiate(self, world: TWorld) -> Rule.Resolved:
        abilities = resolve_field(self.abilities, world, CharacterAbility)

        return self._make_rule(abilities).resolve(world)

    @staticmethod
    def _make_rule(abilities: CharacterAbility) -> Rule:
        # Remove abilities implied by another ability that is requested.
        # e.g. (JEDI | CAN_MELEE) can be reduced to just (JEDI)
        simplified = abilities.simplify_combination()
        if simplified.bit_count() == 1:
            return HasAbility(simplified)

        common_abilities = ~CharacterAbility.NONE
        matching_characters = []
        for character in CHARACTERS_AND_VEHICLES_BY_NAME.values():
            # "Super Gonk Droid" is a collect override when "Gonk Droid" and "Super Gonk" are both collected.
            if ((not character.is_sendable and character.name != "Super Gonk Droid")
                    or simplified not in character.abilities):
                continue
            matching_characters.append(character)
            common_abilities &= character.abilities

        if len(matching_characters) >= 8:
            # If there are lots of characters that match this, check for having all the required abilities first
            # because that is a faster check.
            return HasAllAbilities(common_abilities) & HasAny(*matching_characters)
        else:
            return HasAny(*matching_characters)


@dataclasses.dataclass
class HasAbilitiesExceptCharacters(Rule[LegoStarWarsTCSWorld], game=GAME_NAME):
    """A rule that checks if the player has any character with the given ability, except the given characters.

    This is an expensive, but rarely used rule for cases where specific characters cannot use their abilities in
    specific cases, where adding a new CharacterAbility to represent this difference in ability is not worth it.
    """
    abilities: CharacterAbility | FieldResolver
    """The abilities to check for."""

    except_characters: Iterable[str] | FieldResolver
    """The characters excluded from this rule."""

    def __init__(
            self,
            abilities: CharacterAbility | FieldResolver,
            *except_characters: str,
            options: Iterable[OptionFilter] = (),
            filtered_resolution: bool = False,
    ):
        super().__init__(options=options, filtered_resolution=filtered_resolution)
        self.abilities = abilities
        for character_name in except_characters:
            if character_name not in CHARACTERS_AND_VEHICLES_BY_NAME:
                raise Exception(f"Character '{character_name}' does not exist.")
        self.except_characters = set(except_characters)

    @override
    def _instantiate(self, world: TWorld) -> Rule.Resolved:
        abilities = resolve_field(self.abilities, world, CharacterAbility)
        except_characters = set(resolve_field(self.except_characters, world, Iterable))
        characters = [c.name for c in CHARACTERS_AND_VEHICLES_BY_NAME.values()
                      if abilities in c.abilities and c.name not in except_characters]
        # todo: Subclass HasAny.Resolved for a custom __str__, explain_str and explain_json
        return HasAny(*characters, options=self.options, filtered_resolution=self.filtered_resolution).resolve(world)
