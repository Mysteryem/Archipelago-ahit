from rule_builder.rules import True_, Or, False_, CanReachRegion, And, Has, HasAll

from ..macros import (
    CAN_DESTROY_CLOSE_SILVER_BRICKS as BASE_CAN_DESTROY_CLOSE_SILVER_BRICKS,
    CAN_DAMAGE_AT_CLOSE_RANGE as BASE_CAN_DAMAGE_AT_CLOSE_RANGE,
    CAN_USE_SELF_DESTRUCT as BASE_CAN_USE_SELF_DESTRUCT,
    can_jump_distance_rule,
)
from ..option_filters import logic_options
from ..rules import HasAbility, HasAnyAbilities, HasAllAbilities, HasAbilityCombination
from ..types import minikit_data, ExitData, Chapter, LocationData

from ....character_ability import *


# This could be optimised better, but I want to use the original BASE_CAN_USE_SELF_DESTRUCT in the rule.
CAN_USE_SELF_DESTRUCT = BASE_CAN_USE_SELF_DESTRUCT | HasAll("Self Destruct", "Extra Toggle")

CAN_DESTROY_CLOSE_SILVER_BRICKS = BASE_CAN_DESTROY_CLOSE_SILVER_BRICKS.or_rule(
    # Buzz Droid can explode.
    HasAll("Extra Toggle", "Self Destruct"),
    apply_to="normal+",
)
CAN_DAMAGE_AT_CLOSE_RANGE = BASE_CAN_DAMAGE_AT_CLOSE_RANGE.or_rule(
    Has("Extra Toggle"), apply_to="normal+"
)

CAN_MELEE_MACRO = logic_options(
    base=HasAbility(CAN_MELEE),
    normal=HasAbility(CAN_MELEE) | Has("Extra Toggle"),
)


# To complete the chapter, 3 sets of explosives need to be destroyed in a row.
# The logic for these explosives could be implemented using events, however, if 3-3 is the starting chapter, having a
# chain of events at the start like this could cause progression balancing to apply too strongly, so the logic is
# chained together using CanReach rules instead.

CAN_HURT_GRIEVOUS = logic_options(
    # Only consider melee attackers because other attacks are awkward.
    base=CAN_MELEE_MACRO,
    # Non-melee is awkward.
    # Grievous tends to bug out when using Exploding Blaster Bolts, so don't have the logic expect it.
    # todo: See if the client can fix this by either ending the level manually, or by giving Grievous +1 health when
    #  he's alive with zero health.
    # normal=Or(
    #     CAN_MELEE_MACRO,
    #     CAN_DESTROY_CLOSE_SILVER_BRICKS,
    # ),
    # Allow Blasters/Ewoks/Self Destruct.
    moderate=CAN_DAMAGE_AT_CLOSE_RANGE,
)

# The first explosives are not active until you hurt Grievous.
CAN_EXPLODE_FIRST_EXPLOSIVES = CAN_HURT_GRIEVOUS.and_rule(
    logic_options(
        # Shoot them from the spawn region.
        base=HasAbility(BLASTER),
        normal=Or(
            HasAllAbilities(JEDI | BLASTER),
            # If you walk up to Grievous, the explosives explode.
            CanReachRegion("General Grievous - First Explosives Section"),
        )
    )
)

# To shoot the first explosives from "Shoot Second Explosives Section" requires shooting the first explosives so that a
# force platform spawns that a blaster character can stand on and jump to be able to shoot the second explosives.
# The second explosive do NOT require the first explosives to be destroyed.
CAN_EXPLODE_SECOND_EXPLOSIVES = logic_options(
    # In base logic, exploding the first explosives and shooting the second explosives is expected.
    base=And(
        CAN_EXPLODE_FIRST_EXPLOSIVES,
        HasAbility(JEDI),
        HasAbilityCombination(BLASTER | CAN_JUMP_HEIGHT_0_37),
        CanReachRegion("General Grievous - Shoot Second Explosives Section"),
    ),
    normal=(
        And(
            CAN_EXPLODE_FIRST_EXPLOSIVES,
            Or(
                # If you walk up to Grievous the second explosives explode.
                CanReachRegion("General Grievous - Force Third Explosives Section"),
                And(
                    HasAbilityCombination(BLASTER | CAN_JUMP_HEIGHT_0_37),
                    CanReachRegion("General Grievous - Shoot Second Explosives Section"),
                ),
            ),
        ),
    ),
    moderate=Or(
        # Walking up the second explosives makes them explode even if the first explosives have not been destroyed and
        # Grievous is not at the second explosives yet. I am considering this a glitch, so skipping the first explosives
        # is requiring moderate logic.
        CanReachRegion("General Grievous - Force Third Explosives Section"),
        And(
            HasAbilityCombination(BLASTER | CAN_JUMP_HEIGHT_0_37),
            CanReachRegion("General Grievous - Shoot Second Explosives Section"),
        ),
    ),
)

