from rule_builder.rules import And, Or

from ..macros import (
    CAN_DAMAGE_AT_CLOSE_RANGE,
    CAN_SITH_FORCE,
    CAN_ORIGINAL_TRILOGY_HIGH_JUMP,
    CAN_DESTROY_CLOSE_SILVER_BRICKS,
    CAN_GRAPPLE,
    CAN_YODA_CLIP_SKIP_OTHER_CHARACTERS,
    can_jump_distance_rule,
)
from ..option_filters import logic_options
from ..rules import (
    HasAbility,
    HasAnyAbilities,
    HasAllAbilities,
    HasAnyCharacterExcept,
    HasAbilityCombination,
)
from ..types import minikit_data, ExitData, ChapterHelper, LocationData

from ...areas import Area
from ...levels import Level

from ....character_ability import *
from ....data.characters import Character

# C-3PO, run_speed=0.75 can just barely do this.
# One of the destroyable objects covers one of the tiles quite a bit, which makes it difficult for fluttering characters
# to activate, but Watto can still just barely activate the tile (Geonosian can just destroy the object in the way).
_ONE_P_TWO_C_PLATFORMING_ROOM_FLOOR_TILES = HasAnyCharacterExcept(Character.GONK_DROID)

helper = ChapterHelper(
    area=Area.DEATHSTARESCAPE,
    start_region="Trash Compactor",
)

