from rule_builder.rules import Or, And, HasAny

from ...macros import (
    can_grapple,
    can_destroy_close_silver_bricks,
    can_damage_at_close_range,
)
from ...option_filters import logic_options
from ...rules import HasAbility, HasAllAbilities, HasAnyAbilities
from ...types import minikit_data, ExitData, Chapter, LocationData

from .....character_ability import *

COUNT_DOOKU = Chapter(
    name="Count Dooku",
    episode_number=2,
    chapter_number=6,
    story_characters=(
        "Anakin Skywalker (Padawan)",
        "Obi-Wan Kenobi (Jedi Master)",
        "Yoda",
    ),
    start_region="Landing Pad",
    start_level="dooku_b",
    regions={
        "Landing Pad": (
            ExitData(
                "Dooku Fight",
                HasAbility(JEDI),
                new_level="dooku_c",
            ),
        ),
        "Dooku Fight": (
            ExitData(
                "Chapter Completion",
                HasAbility(JEDI),
                new_level="dooku_status",
            ),
        ),
    },
    minikits={
        "Floating Minikit Before Landing Pad": minikit_data(
            "Landing Pad",
            logic_options(
                # Expect an astromech droid specifically so that the minikit can be grabbed without dying.
                base=HasAbility(ASTROMECH_DROID),
                # Just jump towards it and accept the death.
                normal=HasAnyAbilities(CAN_JUMP_NORMAL_DISTANCE),
            ),
            pickup_name="mk_4",
        ),
        "Grapple Up Cliff Minikit": minikit_data(
            "Landing Pad",
            logic_options(
                base=HasAbility(GRAPPLE),
                # Allow Force Grapple Leap.
                normal=can_grapple,
                # Allow Triple Jump.
                moderate=HasAnyAbilities(GRAPPLE | JEDI | CAN_HIGH_JUMP_SLAM),
            ),
            pickup_name="mk_0",
        ),
        "Force Two Explosives Minikit": minikit_data(
            "Landing Pad",
            HasAbility(JEDI),
            pickup_name="MK2",
        ),
        "Geonosians Battle Room Right Minikit": minikit_data(
            "Landing Pad",
            logic_options(
                # Expect defeating the enemies.
                base=HasAbility(HIGH_JUMP) & can_damage_at_close_range,
                normal=Or(
                    # Ignore the enemies if necessary.
                    HasAbility(HIGH_JUMP),
                    # Allow jetpack hover across from the platform with the door release levers.
                    HasAllAbilities(CAN_DOUBLE_JUMP | JETPACK)
                ),
                moderate=Or(
                    # Allow triple jump.
                    HasAnyAbilities(HIGH_JUMP | JEDI),
                    # Allow jumping up, jetpack hovering to get to the platform with the door release levers, and then
                    # jetpack hovering across to the minikit.
                    HasAbility(JETPACK),
                ),
            ),
            pickup_name="mk_3",
        ),
        "Geonosians Battle Room Left Lower Minikit": minikit_data(
            "Landing Pad",
            logic_options(
                # Expect defeating the enemies.
                base=HasAbility(CAN_DOUBLE_JUMP) & can_damage_at_close_range,
                # Ignore the enemies if necessary.
                normal=HasAbility(CAN_DOUBLE_JUMP),
                # The jump + jetpack hover can just barely make it onto the second platform.
                moderate=HasAnyAbilities(CAN_DOUBLE_JUMP | JETPACK),
            ),
            pickup_name="mk_1",
        ),
        "Geonosians Battle Room Left Upper Minikit": minikit_data(
            "Landing Pad",
            logic_options(
                # Expect defeating enemies.
                base=HasAbility(HIGH_JUMP) & can_damage_at_close_range,
                # Ignore the enemies if necessary.
                normal=HasAbility(HIGH_JUMP),
                # Allow triple jump.
                moderate=HasAnyAbilities(JEDI | HIGH_JUMP),
                # Allow 1P2C jetpack strategy. Use the jetpack the same way in Geonosians Battle Room Right Minikit
                # moderate logic, to get up to the platform with the door release levers.
                # Have P1 hover down to the left, to the rock platform sticking out from the wall.
                # Have P2 hover to the second highest extending platform on the left wall, remaining hovering above the
                # unextended platform.
                # Have P1 hover to the button to activate the extending platforms, then P2 can land on the platform and
                # jump up to the minikit.
                hard=HasAnyAbilities(JEDI | HIGH_JUMP | JETPACK),
            ),
            pickup_name="mk_2",
        ),
        "Shoot Targets Minikit": minikit_data(
            "Dooku Fight",
            logic_options(
                # These targets do not seem to respond to Self Destruct, and instead only work with projectiles.
                base=HasAbility(BLASTER),
                # Ewoks need to jump up right in front of the targets to hit them, they are too high up/blocked by
                # terrain otherwise.
                normal=HasAnyAbilities(BLASTER | WEAPON_EWOK),
            ),
            pickup_name="MK_2TAR",
        ),
        "Platform Minikit Above Collapsed Tower": minikit_data(
            "Dooku Fight",
            logic_options(
                # The jump from the tower looks more like it is intended for a high jump.
                base=HasAllAbilities(JEDI | HIGH_JUMP),
                # Just do the final jump with a jedi instead.
                normal=HasAbility(JEDI),
                # Alternatively, triple high jump can jump up to the minikit platform from the stabable terrain on the
                # wall.
                moderate=HasAnyAbilities(JEDI | CAN_HIGH_JUMP_SLAM),
                # You can continuously jump while under the right edge of the platform the minikit is on, or switch
                # characters to upwarp to the platform.
                # It seems to be possible to also upward from the ground, but it is far less consistent than jumping up
                # to the first bit of standable terrain on the wall, which requires building the tower, a triple jump or
                # a high jump.
                # Yoda's extra triple jump height (from switching from yoda to a non-yoda character) can also just
                # barely manage to get onto this platform from the left side, standing on the standable terrain on the
                # wall.
                hard=HasAbility(CAN_DOUBLE_JUMP),
            ),
            pickup_name="mk_0",
        ),
        "Obscured Minikit Above Collapsed Tower": minikit_data(
            "Dooku Fight",
            # Same as the non-obscured minikit to start with.
            logic_options(
                # Once up to the platform minikit, blast the obstacles obscuring the minikit, and then hover across to
                # collect the minikit.
                base=HasAllAbilities(JEDI | HIGH_JUMP | BLASTER | HOVER),
                # Allow ewoks to destroy the obstacles instead of blasters.
                normal=HasAllAbilities(JEDI | HOVER) & HasAnyAbilities(BLASTER | WEAPON_EWOK),
                # The obstacles don't actually need to be destroyed, hug the left side and the minikit can be grabbed
                # through the obstacles, even without Stud Magnet.
                # Not even a triple jump is required to reach the minikit, just a regular double jump will do.
                moderate=HasAnyAbilities(JEDI | CAN_HIGH_JUMP_SLAM),
                # You can continuously jump while under the right edge of the platform the minikit is on, or switch
                # characters to upwarp to the platform.
                # It seems to be possible to also upward from the ground, but it is far less consistent than jumping up
                # to the first bit of standable terrain on the wall, which requires building the tower, a triple jump or
                # a high jump.
                # Yoda's extra triple jump height (from switching from yoda to a non-yoda character) can also just
                # barely manage to get onto this platform from the left side, standing on the standable terrain on the
                # wall.
            ),
            pickup_name="mk_2",
        ),
        "Minikit Above Solar Sailor": minikit_data(
            "Dooku Fight",
            logic_options(
                base=HasAbility(HIGH_JUMP),
                # Triple jump can replace high jump.
                moderate=HasAnyAbilities(JEDI | HIGH_JUMP),
            ),
            pickup_name="mk_1",
        ),
    },
    power_brick=LocationData(
        "Dooku Fight",
        logic_options(
            # Destroy the silver brick object blocking the access hatch, use the hatch, then grapple to the Power Brick.
            base=HasAllAbilities(BOUNTY_HUNTER | SHORTIE | GRAPPLE),
            # Allow other means of destroying silver bricks, and Force Grapple Leap.
            normal=And(
                can_destroy_close_silver_bricks,
                HasAbility(SHORTIE),
                # High jumpers, except Grievous' Bodyguard, can jump to the Power Brick from the grapple point.
                can_grapple | HasAny("General Grievous", "Jar Jar Binks", "Captain Tarpals"),
            ),
            # Triple jump can skip the access hatch and skip the grapple.
            moderate=Or(
                HasAnyAbilities(JEDI | CAN_HIGH_JUMP_SLAM),
                And(
                    can_destroy_close_silver_bricks,
                    HasAbility(SHORTIE),
                    # There is no need to list Jar Jar Binks and Captain Tarpals individually, instead of HIGH_JUMP,
                    # because the CAN_HIGH_JUMP_SLAM characters can reach the Power Brick on their own.
                    HasAnyAbilities(GRAPPLE | HIGH_JUMP),
                ),
            ),
        ),
    ),
)
