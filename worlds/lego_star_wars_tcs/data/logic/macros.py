from rule_builder.rules import Has, HasAny, True_, Or, And
from rule_builder.options import OptionFilter

from .option_filters import normal_logic, logic_options
from .rules import HasAbility, HasAnyAbilities, HasAbilitiesExceptCharacters
from ...character_ability import *
from ...options import LogicExpectNonInfiniteTorpedoesPodRacer

# Implemented as a CharacterAbility for now.
# can_jetpack_hover = HasAny("Boba Fett", "Jango Fett")
can_self_destruct = HasAbility(CAN_SELF_DESTRUCT) & Has("Self Destruct")
can_super_ewok_catapult = HasAbility(WEAPON_EWOK) & Has("Super Ewok Catapult")


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
        can_self_destruct,
        Has("Exploding Blaster Bolts") & HasAnyAbilities(BLASTER | WEAPON_EWOK),
        Has("Super Ewok Catapult") & HasAbility(WEAPON_EWOK),
    )
)
can_deflect_bolts = Or(
    HasAbility(CAN_DEFLECT_BOLTS),
    HasAbility(CAN_AGGRAVATE_ENEMIES) & Has("Deflect Bolts"),
)
can_super_zap = HasAbility(WEAPON_ZAPPER) & Has("Super Zapper")
base_can_damage_at_close_range = HasAnyAbilities(BLASTER | WEAPON_EWOK | CAN_MELEE)
can_damage_at_close_range = Or(
    HasAnyAbilities(BLASTER | WEAPON_EWOK | CAN_MELEE),
    can_self_destruct
)
can_damage_at_close_range = logic_options(
    base=HasAnyAbilities(BLASTER | WEAPON_EWOK | CAN_MELEE),
    normal=Or(
        HasAnyAbilities(BLASTER | WEAPON_EWOK | CAN_MELEE),
        can_self_destruct,
    ),
)
can_damage_shielded_droideka = logic_options(
    # Only expect slam attacks, Bounty Hunter thermal detonators, or Droideka bolts.
    base=Or(
        HasAnyAbilities(JEDI | BOUNTY_HUNTER | CAN_HIGH_JUMP_SLAM),
        Has("Droideka"),
    ),
    # Adds zappers and Extras.
    normal=Or(
        HasAnyAbilities(JEDI | BOUNTY_HUNTER | CAN_HIGH_JUMP_SLAM),
        Has("Droideka"),
        HasAbility(WEAPON_ZAPPER) & can_damage_at_close_range,
        can_super_zap,
        Or(
            can_self_destruct,
            Has("Exploding Blaster Bolts") & HasAnyAbilities(BLASTER | WEAPON_EWOK),
            Has("Super Ewok Catapult") & HasAbility(WEAPON_EWOK),
        )
    ),
    # Adds Deflect Bolts Extra.
    moderate=Or(
        HasAnyAbilities(JEDI | BOUNTY_HUNTER | CAN_HIGH_JUMP_SLAM),
        Has("Droideka"),
        HasAbility(WEAPON_ZAPPER) & can_damage_at_close_range,
        can_super_zap,
        Or(
            can_self_destruct,
            Has("Exploding Blaster Bolts") & HasAnyAbilities(BLASTER | WEAPON_EWOK),
            Has("Super Ewok Catapult") & HasAbility(WEAPON_EWOK),
            can_deflect_bolts,
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

can_activate_close_target = logic_options(
    base=HasAbility(BLASTER),
    # Ewoks are awkward because they don't auto-target the targets.
    normal=HasAnyAbilities(BLASTER | WEAPON_EWOK),
    # Self Destruct works too, though this is probably not well known.
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

# Either Infinite Torpedos [sic] is unlocked, or the player enabled gathering torpedoes within the level.
can_destroy_objects_with_pod_racers = (
        Has("Infinite Torpedos")
        | OptionFilter(LogicExpectNonInfiniteTorpedoesPodRacer, True)
)
can_shoot_allow_torpedoes = HasAbility(VEHICLE_BLASTER) | can_destroy_objects_with_pod_racers
