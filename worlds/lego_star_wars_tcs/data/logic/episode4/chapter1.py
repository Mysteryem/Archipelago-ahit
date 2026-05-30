from rule_builder.rules import And, Or, CanReachRegion

from ..macros import (
    CAN_DAMAGE_AT_CLOSE_RANGE,
    CAN_SITH_FORCE,
    CAN_ORIGINAL_TRILOGY_HIGH_JUMP,
    CAN_DESTROY_CLOSE_SILVER_BRICKS,
)
from ..option_filters import logic_options
from ..rules import HasAbility, HasAnyAbilities, HasAllAbilities
from ..types import minikit_data, ExitData, Chapter, LocationData, MinikitData

from ....character_ability import *

NAME = "Secret Plans"

R_SPAWN = "Spawn"
R_FIRST_HALLWAY = "First Hallway"
R_SECOND_HALLWAY = "Second Hallway"
R_SITH_DOUBLE_SCORE_ZONE = "Sith Double Score Zone"
R_GRAPPLE_ROOM = "Grapple Room"
R_GRAPPLE_ROOM_TOP = "Grapple Room Top"
R_VADER_EXPLOSIVES_HALLWAY = "Vader Explosives Hallway"
R_SECOND_STORMTROOPER_BATTLE = "Second Stormtrooper Battle"
R_SIDE_ACCESS_CORRIDOR = "Side Access Corridor"
R_SIDE_ACCESS_CORRIDOR_BEHIND_FORCE_FIELD = "Side Access Corridor Behind Force Field"
R_SLIDING_BLOCKS_ROOM = "Sliding Blocks Room"
R_ACCESS_CORRIDOR_BEFORE_R2_D2_AND_LEIA = "Access Corridor Before R2-D2 And Leia"
R_R2_D2_AND_LEIA_ACCESS_CORRIDOR = "R2-D2 And Leia Access Corridor"
R_CRANE_ROOM = "Crane Room"
R_CAPTIVE_REBELS_HALLWAY = "Captive Rebels Hallway"
R_ESCAPE_POD_CORRIDOR = "Escape Pod Corridor"


