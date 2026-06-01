from rule_builder.rules import And, Or, HasAny, False_, Has, True_

from ..macros import (
    CAN_DAMAGE_AT_CLOSE_RANGE,
    CAN_SITH_FORCE,
    CAN_ORIGINAL_TRILOGY_HIGH_JUMP,
    CAN_DESTROY_CLOSE_SILVER_BRICKS,
    CAN_GRAPPLE,
)
from ..option_filters import logic_options, OT_HIGH_JUMP_ENABLED, OT_HIGH_JUMP_DISABLED, ot_high_jump_ternary
from ..rules import HasAbility, HasAnyAbilities, HasAllAbilities, HasAbilityCombination, HasAbilityExceptCharacters
from ..types import minikit_data, ExitData, Chapter, LocationData, MinikitData

from ....character_ability import *


THROUGH_THE_JUNDLAND_WASTES = Chapter(
    name="Through The Jundland Wastes",
    episode_number=4,
    chapter_number=2,
    start_region="Spawn",
    start_level="tatooine_a",
    story_characters=(
        "Ben Kenobi",
        "C-3PO",
        "Luke Skywalker (Tatooine)",
        "R2-D2",
    ),
    purchase_characters={
        "Tusken Raider": 23_000,
        "Jawa": 24_000,
    },
    extra_toggle_characters=(
        "Womp Rat",
        "Droid 1",
        "Droid 2",
        "Droid 3",
        "Droid 4",
        "Skeleton",
    ),
    regions={
        "Spawn": (
            ExitData(
                "Across Gap",
                # `HasAbility(CAN_HIGH_JUMP_SLAM) & OT_HIGH_JUMP_ENABLED` can cross the entire gap, but this is not
                # logically relevant.
                Or(
                    CAN_DAMAGE_AT_CLOSE_RANGE & HasAbility(CAN_JUMP_HEIGHT_0_37),
                    CAN_ORIGINAL_TRILOGY_HIGH_JUMP,
                ),
            ),
            ExitData(
                "Silver Bricks Side Path Lower Before Silver Bricks",
                logic_options(
                    base=HasAbility(HOVER),
                    # Even without high jump enabled, Grievous and Bodyguard can make it with a triple jump.
                    moderate=HasAnyAbilities(HOVER | CAN_TRIPLE_JUMP_GREAT_DISTANCE),
                ),
            ),
        ),
        "Across Gap": (
            ExitData(
                "Behind Sith Force Doors",
                logic_options(
                    base=CAN_SITH_FORCE,
                    # Triple jump from the elevated area with the Access Hatch, and get over the top of the Sith Force
                    # doors. Yoda cannot get the required distance. Bodyguard can only get the required distance when
                    # high jump is enabled.
                    moderate=Or(
                        CAN_SITH_FORCE,
                        ot_high_jump_ternary(
                            uncapped=HasAnyAbilities(CAN_TRIPLE_JUMP_GREAT_DISTANCE | CAN_HIGH_JUMP_SLAM),
                            capped=HasAbility(CAN_TRIPLE_JUMP_GREAT_DISTANCE),
                        ),
                    ),
                ),
            ),
            ExitData(
                "Platform Above Tin Cans",
                logic_options(
                    base=False_(),
                    # Stand on destroyable objects or where the tin cans go, and high jump up.
                    normal=HasAbility(HIGH_JUMP) & OT_HIGH_JUMP_ENABLED,
                    # Triple jump up.
                    moderate=ot_high_jump_ternary(
                        uncapped=HasAnyAbilities(JEDI | HIGH_JUMP),
                        capped=HasAnyAbilities(JEDI | CAN_HIGH_JUMP_SLAM),
                    ),
                ),
            ),
            ExitData(
                "Silver Bricks Side Path Upper",
                logic_options(
                    # It's not immediately obvious that there is a slightly raised area on the right side, that can be
                    # used to high jump up to the upper area of the silver bricks side path, so using high jump here is
                    # requiring normal+ logic.
                    base=False_(),
                    normal=HasAbility(HIGH_JUMP) & OT_HIGH_JUMP_ENABLED,
                    # Triple jump up.
                    moderate=ot_high_jump_ternary(
                        uncapped=HasAnyAbilities(JEDI | HIGH_JUMP),
                        capped=HasAnyAbilities(JEDI | CAN_HIGH_JUMP_SLAM),
                    ),
                ),
            ),
            ExitData(
                "Sandcrawler Approach Before Quicksand",
                logic_options(
                    base=HasAbility(JEDI),
                    # High jump up is easier on the right side.
                    normal=HasAbility(JEDI) | CAN_ORIGINAL_TRILOGY_HIGH_JUMP,
                    # Allow triple jump when High Jump is capped.
                    moderate=ot_high_jump_ternary(
                        uncapped=HasAnyAbilities(JEDI | HIGH_JUMP),
                        capped=HasAnyAbilities(JEDI | CAN_HIGH_JUMP_SLAM),
                    ),
                ),
                new_level="tatooine_d",
            ),
        ),
        "Silver Bricks Side Path Lower Before Silver Bricks": (
            ExitData(
                "Silver Bricks Side Path Lower",
                logic_options(
                    base=CAN_DESTROY_CLOSE_SILVER_BRICKS,
                    # Allow triple jump, except yoda, as well as high jump when enabled.
                    moderate=Or(
                        CAN_DESTROY_CLOSE_SILVER_BRICKS,
                        ot_high_jump_ternary(
                            uncapped=HasAnyAbilities(CAN_TRIPLE_JUMP_GREAT_DISTANCE | HIGH_JUMP),
                            capped=HasAbility(CAN_TRIPLE_JUMP_GREAT_DISTANCE),
                        ),
                    ),
                    # Allow yoda, who has a harder time getting over the silver bricks due to his low movement speed and
                    # the top of the silver bricks being sloped. To get yoda over the silver bricks,
                    hard=Or(
                        CAN_DESTROY_CLOSE_SILVER_BRICKS,
                        ot_high_jump_ternary(
                            uncapped=HasAnyAbilities(JEDI | CAN_TRIPLE_JUMP_GREAT_DISTANCE | HIGH_JUMP),
                            capped=HasAnyAbilities(JEDI | CAN_TRIPLE_JUMP_GREAT_DISTANCE)
                        ),
                    ),
                    # From on top of the silver bricks, it's pretty easy to get onto the edge of the level/out-of-bounds
                    # on the left side. This can be used to get the access hatch minikit.
                ),
            ),
        ),
        "Behind Sith Force Doors": (),
        "Silver Bricks Side Path Lower": (
            ExitData(
                "Silver Bricks Side Path Upper",
                logic_options(
                    base=ot_high_jump_ternary(
                        uncapped=HasAnyAbilities(JEDI | HIGH_JUMP),
                        capped=HasAbility(JEDI),
                    ),
                    # Allow triple jump.
                    # Allow jetpack hover by starting from one of the destroyable objects for extra height, then hover
                    # up the left side. The right side also works, but seems slightly more difficult.
                    moderate=ot_high_jump_ternary(
                        uncapped=HasAnyAbilities(JEDI | HIGH_JUMP | JETPACK),
                        capped=HasAnyAbilities(JEDI | CAN_HIGH_JUMP_SLAM | JETPACK),
                    ),
                ),
            ),
        ),
        "Silver Bricks Side Path Upper": (
            # Drop down. I'm not sure if this is ever logically relevant.
            ExitData("Across Gap"),
            # Drop down.
            ExitData("Silver Bricks Side Path Lower"),
            ExitData(
                "Platform Above Tin Cans",
                logic_options(
                    base=HasAbility(HOVER),
                    # Allow triple jump.
                    moderate=ot_high_jump_ternary(
                        uncapped=HasAnyAbilities(HOVER | JEDI | CAN_HIGH_JUMP_SLAM),
                        # Yoda and Bodyguard can't make it (though they can just triple jump up to this platform from
                        # below).
                        capped=HasAnyAbilities(HOVER | CAN_TRIPLE_JUMP_GREAT_DISTANCE)
                    )
                ),
            ),
        ),
        "Platform Above Tin Cans": (),
        "Sandcrawler Approach Before Quicksand": (
            ExitData(
                "Sandcrawler Ground Level",
                logic_options(
                    # Hover across the quicksand.
                    # Build the object, push it into position and double jump to the platforms over the quicksand.
                    # High jump straight up to the platforms over the quicksand.
                    base=Or(
                        HasAnyAbilities(HOVER | JEDI) | CAN_ORIGINAL_TRILOGY_HIGH_JUMP,
                        HasAllAbilities(CAN_JUMP_0_44 | CAN_BUILD_BRICKS | CAN_PUSH_OBJECTS),
                    ),
                    # Hug the left side of the cliff, and double jump up to the second platform over the quicksand.
                    # Lower jump height can make it up too, but requires enough movement speed to prevent sliding down.
                    # Boba Fett (Boy) (run_speed=0.8) cannot make the jump.
                    # Clone (run_speed=1.0, jump_height=0.37) can make the jump.
                    normal=Or(
                        HasAnyAbilities(HOVER | CAN_DOUBLE_JUMP),
                        And(
                            HasAllAbilities(CAN_BUILD_BRICKS | CAN_PUSH_OBJECTS),
                            Or(
                                HasAbility(CAN_JUMP_0_44),
                                HasAbilityExceptCharacters(CAN_JUMP_HEIGHT_0_37, "Boba Fett (Boy)")
                                # HasAbilityCombination(CAN_JUMP_HEIGHT_0_37 | RUN_SPEED_1_18_OR_HIGHER),
                            )
                        )
                    ),
                ),
            ),
        ),
        "Sandcrawler Ground Level": (
            ExitData(
                "Top Of Sandcrawler",
                logic_options(
                    base=HasAllAbilities(JEDI | CAN_BUILD_BRICKS | CAN_PULL_LEVERS) & CAN_GRAPPLE,
                    # All forcing the first platform, stacking two boxes, then high jumping up to the first platform.
                    normal=And(
                        HasAllAbilities(JEDI | CAN_PULL_LEVERS),
                        Or(
                            HasAbility(CAN_BUILD_BRICKS) & CAN_GRAPPLE,
                            CAN_ORIGINAL_TRILOGY_HIGH_JUMP,
                        ),
                    ),
                    moderate=HasAllAbilities(JEDI | CAN_PULL_LEVERS),
                ),
            ),
            ExitData(
                "Sandcrawler Interior Start",
                logic_options(
                    base=False_(),
                    # Triple jump under the entrance, and you can hit the loading zone without needing to activate the
                    # suction effect.
                    moderate=HasAnyAbilities(JEDI | CAN_HIGH_JUMP_SLAM),
                ),
                new_level="tatooine_b",
            ),
        ),
        "Top Of Sandcrawler": (
            ExitData(
                "Sandcrawler Interior Start",
                HasAbility(CAN_PULL_LEVERS),
                new_level="tatooine_b",
            ),
        ),
        "Sandcrawler Interior Start": (
            ExitData(
                "Sandcrawler Elevator Room",
                HasAbility(JEDI),
            ),
        ),
        "Sandcrawler Elevator Room": (
            ExitData(
                "Sandcrawler Twin Switches Room",
                logic_options(
                    base=HasAbility(ASTROMECH_PANEL),
                    # Ceiling clip and jump into the loading zone.
                    hard=HasAbility(ASTROMECH_PANEL) | HasAny("Yoda", "Yoda (Ghost)"),
                ),
            ),
        ),
        "Sandcrawler Twin Switches Room": (
            ExitData(
                "Sandcrawler Caged Droids Room",
                HasAllAbilities(CAN_PULL_LEVERS | RUN_SPEED_0_9_OR_HIGHER),
            ),
            ExitData(
                "Sandcrawler Lava Flow",
                logic_options(
                    base=CAN_SITH_FORCE & HasAbility(SHORTIE),
                    hard=Or(
                        CAN_SITH_FORCE & HasAbility(SHORTIE),
                        # Ceiling clip over the fence.
                        HasAny("Yoda", "Yoda (Ghost)"),
                    ),
                ),
            ),
        ),
        "Sandcrawler Caged Droids Room": (
            ExitData(
                "Sandcrawler Enclosed Area After Lava Flow",
                logic_options(
                    base=False_(),
                    # Jump up onto the fence in this room, then hover across to the minikit.
                    # Triple jump is needed to get back.
                    # Note that the fence around the enclosed area with the minikit has collision that reaches the
                    # ceiling, so you must hover around to where there is no fence.
                    moderate=Or(
                        HasAbility(JETPACK),
                        HasAllAbilities(HOVER | CAN_JUMP_0_44),
                    ),
                ),
            ),
            ExitData(
                "Sandcrawler Exit Room",
                logic_options(
                    base=HasAbility(PROTOCOL_PANEL),
                    hard=Or(
                        HasAbility(PROTOCOL_PANEL),
                        # Ceiling clip over the door.
                        HasAny("Yoda", "Yoda (Ghost)"),
                    ),
                ),
            ),
        ),
        "Sandcrawler Lava Flow": (
            ExitData(
                "Sandcrawler Enclosed Area After Lava Flow",
                HasAllAbilities(JEDI | HOVER),
            ),
        ),
        "Sandcrawler Enclosed Area After Lava Flow": (),
        "Sandcrawler Exit Room": (
            ExitData(
                "Post-Sandcrawler Spawn",
                # Bizarrely, they can be shot, but not damaged by other sources.
                HasAnyAbilities(JEDI | BLASTER | WEAPON_EWOK),
                new_level="tatooine_c",
            ),
        ),
        "Post-Sandcrawler Spawn": (
            ExitData(
                "Bantha Oasis",
                logic_options(
                    base=Or(
                        CAN_SITH_FORCE,
                        CAN_ORIGINAL_TRILOGY_HIGH_JUMP,
                    ),
                    normal=Or(
                        CAN_SITH_FORCE,
                        CAN_ORIGINAL_TRILOGY_HIGH_JUMP,
                    ),
                    # Allow Triple jump.
                    # Allow jumping onto the left cliff edge and hovering across. The terrain is deliberately slippery
                    # to prevent Astromechs from getting across, but Jetpacks can jump first, and then hover, for
                    # slightly more distance.
                    moderate=Or(
                        HasAnyAbilities(JEDI | CAN_HIGH_JUMP_SLAM),
                        CAN_ORIGINAL_TRILOGY_HIGH_JUMP,
                        HasAllAbilities(JETPACK),
                    ),
                ),
            ),
            ExitData(
                "Post-Sandcrawler Elevated Grapple Area",
                logic_options(
                    base=Or(
                        # Build the grapple point, force the hook, then grapple up.
                        HasAllAbilities(CAN_BUILD_BRICKS | JEDI) & CAN_GRAPPLE,
                        # High jump directly up.
                        CAN_ORIGINAL_TRILOGY_HIGH_JUMP,
                    ),
                    # Allow triple jump.
                    moderate=HasAbility(JEDI) | CAN_ORIGINAL_TRILOGY_HIGH_JUMP
                ),
            ),
            ExitData(
                "After Quicksand Arch",
                # There is anti-hover triggers under the arch, preventing hovering over the quicksand.
                logic_options(
                    base=HasAbility(PROTOCOL_PANEL),
                    # Triple jump to the top right of the arch.
                    moderate=HasAnyAbilities(PROTOCOL_PANEL | JEDI | CAN_HIGH_JUMP_SLAM),
                ),
            ),
        ),
        "Bantha Oasis": (),
        "Post-Sandcrawler Elevated Grapple Area": (
            ExitData(
                "After Quicksand Arch",
                logic_options(
                    base=False_(),
                    # Hover to the top right of the arch.
                    normal=HasAbility(JETPACK),
                    # Astromech hover can just barely make it.
                    moderate=HasAbility(HOVER),
                ),
            ),
        ),
        "After Quicksand Arch": (
            ExitData(
                "Large Quicksand Pool",
                logic_options(
                    # Force the bones to make a bridge.
                    base=HasAbility(JEDI),
                    # Jetpack hover across.
                    # Yoda can also double jump across.
                    normal=HasAnyAbilities(JEDI | JETPACK),
                    moderate=HasAnyAbilities(JEDI | JETPACK | CAN_HIGH_JUMP_SLAM)
                ),
            ),
        ),
        "Large Quicksand Pool": (
            ExitData(
                "After Large Quicksand Pool",
                logic_options(
                    base=HasAllAbilities(CAN_JUMP_0_44 | CAN_PUSH_OBJECTS | PROTOCOL_PANEL | JEDI),
                    # You can hug the right wall to avoid dying in the quicksand. There is one part midway through that
                    # you must jump around, and a second part right at the end.
                    moderate=Or(
                        HasAbility(CAN_BARELY_JUMP),
                        HasAllAbilities(CAN_JUMP_0_44 | CAN_PUSH_OBJECTS | PROTOCOL_PANEL | JEDI)
                    ),
                ),
            ),
        ),
        "After Large Quicksand Pool": (
            ExitData("Before Sea Of Quicksand", new_level="tatooine_e"),
        ),
        "Before Sea Of Quicksand": (
            ExitData(
                "Across Sea Of Quicksand",
                logic_options(
                    # Fix the landspeeder and ride it across.
                    base=HasAllAbilities(CAN_BUILD_BRICKS | CAN_RIDE_VEHICLES),
                    # Grievous can triple jump across the entire quicksand sea.
                    moderate=Or(
                        HasAllAbilities(CAN_BUILD_BRICKS | CAN_RIDE_VEHICLES),
                        Has("General Grievous") & OT_HIGH_JUMP_ENABLED,
                    ),
                ),
            ),
        ),
        "Across Sea Of Quicksand": (
            ExitData(
                "Chapter Completion",
                HasAbility(CAN_PULL_LEVERS),
                new_level="tatooine_status",
            ),
        ),
    },
    minikits={
        "Sith Force Area Alcove Minikit": minikit_data(
            "Behind Sith Force Doors",
            logic_options(
                base=HasAbility(JEDI),
                # High jump can jump up on the right side where the minikit alcove is slightly lower.
                normal=ot_high_jump_ternary(
                    uncapped=HasAnyAbilities(JEDI | HIGH_JUMP),
                    capped=HasAbility(JEDI),
                ),
                moderate=ot_high_jump_ternary(
                    uncapped=HasAnyAbilities(JEDI | HIGH_JUMP),
                    capped=HasAnyAbilities(JEDI | CAN_HIGH_JUMP_SLAM),
                ),
            ),
            pickup_name="mk_1",
        ),
        "Access Hatch Minikit": minikit_data(
            "Across Gap",
            logic_options(
                base=Or(
                    HasAllAbilities(CAN_BUILD_BRICKS | HOVER) & CAN_GRAPPLE,
                    HasAbility(HIGH_JUMP) & OT_HIGH_JUMP_ENABLED,
                ),
                # Allow double jumping across with Yoda.
                normal=Or(
                    And(
                        HasAbility(CAN_BUILD_BRICKS) & CAN_GRAPPLE,
                        HasAbility(HOVER) | HasAny("Yoda", "Yoda (Ghost)"),
                    ),
                    HasAbility(HIGH_JUMP) & OT_HIGH_JUMP_ENABLED,
                ),
                # Allow triple jump.
                moderate=Or(
                    HasAllAbilities(CAN_BUILD_BRICKS | HOVER) & CAN_GRAPPLE,
                    HasAnyAbilities(JEDI | CAN_HIGH_JUMP_SLAM),
                    HasAbility(HIGH_JUMP) & OT_HIGH_JUMP_ENABLED,
                ),
            ).and_rule(HasAbility(SHORTIE)),
            pickup_name="mk_0",
        ),
        "Above Tin Cans Minikit": minikit_data(
            "Platform Above Tin Cans",
            pickup_name="mk_2",
        ),
        "Sandcrawler Exterior Access Hatch Minikit": minikit_data(
            "Top Of Sandcrawler",
            HasAllAbilities(CAN_PULL_LEVERS | SHORTIE) & CAN_DESTROY_CLOSE_SILVER_BRICKS,
            pickup_name="m_pup1",
        ),
        "Sandcrawler Elevator Room Minikit": minikit_data(
            "Sandcrawler Elevator Room",
            HasAllAbilities(CAN_PULL_LEVERS | CAN_PUSH_OBJECTS),
            pickup_name="mk_1",
        ),
        "Sandcrawler Lava Platform Minikit": minikit_data(
            "Sandcrawler Enclosed Area After Lava Flow",
            pickup_name="mk_0",
        ),
        "Bantha Oasis Minikit": minikit_data(
            "Bantha Oasis",
            logic_options(
                base=HasAbility(CAN_RIDE_VEHICLES),
                # Yoda can also magically grab this through the wall without needing to activate the buttons.
                # Droideka and Grievous also can with a character swap.
                moderate=Or(
                    HasAbility(CAN_RIDE_VEHICLES),
                    HasAny("Droideka", "General Grievous"),
                ),
            ),
            pickup_name="mk_0",
        ),
        "Grapple And Fight Tusken Raiders Minikit": minikit_data(
            "Post-Sandcrawler Elevated Grapple Area",
            pickup_name="mk_1",
        ),
        "Collapse The Column Minikit": minikit_data(
            "Large Quicksand Pool",
            logic_options(
                base=HasAllAbilities(HOVER | CAN_JUMP_0_44) | CAN_ORIGINAL_TRILOGY_HIGH_JUMP,
                # Allow triple jump.
                moderate=Or(
                    HasAnyAbilities(JEDI | CAN_HIGH_JUMP_SLAM),
                    HasAllAbilities(HOVER | CAN_JUMP_0_44),
                    CAN_ORIGINAL_TRILOGY_HIGH_JUMP,
                ),
            ),
            pickup_name="mk_2",
        ),
        "Minikit Far Out In Quicksand Sea": minikit_data(
            "Before Sea Of Quicksand",
            And(
                HasAllAbilities(CAN_BUILD_BRICKS | CAN_RIDE_VEHICLES),
                HasAbility(CAN_DOUBLE_JUMP) | CAN_GRAPPLE
            ),
            pickup_name="m_pup1",
        )
    },
    power_brick=LocationData(
        "Silver Bricks Side Path Lower",
        logic_options(
            base=ot_high_jump_ternary(
                uncapped=HasAllAbilities(JEDI | CAN_PUSH_OBJECTS) & HasAnyAbilities(HOVER | HIGH_JUMP),
                capped=HasAllAbilities(JEDI | HOVER | CAN_PUSH_OBJECTS),
            ),
            # Triple jump across the gap between the raised areas.
            # Even with OT High Jump enabled, regular high jump cannot get up to the first raised area where the force
            # blocks are, due to not getting enough jump distance.
            moderate=HasAbility(CAN_PUSH_OBJECTS) & HasAnyAbilities(JEDI | CAN_HIGH_JUMP_SLAM),
        ),
    ),
    ridables={
        "Bantha": LocationData("Spawn"),
        "Dewback": LocationData(
            "Across Sea Of Quicksand",
            logic_options(
                # Expect fighting the Stormtroopers
                base=CAN_DAMAGE_AT_CLOSE_RANGE,
                normal=True_(),
            ),
        ),
    },
)
