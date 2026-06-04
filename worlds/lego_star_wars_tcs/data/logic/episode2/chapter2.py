from rule_builder.rules import And, Or, Has, HasAny

from ..macros import CAN_SITH_FORCE, CAN_USE_DEFLECT_BOLTS, CAN_JUMP_DISTANCE_0_77_DEXTER_PLUS
from ..option_filters import logic_options
from ..rules import HasAbility, HasAllAbilities, HasAnyAbilities
from ..types import minikit_data, ExitData, Chapter, LocationData

from ...areas import Area
from ...levels import Level

from ....character_ability import *

NAME = "Discovery On Kamino"

R_LANDING_PAD = "Landing Pad"
R_CLONE_VIEWING_AREA = "Clone Viewing Area"
R_BOUNTY_HUNTER_AREA = "Bounty Hunter Area"
R_LIVING_QUARTERS = "Living Quarters"
R_LIVING_QUARTERS_BEHIND_FORCE_FIELD = "Living Quarters Behind Force Field"
R_OUTSIDE_JANGO_CHASE = "Outside Jango Chase"
R_END_OF_OUTSIDE_JANGO_CHASE = "End Of Outside Jango Chase"
R_INTERIOR_BEFORE_JANGO_FIGHT = "Interior Before Jango Fight"