CAN_EXPLODE_FIRST_TWO_EXPLOSIVES = CAN_EXPLODE_SECOND_EXPLOSIVES.and_rule(
    # Moderate+ logic can explode the second explosives without exploding the first explosives.
    CAN_EXPLODE_FIRST_EXPLOSIVES, apply_to="moderate+"
)

# The last explosives are not active until the first and second explosives have been exploded.
CAN_EXPLODE_LAST_EXPLOSIVES = logic_options(
    # Destroy the wall, force the explosive into position, then shoot it.
    base=HasAllAbilities(JEDI | BLASTER) & CanReachRegion("General Grievous - Force Third Explosives Section"),
    normal=And(
        HasAbility(JEDI) & CanReachRegion("General Grievous - Force Third Explosives Section"),
        Or(
            HasAbility(BLASTER),
            # Walking up to Grievous also makes the explosives explode instead of needing to shoot them.
            CanReachRegion("General Grievous - Third Explosives Cliff")
        ),
    ),
).and_rule(
    # Require the first two explosives rules for each logic difficulty.
    CAN_EXPLODE_FIRST_TWO_EXPLOSIVES
)

# CAN_MELEE_BRICKS_BLOCKING_ALCOVE_MINIKIT = logic_options(
#     # Only expect shooting.
#     base=False_(),
#     # Yoda can melee this, but tends to die.
#     moderate=HasAnyAbilities(JEDI | CAN_HIGH_JUMP_SLAM),
# )


