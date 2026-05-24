from rule_builder.rules import And

from ...macros import can_true_triple_jump
from ...option_filters import logic_options
from ...rules import HasAbility, HasAllAbilities, HasAnyAbilities
from ...types import minikit_data, ExitData, Chapter, LocationData

from .....character_ability import *

NEGOTIATIONS = Chapter(
    name="Negotiations",
    episode_number=1,
    chapter_number=1,
    story_characters=(
        "Obi-Wan Kenobi",
        "Qui-Gon Jinn",
        "TC-14",
    ),
    purchase_characters={
        "Battle Droid": 6500,
        "Battle Droid (Security)": 8500,
        "Battle Droid (Commander)": 10_000,
        "Droideka": 40_000,
    },
    start_region="Meeting Room",
    start_level="negotiations_a",
    regions={
        "Meeting Room": (
            ExitData("Main Corridor", HasAbility(JEDI)),
        ),
        "Main Corridor": (
            ExitData(
                "Single Force Field Room",
                HasAbility(PROTOCOL_PANEL),
            ),
            ExitData(
                "High Force Fields Room",
                HasAbility(PROTOCOL_PANEL),
            ),
            ExitData(
                "Vulture Droid Room",
                HasAbility(ASTROMECH_PANEL),
                new_level="negotiations_b",
            ),
            ExitData(
                "Small Room Between Main Corridor and Room Before Hangar",
                HasAbility(PROTOCOL_PANEL),
            ),
        ),
        "Single Force Field Room": (),
        "High Force Fields Room": (),
        "Vulture Droid Room": (),
        "Small Room Between Main Corridor and Room Before Hangar": (
            ExitData(
                "Room Before Hangar",
                HasAllAbilities(JEDI | CAN_BUILD_BRICKS | PROTOCOL_PANEL)
            ),
        ),
        "Room Before Hangar": (
            ExitData(
                "Main Hangar",
                HasAbility(JEDI),
                new_level="negotiations_c",
            ),
        ),
        "Main Hangar": (
            ExitData(
                "Power Brick Room",
                And(
                    HasAbility(ASTROMECH_PANEL),
                    logic_options(
                        base=HasAbility(JEDI),
                        # ER Note: With ER, entering the Main Hangar from the MTT Hangar would require Moderate logic to
                        #  use Jetpack to get to the Power Brick Room entrance.
                        normal=HasAnyAbilities(CAN_DOUBLE_JUMP | JETPACK),
                    )
                ),
            ),
            ExitData(
                "MTT Hangar",
                logic_options(
                    # Defeat the Droideka and force the platforms to jump over the fence.
                    base=HasAbility(JEDI),
                    # Alternatively high jump over the fence, potentially ignoring the Droideka.
                    normal=HasAnyAbilities(JEDI | HIGH_JUMP),
                    # Alternatively jump + jetpack hover from on top of the magnet to get over the fence.
                    moderate=HasAnyAbilities(JEDI | HIGH_JUMP | JETPACK),
                )
            ),
        ),
        "Power Brick Room": (),
        "MTT Hangar": (
            ExitData(
                "Chapter Completion",
                HasAbility(PROTOCOL_PANEL),
                new_level="negotiations_status",
            ),
        ),
    },
    minikits={
        "Blue Levers Minikit": minikit_data(
            "Main Corridor",
            HasAbility(JEDI),
            pickup_name="m_pup4",
        ),
        "Purple Levers Minikit": minikit_data(
            "Main Corridor",
            HasAbility(JEDI),
            pickup_name="m_pup1",
        ),
        "Force Field With Battle Droids Minikit": minikit_data(
            "Single Force Field Room",
            pickup_name="m_pup3",
        ),
        "Minikit Behind Left High Force Field": minikit_data(
            "High Force Fields Room",
            HasAbility(SHORTIE),
            pickup_name="m_pup5",
        ),
        "Minikit Behind Right High Force Field": minikit_data(
            "High Force Fields Room",
            And(
                # Needed to disable the force fields.
                HasAbility(SHORTIE),
                logic_options(
                    # Stack 3 boxes, double jump on top, then double jump to the Minikit.
                    base=HasAbility(JEDI),
                    # Alternatively, high jump up to the minikit, either holding the control stick in the
                    # direction of the elevated area to prevent sliding off, or by standing on
                    normal=HasAnyAbilities(JEDI | HIGH_JUMP),
                    # Moderate (simpler): Triple jump up to the minikit.
                ),
            ),
            pickup_name="pup2",
        ),
        "High Minikit In Vulture Droid Room": minikit_data(
            "Vulture Droid Room",
            logic_options(
                # Stand on the moving platform. P2 will force the platform into position, then high jump to the
                # minikit.
                base=HasAllAbilities(JEDI | HIGH_JUMP),
                # Stand on the air tanks by the table, then high jump up to the minikit.
                normal=HasAbility(HIGH_JUMP),
                # A triple jump can be used instead of a high jump.
                moderate=HasAnyAbilities(JEDI | HIGH_JUMP),
            ),
            pickup_name="m_pup1",
        ),
        "Minikit Above Repaired Vulture Droid": minikit_data(
            "Vulture Droid Room",
            logic_options(
                # Force the grate out of the way, high jump into the vent, hover across the gap, then high jump up
                # to the minikit.
                base=HasAllAbilities(JEDI | HIGH_JUMP | HOVER),
                # Force the grate most of the way down, then jump onto the grate as it starts to return upwards and use
                # that extra height to jump into the vent. Hover across the gap, then double jump to the minikit by
                # standing on one of the wings of the vulture droid. Slam for extra height if you are having trouble.
                # While not relevant until ER, and not logically relevant either way, a double jump is just enough to
                # get back into the vent if this minikit has been reached without a character that can use Astromech
                # panels.
                normal=HasAllAbilities(JEDI | HOVER),
                # Force the grate out of the way and triple jump up to the vent. Triple jump across the gap (may take a
                # few tries, you'll need good timing), and then triple jump up to the minikit.
                moderate=HasAbility(JEDI),
            ),
            pickup_name="pup2",
        ),
        "High Minikit In Room Before Hangar": minikit_data(
            "Room Before Hangar",
            logic_options(
                # Force the grate, and then high jump from the grate's bricks.
                base=HasAllAbilities(JEDI | HIGH_JUMP),
                # TODO: Can a regular double jump + Stud Magnet also reach it?
                # A double jump + slam can reach the minikit.
                normal=HasAbility(JEDI),
                # A high triple jump can also reach the minikit, but both ways to get to the minikit require a Jedi, so
                # this is not relevant even with ER.
            ),
            pickup_name="m_pup2",
        ),
        "Minikit Left of Hangar Entrance": minikit_data(
            "Main Hangar",
            logic_options(
                # If the jump from the entrance with to where the minikit is, is missed, the force can be used on boxes
                # to build a tower back up to the entrance.
                base=HasAbility(JEDI),
                # Don't mess up the jump to where the minikit is, though a high jump can also get back to the entrance
                # with some platforming.
                normal=HasAbility(CAN_DOUBLE_JUMP),
            ),
            pickup_name="m_pup1",
        ),
        "Moving Platform Minikit": minikit_data(
            "Main Hangar",
            logic_options(
                # Stack the boxes and force the lever to activate the platform.
                base=HasAbility(JEDI),
                # Triple jump up to the platform then triple jump to the minikit. Grievous' Bodyguard cannot get the
                # distance required. TODO: Check Grievous' Bodyguard.
                moderate=can_true_triple_jump,
            ),
            pickup_name="m_pup2",
        ),
    },
    power_brick=LocationData(
        "Power Brick Room",
        logic_options(
            base=HasAbility(JEDI),
            normal=HasAnyAbilities(JEDI | HIGH_JUMP),
        )
    ),
    ridables={
        "STAP": LocationData(
            "Main Hangar",
            HasAbility(CAN_BUILD_BRICKS),
        )
    },
)
