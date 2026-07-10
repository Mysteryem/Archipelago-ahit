from rule_builder.rules import And, Or, True_, False_

from ..macros import (
    CAN_DAMAGE_AT_CLOSE_RANGE,
    CAN_SITH_FORCE,
    CAN_ORIGINAL_TRILOGY_HIGH_JUMP,
    CAN_YODA_CLIP_SKIP_OTHER_CHARACTERS,
    CAN_YODA_CLIP,
    CAN_USE_SELF_DESTRUCT,
    CAN_GRAPPLE,
    HAS_ANY_YODA,
    HAS_GAS_IMMUNE_EXCEPT_GHOSTS,
    HAS_GAS_IMMUNE,
)
from ..option_filters import logic_options, OT_HIGH_JUMP_ENABLED, ot_high_jump_ternary
from ..rules import (
    HasAbility,
    HasAnyAbilities,
    HasAllAbilities,
    HasAnyCharacterExcept,
)
from ..types import minikit_data, ExitData, ChapterHelper, LocationData, MinikitData

from ...areas import Area
from ...extras import Extra
from ...levels import Level

from ....character_ability import *
from ....data.characters import Character


FOUNTAINS_MINIKIT_NAME = "Build Three Fountain Sculptures Minikit"

_HAS_THIN_NON_YODA_CHARACTER = HasAnyCharacterExcept(
    # Yodas:
    Character.YODA,
    Character.YODA_GHOST,

    # Known to be too big:
    Character.DROIDEKA,

    # Untested, but assumed to be too big:
    Character.GENERAL_GRIEVOUS,
    Character.DEXTER_JETTSTER,
)

_helper = ChapterHelper(
    area=Area.CLOUDCITYESCAPE,
    start_region="Spawn",
)

_CORRIDOR_TO_FALCON_LANDING_PAD_TO_FALCON_LANDING_PAD = logic_options(
    base=HasAbility(ASTROMECH_PANEL),
    # There is no ceiling here, and the walls are slightly lower than other nearby areas, so you can
    # triple high jump over the entire door+wall.
    hard=ot_high_jump_ternary(
        uncapped=HasAnyAbilities(ASTROMECH_PANEL | CAN_HIGH_JUMP_SLAM),
        capped=HasAbility(ASTROMECH_PANEL),
    ),
)