DISCOVERY_ON_KAMINO = Chapter(
    name=NAME,
    area=Area.KAMINO,
    story_characters=(
        "Obi-Wan Kenobi (Jedi Master)",
        "R4-P17",
    ),
    purchase_characters={
        "Clone": 13_000,
        "Lama Su": 9000,
        "Taun We": 9000,
    },
    start_region=R_LANDING_PAD,
    regions={
        R_LANDING_PAD: (
            ExitData(
                R_CLONE_VIEWING_AREA,
                logic_options(
                    # Force to fix the pylon thing and extend the bridge.
                    base=HasAbility(JEDI),
                    # Hover to near the minikit, then hover to the building entrance.
                    # There is a 'fall plane' on the left of the building entrance, which also extends slightly
                    # outwards, so the final part of the hover needs to approach the entrance platform from the front.
                    moderate=HasAnyAbilities(JEDI | JETPACK),
                ),
                # Yes, the levels are out-of-order, and kamino_b does not exist.
                new_level=Level.KAMINO_D,
            ),
        ),
        R_CLONE_VIEWING_AREA: (
            ExitData(
                R_BOUNTY_HUNTER_AREA,
                HasAllAbilities(JEDI | BOUNTY_HUNTER),
            ),
            ExitData(
                R_LIVING_QUARTERS,
                # Notably, clipping past the door does not allow you to enter kamino_c, the trigger does not load until
                # the astromech panel has been used.
                HasAllAbilities(JEDI | ASTROMECH_PANEL),
                new_level=Level.KAMINO_C,
            ),
        ),
        R_BOUNTY_HUNTER_AREA: (),
        R_LIVING_QUARTERS: (
            ExitData(
                R_LIVING_QUARTERS_BEHIND_FORCE_FIELD,
                logic_options(
                    # Meet Jango, then destroy the robots to leave the room and the two ceiling turrets to lower the
                    # force field.
                    base=HasAnyAbilities(IS_NON_GHOST_JEDI | BLASTER),
                    # Standing close to the robots and turrets can cause deflected bolts to destroy them.
                    # Super Zapper can destroy the robots, but cannot destroy the turrets.
                    moderate=Or(
                        HasAnyAbilities(IS_NON_GHOST_JEDI | BLASTER),
                        CAN_USE_DEFLECT_BOLTS,
                    ),
                ),
            ),
        ),
        R_LIVING_QUARTERS_BEHIND_FORCE_FIELD: (
            # The levels are out-of-order again.
            ExitData(R_OUTSIDE_JANGO_CHASE, new_level=Level.KAMINO_F),
        ),
        R_OUTSIDE_JANGO_CHASE: (
            ExitData(
                R_END_OF_OUTSIDE_JANGO_CHASE,
                HasAnyAbilities(CAN_DOUBLE_JUMP | HOVER),
            ),
        ),
        R_END_OF_OUTSIDE_JANGO_CHASE: (
            ExitData(
                R_INTERIOR_BEFORE_JANGO_FIGHT,
                logic_options(
                    base=HasAllAbilities(JEDI | HOVER | ASTROMECH_PANEL),
                    moderate=And(
                        # Cross the gap.
                        HasAnyAbilities(HOVER | CAN_TRIPLE_JUMP_GREAT_DISTANCE),
                        # Use the panel.
                        HasAnyAbilities(JEDI | ASTROMECH_PANEL),
                    ),
                ),
                new_level=Level.KAMINO_F,
            ),
        ),
        R_INTERIOR_BEFORE_JANGO_FIGHT: (
            # Force the bricks out of the way, use the panel and then defeat Jango Fett.
            ExitData("Chapter Completion", HasAllAbilities(JEDI | ASTROMECH_PANEL)),
        )
    },
    minikits={
        "Minikit Above Landing Pad Platform": minikit_data(
            R_LANDING_PAD,
            logic_options(
                # Force the gears, then high jump to reach the minikit.
                base=HasAllAbilities(JEDI | HIGH_JUMP),
                # Force the gears, then stand on the gears, and double jump + slam to reach the minikit.
                # Double jump + slam from beneath the minikit also works when Stud Magnet is enabled.
                normal=HasAbility(JEDI),
            ),
            pickup_name="MINI01",
        ),
        "Floating Platform Minikit": minikit_data(
            R_LANDING_PAD,
            logic_options(
                base=HasAbility(HOVER),
                # Triple jump across the gap.
                moderate=HasAnyAbilities(HOVER | CAN_TRIPLE_JUMP_GREAT_DISTANCE),
                # By swapping to a character with higher air speed after triple jumping, it is just barely possible to
                # triple jump across this gap as Yoda/Yoda (Ghost). This is not currently included in the logic.
            ),
            pickup_name="MINI02",
        ),
        "Six Walkway Lights Minikit": minikit_data(
            R_CLONE_VIEWING_AREA,
            HasAbility(JEDI),
            pickup_name="MINI3",
        ),
        "Four Updrafts Platform Minikit": minikit_data(
            R_BOUNTY_HUNTER_AREA,
            logic_options(
                # Double jump across the platforms and then force the small platform out, to use to reach the minikit.
                # HOVER/CAN_JUMP_DISTANCE_0_77_DEXTER_PLUS/CAN_DOUBLE_JUMP can jump across the circular platforms, but
                # HOVER/'can jump slighter further'(CAN_JUMP_DISTANCE_0_84 + CAN_JUMP_0_44)/CAN_DOUBLE_JUMP
                # is needed to jump to the platform where the minikit is. CAN_JUMP_DISTANCE_0_84 just barely makes the
                # jump, so can_jump_distance_rule(0.9) is more appropriate.
                # Note that the AI P2 will only use JEDI/HIGH_JUMP/Astromech Droid to cross the circular platforms, but
                # we don't have a good way to logically check for just Astromech Hover and not Jetpack Hover currently.
                base=HasAbility(JEDI),
                # High triple jump can reach the minikit without needing to force the small platform out.
                moderate=HasAnyAbilities(JEDI | CAN_HIGH_JUMP_SLAM),
            ),
            pickup_name="MINI05",
        ),
        "Five Access Hatches Minikit": minikit_data(
            R_BOUNTY_HUNTER_AREA,
            logic_options(
                base=HasAnyAbilities(CAN_DOUBLE_JUMP | ASTROMECH_DROID) & HasAllAbilities(BLASTER | SHORTIE),
                moderate=And(
                    Or(
                        # Optimise the CAN_JUMP_DISTANCE_0_84 from CAN_JUMP_DISTANCE_0_77_DEXTER_PLUS into the
                        # HasAnyAbilities.
                        HasAnyAbilities(CAN_DOUBLE_JUMP | HOVER | CAN_JUMP_DISTANCE_0_84),
                        Has("Dexter Jettster"),
                    ),
                    HasAbility(BLASTER) | Has("General Grievous"),
                    HasAbility(SHORTIE),
                ),
            ),
            er_rule=logic_options(
                # AI P2 will only use Double Jump and Astromech Hover, so Jetpack Hover is not allowed here because then
                # 1P2C would be required.
                base=HasAnyAbilities(CAN_DOUBLE_JUMP | ASTROMECH_DROID) & HasAllAbilities(BLASTER | SHORTIE),
                # Allow jumping across the platforms with normal jump distance (may require 1P2C).
                # Jetpack Hover would work too (potentially requiring 1P2C), but both Jango and Boba have normal jump
                # distance.
                # General Grievous's triple jump can skip needing a BLASTER character to extend the bridge.
                # todo: It seems to be possible to grab this minikit with Droideka + Yoda + maybe Stud Magnet, but it
                #  seems inconsistent.
                # The distance from the start area to the first platform is about 0.9376
                # Ewok (0.69) and Clone (0.7) cannot jump across the platforms.
                # Dexter can make it with a good jump.
                moderate=And(
                    HasAnyAbilities(CAN_DOUBLE_JUMP | HOVER) | CAN_JUMP_DISTANCE_0_77_DEXTER_PLUS,
                    HasAbility(BLASTER) | Has("General Grievous"),
                    HasAbility(SHORTIE),
                ),
                # # Instead of using a vent, Yoda ceiling clip over the top of the machine and access the minikit from
                # # behind.
                # hard=And(
                #     HasAnyAbilities(CAN_DOUBLE_JUMP | HOVER | CAN_JUMP_DISTANCE_0_69),
                #     HasAbility(BLASTER) | Has("General Grievous"),
                #     HasAbility(SHORTIE) | HasAny("Yoda", "Yoda (Ghost)"),
                # ),
            ),
            pickup_name="MINI04",
        ),
        "Mosaic Vending Machine Minikit": minikit_data(
            R_LIVING_QUARTERS,
            logic_options(
                base=HasAbility(JEDI),
                # Swap to Droideka while as close to the Minikit as possible. Stud Magnet isn't even needed.
                moderate=Or(
                    HasAbility(JEDI),
                    HasAbility(CAN_JUMP_HEIGHT_0_37) & Has("Droideka"),
                ),
            ),
            pickup_name="mkvend",
        ),
        "Two Player Triple Buttons Minikit": minikit_data(
            R_LIVING_QUARTERS_BEHIND_FORCE_FIELD,
            logic_options(
                # A higher than normal jump is required to get into the alcove that the minikit is in.
                base=HasAbility(CAN_DOUBLE_JUMP),
                # Allow characters with a slightly higher jump.
                normal=HasAbility(CAN_JUMP_0_44),
                # Allow stormtrooper flop for a tiny bit of extra height.
                # Allow Taun We and Lama Su, who only have a basic jump height, but can make this jump anyway, sort of
                # sliding up the wall when holding forwards on the controller.
                moderate=Or(
                    HasAnyAbilities(CAN_JUMP_0_44 | CAN_FLOP_JUMP),
                    HasAny("Taun We", "Lama Su")
                ),
            ),
            pickup_name="mk3way",
        ),
        "Jango Chase Hover Platform Minikit": minikit_data(
            R_OUTSIDE_JANGO_CHASE,
            logic_options(
                # Hover across to the platform.
                base=HasAbility(HOVER),
                # Or triple jump across to the platform. Yodas cannot make the jump. TODO: Check Grievous' Bodyguard.
                moderate=HasAnyAbilities(CAN_TRIPLE_JUMP_GREAT_DISTANCE | HOVER),
            ),
            pickup_name="mk_1",
        ),
        "Blaster Targets Reward Minikit": minikit_data(
            R_END_OF_OUTSIDE_JANGO_CHASE,
            logic_options(
                base=HasAllAbilities(GRAPPLE | PROTOCOL_PANEL),
                moderate=And(
                    # Get to the upper area.
                    HasAnyAbilities(GRAPPLE | CAN_HIGH_JUMP_SLAM),
                    # Access the Minikit.
                    Or(
                        # Self Destruct does not work because the moving platform is not safe ground, so, after
                        # exploding, you respawn back on the ground.
                        # Hitting the targets with an ewok is a bit annoying, but doable.
                        HasAbility(PROTOCOL_PANEL) & HasAnyAbilities(BLASTER | WEAPON_EWOK),
                        # Jump up to the slightly raised part of the machine the minikit is in, and then swap to
                        # Droideka to grab the minikit through the door of the machine. Stud Magnet is not required.
                        Has("Droideka"),
                    )
                ),
            ),
            pickup_name="mk_0",
        ),
        "Dark Side Droid Room Minikit": minikit_data(
            R_INTERIOR_BEFORE_JANGO_FIGHT,
            logic_options(
                base=HasAbility(SITH),
                # Note: AI P2 will only use Sith Force as a SITH, ignoring Dark Side, so using Dark Side here requires
                # Moderate logic for the basic 1P2C usage.
                moderate=CAN_SITH_FORCE,
            ),
            pickup_name="m_pup1",
        )
    },
    power_brick=LocationData(R_LIVING_QUARTERS, HasAbility(IMPERIAL)),
)