GENERAL_GRIEVOUS = Chapter(
    name="General Grievous",
    episode_number=3,
    chapter_number=3,
    start_region="Circular Platform",
    start_level="grievous_a",
    story_characters=(
        "Commander Cody",
        "Obi-Wan Kenobi (Episode III)",
    ),
    purchase_characters={
        "General Grievous": 70_000,
    },
    extra_toggle_characters=(
        "Buzz Droid",
    ),
    regions={
        "Circular Platform": (
            ExitData(
                "Far Left Silver Brick Section",
                logic_options(
                    base=HasAbility(HOVER),
                    # Yoda cannot make it, but Grievous' Bodyguard can.
                    moderate=HasAnyAbilities(HOVER | CAN_TRIPLE_JUMP_GREAT_DISTANCE | CAN_HIGH_JUMP_SLAM),
                ),
            ),
            ExitData(
                "First Explosives Section",
                logic_options(
                    base=Or(
                        HasAbility(HOVER),
                        # Fight Grievous, then shoot the explosives, and then force to make the bridge.
                        HasAllAbilities(BLASTER | JEDI),
                    ),
                    moderate=HasAnyAbilities(HOVER | CAN_TRIPLE_JUMP_GREAT_DISTANCE),
                ),
            ),
            ExitData(
                "Low Platform With Power Up",
                logic_options(
                    base=HasAbility(CAN_JUMP_DISTANCE_0_69),
                    moderate=HasAbility(CAN_BARELY_JUMP),
                ),
                er_rule=logic_options(
                    # Ewok (jump_distance>=0.69) can make it across fairly easily jumping across the left/middle of the
                    # gap.
                    base=can_jump_distance_rule("Ewok"),
                    # Boba Fett (Boy) (jump_distance>=0.56) can only barely make it by jumping across the shortest
                    # distance between the platforms along the far left. Jumping immediately upon landing is probably
                    # required to prevent sliding off.
                    moderate=can_jump_distance_rule("Boba Fett (Boy)"),
                ),
            ),
            ExitData(
                "Third Explosives Section Gap Area",
                logic_options(
                    base=False_(),
                    # The collision on the plants by the wall is weird, you can jump on them and then double jump again.
                    moderate=HasAbility(CAN_DOUBLE_JUMP),
                )
            ),
            ExitData(
                "Far Right Low Platform",
                # Moderate logic can double jump to the middle platform and drop down to here instead, so the triple
                # jump across the gap is logically irrelevant.
                HasAbility(HOVER),
                er_rule=logic_options(
                    base=HasAbility(HOVER),
                    # Yoda cannot make it, but Grievous' Bodyguard can.
                    moderate=HasAnyAbilities(HOVER | CAN_TRIPLE_JUMP_GREAT_DISTANCE | CAN_HIGH_JUMP_SLAM)
                ),
            ),
            ExitData(
                "Chapter Completion",
                # Note: Contains a few CanReachRegion rules.
                CAN_EXPLODE_LAST_EXPLOSIVES,
                new_level="grievous_status",
            )
        ),
        "Far Left Silver Brick Section": (
            # The rule from "Circular Platform -> First Explosives Section" is the same as
            # "Circular Platform -> Far Left Silver Brick Section", so if you can get to
            # "Far Left Silver Brick Section", you can also get to "First Explosives Section".
            # ExitData(
            #     "First Explosives Section",
            #     logic_options(
            #         base=HasAbility(HOVER),
            #         # Yoda cannot make the jump with a triple jump, but can make the jump with a double jump instead.
            #         moderate=HasAnyAbilities(HOVER | JEDI | CAN_HIGH_JUMP_SLAM),
            #     ),
            # ),
        ),
        "First Explosives Section": (
            ExitData(
                "Shoot Second Explosives Section",
                logic_options(
                    base=HasAnyAbilities(GRAPPLE | CAN_DOUBLE_JUMP),
                    normal=HasAnyAbilities(GRAPPLE | CAN_DOUBLE_JUMP | CAN_JUMP_0_44),
                    moderate=Or(
                        HasAnyAbilities(GRAPPLE | CAN_DOUBLE_JUMP | CAN_JUMP_0_44),
                        # (movement speed/jump height/jump distance)
                        # Boba Fett (Boy) I don't think can make the second or third jumps (0.8/0.37/0.56)
                        #   Not enough movement speed to slide up the second jump that he doesn't have enough height for
                        #   and not enough movement speed to make it across the third jump.
                        # Geonosian cannot make any of the jumps (height) (1.5/0.3/'0.65')
                        # Clone struggles with all the jumps (distance and height) (1.0/0.37/0.7)
                        # Captain Panaka struggles with the second jump (getting height) (1.2/0.37/0.84)
                        # Ewok/Ugnaught struggle with the last jump (getting distance) (0.9/0.44/0.69)
                        # Gamorrean Guard struggles with the last jump (getting distance) (0.75/0.53/0.69)
                        HasAbilityCombination(CAN_JUMP_HEIGHT_0_37 | CAN_JUMP_DISTANCE_0_69),
                    ),
                ),
            ),
            ExitData(
                "Far Left Silver Brick Section",
                logic_options(
                    base=HasAbility(HOVER),
                    # Yoda cannot make the jump with a triple jump, but can make the jump with a double jump instead.
                    moderate=HasAnyAbilities(HOVER | JEDI | CAN_HIGH_JUMP_SLAM),
                )
            ),
        ),
        "Low Platform With Power Up": (
            ExitData(
                "Chapter Completion",
                logic_options(
                    base=False_(),
                    moderate=HasAbility(BLASTER),
                ),
                name="Grieve-Cheese",
                new_level="grievous_status",
            ),
            # Logically irrelevant because "Low Platform With Power Up -> Third Explosives Section Gap Area" only
            # requires high jump height, and then
            # "Third Explosives Section Gap Area -> Shoot Second Explosives Section" only requires CAN_DOUBLE_JUMP.
            # ExitData(
            #     "Shoot Second Explosives Section",
            #     logic_options(
            #         base=False_(),
            #         # Near max height triple jump needed.
            #         moderate=HasAnyAbilities(JEDI | CAN_HIGH_JUMP_SLAM),
            #     ),
            # ),
            ExitData(
                "Third Explosives Section Gap Area",
                logic_options(
                    base=HasAbility(HIGH_JUMP),
                    # Logically irrelevant because "Circular Platform -> Third Explosives Section Gap Area" with
                    # CAN_DOUBLE_JUMP.
                    moderate=False_(),
                ),
                er_rule=logic_options(
                    base=HasAbility(HIGH_JUMP),
                    # Triple jump or high jump.
                    moderate=HasAnyAbilities(JEDI | HIGH_JUMP),
                ),
            ),
        ),
        "Third Explosives Section Gap Area": (
            ExitData(
                "Shoot Second Explosives Section",
                logic_options(
                    # Expect going around the top instead.
                    base=False_(),
                    normal=HasAnyAbilities(CAN_DOUBLE_JUMP | JETPACK),
                ),
            ),
            ExitData(
                "Third Explosives Cliff",
                logic_options(
                    # Expect hovering across from "Shoot Second Explosives Section"
                    base=False_(),
                    normal=HasAbility(HIGH_JUMP),
                    moderate=HasAnyAbilities(JEDI | HIGH_JUMP),
                ),
            ),
            ExitData(
                "Force Third Explosives Section",
                logic_options(
                    base=HasAbility(GRAPPLE),
                    # You can get under the cliff a little bit for some extra height, enough to high jump up.
                    # Jedi can triple jump up, though a good amount of height is needed.
                    moderate=HasAnyAbilities(GRAPPLE | HIGH_JUMP | JEDI),
                )
            ),
            ExitData(
                "Bridge And Mines Building",
                logic_options(
                    base=HasAbility(HIGH_JUMP),
                    moderate=HasAnyAbilities(HIGH_JUMP | JEDI),
                )
            ),
            ExitData(
                "Brick Covered Minikit Alcove",
                logic_options(
                    base=HasAbility(CAN_DOUBLE_JUMP),
                    normal=HasAnyAbilities(CAN_DOUBLE_JUMP | JETPACK),
                    moderate=HasAnyAbilities(CAN_DOUBLE_JUMP | CAN_JUMP_0_44),
                )
            )
        ),
        "Far Right Low Platform": (
            ExitData(
                "Third Explosives Section Gap Area",
                # Jetpack Hover can also get here on moderate logic, but all JETPACK can GRAPPLE.
                HasAnyAbilities(GRAPPLE | CAN_DOUBLE_JUMP),
            ),
        ),
        "Shoot Second Explosives Section": (
            # Dropping down to "Low Platform With Power Up" is logically useless because being able to reach any upper
            # area to drop down from, can also use "Circular Platform -> Low Platform With Power Up".
            # ExitData(
            #     "Low Platform With Power Up"
            # ),
            ExitData(
                "Third Explosives Section Gap Area",
                logic_options(
                    # Expect going around the top or far right instead.
                    base=False_(),
                    normal=HasAnyAbilities(CAN_DOUBLE_JUMP | HOVER)
                ),
            ),
            ExitData(
                "Force Third Explosives Section",
                # Exploding the second explosives spawns bricks that can be forced into stairs.
                logic_options(
                    base=HasAbility(JEDI) & CAN_EXPLODE_SECOND_EXPLOSIVES,
                    normal=Or(
                        HasAbility(JEDI) & CAN_EXPLODE_SECOND_EXPLOSIVES,
                        HasAbility(HIGH_JUMP),
                    ),
                    # Triple jump or high jump up.
                    moderate=HasAnyAbilities(JEDI | HIGH_JUMP)
                ),
            ),
            ExitData(
                "Brick Covered Minikit Alcove",
                # Only covers getting to the alcove. Destroying the bricks in the way is covered by the minikit
                # location itself.
                logic_options(
                    # Only expect access from "Third Explosives Section Gap Area".
                    base=False_(),
                    normal=Or(
                        HasAnyAbilities(CAN_DOUBLE_JUMP | JETPACK),
                        # Astromech hover can make it, so long as the bricks from the second explosives have
                        # spawned so that there is enough starting height.
                        HasAbility(ASTROMECH_DROID) & CAN_EXPLODE_SECOND_EXPLOSIVES,
                    ),
                ),
            ),
        ),
        "Force Third Explosives Section": (
            # The base logic can be expected to drop down here instead of double jumping across the gap between
            # "Shoot Second Explosives Section" and "Third Explosives Section Gap Area".
            ExitData(
                "Third Explosives Section Gap Area",
                logic_options(
                    base=True_(),
                    # Entrance is logically irrelevant, so don't create it.
                    normal=False_(),
                ),
                er_rule=True_(),
            ),
            ExitData(
                "Third Explosives Cliff",
                logic_options(
                    base=HasAbility(HOVER),
                    moderate=HasAnyAbilities(HOVER | CAN_TRIPLE_JUMP_GREAT_DISTANCE),
                )
            ),
            ExitData(
                "Brick Covered Minikit Alcove",
                logic_options(
                    # Expect double jump from "Third Explosives Section Gap Area".
                    base=False_(),
                    # Getting into the alcove can be a pain/luck with some characters.
                    # While Gonk Droid might not be able to fall down into here (slides out due to low movement speed),
                    # I'm pretty sure all characters that can reach "Force Third Explosives Section" can get into the
                    # alcove.
                    moderate=True_(),
                )
            ),
        ),
        "Third Explosives Cliff": (
            ExitData(
                "Bridge And Mines Building",
                logic_options(
                    # Only expect hover because the cliff gets very thin and is technically not walkable; you slide off
                    # rather slowly.
                    base=HasAbility(HOVER),
                    # Hug the cliff between these two areas, and you won't fall down, unless you're Gonk Droid, but Gonk
                    # Droid can't get up here on its own to begin with.
                    normal=True_(),
                ),
            ),
        ),
        "Bridge And Mines Building": (
            ExitData(
                "Third Explosives Cliff",
                # If the player can get to "Bridge And Mines Building" without going through "Third Explosives Cliff",
                # then they already have the necessary jump height to go from the bridge to the slightly higher cliff
                # section.
                logic_options(
                    base=HasAbility(HOVER),
                    normal=True_(),
                ),
                er_rule=logic_options(
                    # Jump up and then only expect hover because the cliff gets very thin and is technically not
                    # walkable; you slide off rather slowly.
                    base=HasAllAbilities(HOVER & CAN_JUMP_0_44),
                    # Jump up and then hug the cliff between these two areas, so you won't fall down.
                    normal=HasAbility(CAN_JUMP_0_44),
                ),
            ),
        ),
        "Brick Covered Minikit Alcove": (),
    },
    minikits={
        "Minikit Behind Silver Brick Wall": minikit_data(
            "Far Left Silver Brick Section",
            logic_options(
                base=HasAbility(BOUNTY_HUNTER),
                normal=And(
                    CAN_DESTROY_CLOSE_SILVER_BRICKS,
                    HasAbility(CAN_JUMP_HEIGHT_0_37),
                ),
                moderate=Or(
                    # Triple jump over the silver brick wall.
                    # The devs made the collision box come forwards at the top, but didn't make it high enough, so
                    # making the collision box come forwards actually helps here.
                    # Triple high jump can get enough height from next to the silver brick wall, whereas Jedi need to
                    # move back a bit from the wall, to the slightly higher area, otherwise they do not get enough
                    # height.
                    HasAnyAbilities(JEDI | CAN_HIGH_JUMP_SLAM),
                    And(
                        CAN_DESTROY_CLOSE_SILVER_BRICKS,
                        # Astromech droids can also make it up with their hover.
                        HasAnyAbilities(CAN_JUMP_HEIGHT_0_37 | ASTROMECH_DROID),
                    ),
                ),
            ),
            er_rule=logic_options(
                base=CAN_DESTROY_CLOSE_SILVER_BRICKS & HasAbility(CAN_JUMP_HEIGHT_0_37),
                moderate=Or(
                    # Triple jump over the silver brick wall.
                    # The devs made the collision box come forwards at the top, but didn't make it high enough, so
                    # making the collision box come forwards actually helps here.
                    # Triple high jump can get enough height from next to the silver brick wall, whereas Jedi need to
                    # move back a bit from the wall, to the slightly higher area, otherwise they do not get enough
                    # height.
                    HasAnyAbilities(JEDI | CAN_HIGH_JUMP_SLAM),
                    And(
                        CAN_DESTROY_CLOSE_SILVER_BRICKS,
                        # Astromech droids can also make it up with their hover.
                        HasAnyAbilities(CAN_JUMP_HEIGHT_0_37 | ASTROMECH_DROID),
                    ),
                ),
            ),
            pickup_name="m_pup3",
        ),
        "Force Platforms High Minikit": minikit_data(
            "First Explosives Section",
            logic_options(
                # Fight Grievous and explode the first explosives, then force the platforms and double jump up.
                base=HasAbility(JEDI),
                # Triple high jump to skip forcing the platforms.
                moderate=HasAnyAbilities(JEDI | CAN_HIGH_JUMP_SLAM),
            ),
            pickup_name="m_pup4",
        ),
        "Minikit On Platform With Power Up": minikit_data(
            "Low Platform With Power Up",
            pickup_name="mk_1",
        ),
        "Brick Covered Minikit Alcove": minikit_data(
            "Brick Covered Minikit Alcove",
            # The logic for destroying the bricks is defined here.
            # BLASTER works from all regions that can reach here.
            # Self Destruct also works from all regions that can reach here, but is not always expected.
            logic_options(
                base=HasAbility(BLASTER),
                normal=Or(
                    # Ewoks work too.
                    HasAnyAbilities(BLASTER | WEAPON_EWOK),
                    And(
                        # "Force Third Explosives Section" also works for slam/explode, but if the player can reach
                        # there, they can also reach Third Explosives Section Gap Area
                        CanReachRegion("General Grievous - Third Explosives Section Gap Area"),
                        Or(
                            # Slam next to the bricks.
                            HasAnyAbilities(JEDI | CAN_HIGH_JUMP_SLAM),
                            # Explode next to the bricks.
                            CAN_USE_SELF_DESTRUCT,
                        ),
                    ),
                ),
                moderate=Or(
                    HasAnyAbilities(BLASTER | WEAPON_EWOK),
                    # Exploding also works from "General Grievous - Shoot Second Explosives Section".
                    CAN_USE_SELF_DESTRUCT,
                    And(
                        CanReachRegion("General Grievous - Third Explosives Section Gap Area"),
                        HasAnyAbilities(JEDI | CAN_HIGH_JUMP_SLAM),
                    ),
                ),
            ),
            pickup_name="mk_0"
        ),
        "Force Third Explosives Minikit": minikit_data(
            "Force Third Explosives Section",
            # The minikit spawns when the explosives are forced into position.
            # The explosives cannot be forced until the first and second explosives have been destroyed and Grievous has
            # jumped up to "Third Explosives Cliff".
            # Mostly copied from CAN_EXPLODE_LAST_EXPLOSIVES, but BLASTER is not needed because the explosives do not
            # need to be destroyed to spawn the minikit.
            CAN_EXPLODE_FIRST_TWO_EXPLOSIVES.and_rule(HasAbility(JEDI)),
            pickup_name="m_pup6",
        ),
        "High Minikit Above Third Explosives": minikit_data(
            "Force Third Explosives Section",
            logic_options(
                base=HasAbility(HIGH_JUMP),
                normal=Or(
                    HasAbility(HIGH_JUMP),
                    And(
                        HasAbility(JEDI),
                        Or(
                            # Double Jump + Slam with Stud Magnet active can reach the minikit.
                            Has("Stud Magnet"),
                            # Force the third explosives partially out, then jump on top of them as they return, to get
                            # extra height, to then double jump to the minikit.
                            CAN_EXPLODE_FIRST_TWO_EXPLOSIVES,
                        ),
                    ),
                ),
                # Triple jump or high jump to the minikit.
                moderate=HasAnyAbilities(JEDI | HIGH_JUMP),
            ),
            pickup_name="m_pup5",
        ),
        "Grievous Last Cliff Minikit": minikit_data(
            "Third Explosives Cliff",
            pickup_name="m_pup7",
        ),
        "Far Right Low Platform Minikit": minikit_data(
            "Far Right Low Platform",
            pickup_name="m_pup8",
        ),
        "Bridge Minikit": minikit_data(
            "Bridge And Mines Building",
            pickup_name="m_pup9",
        ),
        "Destroy All Mines Minikit": minikit_data(
            "Bridge And Mines Building",
            logic_options(
                # Expect a ranged weapon.
                base=HasAnyAbilities(BLASTER | WEAPON_EWOK),
                # Let's hope you have a ranged weapon, Force Ghost or Invincibility, or that Death Link is disabled.
                # P2 can be baited into the mines to avoid dying yourself.
                normal=True_(),
            ),
            pickup_name="m_pup2",
        ),
    },
    power_brick=LocationData(
        "Bridge And Mines Building",
        HasAbility(JEDI),
    )
)
