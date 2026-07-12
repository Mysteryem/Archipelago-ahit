from rule_builder.rules import And, Or, True_, False_

from ..macros import (
    CAN_DAMAGE_AT_CLOSE_RANGE,
    CAN_SITH_FORCE,
    CAN_ORIGINAL_TRILOGY_HIGH_JUMP,
    CAN_YODA_CLIP_SKIP_OTHER_CHARACTERS,
    CAN_YODA_CLIP,
    CAN_GRAPPLE,
    HAS_ANY_YODA,
    CAN_DESTROY_CLOSE_SILVER_BRICKS,
    HAS_CAN_REFLECT_BLASTER_BOLTS,
    CAN_DAMAGE_AT_CLOSE_RANGE_NO_BASIC_MELEE,
    HAS_FLUTTER_CHARACTER,
)
from ..option_filters import logic_options, OT_HIGH_JUMP_ENABLED
from ..rules import (
    HasAbility,
    HasAnyAbilities,
    HasAllAbilities,
    HasAnyCharacterExcept,
    HasAbilityExceptCharacters,
)
from ..types import minikit_data, ExitData, Chapter, LocationData

from ...areas import Area
from ...levels import Level

from ....character_ability import *
from ....data.characters import Character

_OTHER_CHARACTERS_THAT_FIT_ABOVE_PORTCULLIS = {
    Character.GONK_DROID,
    Character.PIT_DROID,
    # More difficult to get into the gap, then needs to spam jumps to get through:
    Character.JAWA,
    Character.UGNAUGHT,
    Character.BOBA_FETT_BOY,
    # Jump height seems to be reduced, so is more difficult to get into the gap without triple high jump
    Character.PK_DROID,
}

_HAS_CHARACTER_THAT_FITS_ABOVE_PORTCULLIS = HasAbility(ASTROMECH_DROID) | Character.has_any(
    *_OTHER_CHARACTERS_THAT_FIT_ABOVE_PORTCULLIS,
)

