from rule_builder.rules import Or

from ...macros import (
    can_grapple,
    can_destroy_close_silver_bricks,
    base_can_damage_shielded_droideka,
)
from ...option_filters import logic_options
from ...rules import HasAbility, HasAllAbilities, HasAnyAbilities
from ...types import minikit_data, ExitData, Chapter, LocationData

from .....character_ability import *

JEDI_BATTLE = Chapter(
    name="Jedi Battle",
    episode_number=2,
    chapter_number=4,
    story_characters=(
        "Anakin Skywalker (Padawan)",
        "Mace Windu",
        "Padmé (Clawed)",
        "Obi-Wan Kenobi (Jedi Master)",
        "R2-D2",
    ),
    purchase_characters={
        "Super Battle Droid": 25_000,
        "Jango Fett": 70_000,
        "Boba Fett (Boy)": 5500,
        "Luminara": 28_000,
        "Ki-Adi Mundi": 30_000,
        "Kit Fisto": 35_000,
        "Shaak Ti": 36_000,
        "Aayla Secura": 37_000,
        "Plo Koon": 39_000,
    },
    start_region="Arena",
    start_level="jedi_b",
    regions={
        "Arena": (
            ExitData("Chapter Completion", HasAbility(JEDI), new_level="jedi_status"),
        ),
    },
    minikits={
        "Padmé Pillar Lower Minikit": minikit_data(
            "Arena",
            logic_options(
                base=HasAbility(HIGH_JUMP) & base_can_damage_shielded_droideka,
                normal=HasAbility(HIGH_JUMP),
                moderate=HasAnyAbilities(HIGH_JUMP | JEDI),
            ),
            pickup_name="m_pup7",
        ),
        "Padmé Pillar Upper Minikit": minikit_data(
            "Arena",
            logic_options(
                base=HasAbility(HIGH_JUMP) & base_can_damage_shielded_droideka,
                normal=HasAbility(HIGH_JUMP),
                moderate=HasAnyAbilities(HIGH_JUMP | JEDI),
            ),
            pickup_name="m_pup8",
        ),
        "Two Player Force Gate Minikit": minikit_data(
            "Arena",
            HasAbility(JEDI),
            pickup_name="m_pup9",
        ),
        "Anakin Pillar Lower Minikit": minikit_data(
            "Arena",
            logic_options(
                base=HasAnyAbilities(GRAPPLE | HIGH_JUMP) & base_can_damage_shielded_droideka,
                normal=HasAbility(HIGH_JUMP) | can_grapple,
                moderate=HasAnyAbilities(GRAPPLE | HIGH_JUMP | JEDI),
            ),
            pickup_name="m_pup4",
        ),
        "Anakin Pillar Upper Minikit": minikit_data(
            "Arena",
            logic_options(
                base=HasAnyAbilities(GRAPPLE | HIGH_JUMP) & base_can_damage_shielded_droideka,
                normal=HasAbility(HIGH_JUMP) | can_grapple,
                moderate=HasAnyAbilities(GRAPPLE | HIGH_JUMP | JEDI),
            ),
            pickup_name="m_pup5",
        ),
        "Obi-Wan Pillar Lower Minikit": minikit_data(
            "Arena",
            logic_options(
                # High jump ignores the need to grapple/imperial.
                # Grapple up and activate the Imperial panel to make the platform move.
                base=Or(
                    HasAbility(HIGH_JUMP),
                    HasAllAbilities(GRAPPLE | IMPERIAL),
                ) & base_can_damage_shielded_droideka,
                normal=HasAbility(HIGH_JUMP) | HasAllAbilities(GRAPPLE | IMPERIAL),
                moderate=HasAnyAbilities(HIGH_JUMP | JEDI) | HasAllAbilities(GRAPPLE | IMPERIAL),
            ),
            pickup_name="m_pup2",
        ),
        "Obi-Wan Pillar Upper Minikit": minikit_data(
            "Arena",
            # Same as the lower minikit, but use force to rebuild the second platform to go from the lower minikit
            # platform to the upper minikit platform.
            logic_options(
                base=Or(
                    HasAbility(HIGH_JUMP) & base_can_damage_shielded_droideka,
                    HasAllAbilities(GRAPPLE | IMPERIAL | JEDI),
                ),
                normal=HasAbility(HIGH_JUMP) | HasAllAbilities(GRAPPLE | IMPERIAL | JEDI),
                moderate=HasAnyAbilities(HIGH_JUMP | JEDI),
            ),
            pickup_name="m_pup3",
        ),
        "Access Hatch Minikit": minikit_data(
            "Arena",
            HasAllAbilities(JEDI | SHORTIE),
            pickup_name="m_pup1",
        ),
        "Rebuild Destroyed Pillar Minikit": minikit_data(
            "Arena",
            logic_options(
                # Force to rebuild the pillar. Sith force to make platforms. High jump to get up to the first platform.
                base=HasAllAbilities(SITH | HIGH_JUMP),
                # Force to rebuild the pillar. Then force to un-build two pieces. Double jump to the top of the
                # partially built pillar and then double jump + slam to get the minikit.
                normal=HasAbility(JEDI),
            ),
            pickup_name="m_pup6",
        ),
        "Minikit Hiding Behind Pillar": minikit_data(
            "Arena",
            pickup_name="m_pup10",
        )
    },
    power_brick=LocationData(
        "Arena",
        logic_options(
            base=HasAllAbilities(BOUNTY_HUNTER | CAN_BUILD_BRICKS | CAN_JUMP_NORMAL_HEIGHT),
            normal=can_destroy_close_silver_bricks & HasAllAbilities(CAN_BUILD_BRICKS | CAN_JUMP_NORMAL_HEIGHT),
        ),
    ),
)
