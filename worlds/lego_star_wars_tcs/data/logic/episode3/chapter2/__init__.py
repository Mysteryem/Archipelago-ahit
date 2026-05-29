from rule_builder.rules import HasAny, True_, HasAll, Has

from ...macros import (
    CAN_GRAPPLE,
    CAN_DESTROY_CLOSE_SILVER_BRICKS as BASE_CAN_DESTROY_CLOSE_SILVER_BRICKS,
)
from ...option_filters import logic_options
from ...rules import HasAbility, HasAnyAbilities
from ...types import minikit_data, ExitData, Chapter, LocationData

from .....character_ability import *

CAN_DESTROY_CLOSE_SILVER_BRICKS = BASE_CAN_DESTROY_CLOSE_SILVER_BRICKS.or_rule(
    # The Extra Toggle character Buzz Droid can explode.
    HasAll("Extra Toggle", "Self Destruct"),
    apply_to="normal+",
)

CAN_MELEE_MACRO = logic_options(
    base=HasAbility(CAN_MELEE),
    # The Extra Toggle character Buzz Droid can melee.
    normal=HasAbility(CAN_MELEE) | Has("Extra Toggle"),
)


CHANCELLOR_IN_PERIL = Chapter(
    name="Chancellor In Peril",
    episode_number=3,
    chapter_number=2,
    start_region="Hangar",
    start_level="cruiser_a",
    story_characters=(
        "Anakin Skywalker (Jedi)",
        "Chancellor Palpatine",
        "Obi-Wan Kenobi (Episode 3)",
        "R2-D2",
    ),
    purchase_characters={
        "Count Dooku": 100_000,
        "Grievous' Bodyguard": 42_000,
    },
    extra_toggle_characters=(
        "Buzz Droid",
    ),
    regions={
        "Hangar": (
            ExitData(
                "Generator Room",
                HasAbility(JEDI),
                new_level="cruiser_g",
            ),
        ),
        "Generator Room": (
            # ExitData(
            #     "Generator Room (Upper)",
            #     # Getting here implies Jedi.
            #     logic_options(
            #         # Astromech panel to activate the elevator, or force the platforms as a Jedi.
            #         base=HasAnyAbilities(ASTROMECH_PANEL | JEDI),
            #         # Triple high jump up from the Astromech Panel.
            #         moderate=HasAnyAbilities(ASTROMECH_PANEL | JEDI | CAN_HIGH_JUMP_SLAM),
            #     ),
            # ),
            ExitData(
                "Droid Doors And Droid Enemies Room",
                # Force the platformsForce off the grates to the next area.
                # HasAbility(JEDI),
                new_level="cruiser_b",
            ),
        ),
        "Droid Doors And Droid Enemies Room": (
            ExitData(
                "Tower Climb",
                # logic_options(
                #     # Use the panel to open the door, force the explosive into position, and then force the explosive
                #     # again to explode it and open the way forward.
                #     base=HasAllAbilities(ASTROMECH_PANEL | JEDI),
                #     # Yoda can triple jump under the trigger to the next area, swap to another character,
                #     # and then hit the trigger to load into the next area, skipping the Astromech Panel requirement.
                #     hard=HasAllAbilities(ASTROMECH_PANEL | JEDI) | HasAny("Yoda", "Yoda (Ghost)"),
                # ),
                # Simplified without ER:
                logic_options(
                    base=HasAbility(ASTROMECH_PANEL),
                    hard=HasAbility(ASTROMECH_PANEL) | HasAny("Yoda", "Yoda (Ghost)"),
                ),
            ),
        ),
        "Tower Climb": (
            ExitData(
                "Dooku Fight",
                # logic_options(
                #     # Jump up, force to activate the updraft, defeat the Droideka and use the panel to open the door.
                #     base=HasAllAbilities(JEDI | ASTROMECH_PANEL),
                #     # Triple high jump can skip the updraft.
                #     moderate=HasAbility(ASTROMECH_PANEL) & HasAnyAbilities(JEDI | CAN_HIGH_JUMP_SLAM)
                # ),
                # Simplified without ER:
                logic_options(
                    base=True_(),
                    hard=HasAbility(ASTROMECH_PANEL),
                ),
                new_level="cruiser_c",
            ),
        ),
        "Dooku Fight": (
            ExitData(
                "Horizontal Elevator Shaft",
                # Fully covered without ER.
                # Being able to reach here provides everything necessary to defeat Dooku.
                # logic_options(
                #     base=HasAbility(JEDI),
                #     # Would need to double check, but I was able to defeat him entirely as a Droideka.
                #     normal=can_damage_at_close_range,
                # ),
                new_level="cruiser_d",
            ),
        ),
        "Horizontal Elevator Shaft": (
            ExitData(
                "Rotated Path To The Bridge",
                # Fully covered without ER.
                # All astromech panel characters can move fast enough to outrun the falling lift/elevator.
                # logic_options(
                #     # Ewok (0.9) is too slow, and R2-D2 (1.0) only just outruns the elevator.
                #     base=HasAbility(RUN_SPEED_1_0_OR_HIGHER),
                #     # Yoda has too slow movement speed, but fast ground attacks and jumps.
                #     normal=HasAbility(RUN_SPEED_1_0_OR_HIGHER) | HasAny("Yoda", "Yoda (Ghost)"),
                # ),
                new_level="cruiser_e",
            ),
        ),
        "Rotated Path To The Bridge": (
            ExitData(
                "Ship's Bridge",
                # Fully covered without ER.
                # All Astromech Panel users can walk through the gas, then all that is needed is a jump to get up a
                # later part.
                # logic_options(
                #     base=HasAllAbilities(ASTROMECH_PANEL | CAN_JUMP_HEIGHT_0_37),
                #     # Astromech Droids can just barely hover around the jump obstacle. The other Astromech Panel users
                #     # are IG-88 and 4-LOM, who can jump.
                #     moderate=HasAbility(ASTROMECH_PANEL),
                # ),
                new_level="cruiser_f",
            ),
        ),
        "Ship's Bridge": (
            ExitData(
                "Chapter Completion",
                # Fully covered without ER.
                # logic_options(
                #     base=HasAbility(JEDI),
                # ),
                new_level="cruiser_status",
            ),
        )
    },
    minikits={
        "Hangar Minikit": minikit_data(
            "Hangar",
            logic_options(
                base=CAN_GRAPPLE,
                # Triple jump from the red starfighter
                moderate=HasAnyAbilities(JEDI | GRAPPLE | CAN_HIGH_JUMP_SLAM),
            ),
            pickup_name="m_pup1",
        ),
        "Generator Room Grapple Minikit": minikit_data(
            "Generator Room",
            logic_options(
                base=CAN_GRAPPLE,
                normal=CAN_GRAPPLE | HasAbility(HIGH_JUMP),
                moderate=HasAnyAbilities(GRAPPLE | JEDI | HIGH_JUMP),
            ),
            pickup_name="m_pup1",
        ),
        "Minikit Behind Astromech Droid Door": minikit_data(
            "Droid Doors And Droid Enemies Room",
            HasAbility(ASTROMECH_PANEL),
            pickup_name="mk_0",
        ),
        "Minikit Behind Protocol Droid Door": minikit_data(
            "Droid Doors And Droid Enemies Room",
            HasAbility(ASTROMECH_PANEL),
            pickup_name="mk_1",
        ),
        "Tower Far Left Minikit": minikit_data(
            "Tower Climb",
            # Fully covered without ER.
            # HasAbility(CAN_JUMP_HEIGHT_0_37),
            pickup_name="mk_3",
        ),
        "Tower Access Hatch Minikit": minikit_data(
            "Tower Climb",
            # logic_options(
            #     base=HasAbility(SHORTIE),
            #     # High jump to the minikit.
            #     normal=HasAnyAbilities(SHORTIE | HIGH_JUMP),
            #     # Triple jump to the minikit.
            #     moderate=HasAnyAbilities(SHORTIE | HIGH_JUMP | JEDI),
            # ),
            # Simplified without ER:
            logic_options(
                base=HasAbility(SHORTIE),
                normal=HasAnyAbilities(SHORTIE | HIGH_JUMP),
                moderate=True_(),
            ),
            pickup_name="mk_2",
        ),
        "Minikit Behind Door After Dooku Fight": minikit_data(
            "Dooku Fight",
            # Fully covered without ER.
            # logic_options(
            #     base=HasAbility(JEDI),
            #     # Would need to double check, but I was able to defeat him entirely as a Droideka.
            #     normal=can_damage_at_close_range,
            # ),
            pickup_name="m_pup1",
        ),
        "Minikit Behind Orange Piping": minikit_data(
            "Rotated Path To The Bridge",
            # Already covered without ER.
            # logic_options(
            #     base=HasAllAbilities(ASTROMECH_PANEL | JEDI),
            #     # Include force ghosts.
            #     normal=HasAnyAbilities(ASTROMECH_PANEL | GAS_IMMUNE) & HasAbility(JEDI),
            #     # Jump around the gas...
            #     moderate=HasAbility(JEDI),
            # ),
            pickup_name="m_pup1",
        ),
        "Bridge Left Minikit": minikit_data(
            "Ship's Bridge",
            # With ER, base logic would need to consider defeating the Bodyguards, a melee attack or explosion are
            # required, as they seem to always deflect blasters.
            # er_rule=HasAbility(CAN_JUMP_HEIGHT_0_37) & (CAN_MELEE_MACRO | CAN_DESTROY_CLOSE_SILVER_BRICKS),
            pickup_name="mk_0",
        ),
        "Bridge Right Minikit": minikit_data(
            "Ship's Bridge",
            # Same logic as the left minikit
            pickup_name="mk_1",
        ),
    },
    power_brick=LocationData(
        "Horizontal Elevator Shaft",
        CAN_DESTROY_CLOSE_SILVER_BRICKS,
        # With ER, base logic would expect reversing the elevator to get the Power Brick.
        er_rule=logic_options(
            base=CAN_DESTROY_CLOSE_SILVER_BRICKS & HasAbility(ASTROMECH_PANEL),
            normal=CAN_DESTROY_CLOSE_SILVER_BRICKS,
        ),
    ),
)
