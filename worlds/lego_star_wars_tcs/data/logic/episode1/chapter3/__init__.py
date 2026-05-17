from rule_builder.rules import And, Or, Has

from ...macros import (
    can_grapple,
    can_self_destruct,
    can_destroy_close_silver_bricks,
    can_damage_at_close_range,
    can_sith_force_and_grapple,
    can_sith_force,
)
from ...option_filters import logic_options
from ...rules import HasAbility, HasAllAbilities, HasAnyAbilities, HasAbilitiesExceptCharacters
from ...types import minikit_data, ExitData, Chapter, LocationData

from .....character_ability import *

ESCAPE_FROM_NABOO = Chapter(
    name="Escape From Naboo",
    episode_number=1,
    chapter_number=3,
    start_region="Rooftops Spawn",
    start_level="rescue_a",
    regions={
        "Rooftops Spawn": (
            ExitData(
                "Rooftops Climb",
                logic_options(
                    base=HasAbility(GRAPPLE),
                    normal=can_grapple,
                    moderate=can_grapple | HasAbility(CAN_HIGH_JUMP_SLAM),
                )
            ),
        ),
        "Rooftops Climb": (
            ExitData("Tower", new_level="rescue_b"),
        ),
        "Tower": (
            ExitData(
                "Rooftops After Small Blaster Target Gate",
                logic_options(
                    base=HasAbility(BLASTER),
                    # Ewoks are awkward because they don't auto-target the targets.
                    normal=HasAnyAbilities(BLASTER | WEAPON_EWOK),
                    # Self Destruct works too, though this is probably not well known.
                    moderate=Or(
                        HasAnyAbilities(BLASTER | WEAPON_EWOK),
                        can_self_destruct,
                    ),
                ),
                new_level="rescue_c",
            ),
        ),
        "Rooftops After Small Blaster Target Gate": (
            ExitData(
                "Final Rooftop",
                logic_options(
                    base=HasAbility(BLASTER),
                    # Ewoks are awkward because they don't auto-target the targets.
                    normal=HasAnyAbilities(BLASTER | WEAPON_EWOK),
                    # The platforms that raise up to the targets start slightly raised above the ground, too high for
                    # Astromech Doirds and Droids that cannot jump to get on, so if using Self Destruct to activate
                    # these targets, a Droid that can jump is required.
                    moderate=Or(
                        HasAnyAbilities(BLASTER | WEAPON_EWOK),
                        can_self_destruct & HasAbility(CAN_JUMP_NORMALLY),
                    ),
                ),
                # rescue_d does not exist.
                new_level="rescue_e",
            ),
        ),
        "Final Rooftop": (
            ExitData(
                "Chapter Completion",
                logic_options(
                    # The button to press is in a raised area, and there is a destroyable cover over the chapter
                    # completion.
                    base=HasAllAbilities(CAN_JUMP_NORMALLY | CAN_ATTACK_UP_CLOSE),
                    # Consider Self Destruct for dealing damage.
                    normal=can_damage_at_close_range & HasAbility(CAN_JUMP_NORMALLY),
                    # Astromech droids can just barely get up to the raised area.
                    moderate=can_damage_at_close_range & HasAbility(CAN_BARELY_JUMP),
                ),
                new_level="rescue_status",
            ),
        ),
        "Chapter Completion": (),
    },
    minikits={
        "Stack Boxes Minikit": minikit_data(
            "Rooftops Spawn",
            logic_options(
                # Destroy the doors, force the columns into boxes, stack the boxes and then high jump up.
                base=HasAllAbilities(JEDI | HIGH_JUMP),
                # Triple High Jump can reach the minikit without stacking any boxes.
                moderate=HasAllAbilities(JEDI | HIGH_JUMP) | HasAbility(CAN_HIGH_JUMP_SLAM)
            ),
            pickup_name="mk_0",
        ),
        "Minikit Hidden In Climbing Plants": minikit_data(
            "Rooftops Climb",
            logic_options(
                # Force the wall platforms, high jump up and then hover across.
                base=HasAllAbilities(JEDI | HOVER | HIGH_JUMP),
                # Double jump + slam (no triple jump needed) is enough to reach the kit from the silver objects beneath
                # it. Alternatively, a High Jump from the silver objects works too.
                normal=HasAnyAbilities(JEDI | HIGH_JUMP),
            ),
            pickup_name="mk_1",
        ),
        "Minikit Behind Camera At Roof Tower Spawn": minikit_data(
            "Tower",
            pickup_name="mk_1",
        ),
        "Roof Tower Lower Ledge Minikit": minikit_data(
            "Tower",
            logic_options(
                # Destroy the windows to get into the outside area.
                # If the player jumps down without being able to grapple back up, they have to restart the level, so
                # expect grapple on the base logic difficulty.
                # All grapple users have blasters and can jump.
                base=HasAbility(GRAPPLE),
                # There is a small lip around the upper area, that needs a jump or Astromech hover to cross.
                # TODO: Check if Captain Tarpals can destroy these windows.
                normal=And(
                    can_damage_at_close_range,
                    HasAbility(CAN_BARELY_JUMP),
                ),
                # Droideka can also get over the lip by taking a running start from the furthest right flower bed.
                moderate=And(
                    can_damage_at_close_range,
                    HasAbility(CAN_BARELY_JUMP) | Has("Droideka"),
                ),
            ),
            pickup_name="mk_0",
        ),
        "Sith Force Flowerbeds Minikit": minikit_data(
            "Tower",
            logic_options(
                # Grapple to get up/down the tower/roofing. Hover to cross the gap between roofs. Sith to force the
                # flowers.
                base=HasAllAbilities(SITH | HOVER | GRAPPLE),
                # Dark Side and Force Grapple Leap are considered.
                normal=HasAbility(HOVER) & can_sith_force_and_grapple,
                # Triple jump can cross the gap and replace using grapple to get to the minikit.
                # Note that to continue with the level, one of the flowerbeds in the first lower section cannot be
                # destroyed because it is needed to get enough height to triple jump back up to the higher section and
                # continue with the level.
                moderate=can_sith_force
            ),
            pickup_name="m_pup1",
        ),
        "Minikit After Access Hatch": minikit_data(
            "Rooftops After Small Blaster Target Gate",
            logic_options(
                # Grapple or High Jump up and then use the hatch.
                base=HasAbility(SHORTIE) & HasAnyAbilities(GRAPPLE | HIGH_JUMP),
                # Force Grapple Leap is considered.
                normal=HasAbility(SHORTIE) & (can_grapple | HasAbility(HIGH_JUMP)),
                # Jedi can triple jump up instead of using high jump, so Force Grapple Leap is irrelevant.
                moderate=HasAbility(SHORTIE) & HasAnyAbilities(JEDI | GRAPPLE | HIGH_JUMP),
            ),
            pickup_name="mk_0",
        ),
        "Force All Fences Minikit": minikit_data(
            "Rooftops After Small Blaster Target Gate",
            logic_options(
                # Jedi alone cannot get here, so Grapple or High Jump are needed.
                base=HasAbility(JEDI) & HasAnyAbilities(GRAPPLE | HIGH_JUMP),
                # Also consider Force Grapple Leap.
                normal=And(
                    HasAbility(JEDI),
                    HasAnyAbilities(GRAPPLE | HIGH_JUMP) | Has("Force Grapple Leap")
                ),
                # Triple jump to the fences area.
                moderate=HasAbility(JEDI),
            ),
            pickup_name="MINI_1",
        ),
        "Force Mural Minikit": minikit_data(
            "Rooftops After Small Blaster Target Gate",
            logic_options(
                # All Bounty Hunters can grapple.
                base=HasAllAbilities(BOUNTY_HUNTER | JEDI),
                # Allow using extras to destroy the silver brick windows, and allow Force Grapple Leap.
                normal=And(
                    HasAbility(JEDI),
                    can_destroy_close_silver_bricks,
                    HasAnyAbilities(GRAPPLE | HIGH_JUMP) | Has("Force Grapple Leap")
                ),
                # Triple jump skips any need to grapple.
                moderate=can_destroy_close_silver_bricks & HasAbility(JEDI),
            ),
            pickup_name="m_pup1",
        ),
        "Minikit Under Silver Cover": minikit_data(
            "Final Rooftop",
            logic_options(
                base=HasAbility(BOUNTY_HUNTER),
                # The button to press is in a raised area.
                normal=can_destroy_close_silver_bricks & HasAbility(CAN_JUMP_NORMALLY),
                # The button to press is in a raised area. Astromech droids can just barely get up.
                moderate=can_destroy_close_silver_bricks & HasAbility(CAN_BARELY_JUMP),
            ),
            pickup_name="mk_1",
        ),
        "Stack Plant Pots High Minikit": minikit_data(
            "Final Rooftop",
            logic_options(
                # Stack the plant pots and then double jump to the minikit.
                base=HasAbility(JEDI),
                # Triple high jump can reach the minikit without stacking any plant pots.
                moderate=HasAnyAbilities(JEDI | CAN_HIGH_JUMP_SLAM),
            ),
            pickup_name="mk_0"
        ),
    },
    power_brick=LocationData(
        "Rooftops Climb",
        logic_options(
            # There are Silver brick objects to destroy and Dark Side force flowers to force.
            # All Sith (and Jedi) can build bricks and push blocks.
            base=HasAllAbilities(SITH | BOUNTY_HUNTER),
            # Allow using Dark Side instead of Sith. Yoda (and Yoda (Ghost)) struggle a lot to use force on one of the
            # flowers, so they are excluded.
            normal=And(
                Or(
                    HasAbility(SITH),
                    Has("Dark Side") & HasAbilitiesExceptCharacters(JEDI, "Yoda", "Yoda (Ghost)")
                ),
                can_destroy_close_silver_bricks
            ),
            # The Silver brick objects can actually be destroyed with a slam attack for some reason, so being able to
            # destroy Silver brick objects is not needed.
            moderate=Or(
                HasAbility(SITH),
                Has("Dark Side") & HasAbilitiesExceptCharacters(JEDI, "Yoda", "Yoda (Ghost)")
            )
        )
    ),
)