SECRET_PLANS = Chapter(
    name=NAME,
    episode_number=4,
    chapter_number=1,
    start_region=R_SPAWN,
    start_level="blockade_runner_a",
    regions={
        R_SPAWN: (
            ExitData(R_FIRST_HALLWAY, HasAbility(CAN_BUILD_BRICKS), name="Build bricks to restore power"),
        ),
        R_FIRST_HALLWAY: (
            ExitData(R_SECOND_HALLWAY, HasAbility(CAN_PULL_LEVERS), name="Open lever door"),
        ),
        R_SECOND_HALLWAY: (
            ExitData(R_SITH_DOUBLE_SCORE_ZONE, CAN_SITH_FORCE),
            ExitData(R_GRAPPLE_ROOM, CAN_DAMAGE_AT_CLOSE_RANGE, new_level="blockade_runner_b"),
        ),
        R_SITH_DOUBLE_SCORE_ZONE: (),
        R_GRAPPLE_ROOM: (
            # todo: triple jump logic
            ExitData(R_GRAPPLE_ROOM_TOP, HasAnyAbilities(GRAPPLE | ASTROMECH_PANEL) | CAN_ORIGINAL_TRILOGY_HIGH_JUMP),
        ),
        R_GRAPPLE_ROOM_TOP: (
            ExitData(R_VADER_EXPLOSIVES_HALLWAY, HasAnyAbilities(CAN_BUILD_BRICKS | HOVER)),
        ),
        R_VADER_EXPLOSIVES_HALLWAY: (
            ExitData(R_SECOND_STORMTROOPER_BATTLE, HasAllAbilities(CAN_PULL_LEVERS | BLASTER)),
        ),
        R_SECOND_STORMTROOPER_BATTLE: (
            ExitData(R_SIDE_ACCESS_CORRIDOR, HasAnyAbilities(IMPERIAL | BOUNTY_HUNTER)),
            ExitData(R_SLIDING_BLOCKS_ROOM, CAN_DAMAGE_AT_CLOSE_RANGE, new_level="blockade_runner_c"),
        ),
        R_SIDE_ACCESS_CORRIDOR: (
            ExitData(R_SIDE_ACCESS_CORRIDOR_BEHIND_FORCE_FIELD, HasAbility(PROTOCOL_PANEL)),
        ),
        R_SIDE_ACCESS_CORRIDOR_BEHIND_FORCE_FIELD: (),
        R_SLIDING_BLOCKS_ROOM: (
            ExitData(R_ACCESS_CORRIDOR_BEFORE_R2_D2_AND_LEIA, HasAbility(CAN_PUSH_OBJECTS) & CAN_DAMAGE_AT_CLOSE_RANGE),
        ),
        R_ACCESS_CORRIDOR_BEFORE_R2_D2_AND_LEIA: (
            ExitData(R_R2_D2_AND_LEIA_ACCESS_CORRIDOR, HasAbility(PROTOCOL_PANEL)),
        ),
        R_R2_D2_AND_LEIA_ACCESS_CORRIDOR: (
            ExitData(R_CRANE_ROOM, HasAbility(ASTROMECH_PANEL)),
        ),
        R_CRANE_ROOM: (
            # todo: There are lots of alternative rules for this entrance.
            ExitData(
                R_CAPTIVE_REBELS_HALLWAY,
                HasAllAbilities(CAN_RIDE_VEHICLES | PROTOCOL_PANEL),
                new_level="blockaderunner_d"
            ),
        ),
        R_CAPTIVE_REBELS_HALLWAY: (
            ExitData(R_ESCAPE_POD_CORRIDOR, CAN_DAMAGE_AT_CLOSE_RANGE),
        ),
        R_ESCAPE_POD_CORRIDOR: (
            # No locations defined currently.
            # ExitData("Vent Imperials Into Space Room", HasAbility(IMPERIAL)),
            ExitData(
                "Chapter Completion",
                HasAllAbilities(PROTOCOL_PANEL | ASTROMECH_PANEL | CAN_PULL_LEVERS),
                new_level="blockade_runner_status"),
        ),
        # "Vent Imperials Into Space Room": (),
    },
    minikits={
        "Dark Side Double Score Zone Minikit": minikit_data(
            R_SITH_DOUBLE_SCORE_ZONE,
            pickup_name="m_pup1",
        ),
        "Grapple Room Beneath Floor Minikit": minikit_data(
            R_GRAPPLE_ROOM,
            logic_options(
                # Expect getting back out.
                # todo: If the elevator is active, does it go down here?
                base=CAN_DESTROY_CLOSE_SILVER_BRICKS & HasAbility(CAN_DOUBLE_JUMP),
                normal=CAN_DESTROY_CLOSE_SILVER_BRICKS,
            ),
            pickup_name="mk_0",
        ),
        "Grapple Room High Minikit": minikit_data(
            R_GRAPPLE_ROOM_TOP,
            HasAbility(JEDI),
            pickup_name="m_pup2",
        ),
        "Build Door Minikit": minikit_data(
            R_SIDE_ACCESS_CORRIDOR,
            HasAbility(CAN_BUILD_BRICKS),
            pickup_name="mk_1",
        ),
        "Three Grape Tiles Minikit": MinikitData(
            # Physically, this minikit spawns in Side Access Corridor.
            # Logically this is behind the force field because one of the tiles is there, and to access that tile means
            # you have access to where the minikit spawns.
            R_SIDE_ACCESS_CORRIDOR_BEHIND_FORCE_FIELD,
            CAN_DAMAGE_AT_CLOSE_RANGE,
            pickup_names=(
                "m_pup1",
                "m_pup3",
                "m_pup4",
            ),
        ),
        "Sliding Blocks Room Minikit": minikit_data(
            R_SLIDING_BLOCKS_ROOM,
            HasAbility(JEDI),
            pickup_name="mk_0",
        ),
        "Secret Wall Compartment Minikit": minikit_data(
            R_R2_D2_AND_LEIA_ACCESS_CORRIDOR,
            HasAbility(JEDI),
            pickup_name="pup1",
        ),
        "Crane Room Minikit": minikit_data(
            R_CRANE_ROOM,
            # The ridesanity entrances won't exist unless Ridesanity is enabled, so the access rules from them are
            # copied here.
            And(
                HasAbility(CAN_RIDE_VEHICLES),
                CanReachRegion("Secret Plans - Side Access Corridor"),
                Or(
                    HasAbility(CAN_BUILD_BRICKS) & CAN_DESTROY_CLOSE_SILVER_BRICKS,
                    CanReachRegion("Secret Plans - Side Access Corridor Behind Force Field") & HasAbility(JEDI),
                ),
            ),
            pickup_name="m_pup1",
        ),
        "Three Flowers Minikit": MinikitData(
            R_ESCAPE_POD_CORRIDOR,
            And(
                CAN_DESTROY_CLOSE_SILVER_BRICKS,
                # CanReachRegion("Secret Plans - Vent Imperials Into Space Room"),
                HasAbility(IMPERIAL),
            ),
            pickup_names=(
                "m_pup3",
                "m_pup2",
                "m_pup4",
            ),
        ),
        "Pull The Plug Minikit": minikit_data(
            R_ESCAPE_POD_CORRIDOR,
            CAN_SITH_FORCE & HasAbility(ASTROMECH_PANEL),
            pickup_name="m_pup1",
        ),
    },
    power_brick=LocationData(R_SIDE_ACCESS_CORRIDOR_BEHIND_FORCE_FIELD, HasAbility(JEDI)),
    ridables={
        "Moon Car": LocationData(R_SIDE_ACCESS_CORRIDOR,
                                 HasAbility(CAN_BUILD_BRICKS) & CAN_DESTROY_CLOSE_SILVER_BRICKS),
        "Town Car": LocationData(R_SIDE_ACCESS_CORRIDOR_BEHIND_FORCE_FIELD, HasAbility(JEDI)),
    },
)
