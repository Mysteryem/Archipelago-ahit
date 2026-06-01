from rule_builder.rules import And, Or, HasAny, False_, Has, True_, Rule

from ..macros import (
    CAN_DAMAGE_AT_CLOSE_RANGE,
    CAN_SITH_FORCE,
    CAN_ORIGINAL_TRILOGY_HIGH_JUMP,
    CAN_DESTROY_CLOSE_SILVER_BRICKS,
    CAN_GRAPPLE,
    CAN_DAMAGE_AT_CLOSE_RANGE_NO_BASIC_MELEE,
)
from ..option_filters import logic_options, OT_HIGH_JUMP_ENABLED, ot_high_jump_ternary
from ..rules import (
    HasAbility,
    HasAnyAbilities,
    HasAllAbilities,
    HasAbilityExceptCharacters,
    HasAbilityCombination,
    HasAnyCharacterExcept,
)
from ..types import minikit_data, ExitData, ChapterHelper, LocationData, MinikitData
from ....character_ability import *
from ....items import CHARACTERS_AND_VEHICLES_BY_NAME

CAN_BUILD_FIRST_AT_ST = HasAllAbilities(PROTOCOL_PANEL | JEDI | ASTROMECH_PANEL)


def _make_can_pass_cantina_anti_droid_field() -> Rule:
    affected_by_anti_droid_field = {
        "R2-D2",
        "C-3PO",
        "Gonk Droid",
        "Super Gonk Droid",
        # "General Grievous" is unaffected by the anti-droid field for some reason.
        "Grievous' Bodyguard",
        "Droideka",
        "R4-P17",
        "Battle Droid",
        "Battle Droid (Commander)",
        "Battle Droid (Geonosis)",
        "Battle Droid (Security)",
        "TC-14",
        "Super Battle Droid",
        "PK Droid",
        "IG-88",
        "4-LOM",
        "Pit Droid",
        "R2-Q5",
        # Extra toggle characters:
        "Droid 1",
        "Droid 2",
        "Droid 3",
        "Droid 4",
        # While Mouse Droid and Buzz Droid might be affect, they are not available in this chapter.
    }
    # Remove droids that can destroy the anti-droid field on their own.
    for character_name in tuple(affected_by_anti_droid_field):
        if BLASTER in CHARACTERS_AND_VEHICLES_BY_NAME[character_name].abilities:
            affected_by_anti_droid_field.remove(character_name)
    characters_rule = HasAbilityExceptCharacters(CharacterAbility.NONE, *affected_by_anti_droid_field)
    # The ceiling has no collision, so Bodyguard can jump over the emitters when either OT high jump is enabled, or by
    # performing a triple jump.
    characters_rule_moderate = HasAbilityExceptCharacters(
        CharacterAbility.NONE, *(affected_by_anti_droid_field - {"Grievous' Bodyguard"})
    )
    return logic_options(
        base=characters_rule,
        moderate=characters_rule_moderate,
    )


CAN_PASS_CANTINA_ANTI_DROID_FIELD = _make_can_pass_cantina_anti_droid_field()
del _make_can_pass_cantina_anti_droid_field


helper = ChapterHelper(
    name="Mos Eisley Spaceport",
    episode_number=4,
    chapter_number=3,
    start_region="Spawn",
    start_level="moseisley_a",
    story_characters=(
        "Ben Kenobi",
        "C-3PO",
        "Chewbacca",
        "Han Solo",
        "Luke Skywalker (Tatooine)",
        "R2-D2",
    ),
    purchase_characters={
        "Sandtrooper": 14_000,
        "Greedo": 60_000,
        "Imperial Spy": 13_500,
    },
    extra_toggle_characters=(
        "Droid 1",
        "Droid 2",
        "Droid 3",
        "Droid 4",
        "Womp Rat",
    ),
)


