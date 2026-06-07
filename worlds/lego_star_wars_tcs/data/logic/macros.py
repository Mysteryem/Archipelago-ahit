from rule_builder.rules import HasAny, True_, Or, Rule, False_
from rule_builder.options import OptionFilter

from .option_filters import normal_logic, logic_options, OT_HIGH_JUMP_ENABLED
from .rules import HasAbility, HasAnyAbilities, HasAbilityExceptCharacters
from ..characters import Character
from ..extras import Extra
from ..items.character_items import NON_VEHICLE_CHARACTER_TO_ITEM_DATA
from ...character_ability import *
from ...items import SORTED_SINGLE_JUMP_DISTANCE_TO_CHARACTER_NAMES
from ...options import LogicExpectNonInfiniteTorpedoesPodRacer

# Implemented as a CharacterAbility for now.
# can_jetpack_hover = Character.has_any(Character.BOBA_FETT, Character.JANGO_FETT)
CAN_USE_SELF_DESTRUCT = logic_options(
    base=False_(),
    normal=HasAbility(CAN_SELF_DESTRUCT) & Extra.SELF_DESTRUCT.has(),
)
CAN_SUPER_EWOK_CATAPULT = logic_options(
    base=False_(),
    normal=HasAbility(WEAPON_EWOK) & Extra.SUPER_EWOK_CATAPULT.has()
)

HAS_FLUTTER_CHARACTER = Character.has_any(Character.GEONOSIAN, Character.WATTO)


# FIXME: Jump Distance needs to be a custom rule so that Extra Toggle rules can correctly adjust it if an Extra Toggle
#  character has the requested jump distance.
def can_jump_distance_rule(distance_or_character: float | Character) -> Rule:
    distance: float
    if isinstance(distance_or_character, Character):
        distance = NON_VEHICLE_CHARACTER_TO_ITEM_DATA[distance_or_character].single_jump_distance
    else:
        distance = distance_or_character

    if distance <= 0:
        raise ValueError(f"Tried to create rule for distance less than or equal to zero. This does not make sens.")

    if distance <= NON_VEHICLE_CHARACTER_TO_ITEM_DATA[Character.BOBA_FETT_BOY].single_jump_distance:
        return HasAbility(CAN_BARELY_JUMP)
    if distance <= 0.69:
        base_ability = CAN_JUMP_DISTANCE_0_69
        max_distance_exclusive = 0.69
    elif distance <= 0.84:
        base_ability = CAN_JUMP_DISTANCE_0_84
        max_distance_exclusive = 0.84
    elif distance <= 0.92:
        base_ability = CAN_JUMP_DISTANCE_0_92
        max_distance_exclusive = 0.92
    else:
        raise ValueError(f"Tried to create rule for distance greater than 0.92, but the furthest regular single-jump is"
                         f" 0.92. Use ")

    all_character_names = []
    for jump_distance, character_names in SORTED_SINGLE_JUMP_DISTANCE_TO_CHARACTER_NAMES.items():
        if jump_distance >= max_distance_exclusive:
            # The `base_ability` covers all other characters that can jump this distance.
            break
        if jump_distance >= distance:
            all_character_names.extend(character_names)

    if all_character_names:
        return HasAbility(base_ability) | HasAny(*all_character_names)
    else:
        return HasAbility(base_ability)


# No rule is defined for being able to jump at least as far as Boba Fett (Boy) (0.56) because he is the only character
# with that jump distance, and has the worst jump distance.
CAN_JUMP_DISTANCE_0_56_BOBA_BOY_PLUS = HasAbility(CAN_BARELY_JUMP)
CAN_JUMP_DISTANCE_0_7_CLONE_PLUS = can_jump_distance_rule(Character.CLONE)
CAN_JUMP_DISTANCE_0_77_DEXTER_PLUS = can_jump_distance_rule(Character.DEXTER_JETTSTER)
CAN_JUMP_DISTANCE_0_904_LANDO_PLUS = can_jump_distance_rule(Character.LANDO_CALRISSIAN)


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
        Extra.DARK_SIDE.has() & HasAbility(JEDI),
    )
)

CAN_DESTROY_CLOSE_SILVER_BRICKS = logic_options(
    base=HasAbility(BOUNTY_HUNTER),
    normal=Or(
        CAN_USE_SELF_DESTRUCT,
        Extra.EXPLODING_BLASTER_BOLTS.has() & HasAnyAbilities(BLASTER | WEAPON_EWOK),
        Extra.SUPER_EWOK_CATAPULT.has() & HasAbility(WEAPON_EWOK),
    ),
)

CAN_USE_DEFLECT_BOLTS = Or(
    HasAbility(CAN_DEFLECT_BOLTS),
    HasAbility(CAN_AGGRAVATE_ENEMIES) & Extra.DEFLECT_BOLTS.has(),
)
CAN_SUPER_ZAP = HasAbility(WEAPON_ZAPPER) & Extra.SUPER_ZAPPER.has()
CAN_DAMAGE_AT_CLOSE_RANGE = logic_options(
    base=HasAnyAbilities(BLASTER | WEAPON_EWOK | CAN_MELEE),
    normal=Or(
        HasAnyAbilities(BLASTER | WEAPON_EWOK | CAN_MELEE),
        CAN_USE_SELF_DESTRUCT,
    ),
)
CAN_DAMAGE_AT_CLOSE_RANGE_NO_SELF_DESTRUCT = CAN_DAMAGE_AT_CLOSE_RANGE.base

