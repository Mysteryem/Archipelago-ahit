from rule_builder.rules import And, Or, True_

from ..macros import (
    CAN_SITH_FORCE,
    CAN_USE_DEFLECT_BOLTS,
    CAN_JUMP_DISTANCE_0_77_DEXTER_PLUS,
    CAN_USE_SELF_DESTRUCT,
    CAN_YODA_CLIP,
    CAN_YODA_CLIP_SKIP_OTHER_CHARACTERS,
    CAN_GRAPPLE,
    HAS_ANY_YODA,
    HAS_P2_AI_DOUBLE_JUMP,
)
from ..option_filters import logic_options
from ..rules import HasAbility, HasAllAbilities, HasAnyAbilities, HasAbilityExceptCharacters
from ..types import minikit_data, ExitData, Chapter, LocationData

from ...areas import Area
from ...characters import Character
from ...extras import Extra
from ...levels import Level

from ....character_ability import *

R_LANDING_PAD = "Landing Pad"
R_CLONE_VIEWING_AREA = "Clone Viewing Area"
R_BOUNTY_HUNTER_AREA = "Bounty Hunter Area"
R_LIVING_QUARTERS = "Living Quarters"
R_LIVING_QUARTERS_BEHIND_FORCE_FIELD = "Living Quarters Behind Force Field"
R_OUTSIDE_JANGO_CHASE = "Outside Jango Chase"
R_END_OF_OUTSIDE_JANGO_CHASE = "End Of Outside Jango Chase"
R_INTERIOR_BEFORE_JANGO_FIGHT = "Interior Before Jango Fight"
R_SITH_FORCE_DROID_ROOM = "Sith Force Droid Room"
R_JANGO_FIGHT = "Jango Fight"

