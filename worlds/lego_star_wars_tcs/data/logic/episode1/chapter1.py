from rule_builder.rules import And, True_

from ..option_filters import logic_options
from ..rules import HasAbility, HasAllAbilities, HasAnyAbilities
from ..types import minikit_data, ExitData, Chapter, LocationData

from ...areas import Area
from ...levels import Level

from ....character_ability import *

R_MEETING_ROOM = "Meeting Room"
R_MAIN_CORRIDOR = "Main Corridor"
R_SINGLE_FORCE_FIELD_ROOM = "Single Force Field Room"
R_HIGH_FORCE_FIELDS_ROOM = "High Force Fields Room"
R_VULTURE_DROID_ROOM = "Vulture Droid Room"
R_SMALL_ROOM_BETWEEN_MAIN_CORRIDOR_AND_ROOM_BEFORE_HANGAR = "Small Room Between Main Corridor and Room Before Hangar"
R_ROOM_BEFORE_HANGAR = "Room Before Hangar"
R_MAIN_HANGAR = "Main Hangar"
R_POWER_BRICK_ROOM = "Power Brick Room"
R_MTT_HANGAR = "MTT Hangar"

NEGOTIATIONS = Chapter(
    area=Area.NEGOTIATIONS,
    start_region=R_MEETING_ROOM,
    regions={
        R_MEETING_ROOM: (
            ExitData(R_MAIN_CORRIDOR, HasAbility(JEDI)),
        ),
        R_MAIN_CORRIDOR: (
            ExitData(
                R_SINGLE_FORCE_FIELD_ROOM,
                HasAbility(PROTOCOL_PANEL),
            ),
            ExitData(
                R_HIGH_FORCE_FIELDS_ROOM,
                HasAbility(PROTOCOL_PANEL),
            ),
            ExitData(
                R_VULTURE_DROID_ROOM,
                HasAbility(ASTROMECH_PANEL),
                new_level=Level.NEGOTIATIONS_B,
            ),
            ExitData(
                R_SMALL_ROOM_BETWEEN_MAIN_CORRIDOR_AND_ROOM_BEFORE_HANGAR,
                HasAbility(PROTOCOL_PANEL),
            ),
        ),
        R_SINGLE_FORCE_FIELD_ROOM: (),
        R_HIGH_FORCE_FIELDS_ROOM: (),
        R_VULTURE_DROID_ROOM: (),
        R_SMALL_ROOM_BETWEEN_MAIN_CORRIDOR_AND_ROOM_BEFORE_HANGAR: (
            ExitData(
                R_ROOM_BEFORE_HANGAR,
                er_rule=HasAllAbilities(JEDI | CAN_BUILD_BRICKS | PROTOCOL_PANEL),
            ),
        ),
        R_ROOM_BEFORE_HANGAR: (
            ExitData(
                R_MAIN_HANGAR,
                er_rule=HasAbility(JEDI),
                new_level=Level.NEGOTIATIONS_C,
            ),
        ),
        R_MAIN_HANGAR: (
            ExitData(
                R_POWER_BRICK_ROOM,
                HasAbility(ASTROMECH_PANEL),
                er_rule=And(
                    HasAbility(ASTROMECH_PANEL),
                    logic_options(
                        base=HasAbility(JEDI),
                        # ER Note: With ER, entering the Main Hangar from the MTT Hangar would require Moderate logic
                        #  to use Jetpack to get to the Power Brick Room entrance.
                        normal=HasAnyAbilities(CAN_DOUBLE_JUMP | JETPACK),
                    )
                ),
            ),
            ExitData(
                R_MTT_HANGAR,
                er_rule=logic_options(
                    # Defeat the Droideka and force the platforms to jump over the fence.
                    base=HasAbility(JEDI),
                    # Alternatively high jump over the fence, potentially ignoring the Droideka.
                    normal=HasAnyAbilities(JEDI | HIGH_JUMP),
                    # Alternatively jump + jetpack hover from on top of the magnet to get over the fence.
                    moderate=HasAnyAbilities(JEDI | HIGH_JUMP | JETPACK),
                )
            ),
        ),
        R_POWER_BRICK_ROOM: (),
        R_MTT_HANGAR: (
            ExitData(
                "Chapter Completion",
                er_rule=HasAbility(PROTOCOL_PANEL),
            ),
        ),
    },
    minikits={
        "Blue Levers Minikit": minikit_data(
            R_MAIN_CORRIDOR,
            er_rule=HasAbility(JEDI),
            pickup_name="m_pup4",
        ),
        "Purple Levers Minikit": minikit_data(
            R_MAIN_CORRIDOR,
            er_rule=HasAbility(JEDI),
            pickup_name="m_pup1",
        ),
        "Force Field With Battle Droids Minikit": minikit_data(
            R_SINGLE_FORCE_FIELD_ROOM,
            pickup_name="m_pup3",
        ),
        "Minikit Behind Left High Force Field": minikit_data(
            R_HIGH_FORCE_FIELDS_ROOM,
            HasAbility(SHORTIE),
            pickup_name="m_pup5",
        ),
        "Minikit Behind Right High Force Field": minikit_data(
            R_HIGH_FORCE_FIELDS_ROOM,
            HasAbility(SHORTIE),
            er_rule=And(
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
            R_VULTURE_DROID_ROOM,
            logic_options(
                base=HasAbility(HIGH_JUMP),
                moderate=True_(),
            ),
            er_rule=logic_options(
                # Stand on the moving platform. P2 will force the platform into position, then high jump to the
                # minikit.
                base=HasAllAbilities(JEDI | HIGH_JUMP),
                # Stand on the air tanks by the table, then high jump up to the minikit.
                normal=HasAbility(HIGH_JUMP),
                # A triple jump can be used instead of a high jump.
                moderate=HasAnyAbilities(JEDI | HIGH_JUMP),
            ),
            # Simplified without ER.
            pickup_name="m_pup1",
        ),
        "Minikit Above Repaired Vulture Droid": minikit_data(
            R_VULTURE_DROID_ROOM,
            logic_options(
                base=HasAllAbilities(HIGH_JUMP | HOVER),
                normal=HasAllAbilities(HOVER),
                moderate=True_(),
            ),
            er_rule=logic_options(
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
            R_ROOM_BEFORE_HANGAR,
            logic_options(
                base=HasAbility(HIGH_JUMP),
                normal=True_(),
            ),
            er_rule=logic_options(
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
            R_MAIN_HANGAR,
            er_rule=logic_options(
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
            R_MAIN_HANGAR,
            er_rule=logic_options(
                # Stack the boxes and force the lever to activate the platform.
                base=HasAbility(JEDI),
                # Triple jump up to the platform then triple jump to the minikit.
                moderate=HasAnyAbilities(JEDI | CAN_HIGH_JUMP_SLAM),
            ),
            pickup_name="m_pup2",
        ),
    },
    power_brick=LocationData(
        R_POWER_BRICK_ROOM,
        er_rule=logic_options(
            base=HasAbility(JEDI),
            normal=HasAnyAbilities(JEDI | HIGH_JUMP),
        )
    ),
    ridables={
        "STAP": LocationData(
            R_MAIN_HANGAR,
            er_rule=HasAbility(CAN_BUILD_BRICKS),
        )
    },
)
