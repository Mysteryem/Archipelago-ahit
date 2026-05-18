from rule_builder.rules import Has, HasAny, True_, Or, And

from .option_filters import normal_logic, logic_options
from .rules import HasAbility, HasAnyAbilities, HasAllAbilities
from ...character_ability import *

# Implemented as a CharacterAbility for now.
# can_jetpack_hover = HasAny("Boba Fett", "Jango Fett")
can_self_destruct = HasAbility(CAN_SELF_DESTRUCT) & Has("Self Destruct")


# All Sith are Jedi.
can_sith_force = And(
    HasAbility(JEDI),
    HasAbility(SITH) | Has("Dark Side"),
)
# Alternative:
# can_sith_force = Or(
#     HasAbility(SITH),
#     HasAbility(JEDI) & Has("Dark Side"),
# )
can_destroy_close_silver_bricks = Or(
    HasAbility(BOUNTY_HUNTER),
    Or(
        HasAbility(CAN_SELF_DESTRUCT) & Has("Self Destruct"),
        Has("Exploding Blaster Bolts") & HasAnyAbilities(BLASTER | WEAPON_EWOK),
        Has("Super Ewok Catapult") & HasAbility(WEAPON_EWOK),
    )
)
# Only expect Jedi, Bounty Hunter or Droideka.
base_can_damage_shielded_droideka = Or(
    HasAnyAbilities(JEDI | BOUNTY_HUNTER),
    Has("Droideka"),
)
can_damage_shielded_droideka = logic_options(
    base=base_can_damage_shielded_droideka,
    # Adds zappers and Extras.
    normal=Or(
        HasAnyAbilities(JEDI | BOUNTY_HUNTER),
        Has("Droideka"),
        HasAllAbilities(WEAPON_ZAPPER | CAN_ATTACK_UP_CLOSE),
        Or(
            HasAbility(CAN_SELF_DESTRUCT) & Has("Self Destruct"),
            Has("Exploding Blaster Bolts") & HasAnyAbilities(BLASTER | WEAPON_EWOK),
            Has("Super Ewok Catapult") & HasAbility(WEAPON_EWOK),
        )
    ),
    # Adds Deflect Bolts Extra.
    moderate=Or(
        HasAnyAbilities(JEDI | BOUNTY_HUNTER),
        Has("Droideka"),
        HasAllAbilities(WEAPON_ZAPPER | CAN_ATTACK_UP_CLOSE),
        Or(
            HasAbility(CAN_SELF_DESTRUCT) & Has("Self Destruct"),
            Has("Exploding Blaster Bolts") & HasAnyAbilities(BLASTER | WEAPON_EWOK),
            Has("Super Ewok Catapult") & HasAbility(WEAPON_EWOK),
            Has("Deflect Bolts"),
        )
    ),
)
can_destroy_far_silver_bricks = Or(
    HasAbility(BOUNTY_HUNTER),
    HasAbility(BLASTER) & Has("Exploding Blaster Bolts"),
)
can_grapple = Or(
    HasAbility(GRAPPLE),
    HasAbility(JEDI) & Has("Force Grapple Leap")
)
# Pre-optimised version of can_sith_force & can_grapple.
can_sith_force_and_grapple = can_sith_force & (HasAbility(GRAPPLE) | Has("Force Grapple Leap"))
can_fight_or_bypass_skippable_droideka = Or(
    can_damage_shielded_droideka,
    True_(options=normal_logic)
)
can_damage_at_close_range = Or(
    HasAbility(CAN_ATTACK_UP_CLOSE),
    can_self_destruct
)

can_activate_close_target = logic_options(
    base=HasAbility(BLASTER),
    normal=HasAnyAbilities(BLASTER | WEAPON_EWOK),
    moderate=Or(
        HasAnyAbilities(BLASTER | WEAPON_EWOK),
        can_self_destruct,
    ),
)
# can_triple_jump = (
#     HasAbility(JEDI)
# )
# can_triple_high_jump = (
#     HasAbility(CAN_HIGH_JUMP_SLAM)
# )
# Does not include Grievous' Bodyguard who has the height of a triple jump, but not the distance.
can_true_triple_jump = (
    Or(HasAbility(JEDI), Has("General Grievous"))
)
can_true_high_double_jump = (
    HasAny("Jar Jar Binks", "Captain Tarpals", "General Grievous")
)
# can_true_triple_high_jump = (
#     Has("General Grievous")
# )
