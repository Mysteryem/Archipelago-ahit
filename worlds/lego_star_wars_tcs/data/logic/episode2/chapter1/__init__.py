from rule_builder.rules import Has

from ...macros import (
    can_shoot_allow_torpedoes,
)
from ...option_filters import logic_options
from ...rules import HasAbility
from ...types import minikit_data, ExitData, Chapter, LocationData, MinikitData

from .....character_ability import *

BOUNTY_HUNTER_PURSUIT = Chapter(
    name="Bounty Hunter Pursuit",
    episode_number=2,
    chapter_number=1,
    start_region="Spawn",
    start_level="pursuit_a",
    chapter_entrance_rule=HasAbility(IS_A_VEHICLE),
    regions={
        "Spawn": (
            ExitData("First Forcefield Trap", new_level="pursuit_b"),
        ),
        "First Forcefield Trap": (
            ExitData("After First Forcefield Trap", new_level="pursuit_c"),
        ),
        "After First Forcefield Trap": (
            ExitData("Second Forcefield Trap", new_level="pursuit_d"),
        ),
        "Second Forcefield Trap": (
            # Logically, pursuit_e is skipped because that is just the boss battle itself.
            ExitData(
                "Chapter Completion",
                HasAbility(VEHICLE_BLASTER),
                new_level="pursuit_status",
            ),
        ),
    },
    minikits={
        "Destroy First Turrets Minikit": MinikitData(
            "Spawn",
            logic_options(
                base=HasAbility(VEHICLE_BLASTER),
                normal=can_shoot_allow_torpedoes,
            ),
            pickup_names=("TKIT1", "TKIT2", "TKIT3", "TKIT4", "TKIT5")
        ),
        "Torpedo Spires Minikit": MinikitData(
            "Spawn",
            # These are awful to target. It would be nice to require Infinite Torpedos [sic] on the lowest logic
            # difficulty, but the lowest logic difficulty specifically avoids including Extras in logic.
            pickup_names=("SPIRES1", "SPIRES2", "SPIRES3", "SPIRES4", "SPIRES5")
        ),
        "Traffic Light Minikit": minikit_data(
            "Spawn",
            logic_options(
                base=HasAbility(VEHICLE_BLASTER),
                normal=can_shoot_allow_torpedoes,
            ),
            pickup_name="JJ_KIT",
        ),
        "First TIE Gate Minikit": minikit_data(
            "Spawn",
            HasAbility(VEHICLE_TIE),
            pickup_name="MINTIE"
        ),
        "Cylinder Advertisements Minikit": MinikitData(
            "After First Forcefield Trap",
            # Some of these objects are particularly difficult to target with torpedoes, potentially needing a direct
            # shot in one case, so normal logic does not consider using torpedoes, and moderate logic always expects
            # Infinite Torpedos [sic] if using torpedoes.
            # ER Note: Needs `CanReachRegion("Bounty Hunter Pursuit - Spawn") &`
            logic_options(
                base=HasAbility(VEHICLE_BLASTER),
                moderate=HasAbility(VEHICLE_BLASTER) | Has("Infinite Torpedos"),
                hard=can_shoot_allow_torpedoes,
            ),
            pickup_names=(
                # In "Spawn".
                "m_1A",
                "m_1",
                "m_2",
                "m_3",
                "m_4",
                "m_5",
                # In "After First Forcefield Trap".
                "m_15",
                "m_14",
                "m_13",
                "m_11",
            )
        ),
        "First Forcefield Trap Minikit": minikit_data(
            "First Forcefield Trap",
            HasAbility(VEHICLE_BLASTER),
            pickup_name="mK",
        ),
        "Second TIE Gate Minikit": minikit_data(
            "After First Forcefield Trap",
            HasAbility(VEHICLE_TIE),
            pickup_name="TIEMIN",
        ),
        "Triple Triangle Sign Minikit": minikit_data(
            "After First Forcefield Trap",
            # Cannot be hit with torpedoes.
            HasAbility(VEHICLE_BLASTER),
            pickup_name="TRI_KIT",
        ),
        "Destroy Second Turrets Minikit": MinikitData(
            "After First Forcefield Trap",
            logic_options(
                base=HasAbility(VEHICLE_BLASTER),
                normal=can_shoot_allow_torpedoes,
            ),
            pickup_names=("TKIT1", "TKIT2", "TKIT3", "TKIT4", "TKIT5")
        ),
        "Second Forcefield Trap Minikit": minikit_data(
            "Second Forcefield Trap",
            HasAbility(VEHICLE_BLASTER),
            pickup_name="mK1",
        )
    },
    power_brick=LocationData("After First Forcefield Trap", HasAbility(VEHICLE_BLASTER))
)

# This is the only Minikit in the entire game that is split across multiple levels.
BOUNTY_HUNTER_PURSUIT.level_minikits["pursuit_a"]["Cylinder Advertisements Minikit"] \
    = BOUNTY_HUNTER_PURSUIT.minikits["Cylinder Advertisements Minikit"]
