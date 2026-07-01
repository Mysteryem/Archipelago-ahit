from rule_builder.rules import True_, False_, Or

from ..option_filters import logic_options
from ..rules import HasAbility
from ..types import minikit_data, ExitData, Chapter, LocationData

from ...areas import Area
from ...extras import Extra
from ...levels import Level

from ....character_ability import *
from ....data.characters import Character

# Maybe this could be in Moderate logic, but it kind of sucks due to RNG and how long it can take, so it's going in Hard
# logic.
_CAN_DEFLECT_BOLTS_TO_DESTROY_THINGS = logic_options(
    base=False_(),
    hard=Extra.DEFLECT_BOLTS.has(),
)

FALCON_FLIGHT = Chapter(
    area=Area.ASTEROIDCHASE,
    start_region="Star Destroyer Battle",
    regions={
        "Star Destroyer Battle": (
            ExitData(
                "After Star Destroyer Battle",
                # Torpedoes do not target the Star Destroyer weapons.
                HasAbility(VEHICLE_BLASTER) | _CAN_DEFLECT_BOLTS_TO_DESTROY_THINGS,
                new_level=Level.ASTEROIDCHASE_A,
            ),
        ),
        "After Star Destroyer Battle": (
            ExitData(
                "First TIE Gate Area",
                logic_options(
                    base=HasAbility(VEHICLE_TIE),
                    # For this TIE Gate skip, approach the gate and allow your vehicle to automatically turn to the
                    # side upon colliding with the gate. Then turn the vehicle slightly back towards the camera so that
                    # when the vehicle collides with the wall on either side of the TIE gate, the vehicle turns away
                    # from the TIE Gate (instead of getting stuck in the corner and automatically performing a
                    # turn-around-loop. As soon as the vehicle turns away from the TIE gate, input a regular loop
                    hard=Or(
                        HasAbility(VEHICLE_TIE),
                        Character.has_any(
                            Character.SLAVE_1,
                            Character.IMPERIAL_SHUTTLE,
                            Character.MILLENNIUM_FALCON,
                            Character.X_WING,
                            Character.Y_WING,
                            Character.NABOO_STARFIGHTER,
                            Character.ANAKINS_POD,  # P1 tends to get over the gate rather than P2.
                            Character.CLONE_ARCFIGHTER,
                            Character.SEBULBAS_POD,  # P1 tends to get over the gate rather than P2.
                            Character.REPUBLIC_GUNSHIP,
                        ),
                    ),
                ),
            ),
            ExitData(
                "After Blocked Tunnel",
                # Need torpedoes to un-block the tunnel. The small destroyable asteroids in this area spawn brick chunks
                # that drop torpedoes when colliding into them with a vehicle. These asteroids respawn after a short
                # period, and can be destroyed with deflected enemy blaster bolts.
                logic_options(
                    base=True_(),
                    hard=Or(
                        HasAbility(VEHICLE_BLASTER),
                        Extra.has_any(Extra.INFINITE_TORPEDOS, Extra.DEFLECT_BOLTS),
                    ),
                ),
                new_level=Level.ASTEROIDCHASE_B,
            ),
        ),
        "First TIE Gate Area": (),
        "After Blocked Tunnel": (
            ExitData(
                "Huge Asteroid TIE Gate Area",
                logic_options(
                    base=HasAbility(VEHICLE_TIE),
                    # Skipping this TIE Gate is more difficult than the first TIE Gate because one side of the gate does
                    # not orientate the player away from the TIE Gate, and the other side of the gate is obscured by
                    # terrain.
                    # However, most smaller vehicles can also get over this TIE Gate; the collision of the gate seems to
                    # not extend as high as with the first TIE Gate.
                    hard=Or(
                        HasAbility(VEHICLE_TIE),
                        Character.has_any(
                            Character.SLAVE_1,
                            Character.IMPERIAL_SHUTTLE,
                            Character.MILLENNIUM_FALCON,
                            Character.SNOWSPEEDER,
                            Character.X_WING,
                            Character.Y_WING,
                            Character.NABOO_STARFIGHTER,
                            Character.ANAKINS_POD,
                            Character.CLONE_ARCFIGHTER,
                            Character.VULTURE_DROID,
                            Character.DROID_TRIFIGHTER,
                            Character.SEBULBAS_POD,
                            Character.JEDI_STARFIGHTER_RED,
                            Character.JEDI_STARFIGHTER_YELLOW,
                            Character.REPUBLIC_GUNSHIP,
                        ),
                    )
                )
            ),
            ExitData(
                "After Huge Asteroid",
                new_level=Level.ASTEROIDCHASE_C,
            )
        ),
        "Huge Asteroid TIE Gate Area": (),
        "After Huge Asteroid": (
            ExitData(
                "Chapter Completion"
            ),
        ),
    },
    minikits={
        "Behind Star Destroyer Minikit": minikit_data(
            "Star Destroyer Battle",
            # Probably possible with just Deflect Bolts, but most of the enemy vehicles do not fly over here, and the
            # turrets in the level will target the closest friendly vehicle
            HasAbility(VEHICLE_BLASTER),
            pickup_name="m_pup1",
        ),
        "Behind First TIE Gate Minikit 1": minikit_data(
            "First TIE Gate Area",
            HasAbility(VEHICLE_TOW),
            pickup_name="m_pup2",
        ),
        "Behind First TIE Gate Minikit 2": minikit_data(
            "First TIE Gate Area",
            HasAbility(VEHICLE_TOW),
            pickup_name="m_pup3",
        ),
        "Loose Minikit Before Blocked Tunnel": minikit_data(
            "After Star Destroyer Battle",
            # Base through to Moderate expect VEHICLE_BLASTER to get here.
            logic_options(
                base=True_(),
                hard=HasAbility(VEHICLE_BLASTER) | Extra.has_any(Extra.INFINITE_TORPEDOS, Extra.DEFLECT_BOLTS),
            ),
            er_rule=logic_options(
                base=HasAbility(VEHICLE_BLASTER),
                # Allow using torpedoes. A point-blank torpedo destroys the minikit.
                moderate=HasAbility(VEHICLE_BLASTER) | Extra.INFINITE_TORPEDOS.has(),
                # Allow deflecting enemy vehicle blaster bolts into the minikit.
                hard=HasAbility(VEHICLE_BLASTER) | Extra.has_any(Extra.INFINITE_TORPEDOS, Extra.DEFLECT_BOLTS),
            ),
            pickup_name="m_pup4",
        ),
        "Loose Minikit After Blocked Tunnel": minikit_data(
            "After Blocked Tunnel",
            pickup_name="m_pup5",
        ),
        "Huge Asteroid TIE Gate Torpedo Minikit": minikit_data(
            "Huge Asteroid TIE Gate Area",
            pickup_name="m_pup6",
        ),
        "Huge Asteroid Torpedo Minikit 1": minikit_data(
            "After Blocked Tunnel",
            pickup_name="m_pup7",
        ),
        "Huge Asteroid Torpedo Minikit 2": minikit_data(
            "After Blocked Tunnel",
            pickup_name="m_pup8",
        ),
        "Minikit Inside Space Slug Mouth": minikit_data(
            "After Blocked Tunnel",
            logic_options(
                base=True_(),
                hard=HasAbility(VEHICLE_BLASTER),
            ),
            pickup_name="m_pup9",
        ),
        "Final Area Asteroid Alcove Minikit": minikit_data(
            "After Huge Asteroid",
            pickup_name="m_pup10",
        )
    },
    power_brick=LocationData("Star Destroyer Battle"),
)
