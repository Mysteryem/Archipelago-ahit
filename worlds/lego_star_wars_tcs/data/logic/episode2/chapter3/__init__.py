from rule_builder.rules import And, Or, Has, HasAny

from ...macros import (
    can_grapple,
    base_can_damage_at_close_range,
    can_damage_at_close_range,
    can_deflect_bolts,
    can_damage_shielded_droideka,
    can_activate_close_target,
)
from ...option_filters import logic_options
from ...rules import HasAbility, HasAllAbilities, HasAnyAbilities
from ...types import minikit_data, ExitData, Chapter, LocationData

from .....character_ability import *


DROID_FACTORY = Chapter(
    name="Droid Factory",
    episode_number=2,
    chapter_number=3,
    story_characters=(
        "Anakin Skywalker (Padawan)",
        "C-3PO",
        "Padmé (Geonosis)",
        "R2-D2",
    ),
    purchase_characters={
        "Geonosian": 20_000,
        "Battle Droid (Geonosis)": 8500,
    },
    start_region="Entrance Corridor",
    start_level="factory_a",
    regions={
        "Entrance Corridor": (
            ExitData(
                "Factory Conveyor",
                logic_options(
                    # The Geonosians must be killed to proceed.
                    base=base_can_damage_at_close_range,
                    # Allow Self Destruct.
                    normal=can_damage_at_close_range,
                    # Allow Deflect Bolts.
                    moderate=can_damage_at_close_range | can_deflect_bolts,
                ),
                new_level="factory_b",
            ),
        ),
        "Factory Conveyor": (
            ExitData(
                "After Factory Conveyor",
                logic_options(
                    # No fancy tricks, just outrun the conveyor enough to pass under the crusher.
                    # There is a Droideka in the middle that base logic is expected to be able to defeat.
                    base=HasAbility(RUN_SPEED_0_9_OR_HIGHER) & can_damage_shielded_droideka,
                    # Yoda/Yoda (Ghost) can attack to move faster.
                    # Boba Fett (Boy) can safely jump beneath the crusher, whereas other slow characters appear to be
                    # unable to, instead hitting the crusher's hurtbox and dying.
                    normal=Or(
                        HasAnyAbilities(RUN_SPEED_0_9_OR_HIGHER | JEDI),
                        Has("Boba Fett (Boy)")
                    ),
                    # All characters can walk around crushers by hugging the edge of the conveyor, except Gonk Droid,
                    # who is unable to walk over the slight increases in height between each flap along the edge of the
                    # conveyor.
                    # At moderate, we also expect jumping on the collapsing flaps to go around the crushers, potentially
                    # needing to restart the level if messing up.
                    moderate=Or(
                        HasAnyAbilities(RUN_SPEED_0_9_OR_HIGHER | CAN_BARELY_JUMP),
                        # HasAny(*(c for c in NON_VEHICLE_CHARACTER_BY_INDEX.values()
                        #        if c.is_sendable
                        #        and CAN_PASS_UNDER_DROID_FACTORY_CRUSHERS not in c.abilities
                        #        and JEDI not in c.abilities
                        #        and c.name != "Gonk Droid"))
                        HasAny("C-3PO", "PK Droid", "Pit Droid", "TC-14")
                    ),
                    # Even Gonk Droid can actually move past the crushers because the trigger for the conveyor flaps
                    # collapsing does not extend all the way along the flap, so hugging the top of the flaps allows for
                    # walking along the flaps without them collapsing. The issue is that messing this up and causing
                    # *any* flap to drop requires restarting the level, and doing this sucks in general because of how
                    # slow Gonk Droid is.
                    # expert=True_(),
                ),
            ),
        ),
        "After Factory Conveyor": (
            ExitData(
                "Color Mixing Room",
                logic_options(
                    # JEDI is definitely not needed, but I can't imagine it not being intended.
                    # GRAPPLE implies BLASTER.
                    base=HasAllAbilities(JEDI | GRAPPLE | BLASTER | IMPERIAL),
                    normal=And(
                        HasAnyAbilities(CAN_DOUBLE_JUMP | HOVER),
                        # Despite being a target, it is just a regular destroyable object.
                        can_damage_at_close_range,
                        HasAbility(IMPERIAL),
                    ),
                ),
            ),
            ExitData(
                "Furnace Start",
                logic_options(
                    # Force a fan and then float up.
                    base=HasAbility(JEDI),
                    # From the entrance to the Color Mixing Room, jetpack hover across.
                    normal=HasAnyAbilities(JEDI | JETPACK),
                    # Triple jump can also get up.
                    # The grapple point from the entrance to the Color Mixing Room can be stood on, so double jump onto
                    # it (only non-slam high jump is relevant here) and then astromech hover across.
                    moderate=Or(
                        HasAnyAbilities(JEDI | JETPACK | CAN_HIGH_JUMP_SLAM),
                        HasAllAbilities(CAN_DOUBLE_JUMP | HOVER),
                    ),
                ),
                new_level="factory_d",
            ),
        ),
        "Color Mixing Room": (),
        "Furnace Start": (
            ExitData(
                "After First Crucible Puzzle",
                logic_options(
                    base=Or(
                        # Activate the first two targets by grappling up to them and shooting the targets, then jump off
                        # the now moving crucible to get to the upper area.
                        HasAbility(GRAPPLE),
                        # Skip the first two targets and hover to the second, where objects must be destroyed to spawn
                        # a third target, and then the third target must be activated. A basic jump is required to get
                        # onto the crucible that is now moving up and down.
                        # This is considered intended because P2's AI will hover over here
                        HasAllAbilities(HOVER | JEDI) & can_activate_close_target
                    ),
                    # General Grievous can just high jump up with good timing so that he rolls forwards at the edge of
                    # the platform, but this is too niche of trick for normal imo.
                    normal=Or(
                        # Skip the first two targets, but instead of spawning and activating the third target, the
                        # machinery on the wall with the two lights has collision that can be stood on by jumping with
                        # high jump, which can then jump up to the upper area.
                        HasAllAbilities(HOVER | HIGH_JUMP),
                        And(
                            can_activate_close_target,
                            Or(
                                # Activate the first two targets.
                                can_grapple,
                                # Skip the first two targets [...]
                                HasAllAbilities(HOVER | JEDI)
                            ),
                        ),
                    ),
                    moderate=Or(
                        # Triple jump up to the second target platform and then the upper area, or triple jump across
                        # the hover gap to the third target, and then triple jump up to the upper area.
                        HasAnyAbilities(JEDI | CAN_HIGH_JUMP_SLAM),
                        # Skip the first two targets, but instead of spawning and activating the third target, the
                        # machinery on the wall with the two lights has collision that can be stood on by jumping with
                        # high jump, which can then jump up to the upper area.
                        HasAllAbilities(HOVER | HIGH_JUMP),
                        # Activate the first two targets. can_grapple is irrelevant because JEDI alone can traverse this
                        # entrance, so can_activate_close_target is also irrelevant because all GRAPPLE have BLASTER.
                        HasAbility(GRAPPLE),
                    ),
                ),
            ),
        ),
        "After First Crucible Puzzle": (
            ExitData(
                "Rolling Platforms Room",
                HasAbility(ASTROMECH_PANEL),
            ),
            ExitData(
                "Lava Room",
                logic_options(
                    base=And(
                        HasAnyAbilities(HOVER | GRAPPLE | CAN_DOUBLE_JUMP),
                        HasAbility(ASTROMECH_PANEL),
                        base_can_damage_at_close_range,
                    ),
                    moderate=Or(
                        HasAnyAbilities(HOVER | GRAPPLE | CAN_DOUBLE_JUMP),
                        HasAny("Geonosian", "Watto"),
                    )
                ),
                new_level="factory_e",
            ),
        ),
        "Rolling Platforms Room": (),
        "Lava Room": (
            ExitData(
                "Geonosian Hive",
                logic_options(
                    # The door has a protocol panel.
                    # Jedi can use the spinning platforms in the centre of the room.
                    # Hover can go basically wherever in this room.
                    # Grapple can take the outer route.
                    base=HasAbility(PROTOCOL_PANEL) & HasAnyAbilities(JEDI | HOVER | GRAPPLE),
                    # Jar Jar, Tarpals and Grievous can double jump across the spinning platforms.
                    # Grievous' Bodyguard also barely can, but jumping to the middle platform along the outside is
                    # easier (which Jedi can also jump to from the spinning platforms).
                    normal=HasAbility(PROTOCOL_PANEL) & HasAnyAbilities(JEDI | HOVER | GRAPPLE | HIGH_JUMP),
                ),
                new_level="factory_f",
            ),
        ),
        "Geonosian Hive": (
            ExitData(
                "Force Fields Maze Room",
                logic_options(
                    base=base_can_damage_at_close_range,
                    normal=can_damage_at_close_range,
                ),
            ),
            ExitData(
                "Geonosian Hive Across Lava",
                logic_options(
                    # Grapple up to the cave support thing and destroy it, force the platform and then jump across.
                    base=HasAllAbilities(GRAPPLE | JEDI),
                    normal=Or(
                        # Shoot the cave support thing from afar to avoid needing GRAPPLE.
                        HasAllAbilities(BLASTER | JEDI),
                        # Grapple up to the cave support thing, shoot it, and then hover across from the higher area.
                        And(
                            # Grapple or high jump up to the cave support thing and destroy it, then hover across.
                            Or(
                                HasAbility(GRAPPLE),
                                HasAbility(HIGH_JUMP) & can_damage_at_close_range,
                            ),
                            HasAbility(HOVER),
                        ),
                        # JETPACK implies GRAPPLE and HOVER, so JETPACK does not need to be checked explicitly.
                        # # JETPACK hover can actually just cross the entire gap.
                        # HasAbility(JETPACK),
                    ),
                    moderate=Or(
                        # JEDI/Grievous can triple jump up to the cave support now and just triple jump across the lava.
                        HasAbility(CAN_TRIPLE_JUMP_GREAT_DISTANCE),
                        And(
                            # Grapple or high jump up to the cave support thing and destroy it, then hover across.
                            Or(
                                HasAbility(GRAPPLE),
                                HasAbility(HIGH_JUMP) & can_damage_at_close_range,
                            ),
                            HasAbility(HOVER),
                        ),
                    ),
                ),
            ),
        ),
        "Force Fields Maze Room": (),
        "Geonosian Hive Across Lava": (
            ExitData(
                "Twin Conveyor Room",
                HasAbility(PROTOCOL_PANEL),
                new_level="factory_g",
            ),
        ),
        "Twin Conveyor Room": (
            ExitData(
                "Obi-Wan Holding Cell Room",
                HasAllAbilities(JEDI | ASTROMECH_PANEL),
            ),
        ),
        "Obi-Wan Holding Cell Room": (
            ExitData(
                "Chapter Completion",
                # Impossible to get in here without JEDI.
                # HasAbility(JEDI),
                new_level="factory_status",
            ),
        ),
    },
    minikits={
        "Minikit Behind Spawn Camera": minikit_data(
            "Entrance Corridor",
            pickup_name="m_pup1",
        ),
        "Entrance Corridor Right Alcove Minikit": minikit_data(
            "Entrance Corridor",
            logic_options(
                base=HasAbility(CAN_JUMP_NORMAL_HEIGHT),
                normal=HasAbility(CAN_BARELY_JUMP),
            ),
            pickup_name="m_pup2",
        ),
        "Conveyor Start Access Hatch Minikit": minikit_data(
            "Factory Conveyor",
            logic_options(
                # While it may become missable without restarting the chapter if the platform retracts before grabbing
                # this minikit, it is right towards the start of the chapter, and this is probably the developer
                # intended solution.
                base=HasAllAbilities(CAN_DOUBLE_JUMP | SHORTIE),
                # High jump can skip needing to use the Access Hatch.
                normal=Or(
                    HasAbility(HIGH_JUMP),
                    And(
                        HasAnyAbilities(JETPACK | CAN_DOUBLE_JUMP),
                        HasAbility(SHORTIE),
                    )
                ),
                # Triple jump gets more height than high jump, so all double jumpers can skip using the Access Hatch.
                moderate=Or(
                    HasAbility(CAN_DOUBLE_JUMP),
                    HasAllAbilities(JETPACK | SHORTIE),
                ),
            ),
            pickup_name="mk_0",
        ),
        "Color Mixing Minikit": minikit_data(
            "Color Mixing Room",
            HasAbility(ASTROMECH_PANEL),
            pickup_name="mk_1",
        ),
        "Minikit After First Crucibles": minikit_data(
            "After First Crucible Puzzle",
            pickup_name="mk_0",
        ),
        "Rolling Platforms Minikit": minikit_data(
            "Rolling Platforms Room",
            pickup_name="mk_1",
        ),
        "Lava Room Minikit": minikit_data(
            "Lava Room",
            logic_options(
                base=HasAbility(GRAPPLE),
                # JEDI/HIGH_JUMP can jump from the corner of a spinning platform.
                normal=can_grapple | HasAbility(HIGH_JUMP),
            ),
            pickup_name="m_pup1",
        ),
        "High Minikit Inside Hive Wall": minikit_data(
            "Geonosian Hive",
            logic_options(
                # The jump is pretty tight, but seems to be intended.
                base=HasAllAbilities(JEDI | HIGH_JUMP),
                # Triple high jump straight up.
                moderate=HasAllAbilities(JEDI | HIGH_JUMP) | HasAbility(CAN_HIGH_JUMP_SLAM),
            ),
            pickup_name="mk_1",
        ),
        "Minikit Behind Droidekas Across Lava": minikit_data(
            "Geonosian Hive Across Lava",
            pickup_name="mk_0",
        ),
        "High Minikit In Twin Conveyor Room": minikit_data(
            "Twin Conveyor Room",
            logic_options(
                # Activate the left conveyor, force to build the platform, then high jump from the top after P2 has used
                # force to extend the platform.
                base=HasAllAbilities(JEDI | ASTROMECH_PANEL | HIGH_JUMP),
                normal=And(
                    HasAllAbilities(JEDI | ASTROMECH_PANEL),
                    Or(
                        HasAbility(HIGH_JUMP),
                        # Double jump slam with Stud Magnet active can reach the minikit.
                        Has("Stud Magnet")
                    ),
                ),
                # Triple jump reaches higher than high jump.
                moderate=Or(
                    HasAllAbilities(JEDI | ASTROMECH_PANEL),
                    # Stand on one of the astromech panel blocks for a bit of extra height, then triple high jump to the
                    # minikit.
                    HasAbility(CAN_HIGH_JUMP_SLAM),
                )
            ),
            pickup_name="m_pup1",
        )
    },
    power_brick=LocationData(
        "Force Fields Maze Room",
        logic_options(
            # Complete the maze the intended way.
            base=HasAbility(ASTROMECH_PANEL),
            # Triple high jump over the force field walls.
            moderate=HasAnyAbilities(ASTROMECH_PANEL | CAN_HIGH_JUMP_SLAM),
            # Jedi triple jump can also just barely get over the walls with a near max height triple jump.
            # This maybe could be in moderate logic, but feels surprisingly difficult, so is only in hard logic
            # currently.
            hard=HasAnyAbilities(ASTROMECH_PANEL | CAN_HIGH_JUMP_SLAM | JEDI),
        )
    ),
)
