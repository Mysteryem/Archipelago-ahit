from rule_builder.rules import Has, HasAny, True_, Or, And
from rule_builder.options import OptionFilter

from .option_filters import normal_logic, logic_options
from .rules import HasAbility, HasAnyAbilities, HasAbilitiesExceptCharacters
from ...character_ability import *
from ...options import LogicExpectNonInfiniteTorpedoesPodRacer

# Implemented as a CharacterAbility for now.
# can_jetpack_hover = HasAny("Boba Fett", "Jango Fett")
CAN_USE_SELF_DESTRUCT = HasAbility(CAN_SELF_DESTRUCT) & Has("Self Destruct")
CAN_SUPER_EWOK_CATAPULT = HasAbility(WEAPON_EWOK) & Has("Super Ewok Catapult")


# All Sith are Jedi.
CAN_SITH_FORCE = logic_options(
    base=HasAbility(SITH),
    # Alternative because SITH implies JEDI:
    # normal=And(
    #     HasAbility(JEDI),
    #     HasAbility(SITH) | Has("Dark Side"),
    # )
    normal=Or(
        HasAbility(SITH),
        Has("Dark Side") & HasAbility(JEDI),
    )
)

CAN_DESTROY_CLOSE_SILVER_BRICKS = logic_options(
    base=HasAbility(BOUNTY_HUNTER),
    normal=Or(
        CAN_USE_SELF_DESTRUCT,
        Has("Exploding Blaster Bolts") & HasAnyAbilities(BLASTER | WEAPON_EWOK),
        Has("Super Ewok Catapult") & HasAbility(WEAPON_EWOK),
    ),
)

CAN_USE_DEFLECT_BOLTS = Or(
    HasAbility(CAN_DEFLECT_BOLTS),
    HasAbility(CAN_AGGRAVATE_ENEMIES) & Has("Deflect Bolts"),
)
CAN_SUPER_ZAP = HasAbility(WEAPON_ZAPPER) & Has("Super Zapper")
CAN_DAMAGE_AT_CLOSE_RANGE = logic_options(
    base=HasAnyAbilities(BLASTER | WEAPON_EWOK | CAN_MELEE),
    normal=Or(
        HasAnyAbilities(BLASTER | WEAPON_EWOK | CAN_MELEE),
        CAN_USE_SELF_DESTRUCT,
    ),
)
# can_fight_close_droids = logic_options(
#     base=CAN_DAMAGE_AT_CLOSE_RANGE,
#     normal=Or(
#         CAN_DAMAGE_AT_CLOSE_RANGE,
#         CAN_SUPER_ZAP,
#     ),
#     moderate=Or(
#         CAN_DAMAGE_AT_CLOSE_RANGE,
#         CAN_SUPER_ZAP,
#         CAN_USE_DEFLECT_BOLTS,
#     ),
# )
CAN_DAMAGE_SHIELDED_DROIDEKA = logic_options(
    # Only expect slam attacks, Bounty Hunter thermal detonators, or Droideka bolts.
    base=Or(
        HasAnyAbilities(JEDI | BOUNTY_HUNTER | CAN_HIGH_JUMP_SLAM),
        Has("Droideka"),
    ),
    # Adds zappers and Extras.
    normal=Or(
        HasAnyAbilities(JEDI | BOUNTY_HUNTER | CAN_HIGH_JUMP_SLAM),
        Has("Droideka"),
        HasAbility(WEAPON_ZAPPER) & CAN_DAMAGE_AT_CLOSE_RANGE,
        CAN_SUPER_ZAP,
        Or(
            CAN_USE_SELF_DESTRUCT,
            Has("Exploding Blaster Bolts") & HasAnyAbilities(BLASTER | WEAPON_EWOK),
            Has("Super Ewok Catapult") & HasAbility(WEAPON_EWOK),
        )
    ),
    # Adds Deflect Bolts Extra.
    moderate=Or(
        HasAnyAbilities(JEDI | BOUNTY_HUNTER | CAN_HIGH_JUMP_SLAM),
        Has("Droideka"),
        HasAbility(WEAPON_ZAPPER) & CAN_DAMAGE_AT_CLOSE_RANGE,
        CAN_SUPER_ZAP,
        Or(
            CAN_USE_SELF_DESTRUCT,
            Has("Exploding Blaster Bolts") & HasAnyAbilities(BLASTER | WEAPON_EWOK),
            Has("Super Ewok Catapult") & HasAbility(WEAPON_EWOK),
            CAN_USE_DEFLECT_BOLTS,
        )
    ),
)
CAN_DESTROY_FAR_SILVER_BRICKS = Or(
    HasAbility(BOUNTY_HUNTER),
    HasAbility(BLASTER) & Has("Exploding Blaster Bolts"),
)
CAN_GRAPPLE = logic_options(
    base=HasAbility(GRAPPLE),
    normal=Or(
        HasAbility(GRAPPLE),
        HasAbility(JEDI) & Has("Force Grapple Leap")
    )
)
# Pre-optimised version of can_sith_force & can_grapple.
CAN_SITH_FORCE_AND_GRAPPLE = logic_options(
    base=CAN_SITH_FORCE & HasAbility(GRAPPLE),
    normal=CAN_SITH_FORCE & (HasAbility(GRAPPLE) | Has("Force Grapple Leap")),
)
CAN_FIGHT_OR_BYPASS_SKIPPABLE_DROIDEKA = Or(
    CAN_DAMAGE_SHIELDED_DROIDEKA,
    True_(options=normal_logic)
)

CAN_ACTIVATE_CLOSE_TARGET = logic_options(
    base=HasAbility(BLASTER),
    # Ewoks are awkward because they don't auto-target the targets.
    normal=HasAnyAbilities(BLASTER | WEAPON_EWOK),
    # Self Destruct works too, though this is probably not well known.
    moderate=Or(
        HasAnyAbilities(BLASTER | WEAPON_EWOK),
        CAN_USE_SELF_DESTRUCT,
    ),
)

# Either Infinite Torpedos [sic] is unlocked, or the player enabled gathering torpedoes within the level.
CAN_DESTROY_OBJECTS_WITH_POD_RACERS = (
        Has("Infinite Torpedos")
        | OptionFilter(LogicExpectNonInfiniteTorpedoesPodRacer, True)
)
CAN_SHOOT_ALLOW_TORPEDOES = HasAbility(VEHICLE_BLASTER) | CAN_DESTROY_OBJECTS_WITH_POD_RACERS

# Captain Tarpals' melee attacks are coded weird, and cannot destroy various objects in the game.
# TODO: Regular melee attacks and Gamorrean Guard could be similar?
CAN_ATTACK_UP_CLOSE_EXCEPT_TARPALS = (
    logic_options(
        base=Or(
            HasAnyAbilities(JEDI | CAN_HIGH_JUMP_SLAM | BLASTER | WEAPON_EWOK),
            HasAbilitiesExceptCharacters(CAN_MELEE, "Captain Tarpals"),
        ),
        # Allow Self Destruct.
        normal=Or(
            HasAnyAbilities(JEDI | CAN_HIGH_JUMP_SLAM | BLASTER | WEAPON_EWOK),
            CAN_USE_SELF_DESTRUCT,
            HasAbilitiesExceptCharacters(CAN_MELEE, "Captain Tarpals"),
        ),
    )
),