BETRAYAL_OVER_BESPIN = _helper.make_chapter(
    intended_completion_path=(
        "After Spawn Stairs",
        "After Bounty Hunter Door",
        "Behind Protocol Droid Door to Elevators",
        "Landing Pad After Imperial Elevator",
        "Building Exterior Magnet Crane Platform",
        "Building Exterior Elevator Upper Platform",
        # todo: Would be better to go to "Building Exterior Platform Above Large Gap" first on Moderate+ because this
        #  skips needing a HOVER character.
        "Building Exterior After Large Gap",
        "Corridor to Falcon Landing Pad",
        "Falcon Landing Pad Bridge Control Room",
        "Falcon Landing Pad Bridge Control Room (Bridge Extended)",
        "Corridor to Falcon Landing Pad (Bridge Extended)",
        "Falcon Landing Pad (Bridge Extended)",
        "Falcon Landing Pad",
    ),
    regions={
        "Spawn": (
            ExitData(
                "After Spawn Stairs",
                logic_options(
                    # Base expects combat.
                    base=HasAbility(CAN_PULL_LEVERS) & CAN_DAMAGE_AT_CLOSE_RANGE,
                    # Remove the combat expectation.
                    # The stairs can also be skipped with Yoda/Ackbar's extra distance double jumps, but they can all
                    # pull levers anyway.
                    normal=HasAbility(CAN_PULL_LEVERS),
                    # Allow skipping the stairs with a triple jump, or using the fact that Jar Jar and Tarpals have
                    # slightly higher movement speed and can just clear the stairs entirely. This means all double jump
                    # characters can skip the stairs.
                    moderate=HasAnyAbilities(CAN_PULL_LEVERS | CAN_DOUBLE_JUMP),
                ),
            ),
        ),
        "After Spawn Stairs": (
            ExitData(
                "After Bounty Hunter Door",
                # Fight Boba Fett, and then he will open the door. This notably causes him to run down the corridor
                # towards his ship, which activates gas in the corridor on the return.
                CAN_DAMAGE_AT_CLOSE_RANGE,
            ),
            ExitData(
                "Behind First Astromech Panel Door",
                logic_options(
                    base=HasAbility(ASTROMECH_PANEL),
                    # Allow Yoda Ceiling clip to skip the door, but exclude bigger characters that get pushed away from
                    # the door because the area to clip through here is quite small.
                    hard=Or(
                        HasAbility(ASTROMECH_PANEL),
                        CAN_YODA_CLIP_SKIP_OTHER_CHARACTERS & _HAS_THIN_NON_YODA_CHARACTER,
                    )
                ),
            ),
        ),
        # It is super easy to get under the ground from here and run around out-of-bounds. Stand on the raised edge by
        # the outside door frame then jump partially around the wall and back into the area on the other side of the
        # door. The death trigger does not extend very far, and the wall is one-way, so you can easily jump under the
        # floor.
        "Behind First Astromech Panel Door": (),
        "After Bounty Hunter Door": (
            # Free Play currently has no reason to go into this room, aside from getting a few studs.
            # ExitData(
            #     "Rebuild C-3PO Room",
            #     logic_options(
            #         base=HasAbility(ASTROMECH_PANEL),
            #         # Yoda can get here all on his own, so it is important to check for another character.
            #         hard=HasAbility(ASTROMECH_PANEL) | CAN_YODA_CLIP,
            #     )
            # ),
            ExitData(
                "Behind Protocol Droid Door to Elevators",
                logic_options(
                    base=HasAbility(PROTOCOL_PANEL),
                    # Yoda can get here all on his own, so it is important to check for another character.
                    hard=HasAbility(PROTOCOL_PANEL) | CAN_YODA_CLIP,
                ),
            ),
            ExitData(
                "After Gas Towards Slave 1 Landing Platform",
                logic_options(
                    # For Base logic only, expect being able to go to the Slave 1 Landing Platform, and then get past
                    # the gas that appears in the corridor when returning from the landing platform.
                    # I think this covers all Droid characters that can walk through gas. Force ghosts can also walk
                    # through gas, but we are not considering that to be the 'developer intended' solution.
                    base=HasAnyAbilities(ASTROMECH_PANEL | PROTOCOL_PANEL | CAN_SELF_DESTRUCT),
                    # Just don't go to the landing platform, and the gas does not spawn.
                    normal=True_(),
                )
            ),
        ),
        "After Gas Towards Slave 1 Landing Platform": (
            ExitData(
                "Slave 1 Landing Platform",
                new_level=Level.CLOUDCITYESCAPE_B,
            ),
        ),
        "Slave 1 Landing Platform": (),
        "Behind Protocol Droid Door to Elevators": (
            ExitData(
                "After Bounty Hunter Elevator",
                logic_options(
                    base=HasAbility(BOUNTY_HUNTER),
                    # General Grievous's triple high jump can get on top of the elevator, which is where the transition
                    # trigger is.
                    hard=Or(
                        HasAbility(BOUNTY_HUNTER),
                        Character.GENERAL_GRIEVOUS.has() & OT_HIGH_JUMP_ENABLED,
                    ),
                )
            ),
            ExitData(
                "Landing Pad After Imperial Elevator",
                logic_options(
                    base=HasAnyAbilities(IMPERIAL | CAN_WEAR_HAT),
                    # General Grievous's triple high jump can get on top of the elevator, which is where the transition
                    # trigger is.
                    hard=Or(
                        HasAnyAbilities(IMPERIAL | CAN_WEAR_HAT),
                        Character.GENERAL_GRIEVOUS.has() & OT_HIGH_JUMP_ENABLED,
                    )
                ),
                new_level=Level.CLOUDCITYESCAPE_C,
            ),
        ),
        "After Bounty Hunter Elevator": (),
        "Landing Pad After Imperial Elevator": (
            ExitData(
                "Building Exterior Magnet Crane Platform",
                logic_options(
                    base=HasAbility(GRAPPLE),
                    normal=HasAnyAbilities(GRAPPLE | CAN_DOUBLE_JUMP),
                )
            ),
        ),
        "Building Exterior Magnet Crane Platform": (
            ExitData(
                "Building Exterior Elevator Upper Platform",
                logic_options(
                    base=CAN_GRAPPLE,
                    moderate=Or(
                        CAN_GRAPPLE,
                        HasAbility(CAN_HIGH_JUMP_SLAM) & OT_HIGH_JUMP_ENABLED
                    ),
                    hard=Or(
                        CAN_GRAPPLE,
                        HasAbility(CAN_HIGH_JUMP_SLAM) & OT_HIGH_JUMP_ENABLED,
                        # Yoda's triple jumps, when switching to a non-Yoda character, give slightly more height than
                        # other Jedi, just enough height to get up here.
                        HAS_ANY_YODA & HasAnyCharacterExcept(Character.YODA, Character.YODA_GHOST),
                    ),
                ),
            ),
        ),
        "Building Exterior Elevator Upper Platform": (
            ExitData(
                "Building Exterior Platform Above Large Gap",
                logic_options(
                    # Only expect using the Grapple point on the other side.
                    base=False_(),
                    # Triple jump up from the destroyable object that prevents C-3PO from progressing in story mode.
                    # If you destroy this by accident, then you'll either need to restart, triple high jump, or triple
                    # jump with Yoda to get up.
                    moderate=HasAnyAbilities(JEDI | CAN_HIGH_JUMP_SLAM),
                )
            ),
            ExitData(
                "Building Exterior After Large Gap",
                # Technically it is possible to triple jump across this gap, but the platform above makes doing so
                # really difficult because you bonk your head on it, preventing you from getting the maximum distance.
                # Fortunately, Moderate+ can just triple jump up to the platform above the gap.
                HasAbility(HOVER),
            ),
        ),
        "Building Exterior Platform Above Large Gap": (
            ExitData(
                "Building Exterior After Large Gap",
                logic_options(
                    # Irrelevant on lower logic difficulties.
                    base=False_(),
                    # Just drop down.
                    moderate=True_(),
                ),
            ),
            ExitData(
                # This is just for the minikit.
                "Building Exterior Air Above Push Blocks",
                logic_options(
                    base=HasAbility(HOVER),
                    normal=HasAnyAbilities(HOVER | CAN_DOUBLE_JUMP),
                ),
            ),
        ),
        "Building Exterior After Large Gap": (
            ExitData(
                # This is just for the minikit.
                "Building Exterior Air Above Push Blocks",
                logic_options(
                    # Only expect hovering from the platform.
                    base=False_(),
                    # Allow high jump, when enabled, and double jump + slam. Stand on one of the push blocks to get
                    # enough height. Stud Magnet helps, and can also work on its own, but is more difficult on its own.
                    normal=ot_high_jump_ternary(
                        uncapped=HasAnyAbilities(JEDI | HIGH_JUMP),
                        capped=HasAnyAbilities(JEDI | CAN_HIGH_JUMP_SLAM),
                    ),
                    # Allow double jump + Stud Magnet (allows Ackbar to reach the minikit).
                    hard=Or(
                        ot_high_jump_ternary(
                            uncapped=HasAnyAbilities(JEDI | HIGH_JUMP),
                            capped=HasAnyAbilities(JEDI | CAN_HIGH_JUMP_SLAM),
                        ),
                        Extra.STUD_MAGNET.has() & HasAbility(CAN_DOUBLE_JUMP),
                    ),
                )
            ),
            ExitData(
                "Corridor to Falcon Landing Pad",
                logic_options(
                    base=HasAbility(PROTOCOL_PANEL),
                    # Allow Yoda Ceiling Clip to bypass the door, but the ceiling to clip through is thin again, so big
                    # characters won't work.
                    hard=Or(
                        HasAbility(PROTOCOL_PANEL),
                        CAN_YODA_CLIP_SKIP_OTHER_CHARACTERS & _HAS_THIN_NON_YODA_CHARACTER,
                    )
                )
            ),
        ),
        # This is just for the minikit.
        "Building Exterior Air Above Push Blocks": (),
        "Corridor to Falcon Landing Pad": (
            ExitData(
                "Falcon Landing Pad Bridge Control Room",
                logic_options(
                    # I don't think there is an in-game hint about passing through gas, but we are considering droids to
                    # be developer intended, but not ghosts.
                    base=HAS_GAS_IMMUNE_EXCEPT_GHOSTS,
                    # Allow ghosts.
                    normal=HAS_GAS_IMMUNE,
                ),
            ),
            ExitData(
                "Sith Force Double Score Zone",
                # I tried, but could not manage to Yoda Ceiling Clip to bypass this door.
                CAN_SITH_FORCE,
            ),
            ExitData(
                "Falcon Landing Pad (Bridge Stowed)",
                _CORRIDOR_TO_FALCON_LANDING_PAD_TO_FALCON_LANDING_PAD,
            )
        ),
        "Sith Force Double Score Zone": (),
        "Falcon Landing Pad Bridge Control Room": (
            ExitData(
                "Falcon Landing Pad Bridge Control Room (Bridge Extended)",
                HasAbility(CAN_PULL_LEVERS),
            ),
        ),
        "Falcon Landing Pad Bridge Control Room (Bridge Extended)": (
            ExitData(
                "Corridor to Falcon Landing Pad (Bridge Extended)",
                logic_options(
                    base=HAS_GAS_IMMUNE_EXCEPT_GHOSTS,
                    normal=HAS_GAS_IMMUNE,
                ),
            ),
            ExitData(
                "Falcon Landing Pad (Bridge Extended)",
                logic_options(
                    base=False_(),
                    # There's no ceiling collision here, so this is not actually a Yoda Ceiling Clip, but instead using
                    # the fact that Yoda's triple jumps give slightly more height than other Jedi triple jumps.
                    # Triple high jumps work too.
                    hard=Or(
                        HasAbility(CAN_HIGH_JUMP_SLAM) & OT_HIGH_JUMP_ENABLED,
                        HAS_ANY_YODA & HasAnyCharacterExcept(Character.YODA, Character.YODA_GHOST),
                    ),
                )
            ),
        ),
        "Corridor to Falcon Landing Pad (Bridge Extended)": (
            ExitData(
                "Falcon Landing Pad (Bridge Extended)",
                _CORRIDOR_TO_FALCON_LANDING_PAD_TO_FALCON_LANDING_PAD,
            ),
        ),
        "Falcon Landing Pad (Bridge Extended)": (
            # This connection is present so that "Falcon Landing Pad (Bridge Stowed)" exits don't need to also be
            # specified here.
            ExitData("Falcon Landing Pad (Bridge Stowed)"),
            # Now that the bridge is extended, just walk across.
            ExitData("Falcon Landing Pad"),
        ),
        "Falcon Landing Pad (Bridge Stowed)": (
            ExitData(
                "Falcon Landing Pad",
                # I tried astromech hover plus shooting the player as they fly across, but was unsuccessful, but it
                # seems close.
                logic_options(
                    # Expect extending the bridge.
                    base=False_(),
                    normal=HasAbility(JETPACK),
                    # Allow triple jump with General Grievous.
                    moderate=Or(
                        HasAbility(JETPACK),
                        Character.GENERAL_GRIEVOUS.has() & OT_HIGH_JUMP_ENABLED,
                    ),
                ),
            ),
            ExitData(
                "Falcon Landing Pad Bridge Control Room",
                logic_options(
                    base=False_(),
                    # The Bridge Control Room's walls are one-way, so you can just jump/hover into it.
                    hard=HasAnyAbilities(CAN_DOUBLE_JUMP | HOVER),
                ),
            ),
        ),
        "Falcon Landing Pad": (
            ExitData(
                "Chapter Completion",
                CAN_DAMAGE_AT_CLOSE_RANGE,
            ),
        ),
    },
    minikits={
        "Spawn Protocol Panel Room Minikit": minikit_data(
            "Spawn",
            # I could not get a ceiling clip to work for this door. There is a more out-of-bounds clip by ceiling
            # clipping out of the corridor and then jumping around beneath the floor, but this should probably require
            # Expert logic.
            HasAbility(PROTOCOL_PANEL),
            pickup_name="pup4",
        ),
        "Boba Fight Room Minikit": minikit_data(
            "After Spawn Stairs",
            HasAbility(JEDI),
            pickup_name="pup3",
        ),
        "Astromech Door Platforming Minikit": minikit_data(
            "Behind First Astromech Panel Door",
            # Note: All jedi can pull levers.
            logic_options(
                base=Or(
                    HasAbility(JEDI),
                    HasAllAbilities(HIGH_JUMP | CAN_PULL_LEVERS) & OT_HIGH_JUMP_ENABLED,
                ),
                normal=Or(
                    HasAnyAbilities(JEDI),
                    CAN_ORIGINAL_TRILOGY_HIGH_JUMP & Or(
                        # Pull the lever and high jump to the second platform, and then to the minikit.
                        HasAbility(CAN_PULL_LEVERS),
                        And(
                            # Hover across to the other side, or double jump with Ackbar.
                            HasAbility(HOVER) | Character.ADMIRAL_ACKBAR.has(),
                            Or(
                                # Double jump + slam to grab the minikit from below.
                                HasAbility(CAN_HIGH_JUMP_SLAM),
                                # Enable Stud Magnet, then High Jump beeneath the minikit to grab it.
                                Extra.STUD_MAGNET.has(),
                            ),
                        ),
                    ),
                ),
                # Allow triple jumps with HIGH_JUMP_SLAM characters.
                moderate=Or(
                    HasAnyAbilities(JEDI | CAN_HIGH_JUMP_SLAM),
                    CAN_ORIGINAL_TRILOGY_HIGH_JUMP & Or(
                        # Pull the lever and high jump to the second platform, and then to the minikit.
                        HasAbility(CAN_PULL_LEVERS),
                        # High Jump across to the other side, enable Stud Magnet, then High Jump to grab the minikit.
                        Extra.STUD_MAGNET.has(),
                    ),
                ),
            ),
            pickup_name="pup2",
        ),
        "Force Chairs Minikit": minikit_data(
            "Behind Protocol Droid Door to Elevators",
            HasAbility(JEDI),
            pickup_name="pup6",
        ),
        "Bounty Hunter Area Force Plant Pots Minikit": minikit_data(
            "After Bounty Hunter Elevator",
            HasAbility(JEDI),
            pickup_name="pup7",
        ),
        "Minikit Behind Camera After Imperial Elevator": minikit_data(
            "Landing Pad After Imperial Elevator",
            pickup_name="pup5",
        ),
        "High Minikit Above Push Blocks": minikit_data(
            "Building Exterior Air Above Push Blocks",
            pickup_name="pup2",
        ),
        "Sith Force Double Score Zone Minikit": minikit_data(
            "Sith Force Double Score Zone",
            # A small jump is required because the minikit is on the table, but if you can get in this room, you can get
            # onto the table.
            pickup_name="pup3",
        ),
        "Millennium Falcon Minikit": minikit_data(
            "Falcon Landing Pad",
            HasAbility(CAN_DOUBLE_JUMP),
            pickup_name="pup4",
        ),
        FOUNTAINS_MINIKIT_NAME: minikit_data(
            "Corridor to Falcon Landing Pad",
            # Obviously, the spawn region is reachable.
            And(
                HasAbility(CAN_BUILD_BRICKS),
                _helper.can_reach_region("After Gas Towards Slave 1 Landing Platform"),
            ),
            er_rule=And(
                HasAbility(CAN_BUILD_BRICKS),
                _helper.can_reach_region("Spawn"),
                _helper.can_reach_region("After Gas Towards Slave 1 Landing Platform"),
            ),
            pickup_name="pup1",
        ),
    },
    power_brick=LocationData(
        "Slave 1 Landing Platform",
        # The Power Brick is on the Slave 1 itself, and is not reachable without a small jump.
        HasAbility(CAN_BARELY_JUMP),
    ),
    ridables={
        Character.CLOUDCAR: LocationData(
            "Behind Protocol Droid Door to Elevators",
            logic_options(
                base=HasAllAbilities(BLASTER | CAN_BUILD_BRICKS),
                # Allow jump + character swap + self-destruct.
                moderate=Or(
                    HasAllAbilities(BLASTER | CAN_BUILD_BRICKS),
                    CAN_USE_SELF_DESTRUCT & HasAbility(CAN_JUMP_HEIGHT_0_37),
                ),
                # It is theoretically possible to deflect bolts into these objects, easier with Exploding Blaster Bolts,
                # but there is just too much RNG involved to be usable in logic.
            ),
        ),
        Character.GRABBERCONTROL: LocationData(
            "Building Exterior Magnet Crane Platform",
        ),
    },
)

# todo: The minikit is logically in two regions in level _A, but level_minikits doesn't actually care about regions, so
#  really, level_minikits should store only the data it needs (the minikit name and the pickup names).
# This is one of the only Minikits in the entire game that is split across multiple levels.
BETRAYAL_OVER_BESPIN.level_minikits[Level.CLOUDCITYESCAPE_A][FOUNTAINS_MINIKIT_NAME] \
    = MinikitData("After Gas Towards Slave 1 Landing Platform", pickup_names=("pup1", "pup5"))