MOS_EISLEY_SPACEPORT = helper.make_chapter(
    regions={
        "Spawn": (
            ExitData(
                "Imperial Showers And Pool",
                # Note: Grievous and Droideka are too big to fit through the door.
                HasAbility(IMPERIAL),
            ),
            ExitData(
                "Above First Stormtrooper Gate",
                logic_options(
                    base=And(
                        # Expect fighting the Stormtroopers.
                        CAN_DAMAGE_AT_CLOSE_RANGE,
                        # Force the steps into a ramp, or high jump up.
                        HasAbility(JEDI) | CAN_ORIGINAL_TRILOGY_HIGH_JUMP,
                    ),
                    # Just double jump up, next to where the ramp goes.
                    normal=HasAbility(CAN_DOUBLE_JUMP),
                    # Walk up the steps, then jump on, and then over the left wall.
                    moderate=HasAbility(CAN_JUMP_HEIGHT_0_37),
                )
            ),
        ),
        "Imperial Showers And Pool": (),
        "Above First Stormtrooper Gate": (
            ExitData(
                "After Stormtrooper Gate (Imperial Exit)",
                HasAbility(IMPERIAL),
            ),
            ExitData(
                "After Stormtrooper Gate (Protocol Exit)",
                HasAbility(PROTOCOL_PANEL),
            ),
        ),
        "After Stormtrooper Gate (Imperial Exit)": (
            # Drop down.
            ExitData("After Stormtrooper Gate (Protocol Exit)"),
            ExitData(
                "Womp Rat Shooting Range",
                logic_options(
                    base=HasAnyAbilities(CAN_DOUBLE_JUMP | HOVER),
                    # A good single-jump distance can cross the broken bridge.
                    moderate=HasAnyAbilities(CAN_DOUBLE_JUMP | HOVER | CAN_JUMP_DISTANCE_0_92),
                ),
            ),
        ),
        "After Stormtrooper Gate (Protocol Exit)": (
            ExitData(
                "Womp Rat Shooting Range",
                logic_options(
                    # Only expect high jumping.
                    base=CAN_ORIGINAL_TRILOGY_HIGH_JUMP,
                    # Double jump up the corner.
                    normal=HasAbility(CAN_DOUBLE_JUMP),
                    # You can also get up here by jumping out of an AT-ST, but the first AT-ST requires force to build
                    # it, making it logically redundant, but there is a second AT-ST later into the level, that you
                    # could bring all the way back here, but it doesn't spawn unless you build the first AT-ST :(
                ),
            ),
            ExitData(
                "After Blocked Street",
                Or(
                    CAN_BUILD_FIRST_AT_ST & HasAbility(CAN_RIDE_VEHICLES),
                    CAN_DESTROY_CLOSE_SILVER_BRICKS,
                ),
            ),
        ),
        "Womp Rat Shooting Range": (),
        "After Blocked Street": (
            ExitData(
                "Cantina Entrance",
                CAN_DAMAGE_AT_CLOSE_RANGE,
                new_level="moseisley_c",
            ),
        ),
        "Cantina Entrance": (
            ExitData(
                "Inside Cantina",
                CAN_PASS_CANTINA_ANTI_DROID_FIELD,
            ),
        ),
        "Inside Cantina": (
            ExitData(
                "Spy Chase Start",
                new_level="moseisley_d",
            ),
        ),
        "Spy Chase Start": (
            ExitData(
                "Spy Chase Spawn First Storey",
                logic_options(
                    base=CAN_GRAPPLE,
                    normal=HasAbility(CAN_DOUBLE_JUMP) | CAN_GRAPPLE,
                ),
            ),
        ),
        "Spy Chase Spawn First Storey": (
            ExitData(
                "Spy Chase Spawn Second Storey",
                logic_options(
                    base=CAN_GRAPPLE & HasAbility(CAN_BUILD_BRICKS),
                    normal=Or(
                        HasAbility(CAN_DOUBLE_JUMP),
                        CAN_GRAPPLE & HasAbility(CAN_BUILD_BRICKS),
                    ),
                ),
            ),
            ExitData("Spy Chase Bomb Ground Level"),
        ),
        "Spy Chase Spawn Second Storey": (
            ExitData(
                "Spy Chase Right Path",
                logic_options(
                    base=HasAbility(BOUNTY_HUNTER),
                    # Triple jump over the bounty hunter door.
                    moderate=HasAnyAbilities(BOUNTY_HUNTER | JEDI | CAN_HIGH_JUMP_SLAM),
                    # High jump onto the antenna on the building to the left of the bounty hunter door, then jump over
                    # the bounty hunter door.
                    # This probably could be in moderate logic, though it is more obscure.
                    hard=ot_high_jump_ternary(
                        uncapped=HasAnyAbilities(BOUNTY_HUNTER | JEDI | HIGH_JUMP),
                        capped=HasAnyAbilities(BOUNTY_HUNTER | JEDI | CAN_HIGH_JUMP_SLAM),
                    ),
                ),
            ),
            ExitData(
                "Spy Chase Bomb Lever",
                CAN_GRAPPLE | HasAnyAbilities(HOVER | CAN_DOUBLE_JUMP),
            ),
            ExitData(
                "Turnips Minikit Ledge",
                HasAbility(HOVER),
            ),
        ),
        "Spy Chase Bomb Ground Level": (
            ExitData(
                "Spy Chase Bomb Lever",
                logic_options(
                    base=HasAbility(CAN_DOUBLE_JUMP),
                    # I don't think it will ever be relevant, but Gamorrean Guard can just jump straight up here.
                    moderate=HasAbility(CAN_DOUBLE_JUMP) | Has("Gamorrean Guard"),
                ),
            ),
            ExitData(
                "Stormtrooper And Dewback Courtyard",
                logic_options(
                    base=And(
                        helper.can_reach_region("Spy Chase Bomb Lever"),
                        HasAbility(CAN_PULL_LEVERS),
                        CAN_DAMAGE_AT_CLOSE_RANGE,
                    ),
                    # You can just blow up the door yourself.
                    normal=Or(
                        CAN_DESTROY_CLOSE_SILVER_BRICKS,
                        And(
                            helper.can_reach_region("Spy Chase Bomb Lever"),
                            HasAbility(CAN_PULL_LEVERS),
                            CAN_DAMAGE_AT_CLOSE_RANGE,
                        )
                    )
                ),
            ),
            ExitData(
                "Spy Chase Right Path",
                HasAbility(PROTOCOL_PANEL),
            ),
        ),
        "Spy Chase Bomb Lever": (
            ExitData(
                "Turnips Minikit Ledge",
                logic_options(
                    base=HasAbility(CAN_DOUBLE_JUMP),
                    normal=HasAbility(CAN_JUMP_0_44),
                ),
            ),
        ),
        "Spy Chase Right Path": (
            ExitData(
                "Stormtrooper And Dewback Courtyard",
                CAN_SITH_FORCE,
            ),
        ),
        "Turnips Minikit Ledge": (),
        "Stormtrooper And Dewback Courtyard": (
            ExitData(
                "Cinema",
                HasAbility(ASTROMECH_PANEL),
                new_level="moseisley_e",
            ),
            ExitData(
                "Hangar",
                logic_options(
                    base=HasAbility(CAN_RIDE_VEHICLES),
                    # Jump on the turnip, jump on the sloped bit of wall adjacent to the turnip, jump to where the hat
                    # machine is, jump onto the wall of that area, then, finally, jump across to the section that leads
                    # to the spaceport.
                    # Bodyguard, who has reduced jump distance, can triple jump to make up for it.
                    moderate=HasAnyAbilities(CAN_RIDE_VEHICLES | CAN_DOUBLE_JUMP),
                )
            ),
            ExitData(
                "Spy Chase Right Path",
                CAN_SITH_FORCE,
            ),
        ),
        "Cinema": (),
        "Hangar": (
            ExitData(
                "Chapter Completion",
                logic_options(
                    base=HasAbility(BLASTER),
                    # There are pipes you can jump on to then jump to the upper level, to kill the stormtroopers up
                    # there.
                    normal=Or(
                        HasAbility(BLASTER),
                        HasAbility(CAN_DOUBLE_JUMP) & CAN_DAMAGE_AT_CLOSE_RANGE,
                    )
                    # Droideka and General Grievous are too big to fit in the door of the Millennium Falcon.
                ) & HasAnyCharacterExcept("Droideka", "General Grievous"),
                new_level="moseisley_status",
            ),
        ),
    },
    minikits={
        "Drain Imperial Pool Minikit": minikit_data(
            "Imperial Showers And Pool",
            HasAbility(JEDI),
            pickup_name="WATER_M",
        ),
        "Reveal Three Carrots Minikit": MinikitData(
            "Spawn",
            logic_options(
                base=And(
                    # Basic melee attacks do not work on the barrels hiding the carrots.
                    CAN_DAMAGE_AT_CLOSE_RANGE_NO_BASIC_MELEE,
                    Or(
                        # Hover across the broken bridge, use the Bounty Hunter panel, then build the fan from the
                        # bricks that spawn.
                        HasAllAbilities(HOVER | BOUNTY_HUNTER | CAN_BUILD_BRICKS),
                        # Just jump up to the bridge and then jump up to the minikit.
                        CAN_ORIGINAL_TRILOGY_HIGH_JUMP,
                    ),
                ),
                # Allow DOUBLE_JUMP to get to the Bounty Hunter panel instead of requiring HOVER. Either double jump
                # across the gap in the bridge, double jump starting from a nearby barrel, or double jump up the terrain
                # that sticks out on the side of the bridge near the bounty hunter panel.
                normal=And(
                    CAN_DAMAGE_AT_CLOSE_RANGE_NO_BASIC_MELEE,
                    Or(
                        HasAllAbilities(BOUNTY_HUNTER | CAN_BUILD_BRICKS) & HasAnyAbilities(HOVER | CAN_DOUBLE_JUMP),
                        # Just jump up to the bridge and then jump up to the minikit.
                        CAN_ORIGINAL_TRILOGY_HIGH_JUMP,
                    ),
                ),
                # Allow triple jump to reach the minikit.
                moderate=And(
                    CAN_DAMAGE_AT_CLOSE_RANGE_NO_BASIC_MELEE,
                    Or(
                        HasAllAbilities(BOUNTY_HUNTER | CAN_BUILD_BRICKS) & HasAnyAbilities(HOVER | CAN_DOUBLE_JUMP),
                        # Just jump up to the bridge and then jump up to the minikit.
                        ot_high_jump_ternary(
                            uncapped=HasAnyAbilities(JEDI | HIGH_JUMP),
                            capped=HasAnyAbilities(JEDI | CAN_HIGH_JUMP_SLAM),
                        ),
                    ),
                )
            ),
            pickup_names=(
                "C_M1",
                "C_M2",
                "C_M3",
            ),
        ),
        "Minikit Beneath Dark Side Roof": minikit_data(
            "Spawn",
            CAN_SITH_FORCE,
            pickup_name="m_pup1",
        ),
        "Womp Rat Shooting Range Minikit": minikit_data(
            "Womp Rat Shooting Range",
            HasAllAbilities(CAN_BUILD_BRICKS | CAN_RIDE_VEHICLES),
            pickup_name="WOMPRAT",
        ),
        "Stack Boxes Near AT-ST Minikit": minikit_data(
            "After Stormtrooper Gate (Protocol Exit)",
            logic_options(
                # Stack the boxes and double jump up.
                base=HasAbility(JEDI),
                # You can build the AT-ST and jump out of it to get this minikit, but you need JEDI to build the AT-ST
                # in the first place, so this is logically irrelevant.
                # CAN_BUILD_FIRST_AT_ST & HasAbility(CAN_RIDE_VEHICLES),
                normal=ot_high_jump_ternary(
                    # High jump up from one of the boxes.
                    uncapped=HasAnyAbilities(JEDI | HIGH_JUMP),
                    capped=HasAbility(JEDI),
                ),
                moderate=ot_high_jump_ternary(
                    uncapped=HasAnyAbilities(JEDI | HIGH_JUMP),
                    # Triple jump up.
                    capped=HasAnyAbilities(JEDI | CAN_HIGH_JUMP_SLAM),
                ),
            ),
            pickup_name="mk_1",
        ),
        "Tall Tower Minikit": minikit_data(
            "After Stormtrooper Gate (Protocol Exit)",
            logic_options(
                base=And(
                    CAN_DESTROY_CLOSE_SILVER_BRICKS,
                    HasAllAbilities(CAN_BUILD_BRICKS | CAN_PUSH_OBJECTS),
                    CAN_GRAPPLE,
                ),
                normal=And(
                    CAN_DESTROY_CLOSE_SILVER_BRICKS,
                    HasAllAbilities(CAN_BUILD_BRICKS | CAN_PUSH_OBJECTS),
                    Or(
                        CAN_GRAPPLE,
                        # Build the AT-ST, then double jump out.
                        CAN_BUILD_FIRST_AT_ST & HasAbilityCombination(CAN_DOUBLE_JUMP | CAN_RIDE_VEHICLES),
                    ),
                ),
                moderate=Or(
                    And(
                        CAN_DESTROY_CLOSE_SILVER_BRICKS,
                        HasAllAbilities(CAN_BUILD_BRICKS | CAN_PUSH_OBJECTS),
                        Or(
                            CAN_GRAPPLE,
                            # Build the AT-ST, then double jump out of it.
                            CAN_BUILD_FIRST_AT_ST & HasAbilityCombination(CAN_DOUBLE_JUMP | CAN_RIDE_VEHICLES),
                        ),
                    ),
                    # Triple High Jump up without making the tower more upright.
                    Has("General Grievous") & OT_HIGH_JUMP_ENABLED,
                ),
            ),
            pickup_name="mk_0",
        ),
        "Cantina Force Field Minikit": minikit_data(
            "Inside Cantina",
            logic_options(
                base=HasAbility(SHORTIE),
                hard=HasAbility(SHORTIE) | HasAny("Yoda", "Yoda (Ghost)")
            ),
            pickup_name="m_pup1",
        ),
        "Reveal Three Turnips Minikit": MinikitData(
            "Turnips Minikit Ledge",
            And(
                # The barrels cannot be destroyed with basic melee attacks, only the lids of the barrels.
                # The barrels are pretty weird in general, since the lids cannot be hit by lightsabers, but Bodyguard
                # can hit the lids without issue.
                CAN_DAMAGE_AT_CLOSE_RANGE_NO_BASIC_MELEE,
                # Third turnip.
                helper.can_reach_region("Stormtrooper And Dewback Courtyard"),
                # Second turnip.
                helper.can_reach_region("Spy Chase Right Path"),
                # First turnip.
                helper.can_reach_region("Spy Chase Start"),
            ),
            pickup_names=(
                "M_T1",
                "M_T2",
                "M_T3",
            ),
        ),
        "Two Player Force Gate Minikit": minikit_data(
            "Spy Chase Right Path",
            logic_options(
                base=HasAbility(JEDI),
                # Triple high jump from the barrel in the corner to get enough height to get over the colision of the
                # wall and land in the area behind the minikit. You are now trapped and must restart the level.
                hard=ot_high_jump_ternary(
                    uncapped=HasAnyAbilities(JEDI | CAN_HIGH_JUMP_SLAM),
                    capped=HasAbility(JEDI),
                ),
            ),
            pickup_name="m_pup1",
        ),
        "Cinema Minikit": minikit_data(
            "Cinema",
            logic_options(
                base=HasAbility(JEDI),
                # Triple high jump over the jumbled cinema screen.
                moderate=ot_high_jump_ternary(
                    uncapped=HasAnyAbilities(JEDI | CAN_HIGH_JUMP_SLAM),
                    capped=HasAbility(JEDI),
                ),
            ),
            pickup_name="m_pup1",
        ),
    },
    power_brick=LocationData(
        "Spawn",
        HasAllAbilities(JEDI | ASTROMECH_PANEL),
    ),
    ridables={
        "Landspeeder": LocationData("Spawn"),
        "Mos Eisley Cannon": LocationData("Womp Rat Shooting Range", HasAbility(CAN_BUILD_BRICKS)),
        "AT-ST": LocationData(
            "After Stormtrooper Gate (Protocol Exit)",
            CAN_BUILD_FIRST_AT_ST,
        ),
        "Dewback": LocationData("Stormtrooper And Dewback Courtyard"),
    }
)
