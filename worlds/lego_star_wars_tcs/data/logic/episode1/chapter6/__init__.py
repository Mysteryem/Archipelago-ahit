from rule_builder.rules import Or, Has, True_, False_

from ...macros import (
    can_destroy_close_silver_bricks,
)
from ...option_filters import logic_options
from ...rules import HasAbility, HasAllAbilities, HasAnyAbilities
from ...types import minikit_data, ExitData, Chapter, LocationData

from .....character_ability import *

DARTH_MAUL = Chapter(
    name="Darth Maul",
    episode_number=1,
    chapter_number=6,
    story_characters=(
        "Obi-Wan Kenobi",
        "Qui-Gon Jinn",
    ),
    purchase_characters={
        "Darth Maul": 60_000,
    },
    start_region="Spawn",
    start_level="maul_a",
    regions={
        "Spawn": (
            ExitData(
                "Hangar",
                logic_options(
                    # Fight Maul from across the gap, then force the bridge.
                    base=HasAbility(IS_NON_GHOST_JEDI),
                    # High jump can actually just jump onto the floating bridge, and walk across. Maul runs away when
                    # the player gets close to him.
                    # The high jump is a bit too difficult/inconsistent with Jar Jar/Captain Tarpals, but is pretty easy
                    # with General Grievous. TODO: Try Grievous' Bodyguard.
                    normal=HasAbility(IS_NON_GHOST_JEDI) | Has("General Grievous"),
                    # Allow Jar Jar/Captain Tarpals and triple jump.
                    moderate=HasAnyAbilities(JEDI | HIGH_JUMP),
                )
            ),
        ),
        "Hangar": (
            ExitData(
                "Imperial Room",
                logic_options(
                    # IS_NON_GHOST_JEDI implies JEDI.
                    base=HasAbility(IMPERIAL),
                    normal=HasAllAbilities(JEDI | IMPERIAL),
                    moderate=HasAbility(IMPERIAL) & HasAnyAbilities(JEDI | CAN_HIGH_JUMP_SLAM)
                ),
                er_rule=logic_options(
                    # Force the platforms with P2, then use the Imperial panel.
                    base=HasAllAbilities(JEDI | IMPERIAL),
                    # Alternatively, triple high jump all the way up.
                    moderate=HasAbility(IMPERIAL) & HasAnyAbilities(JEDI | CAN_HIGH_JUMP_SLAM)
                ),
                new_level="maul_b",
            ),
            ExitData(
                "Tower Room",
                new_level="maul_b",
            ),
        ),
        "Imperial Room": (),
        "Tower Room": (
            ExitData(
                "Tower Room Top",
                logic_options(
                    # IS_NON_GHOST_JEDI implies JEDI.
                    base=HasAbility(GRAPPLE),
                    # Allow Force Grapple Leap.
                    normal=Or(
                        HasAnyAbilities(JEDI | HIGH_JUMP) & HasAbility(GRAPPLE),
                        HasAbility(JEDI) & Has("Force Grapple Leap"),
                    ),
                    # HasAnyAbilities(JEDI | HIGH_JUMP) was used at "Spawn -> Hangar"
                    moderate=True_(),
                ),
                er_rule=logic_options(
                    # Jump up to and use the grapple point.
                    base=HasAnyAbilities(JEDI | HIGH_JUMP) & HasAbility(GRAPPLE),
                    # Allow Force Grapple Leap.
                    normal=Or(
                        HasAnyAbilities(JEDI | HIGH_JUMP) & HasAbility(GRAPPLE),
                        HasAbility(JEDI) & Has("Force Grapple Leap"),
                    ),
                    # The wall collision near the grapple point can be stood on to jump up to the end of the grapple
                    # point.
                    moderate=HasAnyAbilities(JEDI | HIGH_JUMP),
                ),
            ),
            ExitData(
                "Energy Columns Room",
                logic_options(
                    base=True_(),
                    normal=HasAbility(JEDI),
                    # This entrance is now useless to include in logic because the "Tower Room Top" path can be taken.
                    moderate=False_(),
                ),
                er_rule=HasAbility(JEDI),
                # maul_c does not exist.
                new_level="maul_d",
            ),
        ),
        "Tower Room Top": (
            # Just drop down.
            # maul_c does not exist.
            ExitData("Energy Columns Room", new_level="maul_d"),
        ),
        "Energy Columns Room": (
            # Logically, fighting the Droideka and going through the force doors corridor (maul_e), is skipped and the
            # logic goes straight to the boss fight (maul_f).
            # Note: In higher logic, Blasters can skip fighting the Droidekas by shooting Maul into the pit.
            ExitData(
                "Maul Boss Room",
                logic_options(
                    # IS_NON_GHOST_JEDI implies JEDI.
                    base=True_(),
                    normal=HasAbility(JEDI),
                ),
                er_rule=HasAbility(JEDI),
                new_level="maul_f",
            ),
        ),
        "Maul Boss Room": (
            ExitData(
                "Chapter Completion",
                # ER Note: Would be more complicated, but for now, assume JEDI was needed to reach here.
                # HasAbility(JEDI),
                new_level="maul_status",
            ),
        ),
    },
    minikits={
        "Left Starfighter Minikit": minikit_data(
            "Hangar",
            er_rule=HasAnyAbilities(JEDI | HIGH_JUMP),
            pickup_name="m_pup2",
        ),
        "Right Starfighter Minikit": minikit_data(
            "Hangar",
            er_rule=HasAnyAbilities(JEDI | HIGH_JUMP),
            pickup_name="m_pup1",
        ),
        "Imperial Room Minikit": minikit_data(
            "Imperial Room",
            logic_options(
                # Base: IS_NON_GHOST_JEDI implies JEDI.
                # Normal: HasAllAbilities(JEDI | IMPERIAL) is required.
                base=True_(),
                moderate=HasAbility(JEDI),
            ),
            er_rule=HasAbility(JEDI),
            pickup_name="m_pup3",
        ),
        "Top Of Tower Minikit": minikit_data(
            "Tower Room Top",
            logic_options(
                # IS_NON_GHOST_JEDI implies JEDI.
                base=True_(),
                # Normal can get here with General Grievous and GRAPPLE.
                # Moderate can get here with just HIGH_JUMP.
                normal=HasAbility(JEDI),
            ),
            er_rule=logic_options(
                base=HasAbility(JEDI),
                moderate=HasAnyAbilities(JEDI | CAN_HIGH_JUMP_SLAM),
            ),
            pickup_name="m_pup2",
        ),
        "Behind Silver Bricks Minikit": minikit_data(
            "Tower Room",
            # IS_NON_GHOST_JEDI implies CAN_JUMP_NORMAL_DISTANCE.
            # Normal: HasAbility(IS_NON_GHOST_JEDI) | Has("General Grievous") implies CAN_JUMP_NORMAL_DISTANCE.
            # Moderate: HasAnyAbilities(JEDI | HIGH_JUMP) implies CAN_JUMP_NORMAL_DISTANCE.
            can_destroy_close_silver_bricks,
            er_rule=logic_options(
                base=HasAbility(CAN_JUMP_NORMAL_DISTANCE) & can_destroy_close_silver_bricks,
                # Include Ewok and other slow characters that can only barely get enough jump distance.
                moderate=HasAbility(CAN_BARELY_JUMP) & can_destroy_close_silver_bricks,
            ),
            pickup_name="m_pup1",
        ),
        "Imperial Platform Minikit": minikit_data(
            "Energy Columns Room",
            HasAbility(IMPERIAL),
            pickup_name="m_pup1",
        ),
        "Energy Column Minikit": minikit_data(
            "Energy Columns Room",
            # Base: IS_NON_GHOST_JEDI implies CAN_JUMP_NORMAL_DISTANCE.
            # Normal: HasAbility(IS_NON_GHOST_JEDI) | Has("General Grievous") implies CAN_JUMP_NORMAL_DISTANCE.
            # Moderate: HasAnyAbilities(JEDI | HIGH_JUMP) implies CAN_JUMP_NORMAL_DISTANCE.
            True_(),
            # The second gap is just too big for Ewok to cross it.
            er_rule=HasAbility(CAN_JUMP_NORMAL_DISTANCE),
            pickup_name="mk_1",  # "mk_1" + "\x00" + "2"
        ),
        "Maul Fight Minikit 1": minikit_data(
            "Maul Boss Room",
            logic_options(
                # ER Note: Currently assuming JEDI is required to reach this room.
                # High jump up on the platform and then jump to the minikit.
                base=HasAbility(HIGH_JUMP),
                # The platform can be forced down enough to double jump onto, then wait for the platform to rise again,
                # and then the minikit can be double jumped to.
                # Note: Forcing the platform too low destroys it, requiring a level restart.
                normal=True_(),
                # Moderate: Triple jump instead of high jump.
            ),
            pickup_name="m_pup1",
        ),
        "Maul Fight Minikit 2": minikit_data(
            "Maul Boss Room",
            logic_options(
                # ER Note: Currently assuming JEDI is required to reach this room.
                # High jump up on the platform and then jump to the minikit.
                base=HasAbility(HIGH_JUMP),
                # The platform can be forced down enough to double jump onto, then wait for the platform to rise again,
                # and then the minikit can be double jumped to, with a slam used to get the extra height needed.
                # Note: Forcing the platform too low destroys it.
                normal=True_(),
                # Moderate: Triple jump instead of high jump.
            ),
            pickup_name="m_pup2",
        ),
        "Maul Fight Minikit 3": minikit_data(
            "Maul Boss Room",
            logic_options(
                # ER Note: Currently assuming JEDI is required to reach this room.
                # High jump up on the platform and then jump to the minikit.
                base=HasAbility(HIGH_JUMP),
                # The platform can be forced down enough to double jump onto, then wait for the platform to rise again,
                # and then the minikit can be double jumped to.
                # Note: Forcing the platform too low destroys it.
                normal=True_(),
                # Moderate: Triple jump instead of high jump.
            ),
            pickup_name="m_pup3",
        ),
    },
    power_brick=LocationData("Imperial Room"),
    ridables={
        "Service Car": LocationData("Hangar"),
    },
)
