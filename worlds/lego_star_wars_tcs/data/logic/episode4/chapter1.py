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


SECRET_PLANS = Chapter(
    name="Secret Plans",
    episode_number=4,
    chapter_number=1,
    start_region="Spawn",
    start_level="blockade_runner_a",
    regions={
        "Spawn": (
            ExitData("First Hallway", HasAbility(CAN_BUILD_BRICKS), name="Build bricks to restore power"),
        ),
        "First Hallway": (
            ExitData("Second Hallway", HasAbility(CAN_PULL_LEVERS), name="Open lever door"),
        ),
        "Second Hallway": (
            ExitData("Sith Double Score Zone", CAN_SITH_FORCE),
            ExitData("Grapple Room", CAN_DAMAGE_AT_CLOSE_RANGE, new_level="blockade_runner_b"),
        ),
        "Sith Double Score Zone": (),
        "Grapple Room": (
            # todo: triple jump logic
            ExitData("Grapple Room Top", HasAnyAbilities(GRAPPLE | ASTROMECH_PANEL) | CAN_ORIGINAL_TRILOGY_HIGH_JUMP),
        ),
        "Grapple Room Top": (
            ExitData("Vader Explosives Hallway", HasAnyAbilities(CAN_BUILD_BRICKS | HOVER)),
        ),
        "Vader Explosives Hallway": (
            ExitData("Second Stormtrooper Battle", HasAllAbilities(CAN_PULL_LEVERS | BLASTER)),
        ),
        "Second Stormtrooper Battle": (
            ExitData("Side Access Corridor", HasAnyAbilities(IMPERIAL | BOUNTY_HUNTER)),
            ExitData("Sliding Blocks Room", CAN_DAMAGE_AT_CLOSE_RANGE, new_level="blockade_runner_c"),
        ),
        "Side Access Corridor": (
            ExitData("Side Access Corridor Behind Force Field", HasAbility(PROTOCOL_PANEL)),
        ),
        "Side Access Corridor Behind Force Field": (),
        "Sliding Blocks Room": (
            ExitData("Access Corridor Before R2-D2 And Leia", HasAbility(CAN_PUSH_OBJECTS) & CAN_DAMAGE_AT_CLOSE_RANGE),
        ),
        "Access Corridor Before R2-D2 And Leia": (
            ExitData("R2-D2 And Leia Access Corridor", HasAbility(PROTOCOL_PANEL)),
        ),
        "R2-D2 And Leia Access Corridor": (
            ExitData("Crane Room", HasAbility(ASTROMECH_PANEL)),
        ),
        "Crane Room": (
            # todo: There are lots of alternative rules for this entrance.
            ExitData(
                "Captive Rebels Hallway",
                HasAllAbilities(CAN_RIDE_VEHICLES | PROTOCOL_PANEL),
                new_level="blockaderunner_d"
            ),
        ),
        "Captive Rebels Hallway": (
            ExitData("Escape Pod Corridor", CAN_DAMAGE_AT_CLOSE_RANGE),
        ),
        "Escape Pod Corridor": (
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
            "Sith Double Score Zone",
            pickup_name="m_pup1",
        ),
        "Grapple Room Beneath Floor Minikit": minikit_data(
            "Grapple Room",
            logic_options(
                # Expect getting back out.
                # todo: If the elevator is active, does it go down here?
                base=CAN_DESTROY_CLOSE_SILVER_BRICKS & HasAbility(CAN_DOUBLE_JUMP),
                normal=CAN_DESTROY_CLOSE_SILVER_BRICKS,
            ),
            pickup_name="mk_0",
        ),
        "Grapple Room High Minikit": minikit_data(
            "Grapple Room Top",
            HasAbility(JEDI),
            pickup_name="m_pup2",
        ),
        "Build Door Minikit": minikit_data(
            "Side Access Corridor",
            HasAbility(CAN_BUILD_BRICKS),
            pickup_name="mk_1",
        ),
        "Three Grape Tiles Minikit": MinikitData(
            # Physically, this minikit spawns in Side Access Corridor.
            # Logically this is behind the force field because one of the tiles is there, and to access that tile means
            # you have access to where the minikit spawns.
            "Side Access Corridor Behind Force Field",
            CAN_DAMAGE_AT_CLOSE_RANGE,
            pickup_names=(
                "m_pup1",
                "m_pup3",
                "m_pup4",
            ),
        ),
        "Sliding Blocks Room Minikit": minikit_data(
            "Sliding Blocks Room",
            HasAbility(JEDI),
            pickup_name="mk_0",
        ),
        "Secret Wall Compartment Minikit": minikit_data(
            "R2-D2 And Leia Access Corridor",
            HasAbility(JEDI),
            pickup_name="pup1",
        ),
        "Crane Room Minikit": minikit_data(
            "Crane Room",
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
            "Escape Pod Corridor",
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
            "Escape Pod Corridor",
            CAN_SITH_FORCE & HasAbility(ASTROMECH_PANEL),
            pickup_name="m_pup1",
        ),
    },
    power_brick=LocationData("Side Access Corridor Behind Force Field", HasAbility(JEDI)),
    ridables={
        "Moon Car": LocationData("Side Access Corridor",
                                 HasAbility(CAN_BUILD_BRICKS) & CAN_DESTROY_CLOSE_SILVER_BRICKS),
        "Town Car": LocationData("Side Access Corridor Behind Force Field", HasAbility(JEDI)),
    },
)