DEATH_STAR_ESCAPE = helper.make_chapter(
    regions={
        "Trash Compactor": (
            ExitData(
                "First Corridor, And Platforming Room",
                HasAllAbilities(CAN_PULL_LEVERS | CAN_BUILD_BRICKS | CAN_BARELY_JUMP)
            ),
        ),
        "First Corridor, And Platforming Room": (
            ExitData(
                "Large Trash Compactor",
                # The level transition appears to be unusable until the panel is used.
                HasAbility(PROTOCOL_PANEL),
                new_level=Level.DEATHSTARESCAPE_D,
            ),
            ExitData(
                "Platforming Room: Upper Left And Service Car",
                # CAN_PULL_LEVERS is required to reach here, and implies CAN_PUSH_OBJECTS.
                # The worst jump height (0.37) GRAPPLE character can make it to the upper left area with the explosive
                # to push down.
                # Double jump can skip the grappling.
                logic_options(
                    base=HasAbility(GRAPPLE) | HasAbility(CAN_DOUBLE_JUMP),
                    moderate=Or(
                        CAN_GRAPPLE,
                        HasAbility(CAN_DOUBLE_JUMP),
                        HasAbilityCombination(RUN_SPEED_1_18_OR_HIGHER | CAN_JUMP_0_44),
                    )
                ),
            ),
        ),
        "Platforming Room: Upper Left And Service Car": (
            ExitData(
                "Corridor And Tower After First Imperial Panel",
                logic_options(
                    # Get access to the Service Car, destroy the objects on the floor tiles, then drive over the tiles.
                    base=CAN_DAMAGE_AT_CLOSE_RANGE,
                    # Walk over the tiles with two players simultaneously.
                    moderate=CAN_DAMAGE_AT_CLOSE_RANGE | _ONE_P_TWO_C_PLATFORMING_ROOM_FLOOR_TILES,
                ).and_rule(
                    # Use the Imperial Panel.
                    logic_options(
                        # For carrying a hat across, strictly require GRAPPLE to start with because
                        # CAN_WEAR_HAT_AND_DOUBLE_JUMP cannot get a second hat if they mess up.
                        base=HasAnyAbilities(IMPERIAL | CAN_WEAR_HAT_AND_GRAPPLE),
                        # Allow CAN_WEAR_HAT_AND_DOUBLE_JUMP, and just don't mess up, or restart the level if you do.
                        moderate=HasAnyAbilities(IMPERIAL | CAN_WEAR_HAT_AND_GRAPPLE | CAN_WEAR_HAT_AND_DOUBLE_JUMP),
                        # As with getting to the upper left area of the room, this is just enough jump height and run
                        # speed to make it up the extending platform at its lowest, and then have P2 push the spinner to
                        # extend the platform up, carrying the hat to the panel.
                        hard=Or(
                            HasAnyAbilities(IMPERIAL | CAN_WEAR_HAT_AND_GRAPPLE | CAN_WEAR_HAT_AND_DOUBLE_JUMP),
                            # I think Lobot might be the only character this bit of logic applies to.
                            # Other characters either can grapple, double jump, cannot wear hats, or cannot jump high
                            # enough.
                            And(
                                # Ensure enemies can be killed to prevent losing the hat.
                                CAN_DAMAGE_AT_CLOSE_RANGE,
                                HasAbilityCombination(RUN_SPEED_1_18_OR_HIGHER | CAN_JUMP_0_44 | CAN_WEAR_HAT)
                            ),
                        ),
                    ),
                ),
                new_level=Level.DEATHSTARESCAPE_B,
            ),
        ),
        "Large Trash Compactor": (),
        # The corridor through to the bottom of the tower only requires pulling levers and pushing blocks which is
        # required to reach here (pulling levers implies pushing blocks).
        "Corridor And Tower After First Imperial Panel": (
            ExitData(
                "Tower Top",
                logic_options(
                    base=CAN_GRAPPLE,
                    moderate=Or(
                        CAN_GRAPPLE,
                        HasAnyAbilities(JEDI | CAN_HIGH_JUMP_SLAM),
                        # Avoid destroying the objects at the bottom of the tower, then Tarpals and Jar Jar can high
                        # jump off them.
                        CAN_ORIGINAL_TRILOGY_HIGH_JUMP,
                    ),
                ),
            ),
        ),
        "Tower Top": (
            ExitData(
                "After Tower Top Imperial Door",
                logic_options(
                    base=HasAnyAbilities(IMPERIAL | CAN_WEAR_HAT),
                    # Allow Yoda clipping over the door.
                    hard=HasAnyAbilities(IMPERIAL | CAN_WEAR_HAT) | CAN_YODA_CLIP_SKIP_OTHER_CHARACTERS,
                )
            ),
        ),
        "After Tower Top Imperial Door": (
            ExitData(
                "Big Gap Grapple Swinging Room",
                new_level=Level.DEATHSTARESCAPE_C,
            ),
        ),
        "Big Gap Grapple Swinging Room": (
            ExitData(
                "Stormtrooper Corridor Chase, through to Hangar",
                logic_options(
                    base=HasAbility(CAN_WEAR_HAT_AND_GRAPPLE) | HasAllAbilities(GRAPPLE | IMPERIAL),
                    # One of the Stormtroopers across the gap is standing in range of the Imperial Panel. If he attempts
                    # to put his weapon away, he will instead activate the panel.
                    # To do this, aggro the enemies in this room, and then de-aggro by either swapping both characters
                    # to passive characters, or have both players die simultaneously.
                    # If this Stormtrooper is killed, reinforcements appear to continue arriving until the Grapple point
                    # is build, so avoid building it until you get this trick, if needed.
                    moderate=HasAbility(GRAPPLE),
                ),
            ),
        ),
        # Since GRAPPLE is required to reach here, these areas can be the same region.
        "Stormtrooper Corridor Chase, through to Hangar": (
            ExitData(
                "Chapter Completion",
                logic_options(
                    base=HasAllAbilities(PROTOCOL_PANEL | ASTROMECH_PANEL),
                    # All ASTROMECH_PANEL character can jump this distance, so checking for the panel abilities is
                    # pointless:
                    # - Astromech droids can HOVER, which is superior to all jump distance rules.
                    # - 4-LOM has 0.84 jump distance (same as Captain Panaka).
                    # - IG-88 has 0.92 jump distance.
                    hard=can_jump_distance_rule(Character.CAPTAIN_PANAKA),
                ),
                er_rule=logic_options(
                    # Even the worst jumping GRAPPLE characters can reach and push the object on the right.
                    base=HasAllAbilities(PROTOCOL_PANEL | ASTROMECH_PANEL),
                    # There is a fairly well known trick in this level called Falconless where loading the level
                    # containing the Falcon, then going back to the previous level and moving far enough away to
                    # unload the level containing the Falcon (pre-loading the level even earlier), and then going back
                    # and loading the level containing the Falcon again, the level completion trigger of the Falcon's
                    # door will be active even without needing to raise the Falcon and defeat the enemies.
                    hard=Or(
                        HasAllAbilities(PROTOCOL_PANEL | ASTROMECH_PANEL),
                        # Can make it:
                        # - Captain Tarpals (single-jump) (0.90)
                        # - Captain Panaka (0.84)
                        # Cannot make it:
                        # - Dexter Jettster (0.7666)
                        # - Clone (0.7)
                        # - Ewok (0.69)
                        can_jump_distance_rule(Character.CAPTAIN_PANAKA),
                    ),
                ),
            ),
        ),
    },
    minikits={
        "Destroy Silver Bricks Minikit": minikit_data(
            "First Corridor, And Platforming Room",
            # The Minikit does not spawn until the silver bricks are destroyed, so Yoda clipping is useless.
            CAN_DESTROY_CLOSE_SILVER_BRICKS,
            pickup_name="m_pup1",
        ),
        "Access Hatch Minikit Beneath Floor Grate": minikit_data(
            "Platforming Room: Upper Left And Service Car",
            HasAbility(SHORTIE),
            pickup_name="mk_0",
        ),
        "Window Washers Minikit": minikit_data(
            "Corridor And Tower After First Imperial Panel",
            # CAN_PULL_LEVERS and CAN_BUILD_BRICKS are needed at the start of the chapter, and CAN_PULL_LEVERS implies
            # being able to ride vehicles.
            # HasAbility(CAN_RIDE_VEHICLES),
            pickup_name="pup1",
        ),
        "Sith Side Force Minikit": minikit_data(
            "Corridor And Tower After First Imperial Panel",
            logic_options(
                base=CAN_SITH_FORCE,
                # Allow Yoda clip. An IMPERIAL character or a character that can wear hats is required to reach here,
                # and Yodas are neither of those, so having a non-yoda character is guaranteed.
                hard=CAN_SITH_FORCE | CAN_YODA_CLIP_SKIP_OTHER_CHARACTERS,
            ),
            pickup_name="pup2",
        ),
        "Tower High Minikit": minikit_data(
            "Tower Top",
            logic_options(
                base=HasAbility(JEDI),
                # Triple high jump works too.
                moderate=HasAnyAbilities(JEDI | CAN_HIGH_JUMP_SLAM),
            ),
            pickup_name="pup3",
        ),
        "Stormtrooper Chase Start Minikit": minikit_data(
            "Stormtrooper Corridor Chase, through to Hangar",
            pickup_name="pup4",
        ),
        "Reveal Three Berries Minikit": minikit_data(
            "Stormtrooper Corridor Chase, through to Hangar",
            pickup_name="m_pup1",
        ),
        "Stormtrooper Ledge Minikit": minikit_data(
            "Stormtrooper Corridor Chase, through to Hangar",
            logic_options(
                base=HasAbility(JEDI),
                normal=HasAbility(CAN_DOUBLE_JUMP),
                moderate=HasAnyAbilities(CAN_DOUBLE_JUMP | JETPACK),
            ),
            pickup_name="pup3",
        ),
        "Hangar Vader Minikit": minikit_data(
            "Stormtrooper Corridor Chase, through to Hangar",
            logic_options(
                base=HasAbility(BOUNTY_HUNTER),
                hard=HasAbility(BOUNTY_HUNTER) | CAN_YODA_CLIP_SKIP_OTHER_CHARACTERS,
            ),
            pickup_name="pup2",
        ),
        "Hangar Slide Panel Minikit": minikit_data(
            "Stormtrooper Corridor Chase, through to Hangar",
            pickup_name="pup1",
        ),
    },
    power_brick=LocationData(
        "Large Trash Compactor",
        HasAbility(JEDI),
    ),
    ridables={
        Character.SERVICE_CAR: LocationData("Platforming Room: Upper Left And Service Car"),
        Character.GRABBERCONTROL: LocationData("Corridor And Tower After First Imperial Panel"),
    }
)