DISCOVERY_ON_KAMINO = Chapter(
    area=Area.KAMINO,
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
                    hard=HasAnyAbilities(JEDI | JETPACK),
                ),
                # Yes, the levels are out-of-order, and kamino_b does not exist.
                new_level=Level.KAMINO_D,
            ),
        ),
        R_CLONE_VIEWING_AREA: (
            ExitData(
                R_BOUNTY_HUNTER_AREA,
                logic_options(
                    base=HasAllAbilities(JEDI | BOUNTY_HUNTER),
                    # Ceiling clip to get on the other side of the door.
                    hard=HasAllAbilities(JEDI | BOUNTY_HUNTER) | CAN_YODA_CLIP,
                ),
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
                # JEDI is required to reach here.
                # HasAnyAbilities(CAN_DOUBLE_JUMP | HOVER),
            ),
        ),
        R_END_OF_OUTSIDE_JANGO_CHASE: (
            ExitData(
                R_INTERIOR_BEFORE_JANGO_FIGHT,
                # JEDI and ASTROMECH_PANEL are required to reach here.
                logic_options(
                    base=HasAbility(HOVER),
                    moderate=HasAnyAbilities(HOVER | CAN_TRIPLE_JUMP_GREAT_DISTANCE),
                ),
                er_rule=logic_options(
                    base=HasAllAbilities(JEDI | HOVER | ASTROMECH_PANEL),
                    moderate=And(
                        # Cross the gap.
                        HasAnyAbilities(HOVER | CAN_TRIPLE_JUMP_GREAT_DISTANCE),
                        # Use the panel to open the elevator door.
                        HasAllAbilities(JEDI | ASTROMECH_PANEL),
                    ),
                    hard=And(
                        # Cross the gap.
                        HasAnyAbilities(HOVER | CAN_TRIPLE_JUMP_GREAT_DISTANCE),
                        # Use the panel, or ceiling clip with Yoda from where the studs are above the elevator door.
                        Or(
                            HasAllAbilities(JEDI | ASTROMECH_PANEL),
                            CAN_YODA_CLIP,
                        ),
                    ),
                ),
                new_level=Level.KAMINO_E,
            ),
        ),
        R_INTERIOR_BEFORE_JANGO_FIGHT: (
            # Force the bricks out of the way, use the panel and then defeat Jango Fett.
            ExitData(
                R_JANGO_FIGHT,
                # JEDI and ASTROMECH_PANEL are required to reach here.
                True_(),
                er_rule=logic_options(
                    base=HasAllAbilities(JEDI | ASTROMECH_PANEL),
                    # Allow yoda ceiling clip to bypass the door.
                    hard=Or(
                        HasAllAbilities(JEDI | ASTROMECH_PANEL),
                        CAN_YODA_CLIP,
                    )
                ),
            ),
            ExitData(
                R_SITH_FORCE_DROID_ROOM,
                # JEDI and ASTROMECH_PANEL are required to reach here.
                logic_options(
                    base=HasAbility(SITH),
                    normal=HasAbility(SITH) | Extra.DARK_SIDE.has(),
                    hard=Or(
                        HasAbility(SITH),
                        Extra.DARK_SIDE.has(),
                        # ASTROMECH_PANEL means the player must have at least another character.
                        CAN_YODA_CLIP_SKIP_OTHER_CHARACTERS,
                    ),
                ),
                er_rule=logic_options(
                    base=CAN_SITH_FORCE,
                    # Allow using a Yoda ceiling clip to get into the room.
                    hard=CAN_SITH_FORCE | CAN_YODA_CLIP,
                )
            ),
        ),
        R_JANGO_FIGHT: (
            ExitData(
                "Chapter Completion",
                logic_options(
                    base=HasAbility(IS_NON_GHOST_JEDI),
                    # HasAnyAbilities(IS_NON_GHOST_JEDI | BLASTER) is required to get past the ceiling turrets force
                    # field.
                    normal=True_(),
                    # The ceiling turrets could have been destroyed by characters that can deflect bolts, or the Deflect
                    # Bolts Extra and a character that the turrets will shoot at.
                    moderate=Or(
                        HasAnyAbilities(IS_NON_GHOST_JEDI | BLASTER),
                        # JEDI is also required to reach here, and all IS_NON_GHOST_JEDI are JEDI anyway.
                        Extra.SUPER_JEDI_SLAM.has(),
                        CAN_USE_SELF_DESTRUCT,
                    ),
                ),
                er_rule=logic_options(
                    # During the first hovering phase, Jango will not fire Rockets, so a Ghost jedi cannot hit him.
                    # Expect the intended strategy of a Jedi.
                    base=HasAbility(IS_NON_GHOST_JEDI),
                    # Allow Blaster characters.
                    normal=HasAnyAbilities(IS_NON_GHOST_JEDI | BLASTER),
                    moderate=Or(
                        HasAnyAbilities(IS_NON_GHOST_JEDI | BLASTER),
                        # todo?: Also allow Grievous/Bodyguard/Tarpals/Imperial Guard on their own, to deflect bolts
                        #  into Jango during the first hovering phase?
                        # Ghost Jedi can hit Jango in the first hovering phase with Super Jedi Slam.
                        HasAnyAbilities(JEDI | CAN_HIGH_JUMP_SLAM) & Extra.SUPER_JEDI_SLAM.has(),
                        # Self-destruct will also hit Jango if the only character you have is a passive droid.
                        CAN_USE_SELF_DESTRUCT,
                    ),
                ),
            ),
        ),
        R_SITH_FORCE_DROID_ROOM: (),
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
            logic_options(
                # Jedi is required to reach here.
                base=True_(),
                # Hard logic can reach here with a Jetpack character instead.
                hard=HasAbility(JEDI),
            ),
            er_rule=HasAbility(JEDI),
            pickup_name="MINI3",
        ),
        "Four Updrafts Platform Minikit": minikit_data(
            R_BOUNTY_HUNTER_AREA,
            # Jedi is required to reach here.
            True_(),
            er_rule=logic_options(
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
            # Jedi is required to reach here.
            logic_options(
                # Bounty Hunter is required to reach here.
                base=HasAbility(SHORTIE),
                # Bounty Hunter is no longer required, if you can ceiling clip.
                hard=And(
                    # Reach the Access Hatches area.
                    HasAbility(BLASTER) | Character.GENERAL_GRIEVOUS.has(),
                    # Actually get the minikit.
                    HasAbility(SHORTIE) | CAN_YODA_CLIP_SKIP_OTHER_CHARACTERS,
                )
            ),
            er_rule=logic_options(
                # AI P2 will only use Jedi/High-Jump and Astromech Hover, so Jetpack Hover is not allowed here because
                # then 1P2C would be required.
                base=(HAS_P2_AI_DOUBLE_JUMP | HasAbility(ASTROMECH_DROID)) & HasAllAbilities(BLASTER | SHORTIE),
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
                    HasAbility(BLASTER) | Character.GENERAL_GRIEVOUS.has(),
                    HasAbility(SHORTIE),
                ),
                # Instead of using a vent, Yoda ceiling clip over the top of the machine and access the minikit from
                # behind.
                hard=And(
                    HasAnyAbilities(CAN_DOUBLE_JUMP | HOVER | CAN_JUMP_DISTANCE_0_69),
                    HasAbility(BLASTER) | Character.GENERAL_GRIEVOUS.has(),
                    HasAbility(SHORTIE) | CAN_YODA_CLIP_SKIP_OTHER_CHARACTERS,
                ),
            ),
            pickup_name="MINI04",
        ),
        "Mosaic Vending Machine Minikit": minikit_data(
            R_LIVING_QUARTERS,
            # Jedi is required to reach here.
            True_(),
            er_rule=logic_options(
                base=HasAbility(JEDI),
                # Swap to Droideka while as close to the Minikit as possible. Stud Magnet isn't even needed.
                moderate=Or(
                    HasAbility(JEDI),
                    HasAbility(CAN_JUMP_HEIGHT_0_37) & Character.DROIDEKA.has(),
                ),
            ),
            pickup_name="mkvend",
        ),
        "Two Player Triple Buttons Minikit": minikit_data(
            R_LIVING_QUARTERS_BEHIND_FORCE_FIELD,
            # Jedi is required to reach here.
            True_(),
            er_rule=logic_options(
                # A higher than normal jump is required to get into the alcove that the minikit is in.
                base=HasAbility(CAN_DOUBLE_JUMP),
                # Allow characters with a slightly higher jump.
                normal=HasAbility(CAN_JUMP_0_44),
                # Allow stormtrooper flop for a tiny bit of extra height.
                # Allow Taun We and Lama Su, who only have a basic jump height, but can make this jump anyway, sort of
                # sliding up the wall when holding forwards on the controller.
                moderate=Or(
                    HasAnyAbilities(CAN_JUMP_0_44 | CAN_FLOP_JUMP),
                    Character.has_any(Character.TAUN_WE, Character.LAMA_SU),
                ),
            ),
            pickup_name="mk3way",
        ),
        "Jango Chase Hover Platform Minikit": minikit_data(
            R_OUTSIDE_JANGO_CHASE,
            logic_options(
                base=HasAbility(HOVER),
                moderate=HasAnyAbilities(HOVER | CAN_TRIPLE_JUMP_GREAT_DISTANCE | CAN_HIGH_JUMP_SLAM),
                # JEDI is required to reach here.
                hard=Or(
                    HasAnyAbilities(HOVER | CAN_TRIPLE_JUMP_GREAT_DISTANCE | CAN_HIGH_JUMP_SLAM),
                    HasAbilityExceptCharacters(RUN_SPEED_1_18_OR_HIGHER,
                                               Character.GEONOSIAN,
                                               Character.WATTO,
                                               Character.YODA,
                                               Character.YODA_GHOST)
                )
            ),
            er_rule=logic_options(
                # Hover across to the platform.
                base=HasAbility(HOVER),
                # Or triple jump across to the platform. Yodas cannot make the jump.
                moderate=HasAnyAbilities(HOVER | CAN_TRIPLE_JUMP_GREAT_DISTANCE | CAN_HIGH_JUMP_SLAM),
                # Or Yoda triple jump across so long as you have a character with decent movement speed to swap to.
                hard=Or(
                    HasAnyAbilities(HOVER | CAN_TRIPLE_JUMP_GREAT_DISTANCE | CAN_HIGH_JUMP_SLAM),
                    And(
                        HasAbility(JEDI),
                        # Geonosian and Watto only have high movement speed while fluttering, their default movement
                        # speed (which corresponds to their air speed after swapping to them in this case), is very
                        # slow.
                        HasAbilityExceptCharacters(RUN_SPEED_1_18_OR_HIGHER,
                                                   Character.GEONOSIAN,
                                                   Character.WATTO,
                                                   Character.YODA,
                                                   Character.YODA_GHOST)
                    ),
                )
            ),
            pickup_name="mk_1",
        ),
        "Blaster Targets Reward Minikit": minikit_data(
            R_END_OF_OUTSIDE_JANGO_CHASE,
            # Jedi is required to reach here.
            logic_options(
                base=HasAllAbilities(GRAPPLE | PROTOCOL_PANEL),
                normal=And(
                    HasAbility(PROTOCOL_PANEL),
                    HasAbility(GRAPPLE) | Extra.FORCE_GRAPPLE_LEAP.has()
                ),
                moderate=Or(
                    # Self Destruct does not work because the moving platform is not safe ground, so, after
                    # exploding, you respawn back on the ground.
                    # Hitting the targets with an ewok is a bit annoying, but doable.
                    HasAbility(PROTOCOL_PANEL) & HasAnyAbilities(BLASTER | WEAPON_EWOK),
                    # Jump up to the slightly raised part of the machine the minikit is in, and then swap to
                    # Droideka to grab the minikit through the door of the machine. Stud Magnet is not required.
                    Character.DROIDEKA.has(),
                ),
            ),
            er_rule=logic_options(
                base=CAN_GRAPPLE & HasAbility(PROTOCOL_PANEL),
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
                        Character.DROIDEKA.has(),
                    )
                ),
            ),
            pickup_name="mk_0",
        ),
        "Dark Side Droid Room Minikit": minikit_data(
            R_SITH_FORCE_DROID_ROOM,
            # JEDI is required to reach here.
            # ASTROMECH_PANEL is required to reach here.
            logic_options(
                base=HasAbility(SITH),
                normal=HasAbility(SITH) | Extra.DARK_SIDE.has(),
                hard=Or(
                    HasAbility(SITH) | Extra.DARK_SIDE.has(),
                    HAS_ANY_YODA,
                ),
            ),
            er_rule=logic_options(
                base=CAN_SITH_FORCE,
                # Yoda's weird collision can grab it through the force field, no character swapping required.
                hard=CAN_SITH_FORCE | HAS_ANY_YODA,
            ),
            pickup_name="m_pup1",
        )
    },
    power_brick=LocationData(R_LIVING_QUARTERS, HasAbility(IMPERIAL)),
)