JABBAS_PALACE = Chapter(
    area=Area.JABBASPALACE,
    start_region="Spawn",
    regions={
        "Spawn": (
            ExitData(
                "Far Minikit Platform Left Of Spawn",
                logic_options(
                    base=Or(
                        CAN_SITH_FORCE & CAN_GRAPPLE,
                        # Bodyguard can reach the minikit, but cannot jump back, so is excluded from Base logic.
                        HasAbilityExceptCharacters(HIGH_JUMP, Character.GRIEVOUS_BODYGUARD) & OT_HIGH_JUMP_ENABLED,
                    ),
                    # Allow standing on the Sith Force bricks and double jumping up.
                    # Allow Bodyguard, who cannot jump back.
                    normal=Or(
                        HasAbility(CAN_DOUBLE_JUMP) & CAN_GRAPPLE,
                        CAN_ORIGINAL_TRILOGY_HIGH_JUMP,
                    ),
                    # Allow triple jump, letting slam characters get to the minikit on their own, and letting Bodyguard
                    # get back on its own (actually barely possible event without a triple jump)
                    moderate=Or(
                        HasAnyAbilities(JEDI | CAN_HIGH_JUMP_SLAM),
                        HasAbility(CAN_DOUBLE_JUMP) & CAN_GRAPPLE,
                        CAN_ORIGINAL_TRILOGY_HIGH_JUMP,
                    ),
                )
            ),
            ExitData(
                "Initial Interior",
                logic_options(
                    # It seems that only Blaster Bolts can damage the turrets.
                    # Jump height/building bricks are needed to activate the middle turret.
                    # Base logic also expects CAN_PULL_LEVERS to stop the Gamorrean Guards from spawning.
                    base=HasAllAbilities(BLASTER | CAN_BUILD_BRICKS | CAN_JUMP_HEIGHT_0_37 | CAN_PULL_LEVERS),
                    # Allow reflecting the turrets' blaster bolts back into the turrets.
                    normal=And(
                        HasAbility(BLASTER) | HAS_CAN_REFLECT_BLASTER_BOLTS,
                        Or(
                            HasAllAbilities(CAN_BUILD_BRICKS | CAN_JUMP_HEIGHT_0_37),
                            HasAbility(CAN_DOUBLE_JUMP),
                        )
                    )
                )
            ),
        ),
        "Far Minikit Platform Left Of Spawn": (),
        "Initial Interior": (
            ExitData(
                "Protocol Panel Jailed B'omarr Bonk",
                logic_options(
                    base=HasAllAbilities(CAN_BUILD_BRICKS | PROTOCOL_PANEL),
                    # Allow Yoda Ceiling Clip.
                    hard=Or(
                        HasAllAbilities(CAN_BUILD_BRICKS | PROTOCOL_PANEL),
                        CAN_YODA_CLIP,
                    ),
                ),
            ),
            ExitData(
                "After First Bounty Hunter Door (Using Panel)",
                HasAnyAbilities(BOUNTY_HUNTER | CAN_WEAR_HAT),
            ),
            ExitData(
                "After First Bounty Hunter Door",
                logic_options(
                    # Expect using the panel to open the door.
                    base=False_(),
                    # Allow jumping on the right torch, then jumping to the top of the portcullis with Yoda.
                    moderate=Or(
                        HasAnyAbilities(BOUNTY_HUNTER | CAN_WEAR_HAT),
                        HAS_ANY_YODA,
                    ),
                    # Allow triple jump + character swap to a small character (other than yoda who can do this jump
                    # on his own).
                    hard=Or(
                        HasAnyAbilities(BOUNTY_HUNTER | CAN_WEAR_HAT),
                        HAS_ANY_YODA,
                        And(
                            HasAnyAbilities(CAN_HIGH_JUMP_SLAM | JEDI),
                            _HAS_CHARACTER_THAT_FITS_ABOVE_PORTCULLIS,
                        ),
                    ),
                ),
            )
        ),
        "Protocol Panel Jailed B'omarr Bonk": (),
        "After First Bounty Hunter Door": (
            ExitData(
                "Behind First Astromech Panel Door",
                # I could not manage to Yoda Ceiling Clip through this door.
                HasAbility(ASTROMECH_PANEL),
            ),
            ExitData(
                "Power Brick Upper Area",
                logic_options(
                    base=Or(
                        # Build the block, stand on it, and double jump up.
                        HasAllAbilities(CAN_DOUBLE_JUMP | CAN_BUILD_BRICKS),
                        # Build the block, slide it over the button, and grapple up.
                        HasAllAbilities(GRAPPLE | CAN_PUSH_OBJECTS | CAN_BUILD_BRICKS),
                        CAN_ORIGINAL_TRILOGY_HIGH_JUMP,
                    ),
                    # Allow triple jump up.
                    # Allow 1P2C to have 1 player activate the button, and the other player grapple up.
                    moderate=Or(
                        HasAnyAbilities(JEDI | CAN_HIGH_JUMP_SLAM),
                        HasAllAbilities(CAN_DOUBLE_JUMP | CAN_BUILD_BRICKS),
                        CAN_GRAPPLE,
                        CAN_ORIGINAL_TRILOGY_HIGH_JUMP,
                    ),
                )
            ),
            ExitData(
                "Prison Cells",
                # The panel needs to be built.
                HasAllAbilities(BOUNTY_HUNTER | CAN_BUILD_BRICKS),
                name="Use the second Bounty Hunter panel using a Bounty Hunter",
                new_level=Level.JABBASPALACE_B,
            )
        ),
        "Behind First Astromech Panel Door": (),
        "After First Bounty Hunter Door (Using Panel)": (
            ExitData("After First Bounty Hunter Door"),
            ExitData(
                "Prison Cells",
                # If you could use the first panel, you can use the second panel.
                # The panel needs to be built.
                HasAbility(CAN_BUILD_BRICKS),
                name="Use the second Bounty Hunter panel using the Hat Machine",
                new_level=Level.JABBASPALACE_B,
            ),
        ),
        "Power Brick Upper Area": (),
        "Prison Cells": (
            ExitData(
                "After Second Portcullis, through to Droids Room",
                # The Silver Brick debris does not need to be considered because
                logic_options(
                    # Destroy the object, build it into a platform, and then have P2 AI force the platform into the air.
                    base=HasAllAbilities(JEDI),
                    # Allow high jump from on top of the object, without destroying it.
                    normal=Or(
                        HasAbility(JEDI),
                        And(
                            HasAbilityExceptCharacters(HIGH_JUMP, Character.GRIEVOUS_BODYGUARD),
                            HasAbility(CAN_PULL_LEVERS)
                        ) & OT_HIGH_JUMP_ENABLED,
                    ),
                    # Allow triple jump from on top of the object, without destroying it.
                    moderate=Or(
                        HasAnyAbilities(JEDI),
                        HasAllAbilities(CAN_HIGH_JUMP_SLAM | CAN_PULL_LEVERS),
                        And(
                            HasAbilityExceptCharacters(HIGH_JUMP, Character.GRIEVOUS_BODYGUARD),
                            HasAbility(CAN_PULL_LEVERS)
                        ) & OT_HIGH_JUMP_ENABLED,
                    )
                )
            ),
        ),
        # All characters that can either wear hats or are bounty hunters can destroy the objects holding down the third
        # portcullis, cross the falling grates, and make it to the Droids Room.
        "After Second Portcullis, through to Droids Room": (
            ExitData(
                "Corridor After Droids Room",
                logic_options(
                    base=HasAllAbilities(ASTROMECH_PANEL | PROTOCOL_PANEL),
                    # Stand on the rim of one of the droid 'cages', then Yoda Ceiling Clip past the door.
                    hard=HasAllAbilities(ASTROMECH_PANEL | PROTOCOL_PANEL) | CAN_YODA_CLIP_SKIP_OTHER_CHARACTERS,
                ),
            ),
        ),
        "Corridor After Droids Room": (
            ExitData(
                "Open Area With Ramp For C-3PO",
                True_(),
                er_rule=logic_options(
                    base=HasAbility(ASTROMECH_PANEL),
                    # This level transition is active even without activating the panel, so you can clip to get to it.
                    hard=HasAbility(ASTROMECH_PANEL) | CAN_YODA_CLIP,
                ),
                new_level=Level.JABBASPALACE_D,
            ),
        ),
        "Open Area With Ramp For C-3PO": (
            ExitData(
                "Final Rooms Before Rancor",
                logic_options(
                    # The Exit from "Prison Cells" requires JEDI.
                    # The Exit from "Corridor After Droids Room" requires a PROTOCOL_PANEL character.
                    # "After First Bounty Hunter Door" -> "Prison Cells" requires CAN_BUILD_BRICKS.
                    base=Or(
                        HasAbility(HOVER),
                        CAN_ORIGINAL_TRILOGY_HIGH_JUMP,
                    ),
                    # The Exit from "Prison Cells" requires a CAN_DOUBLE_JUMP character.
                    # The Exit from "Corridor After Droids Room" requires a PROTOCOL_PANEL character.
                    # "After First Bounty Hunter Door" -> "Prison Cells" requires CAN_BUILD_BRICKS.
                    normal=True_(),
                    # If the earlier PROTOCOL_PANEL was skipped through a Yoda Ceiling Clip, that is also fine because
                    # a Yoda Ceiling Clip can skip this panel too.
                    # hard=True_(),
                ),
                er_rule=logic_options(
                    # Jump up to the right from one of the ramp parts (or make the ramp), destroy the two
                    # objects on the right area to spawn the first bridge part and force it into position, then
                    # force the bricks on the wall to complete the bridge.
                    # Then hover across the gap by the Sith Force objects on the wall.
                    # Destroy the objects by the door to reveal bricks for a Protocol Panel, build it and use
                    # the panel to progress.
                    # High jump directly to where the Protocol Panel spawns is allowed.
                    base=And(
                        HasAllAbilities(PROTOCOL_PANEL | CAN_BUILD_BRICKS),
                        CAN_DAMAGE_AT_CLOSE_RANGE,
                        Or(
                            CAN_ORIGINAL_TRILOGY_HIGH_JUMP,
                            HasAllAbilities(JEDI | HOVER)
                        )
                    ),
                    # Allow jumping from a destroyable object to the panel.
                    # Alternatively, allow jumping up the ramp parts and then hovering across gaps to get to the panel.
                    normal=And(
                        HasAllAbilities(PROTOCOL_PANEL | CAN_BUILD_BRICKS),
                        CAN_DAMAGE_AT_CLOSE_RANGE,
                        Or(
                            # There is an object on the ground below the protocol panel, avoid destroying it, stand on
                            # it, and then double jump up to where the panel spawns.
                            HasAbility(CAN_DOUBLE_JUMP),
                            # Push the ramp pieces into steps and jump/flutter up them. Hover across the gaps.
                            And(
                                HasAllAbilities(CAN_PUSH_OBJECTS | HOVER),
                                HasAbility(CAN_JUMP_HEIGHT_0_37) | HAS_FLUTTER_CHARACTER,
                            ),
                        ),
                    ),
                    # Allow hovering up the ramp parts without forcing the tops of each ramp part.
                    moderate=And(
                        HasAllAbilities(PROTOCOL_PANEL | CAN_BUILD_BRICKS),
                        CAN_DAMAGE_AT_CLOSE_RANGE,
                        Or(
                            HasAbility(CAN_DOUBLE_JUMP),
                            And(
                                HasAllAbilities(CAN_PUSH_OBJECTS | HOVER),
                                # The ramp parts have lower collision on the sides/rear, allowing astromechs to hover
                                # to those lower parts and then hover to the top of each step, making it the full way up
                                # the steps. All characters that can push objects can jump at least 0.37, so this is not
                                # actually relevant.
                                HasAnyAbilities(CAN_JUMP_HEIGHT_0_37 | HOVER) | HAS_FLUTTER_CHARACTER,
                            ),
                        ),
                    ),
                    # Allow Yoda Ceiling Clip to bypass the panel entirely. Jump on top of the arch, then clip from
                    # there.
                    hard=And(
                        HasAllAbilities(PROTOCOL_PANEL | CAN_BUILD_BRICKS),
                        CAN_DAMAGE_AT_CLOSE_RANGE,
                        Or(
                            HasAbility(CAN_DOUBLE_JUMP),
                            And(
                                HasAllAbilities(CAN_PUSH_OBJECTS | HOVER),
                                # The ramp parts have lower collision on the sides/rear, allowing astromechs to hover
                                # to those lower parts and then hover to the top of each step, making it the full way up
                                # the steps. All characters that can push objects can jump at least 0.37, so this is not
                                # actually relevant.
                                HasAnyAbilities(CAN_JUMP_HEIGHT_0_37 | HOVER) | HAS_FLUTTER_CHARACTER,
                            ),
                        ),
                    ) | CAN_YODA_CLIP,
                ),
            ),
        ),
        # The Exit from "Prison Cells" requires CAN_PULL_LEVERS, so these final rooms can be a single region.
        "Final Rooms Before Rancor": (
            # Pull the levers to prevent more guards from spawning, and defeat all the guards.
            # Get a Bounty Hunter hat from the hat machine, or use a Bounty Hunter character, and use the panel to enter
            # the Rancor fight.
            ExitData("Rancor Pit", new_level=Level.JABBASPALACE_E),
        ),
        "Rancor Pit": (
            ExitData(
                "Chapter Completion",
                logic_options(
                    # Being able to damage at close range is required from the start. Exiting the Droids Room requires
                    # activating both panel types.
                    base=True_(),
                    # Yoda Ceiling Clips could have skipped the droid panels, so logic needs to check for one of them.
                    hard=HasAnyAbilities(ASTROMECH_PANEL | PROTOCOL_PANEL),
                ),
                er_rule=CAN_DAMAGE_AT_CLOSE_RANGE & Or(
                    HasAllAbilities(CAN_PULL_LEVERS | ASTROMECH_PANEL),
                    HasAllAbilities(CAN_PULL_LEVERS | PROTOCOL_PANEL),
                ),
            ),
        ),
    },
    minikits={
        "Spawn Far Left Minikit": minikit_data(
            "Far Minikit Platform Left Of Spawn",
            pickup_name="mk_2"
        ),
        "Minikit Outside Above Silver Bricks": minikit_data(
            "Spawn",
            logic_options(
                base=And(
                    HasAnyAbilities(CAN_DOUBLE_JUMP | HOVER),
                    CAN_DESTROY_CLOSE_SILVER_BRICKS,
                    CAN_GRAPPLE,
                ),
                # Allow triple jump directly to the minikit by standing on the silver bricks for extra height.
                moderate=Or(
                    HasAnyAbilities(JEDI | CAN_HIGH_JUMP_SLAM),
                    And(
                        HasAnyAbilities(CAN_DOUBLE_JUMP | HOVER),
                        CAN_DESTROY_CLOSE_SILVER_BRICKS,
                        CAN_GRAPPLE,
                    )
                )
            ),
            pickup_name="mk_1",
        ),
        "Minikit Behind Gate With B'Omarr Monk": minikit_data(
            "Protocol Panel Jailed B'omarr Bonk",
            pickup_name="mk_3",
        ),
        "Minikit Behind Astromech Door": minikit_data(
            "Behind First Astromech Panel Door",
            pickup_name="mk_0",
        ),
        "Prison Protocol Room Porthole Minikit": minikit_data(
            "Prison Cells",
            # Triple high jump onto the top of the lid of the chute that spawns Gamorrean Guards is possible, and, from
            # there, a Yoda Ceiling Clip can be performed to get into the left prison cell, but the table cannot be
            # destroyed until the table in the right prison cell has been destroyed. So this already annoying ceiling
            # clip would have to be performed twice. Maybe this could go in Expert+ logic.
            #
            # A BLASTER/JEDI/General Grievous is required at the start of the chapter to get through the main gate, so
            # the beds and porthole can be destroyed. Destroying the porthole opens the door of the Prison Cell,
            # allowing any character that can wear hats to get into the tunnel and reach the silver bricks.
            HasAbility(SHORTIE),
            er_rule=HasAbility(SHORTIE) & CAN_DESTROY_CLOSE_SILVER_BRICKS,
            pickup_name="mk_0",
        ),
        "Explode Prison Wall Minikit": minikit_data(
            "After Second Portcullis, through to Droids Room",
            # Build the explosive then destroy it.
            # Being able to use Bounty Hunter panels is required to reach here (either by having a Bounty Hunter or by
            # being able to wear hats).
            HasAbility(CAN_BUILD_BRICKS),
            er_rule=HasAbility(CAN_BUILD_BRICKS) & CAN_DAMAGE_AT_CLOSE_RANGE_NO_BASIC_MELEE,
            pickup_name="mk_1",
        ),
        "Droid Room Porthole Minikit": minikit_data(
            "After Second Portcullis, through to Droids Room",
            # A BLASTER/JEDI/General Grievous is required at the start of the chapter to get through the main gate.
            # All characters that can wear hats or use bounty hunter panels fit inside the tunnel.
            # Normal+ could also be expected to carry a Bounty Hunter hat all the way here.
            True_(),
            er_rule=CAN_DAMAGE_AT_CLOSE_RANGE & HasAnyCharacterExcept(
                Character.DROIDEKA,
                Character.GENERAL_GRIEVOUS,
            ),
            pickup_name="mk_2",
        ),
        "Sith Force Grate Minikit": minikit_data(
            "Open Area With Ramp For C-3PO",
            CAN_SITH_FORCE,
            pickup_name="mk_0",
        ),
        "Imperial Gate Minikit": minikit_data(
            "Final Rooms Before Rancor",
            logic_options(
                base=HasAnyAbilities(IMPERIAL | CAN_WEAR_HAT),
                # Allow Yoda Clip to skip the panel.
                hard=HasAnyAbilities(IMPERIAL | CAN_WEAR_HAT) | CAN_YODA_CLIP_SKIP_OTHER_CHARACTERS,
            ),
            pickup_name="mk_1",
        ),
        "Rancor Pit Minikit": minikit_data(
            "Rancor Pit",
            logic_options(
                base=CAN_GRAPPLE,
                # Triple jump or high jump to the minikit by jumping from on top of the lever.
                # Exiting "Prison Cells" requires JEDI or HIGH_JUMP, both of which can reach the minikit.
                moderate=True_(),
            ),
            pickup_name="m_pup1"
        ),
    },
    power_brick=LocationData("Power Brick Upper Area"),
    ridables={
        Character.BOMARRMONK: LocationData("Initial Interior"),
    },
)
