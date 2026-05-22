from collections import defaultdict
from unittest import TestCase

from ..items import CHARACTERS_AND_VEHICLES_BY_NAME
from ..character_ability import CharacterAbility, IMPLIED_ABILITIES, ABILITY_REDUCTIONS

CHARACTERS = [c for c in CHARACTERS_AND_VEHICLES_BY_NAME.values() if c.is_sendable or c.name == "Super Gonk Droid"]


class TestAbilities(TestCase):
    implied_abilities_dict: dict[CharacterAbility, CharacterAbility]
    implied_by_abilities_dict: dict[CharacterAbility, CharacterAbility]
    ability_to_used_by: dict[CharacterAbility, frozenset[CharacterAbility]]
    unused_abilities: CharacterAbility

    @classmethod
    def setUpClass(cls):
        implied_dict: dict[CharacterAbility, CharacterAbility] = {ability: ~ability for ability in CharacterAbility}

        ability_to_used_by: dict[CharacterAbility, set[CharacterAbility]] = defaultdict(set)
        used_abilities = CharacterAbility.NONE
        for character in CHARACTERS:
            for ability in character.abilities:
                implied_dict[ability] &= character.abilities
                used_abilities |= character.abilities
                ability_to_used_by[ability].add(character.abilities)

        cls.ability_to_used_by = {k: frozenset(ability_to_used_by[k]) for k in CharacterAbility}
        cls.unused_abilities = ~used_abilities

        # The implied_dict relies on at least one character having the ability.
        for ability in cls.unused_abilities:
            implied_dict[ability] = CharacterAbility.NONE

        cls.implied_abilities_dict = implied_dict

        implied_by_dict: dict[CharacterAbility, CharacterAbility] = {
            ability: CharacterAbility.NONE for ability in CharacterAbility
        }
        for ability, implies in implied_dict.items():
            for implied in implies:
                implied_by_dict[implied] |= ability
        cls.implied_by_abilities_dict = implied_by_dict

    @classmethod
    def tearDownClass(cls):
        del cls.implied_abilities_dict

    def test_implied_abilities(self):
        failed = False
        for ability, implied in self.implied_abilities_dict.items():
            with self.subTest(ability.name):
                actual = IMPLIED_ABILITIES.get(ability, CharacterAbility.NONE)
                try:
                    self.assertEqual(implied, actual,
                                     f"Implied abilities for {ability!r} should be"
                                     f"\n\t{implied!r}\nbut were\n\t{actual!r}")
                except AssertionError:
                    failed = True
                    raise
        if failed:
            implied_abilities_lines = [
                "{",
                "    # All characters with this ability: Also have these abilities,",
                "    # HasAllAbilities(left | right) -> HasAbility(left)"
            ]
            for ability, implied in self.implied_abilities_dict.items():
                if implied is CharacterAbility.NONE:
                    implied_name = "CharacterAbility.NONE"
                else:
                    implied_name = implied.name
                    implied_name = implied_name.replace("|", " | ")
                implied_abilities_lines.append(f"    {ability.name}: {implied_name},")
            implied_abilities_lines.append("}")
            lines = "\n".join(implied_abilities_lines)
            self.fail(f"Implied abilities did not match. Expected implied abilities:\n{lines}")

    def test_circular_implications(self):
        for ability, implied in self.implied_abilities_dict.items():
            with self.subTest(ability.name):
                for implied_ability in implied:
                    self.assertNotIn(ability, self.implied_abilities_dict[implied_ability],
                                     f"Circular implication of {ability.name} and {implied_ability.name}")

    def test_no_unused_abilities(self):
        self.assertIs(self.unused_abilities, CharacterAbility.NONE)

    def test_pair_reductions(self):
        def abilities_tup_gen(to_gen_from: CharacterAbility, r_max: int):
            """
            itertools.combinations, but with pre-filtering for known bad cases.
            If A, B are pointless, then A, B, C won't be tried.
            """
            if r_max < 2:
                raise ValueError(f"r_max must be at least 2, but got {r_max}")
            tup_list = [(c, self.implied_abilities_dict[c]) for c in to_gen_from]

            def abilities_tup_gen_recur(
                    start_offset: int,
                    last_v: CharacterAbility,
                    last_v_implies: CharacterAbility,
                    recursion_depth_remaining: int):
                for i in range(start_offset, len(to_gen_from)):
                    v, v_implies = tup_list[i]
                    # Reduce the search space by skipping cases where one already seen abilities imply another ability.
                    # e.g. JEDI is implied_by SITH, so skip combinations involving SITH and JEDI.
                    if v in last_v_implies or (last_v & v_implies is not CharacterAbility.NONE):
                        continue
                    # PyCharm being dumb. The outermost parenthesis are required.
                    # noinspection PyRedundantParentheses
                    yield (combined := (last_v | v))
                    if recursion_depth_remaining > 0:
                        combined_implies = v_implies | last_v_implies
                        yield from abilities_tup_gen_recur(i + 1, combined, combined_implies,
                                                           recursion_depth_remaining - 1)

            yield from abilities_tup_gen_recur(0, CharacterAbility.NONE, CharacterAbility.NONE, r_max - 1)

        reductions: dict[CharacterAbility, CharacterAbility] = {}

        for ability_main, implied_by in self.implied_by_abilities_dict.items():
            relevant_abilities = implied_by

            # At least 2 abilities are needed for a reduction to be possible.
            if relevant_abilities.value.bit_count() < 2:
                continue

            # Do all characters with ability_main have either ability_a or ability_b?
            # Do all HAS_DOUBLE_JUMP characters have either JEDI or HIGH_JUMP? (yes)
            # Do all HAS_DOUBLE_JUMP characters have either JEDI or SITH? (no, there are HIGH_JUMP that are neither)
            # I honestly doubt anything above 3 (A | B | C -> D) will ever be used.
            r_max = min(relevant_abilities.value.bit_count() + 1, 5)
            # So many combinations can be reduced to the basic jump height abilities, and most of the combinations are
            # useless, so skip most combinations by reducing the max combination length.
            if ability_main in CharacterAbility.CAN_BARELY_JUMP | CharacterAbility.CAN_JUMP_NORMAL_HEIGHT:
                r_max = min(r_max, 2)
            for reduced_abilities in abilities_tup_gen(relevant_abilities, r_max):
                for user_of_ability_main in self.ability_to_used_by[ability_main]:
                    if not any(reduce_ability in user_of_ability_main for reduce_ability in reduced_abilities):
                        break
                else:
                    if relevant_abilities in reductions:
                        # If this happens, we'll need to figure something out.
                        raise AssertionError(f"Duplicate reduction for {reduced_abilities.name}."
                                             f" It reduces to both {reductions[reduced_abilities].name}"
                                             f" and {ability_main.name}")
                    reductions[reduced_abilities] = ability_main

        all_keys = set(reductions.keys()) | set(ABILITY_REDUCTIONS.keys())
        for key in sorted(all_keys):
            with self.subTest(key.name):
                calculated = reductions.get(key)
                defined = ABILITY_REDUCTIONS.get(key)
                self.assertEqual(calculated,
                                 defined,
                                 f"Failed to tell that {key.name} can be reduced to {calculated.name}"
                                 if calculated is not None
                                 else f"No reduction should be defined for {key.name}, but a reduction to"
                                      f" {defined.name} is defined.")

