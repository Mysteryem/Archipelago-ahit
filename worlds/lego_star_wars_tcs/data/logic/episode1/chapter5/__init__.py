from rule_builder.rules import And, Or, Has, HasAny

from ...macros import (
    can_self_destruct,
    can_destroy_close_silver_bricks,
    can_damage_at_close_range,
    can_sith_force,
    base_can_damage_shielded_droideka,
    can_deflect_bolts,
)
from ...option_filters import logic_options
from ...rules import HasAbility, HasAllAbilities, HasAnyAbilities
from ...types import minikit_data, ExitData, Chapter, LocationData

from .....character_ability import *

RETAKE_THEED_PALACE = Chapter(
    name="Retake Theed Palace",
    episode_number=1,
    chapter_number=5,
    story_characters=(
        "Obi-Wan Kenobi",
        "Qui-Gon Jinn",
        "Anakin Skywalker (Boy)",
        "Captain Panaka",
        "Padmé (Battle)",
        "R2-D2",
    ),
    start_region="Spawn",
    start_level="retake_a",
    regions={
        "Spawn": (
            ExitData(
                "Inside Palace",
                logic_options(
                    #
                    base=And(
                        # Use the panel.
                        HasAbility(ASTROMECH_PANEL),
                        # Ascend to the higher area with the panel.
                        HasAnyAbilities(JEDI | GRAPPLE | HIGH_JUMP),
                        # Base logic expects being able to defeat the Droideka.
                        HasAnyAbilities(JEDI | BOUNTY_HUNTER) | Has("Droideka"),
                    ),
                    # Jump up the bricks to the side of the bricks that make the ramp.
                    # And just ignore Droideka if they cannot be defeated.
                    normal=HasAllAbilities(ASTROMECH_PANEL | CAN_JUMP_NORMAL_HEIGHT),
                    # Expert can push R2-D2 onto some objects to get him up to the panel, though I don't know if this is
                    # possible with other characters that cannot jump normally.
                    # expert=HasAbility(ASTROMECH_PANEL),
                ),
                new_level="retake_b",
            ),
        ),
        "Inside Palace": (
            ExitData(
                "After Collapsed Floor In Palace",
                logic_options(
                    # Force the platform and double jump across, or use the chute, or hover across.
                    base=HasAnyAbilities(JEDI | SHORTIE | HOVER),
                    # High jump characters can cross the gap by hugging the far wall, except Grievous' Bodyguard, but
                    # Grievous' Bodyguard can triple high jump to cross the gap.
                    moderate=HasAnyAbilities(JEDI | SHORTIE | HOVER | HIGH_JUMP),
                )
            ),
        ),
        "After Collapsed Floor In Palace": (
            ExitData(
                "Courtyard",
                logic_options(
                    # All characters that can build bricks can jump, and being able to damage shielded droideka implies
                    # being able to destroy the statue to spawn the astromech panel bricks.
                    base=HasAllAbilities(CAN_BUILD_BRICKS | ASTROMECH_PANEL) & base_can_damage_shielded_droideka,
                    # There's no expectation to be able to kill droideka so dealing damage at close range is enough,
                    # though Astromech can remove shields anyway.
                    normal=HasAllAbilities(CAN_BUILD_BRICKS | ASTROMECH_PANEL) & can_damage_at_close_range,
                    # Alternatively expect Deflect Bolts to deflect enemy blaster bolts into the statue.
                    moderate=And(
                        HasAllAbilities(CAN_BUILD_BRICKS | ASTROMECH_PANEL),
                        can_damage_at_close_range | can_deflect_bolts,
                    ),
                ),
                # retake_c does not exist.
                new_level="retake_d",
            ),
        ),
        "Courtyard": (
            ExitData(
                "Courtyard After Destroyed Bridge",
                logic_options(
                    # Hover from the rising platform, or jump up the stairs and force the bridge.
                    base=HasAnyAbilities(JEDI | HOVER),
                    # High jump from the rising platform works, but it is easier to high jump up parts of the buildings
                    # on the left.
                    normal=HasAnyAbilities(JEDI | HOVER | HIGH_JUMP),
                )
            ),
        ),
        "Courtyard After Destroyed Bridge": (
            ExitData(
                "Rooftops",
                logic_options(
                    # Destroy the flowerbed and use the chute and use the force to destroy the obstacles blocking the
                    # way.
                    # Or hover past the obstacles.
                    # Then use the chute up to the button.
                    base=HasAbility(SHORTIE) & HasAnyAbilities(JEDI | HOVER),
                    # High jump can jump on the first obstacle and then jump to the button.
                    # This is not in the base logic because the obstacles do not respawn if destroyed.
                    normal=Or(
                        HasAbility(HIGH_JUMP),
                        HasAbility(SHORTIE) & HasAnyAbilities(JEDI | HOVER),
                    ),
                    # Triple jump can replace high jump.
                    moderate=Or(
                        HasAnyAbilities(JEDI | HIGH_JUMP),
                        HasAllAbilities(SHORTIE | HOVER),
                    )
                ),
                new_level="retake_e",
            ),
        ),
        "Rooftops": (
            ExitData(
                "Dining Hall",
                logic_options(
                    # Jedi can force platforms.
                    # Grapple can destroy the flowerbed hiding the grapple point.
                    # Shortie can use the chute.
                    base=HasAnyAbilities(JEDI | GRAPPLE | SHORTIE),
                    # Triple high jump can stand on one of the taller bushes and triple high jump up.
                    moderate=HasAnyAbilities(JEDI | GRAPPLE | SHORTIE | CAN_HIGH_JUMP_SLAM),
                ),
                new_level="retake_f",
            ),
        ),
        "Dining Hall": (
            ExitData(
                "Hangar",
                logic_options(
                    # Fight the Droideka, destroy the statue, and stand on the button.
                    # A character that can jump, even astromech droids, is needed to get up a small lip before the
                    # button.
                    base=Or(
                        HasAnyAbilities(JEDI | BOUNTY_HUNTER),
                        Has("Droideka") & HasAbility(CAN_BARELY_JUMP),
                    ),
                    # The droideka can be ignored.
                    normal=HasAbility(CAN_BARELY_JUMP) & can_damage_at_close_range,
                    # Allow Deflect Bolts to destroy the statue.
                    # Droideka can also get up the small lip to get to the button, by repeatedly switching between
                    # Droideka and another character while rolling against the lip.
                    # ER Note: It is not currently possible to get here with just Droideka, but with ER, it could be
                    # possible, and then logic would need to ensure that the player has another character besides
                    # Droideka.
                    moderate=Or(
                        And(
                            can_damage_at_close_range | can_deflect_bolts,
                            HasAbility(CAN_BARELY_JUMP),
                        ),
                        Has("Droideka"),
                    ),
                ),
                new_level="retake_g",
            ),
        ),
        "Hangar": (
            ExitData(
                "Chapter Completion",
                # Logic breakdown for freeing each set of captive pilots:
                #  High up droid in the middle, with two captive pilots:
                #   Base: Reach the droid by using the force on the boxes with P2 (Jedi)
                #   Normal: Alternatively, shoot the droid from afar, or High Jump up off the starfighter, and then
                #    destroy the Battle Droid with a close range attack (high_jump AND can_damage_at_close_range).
                #  Droids on the ground with two captive pilots:
                #   Base: can_damage_at_close_range
                #  Far left droid at the front:
                #   Base: Destroy the objects in the front far left corner to spawn the grapple point, then grapple up
                #    (grapple [implies blaster])
                #   Normal: Alternatively, shoot the droid from afar (blaster) or stack the nearby boxes as a Jedi and
                #    jump across to the closed hangar exit and jump across to the platform the grapple point would take
                #    the player to (jedi). Force Grapple Leap is therefore not logically relevant here.
                #   Moderate: Alternatively, High Jump off terrain (high_jump AND can_damage_at_close_range) or triple
                #    jump up (jedi)
                #  Far left droid at the back (by the silver bricks):
                #   Base: Stack the boxes and jump up (jedi)
                #   Normal: Alternatively, shoot the droid from afar (blaster) or High Jump up from the large box
                #    (high_jump AND can_damage_at_close_range)
                #  Actually completing the chapter also requires astromech_panel.
                logic_options(
                    base=HasAllAbilities(JEDI | GRAPPLE | ASTROMECH_PANEL),
                    normal=HasAnyAbilities(JEDI | BLASTER | ASTROMECH_PANEL),
                    moderate=And(
                        Or(
                            HasAnyAbilities(JEDI | BLASTER),
                            HasAbility(HIGH_JUMP) & can_damage_at_close_range,
                        ),
                        HasAbility(ASTROMECH_PANEL),
                    )
                ),
                new_level="retake_status",
            ),
        ),
    },
    minikits={
        "Circular Window Minikit": minikit_data(
            "Spawn",
            logic_options(
                base=HasAbility(JEDI),
                # Grapple characters can shoot the window, but the basic jump height (jump_speed=2.1) is not enough to
                # jump into the window. A character with the slightly better jump height (jump_speed=2.3), however, can
                # jump into the window.
                normal=Or(
                    HasAbility(JEDI),
                    HasAllAbilities(GRAPPLE | CAN_JUMP_SLIGHTLY_HIGHER),
                ),
                # Triple High Jump can also reach the upper area that the window is in.
                # But General Grievous is too big to be able to hit the window without Super Jedi Slam or some means of
                # shooting, or exploding, the window.
                # Ewoks cannot hit the upper half of the window on their own, needing their projectile upgraded to cause
                # explosions.
                moderate=Or(
                    HasAbility(JEDI),
                    HasAllAbilities(GRAPPLE | CAN_JUMP_SLIGHTLY_HIGHER),
                    Has("Grievous' Bodyguard"),
                    And(
                        Has("General Grievous"),
                        Or(
                            HasAbility(BLASTER),
                            Has("Super Jedi Slam"),
                            can_self_destruct,
                            HasAbility(WEAPON_EWOK) & HasAny("Super Ewok Catapult", "Exploding Blaster Bolts")
                        )
                    )
                )
            ),
            pickup_name="mk_0",
        ),
        "Window Behind Grapple Point Minikit": minikit_data(
            "Spawn",
            HasAnyAbilities(JEDI | GRAPPLE),
            pickup_name="mk_1",
        ),
        "Minikit In Hidden Panel Behind Statue": minikit_data(
            "After Collapsed Floor In Palace",
            logic_options(
                base=HasAbility(CAN_ATTACK_UP_CLOSE),
                # Includes self-destruct.
                normal=can_damage_at_close_range,
                # Include Deflect Bolts.
                moderate=can_damage_at_close_range | can_deflect_bolts,
            ),
            pickup_name="mk_0",
        ),
        "Minikit Behind Dark Side Barrier": minikit_data(
            "After Collapsed Floor In Palace",
            logic_options(
                base=HasAbility(SITH),
                # Includes Dark Side.
                normal=can_sith_force,
            ),
            pickup_name="mk_1",
        ),
        "Minikit On Courtyard Far Ledge": minikit_data(
            "Courtyard",
            # Hover/jump from the platform that lifts into the air, or take the chute behind it.
            HasAnyAbilities(JEDI | HOVER | SHORTIE | HIGH_JUMP),
            pickup_name="m_pup2",
        ),
        "Courtyard High Minikit": minikit_data(
            "Courtyard After Destroyed Bridge",
            logic_options(
                base=HasAbility(JEDI),
                moderate=HasAnyAbilities(JEDI | CAN_HIGH_JUMP_SLAM),
            ),
            pickup_name="m_pup1",
        ),
        "Build And Destroy Silver Bricks In Boxes Minikit": minikit_data(
            "Rooftops",
            logic_options(
                base=HasAllAbilities(BOUNTY_HUNTER | CAN_BUILD_BRICKS),
                normal=HasAbility(CAN_BUILD_BRICKS) & can_destroy_close_silver_bricks,
            ),
            pickup_name="m_pup1",
        ),
        "Minikit On Dining Hall Ledge": minikit_data(
            "Dining Hall",
            logic_options(
                # High jump up.
                # Or force the tables, double jump up and then grapple the last part.
                base=Or(
                    HasAbility(HIGH_JUMP),
                    HasAllAbilities(JEDI | GRAPPLE),
                ),
                # Jetpack hover is enough to jump from scenery and hover up the slanted lip to the grapple point.
                # Force Grapple Leap is allowed.
                normal=Or(
                    HasAnyAbilities(HIGH_JUMP | JETPACK),
                    And(
                        HasAbility(JEDI),
                        HasAbility(GRAPPLE) | Has("Force Grapple Leap"),
                    ),
                ),
                # Astromech hover from the rail along the steps can get to the alcove next the alcove with the grapple
                # point, from which another astromech hover can get to the alcove with the grapple point.
                # Jedi can triple jump to get more height than high jump.
                moderate=Or(
                    HasAnyAbilities(HIGH_JUMP | JEDI | JETPACK),
                    HasAllAbilities(HOVER | GRAPPLE),
                ),
            ),
            pickup_name="m_pup1",
        ),
        "Hangar Far Right Minikit": minikit_data(
            "Hangar",
            logic_options(
                # Jump up the far left side, then hover across.
                # Or use the jedi blocks to get up to the high up Battle Droid in the middle with two captives, then
                # High Jump up to the upper area.
                # Then walk all the way to the right side to the Minikit.
                base=Or(
                    HasAllAbilities(HOVER | JEDI),
                    HasAllAbilities(HIGH_JUMP | JEDI),
                ),
                # High jump up to the high up battle droid by first jumping from the top of the nearby starfighter.
                normal=Or(
                    HasAllAbilities(HOVER | JEDI),
                    HasAbility(HIGH_JUMP),
                ),
                # Triple jump is higher than high jump.
                moderate=HasAnyAbilities(JEDI | HIGH_JUMP),
            ),
            pickup_name="m_pup2",
        ),
        "Hangar Far Left Minikit": minikit_data(
            "Hangar",
            logic_options(
                # Jedi to move blocks to get to the silver bricks.
                # Bounty hunter to destroy the silver bricks.
                # Build Bricks to build the platform (all Jedi/Sith can build bricks).
                # Sith force to move the platform into position.
                base=HasAllAbilities(SITH | BOUNTY_HUNTER),
                # High jump can just jump up to the minikit from the right side, no Jedi needed.
                normal=Or(
                    HasAbility(HIGH_JUMP),
                    can_sith_force & can_destroy_close_silver_bricks,
                ),
                # Triple jump is higher than high jump.
                moderate=HasAnyAbilities(JEDI | HIGH_JUMP),
            ),
            pickup_name="m_pup1",
        )
    },
    power_brick=LocationData(
        "Dining Hall",
        HasAbility(JEDI),
    ),
    ridables={
        "Service Car": LocationData("Hangar"),
    }
)