# Some objects can only be destroyed by melee attacks that count as 'combo' attacks.
CAN_DAMAGE_AT_CLOSE_RANGE_NO_BASIC_MELEE = logic_options(
    base=HasAnyAbilities(BLASTER | WEAPON_EWOK | JEDI | CAN_HIGH_JUMP_SLAM) | Character.IMPERIAL_GUARD.has(),
    normal=Or(
        HasAnyAbilities(BLASTER | WEAPON_EWOK | JEDI | CAN_HIGH_JUMP_SLAM),
        Character.IMPERIAL_GUARD.has(),
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
        Character.DROIDEKA.has(),
    ),
    # Adds zappers and Extras.
    normal=Or(
        HasAnyAbilities(JEDI | BOUNTY_HUNTER | CAN_HIGH_JUMP_SLAM),
        Character.DROIDEKA.has(),
        HasAbility(WEAPON_ZAPPER) & CAN_DAMAGE_AT_CLOSE_RANGE,
        CAN_SUPER_ZAP,
        Or(
            CAN_USE_SELF_DESTRUCT,
            Extra.EXPLODING_BLASTER_BOLTS.has() & HasAnyAbilities(BLASTER | WEAPON_EWOK),
            Extra.SUPER_EWOK_CATAPULT.has() & HasAbility(WEAPON_EWOK),
        )
    ),
    # Adds Deflect Bolts Extra.
    moderate=Or(
        HasAnyAbilities(JEDI | BOUNTY_HUNTER | CAN_HIGH_JUMP_SLAM),
        Character.DROIDEKA.has(),
        HasAbility(WEAPON_ZAPPER) & CAN_DAMAGE_AT_CLOSE_RANGE,
        CAN_SUPER_ZAP,
        Or(
            CAN_USE_SELF_DESTRUCT,
            Extra.EXPLODING_BLASTER_BOLTS.has() & HasAnyAbilities(BLASTER | WEAPON_EWOK),
            Extra.SUPER_EWOK_CATAPULT.has() & HasAbility(WEAPON_EWOK),
            CAN_USE_DEFLECT_BOLTS,
        )
    ),
)
CAN_DESTROY_FAR_SILVER_BRICKS = logic_options(
    base=HasAbility(BOUNTY_HUNTER),
    normal=Or(
        HasAbility(BOUNTY_HUNTER),
        HasAbility(BLASTER) & Extra.EXPLODING_BLASTER_BOLTS.has(),
    ),
),
CAN_GRAPPLE = logic_options(
    base=HasAbility(GRAPPLE),
    normal=Or(
        HasAbility(GRAPPLE),
        HasAbility(JEDI) & Extra.FORCE_GRAPPLE_LEAP.has()
    )
)
# Pre-optimised version of can_sith_force & can_grapple.
CAN_SITH_FORCE_AND_GRAPPLE = logic_options(
    base=CAN_SITH_FORCE & HasAbility(GRAPPLE),
    normal=CAN_SITH_FORCE & (HasAbility(GRAPPLE) | Extra.FORCE_GRAPPLE_LEAP.has()),
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
        Extra.INFINITE_TORPEDOS.has()
        | OptionFilter(LogicExpectNonInfiniteTorpedoesPodRacer, True)
)
CAN_SHOOT_ALLOW_TORPEDOES = HasAbility(VEHICLE_BLASTER) | CAN_DESTROY_OBJECTS_WITH_POD_RACERS

# Captain Tarpals' melee attacks are coded weird, and cannot destroy various objects in the game.
# TODO: Regular melee attacks and Gamorrean Guard could be similar?
CAN_ATTACK_UP_CLOSE_EXCEPT_TARPALS = (
    logic_options(
        base=Or(
            HasAnyAbilities(JEDI | CAN_HIGH_JUMP_SLAM | BLASTER | WEAPON_EWOK),
            HasAbilityExceptCharacters(CAN_MELEE, Character.CAPTAIN_TARPALS),
        ),
        # Allow Self Destruct.
        normal=Or(
            HasAnyAbilities(JEDI | CAN_HIGH_JUMP_SLAM | BLASTER | WEAPON_EWOK),
            CAN_USE_SELF_DESTRUCT,
            HasAbilityExceptCharacters(CAN_MELEE, Character.CAPTAIN_TARPALS),
        ),
    )
),

CAN_ORIGINAL_TRILOGY_HIGH_JUMP = HasAbility(HIGH_JUMP) & OT_HIGH_JUMP_ENABLED

CAN_USE_BOUNTY_HUNTER_ROCKETS = logic_options(
    base=False_(),
    normal=HasAbility(JETPACK) & Extra.BOUNTY_HUNTER_ROCKETS.has(),
)

NORMAL_PLUS = logic_options(
    base=False_(),
    normal=True_(),
)

MODERATE_PLUS = logic_options(
    base=False_(),
    moderate=True_(),
)

HARD_PLUS = logic_options(
    base=False_(),
    hard=True_(),
)