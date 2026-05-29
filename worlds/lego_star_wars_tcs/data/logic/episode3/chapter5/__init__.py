from rule_builder.rules import True_, And, Has, Or, HasAny

from ...macros import (
    CAN_DESTROY_CLOSE_SILVER_BRICKS as BASE_CAN_DESTROY_CLOSE_SILVER_BRICKS,
    CAN_GRAPPLE,
    CAN_SITH_FORCE,
    CAN_DAMAGE_AT_CLOSE_RANGE as BASE_CAN_DAMAGE_AT_CLOSE_RANGE,
    CAN_JUMP_DISTANCE_0_77_DEXTER_PLUS,
)
from ...option_filters import logic_options
from ...rules import HasAbility, HasAnyAbilities, HasAllAbilities
from ...types import minikit_data, ExitData, Chapter, LocationData

from .....character_ability import *


CAN_DESTROY_CLOSE_SILVER_BRICKS = BASE_CAN_DESTROY_CLOSE_SILVER_BRICKS.or_rule(
    # Use the Training Remote, to either Self Destruct, or shoot exploding bolts.
    Has("Extra Toggle") & HasAny("Self Destruct", "Exploding Blaster Bolts"),
    apply_to="normal+",
)


RUIN_OF_THE_JEDI = Chapter(
    name="Ruin Of The Jedi",
    episode_number=3,
    chapter_number=5,
    start_region="Outside Temple",
    start_level="temple_a",
    # There are enemies at the start, so have the base logic expect fighting them.
    extra_chapter_entrance_rules=logic_options(
        base=BASE_CAN_DAMAGE_AT_CLOSE_RANGE,
        normal=True_(),
    ),
    story_characters=(
        "Obi-Wan Kenobi (Episode 3)",
        "Yoda",
    ),
    purchase_characters={
        "Mace Windu (Episode 3)": 38_000,
        "Disguised Clone": 12_000,
    },
    extra_toggle_characters=(
        "Skeleton",
        "Training Remote",
    ),
    regions={
        "Outside Temple": (
            ExitData(
                "Inside Temple Spawn",
                HasAbility(JEDI),
                new_level="temple_b",
            ),
        ),
        "Inside Temple Spawn": (
            ExitData(
                "Clone Pizza Party",
                HasAbility(IMPERIAL),
                er_rule=logic_options(
                    # Force the red bricks into stairs.
                    base=HasAbility(JEDI),
                    # Ignore the red bricks and just jump up.
                    normal=HasAnyAbilities(JEDI | HIGH_JUMP),
                ).and_rule(HasAbility(IMPERIAL)),
            ),
            ExitData(
                "Archives",
                True_(),
                er_rule=HasAbility(JEDI),
                new_level="temple_c",
            ),
        ),
        "Clone Pizza Party": (),
        "Archives": (
            ExitData(
                "Hologram Room",
                True_(),
                # Activating all 3 switches on the right only needs a Jedi.
                # There is also a drop-in warp to get behind the arm blocking the door, that hard logic could do.
                er_rule=HasAbility(JEDI),
            ),
        ),
        "Hologram Room": (
            ExitData(
                "Chapter Completion",
                True_(),
                # Force is needed to spin the wheel in the hologram projector.
                er_rule=HasAbility(JEDI),
                new_level="temple_status",
            ),
        ),
    },
    minikits={
        "Outside Temple Minikit On Ground": minikit_data(
            "Outside Temple",
            pickup_name="mk_0",
        ),
        "Outside Temple High Minikit": minikit_data(
            "Outside Temple",
            logic_options(
                # Force the platforms, then high jump up.
                base=HasAllAbilities(JEDI | HIGH_JUMP),
                # Double Jump + Slam reaches the minikit from on top of the platforms.
                normal=HasAbility(JEDI),
                moderate=HasAnyAbilities(JEDI | CAN_HIGH_JUMP_SLAM),
            ),
            pickup_name="mk_1",
        ),
        "Minikit Above Temple Entrance": minikit_data(
            "Outside Temple",
            logic_options(
                base=HasAllAbilities(BOUNTY_HUNTER | SITH),
                normal=And(
                    CAN_DESTROY_CLOSE_SILVER_BRICKS,
                    CAN_SITH_FORCE,
                    (CAN_GRAPPLE | HasAbility(HIGH_JUMP)),
                ),
                moderate=CAN_DESTROY_CLOSE_SILVER_BRICKS & CAN_SITH_FORCE,
            ),
            er_rule=logic_options(
                # Destroy the object to reveal the grapple point, grapple up, then double jump and sith force, then
                # explode the silver bricks, then finally build the bricks to make the minikit.
                base=CAN_DESTROY_CLOSE_SILVER_BRICKS & CAN_SITH_FORCE & CAN_GRAPPLE,
                # High jump can skip the grapple.
                normal=CAN_DESTROY_CLOSE_SILVER_BRICKS & CAN_SITH_FORCE & (CAN_GRAPPLE | HasAbility(HIGH_JUMP)),
                # Sith/Jedi can triple jump to skip the grapple.
                moderate=CAN_DESTROY_CLOSE_SILVER_BRICKS & CAN_SITH_FORCE
            ),
            pickup_name="m_pup1"
        ),
        "Pizza Party Minikit": minikit_data(
            "Clone Pizza Party",
            True_(),
            er_rule=HasAbility(CAN_BARELY_JUMP),
            pickup_name="mk_2",
        ),
        "Council Chamber Minikit": minikit_data(
            "Inside Temple Spawn",
            # Stack the chairs and then double jump up to the minikit.
            HasAbility(JEDI),
            pickup_name="mk_1",
        ),
        "Minikit Floating Near Council Chamber": minikit_data(
            "Inside Temple Spawn",
            logic_options(
                base=HasAbility(HOVER),
                normal=True_(),
            ),
            er_rule=logic_options(
                # Force the red bricks into stairs.
                base=HasAbility(JEDI),
                # Ignore the red bricks and just jump up.
                normal=HasAnyAbilities(JEDI | HIGH_JUMP),
            ).and_rule(logic_options(
                # Expect hovering to get the minikit and come back without dying.
                base=HasAbility(HOVER),
                # Jump to the minikit and then die.
                # Cannot get it:
                # - Clone (jump_distance=0.7)
                # I tried the 1P2C strategy of being shot to get extra distance + Stud Magnet, but still could not reach
                # it with Clone.
                # Can get it:
                # - Dexter Jettstar (jump_distance=0.77)
                # - Han Solo (jmup_distance=0.84)
                # - Captain Tarpals (single jump) (jump_distance=0.9051)
                normal=HasAbility(CAN_JUMP_DISTANCE_0_77_DEXTER_PLUS),
            )),
            pickup_name="mk_0",
        ),
        "Archives Right Side Right Lever Minikit": minikit_data(
            "Archives",
            logic_options(
                base=HasAbility(HIGH_JUMP),
                moderate=True_(),
            ),
            er_rule=logic_options(
                base=HasAllAbilities(JEDI | HIGH_JUMP),
                moderate=HasAbility(JEDI)
            ),
            pickup_name="mk_1",
        ),
        "Archives Right Side Left Lever Minikit": minikit_data(
            "Archives",
            True_(),
            er_rule=HasAbility(JEDI),
            pickup_name="mk_0"
        ),
        "Archives Left Side Behind Force Field Minikit": minikit_data(
            "Archives",
            logic_options(
                base=HasAllAbilities(HIGH_JUMP | PROTOCOL_PANEL),
                normal=HasAbility(HIGH_JUMP),
                moderate=True_(),
            ),
            er_rule=logic_options(
                # Force the 3 right levers as a jedi, high jump up onto the arm that now forms a platform.
                # Expect PROTOCOL_PANEL so that the level can be continued without restarting.
                base=HasAllAbilities(JEDI | HIGH_JUMP | PROTOCOL_PANEL),
                # Force out a platform and high jump from it to get over the force field.
                # Grievous' Bodyguard can just get enough horizontal distance to clear the force field, though normal
                # logic could be expected to just restart the level for this minikit.
                normal=HasAllAbilities(JEDI | HIGH_JUMP),
                # Triple jump can skip high jumps (and can also skip forcing the levers on the right side of the room by
                # triple jumping up to the lowest platform area).
                # Triple high jump can similarly jump straight up, or even straight over the forcefield.
                moderate=HasAnyAbilities(JEDI | CAN_HIGH_JUMP_SLAM),
            ),
            pickup_name="mk_2"
        ),
        "Hologram Room Minikit": minikit_data(
            "Hologram Room",
            logic_options(
                base=CAN_DESTROY_CLOSE_SILVER_BRICKS & CAN_SITH_FORCE,
                normal=And(
                    CAN_DESTROY_CLOSE_SILVER_BRICKS,
                    HasAbility(SITH) | Has("Dark Side"),
                ),
            ),
            er_rule=logic_options(
                base=CAN_DESTROY_CLOSE_SILVER_BRICKS & CAN_SITH_FORCE,
                hard=Or(
                    CAN_DESTROY_CLOSE_SILVER_BRICKS & CAN_SITH_FORCE,
                    # Swapping to yoda up against the force field seems to let you grab this minikit through the force
                    # field.
                    HasAny("Yoda", "Yoda (Ghost)"),
                ),
            ),
            pickup_name="m_pup1",
        )
    },
    power_brick=LocationData(
        "Archives",
        logic_options(
            base=HasAllAbilities(HIGH_JUMP | PROTOCOL_PANEL),
            normal=HasAbility(HIGH_JUMP),
            moderate=True_(),
        ),
        er_rule=logic_options(
            # While there is a Grapple point for the left side, middle lever, there are force platforms that can be high
            # jumped up to, and the button to remove the force field in front of the level requires high jump anyway.
            base=HasAllAbilities(JEDI | HIGH_JUMP | PROTOCOL_PANEL),
            normal=And(
                # High jump is expected to get to all 3 levers, and to reach the Power Brick.
                HasAllAbilities(JEDI | HIGH_JUMP),
                # Allow hovering out, or high jumping out instead.
                HasAnyAbilities(PROTOCOL_PANEL | HOVER | HIGH_JUMP),
            ),
            moderate=Or(
                # Just triple jump out, and triple jump up to the Power Brick.
                HasAbility(JEDI),
                # Triple high jump can skip the entire sequence and jump to the Power Brick directly.
                HasAbility(CAN_HIGH_JUMP_SLAM),
            )
        ),
    ),
)
