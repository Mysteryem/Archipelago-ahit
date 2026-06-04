from rule_builder.rules import True_

from ..option_filters import logic_options
from ..rules import HasAbility
from ..types import minikit_data, ExitData, Chapter, LocationData

from ...areas import Area
from ...levels import Level

from ....character_ability import *

NAME = "Gunship Cavalry"

R_SPAWN = "Spawn"
R_BEHIND_FIRST_FORCE_FIELD = "Behind First Force Field"
R_CONTROL_SHIP_BATTLE = "Control Ship Battle"

GUNSHIP_CAVALRY = Chapter(
    name=NAME,
    area=Area.GUNSHIP,
    story_characters=(
        "Republic Gunship",
    ),
    start_region=R_SPAWN,
    extra_chapter_entrance_rules=HasAbility(IS_A_VEHICLE),
    regions={
        R_SPAWN: (
            ExitData(R_BEHIND_FIRST_FORCE_FIELD, HasAbility(VEHICLE_TOW)),
        ),
        R_BEHIND_FIRST_FORCE_FIELD: (
            ExitData(
                R_CONTROL_SHIP_BATTLE,
                HasAbility(VEHICLE_TOW),
                new_level=Level.GUNSHIP_B,
            ),
        ),
        R_CONTROL_SHIP_BATTLE: (
            ExitData(
                "Chapter Completion",
                HasAbility(VEHICLE_TOW),
            ),
        ),
    },
    minikits={
        "Freestanding Minikit Before Lasers": minikit_data(
            R_SPAWN,
            pickup_name="m_pup1",
        ),
        "Freestanding Minikit After Fourth Laser": minikit_data(
            R_SPAWN,
            pickup_name="m_pup2",
        ),
        "TIE Area Minikit": minikit_data(
            R_SPAWN,
            logic_options(
                base=HasAbility(VEHICLE_TIE),
                # TIE vehicles can access as normal.
                #
                # For other vehicles use the Loop and P2 drop-in trick:
                # For larger vehicles:
                # Approach the gate from the north and input a loop while moving south parallel to the TIE gate.
                # Drop in P2 at the top of the loop, and have P2 move immediately to the left to get on top of and
                # over the TIE gate. Some vehicles will pretty much spawn on top of the cliff, trivialising the
                # trick.
                # A few of the larger vehicles can clear the gate doing this on their own, even without a drop-in
                # because the cliff face north of the TIE gate tends to push the player to the left as they loop
                # into it.
                #
                # For smaller vehicles:
                # Approach the gate from the south and allow the vehicle to freely travel north along the gate. Upon
                # reaching the top of the gate, the vehicle will automatically turn to the right. Input a loop here,
                # and drop-in P2 at the apex of the loop. P2 should spawn in, and then P1 will push P2 over the TIE
                # gate.
                # Sometimes, P1 will get over the gate on their own even without the P2 drop-in, but it does not seem
                # very consistent.
                #
                # Can use either method (method for smaller vehicles is easier though):
                # - Anakin's Pod
                # - Snowspeeder
                #
                # Use method for larger vehicles (can also get over on its own pretty consistently):
                # - Naboo Starfighter
                # - X-wing
                # - Y-wing (might not be able to get back out on its own)
                #
                # Use method for larger vehicles:
                # - Millennium Falcon
                # - Imperial Shuttle
                # - Slave 1
                # - Clone Arcfighter
                #
                # Use method for smaller vehicles:
                # - Anakin's Speeder
                # - Republic Gunship
                # - Sebulba's Pod
                # - Zam's Airspeeder
                # - Droid Trifighter
                # - Vulture Droid
                moderate=True_(),
            ),
            pickup_name="m_pup3",
        ),
        "Freestanding Minikit After First Force Field": minikit_data(
            R_BEHIND_FIRST_FORCE_FIELD,
            pickup_name="m_pup4",
        ),
        "Minikit Behind Yellow Wall": minikit_data(
            R_BEHIND_FIRST_FORCE_FIELD,
            pickup_name="m_pup5",
        ),
        "Control Ship Battle Minikit 1": minikit_data(
            R_CONTROL_SHIP_BATTLE,
            pickup_name="m_pup3",
        ),
        "Control Ship Battle Minikit 2": minikit_data(
            R_CONTROL_SHIP_BATTLE,
            pickup_name="m_pup4",
        ),
        "Control Ship Battle Minikit 3": minikit_data(
            R_CONTROL_SHIP_BATTLE,
            pickup_name="m_pup1",
        ),
        "Control Ship Battle Minikit 4": minikit_data(
            R_CONTROL_SHIP_BATTLE,
            pickup_name="m_pup2",
        ),
        "Control Ship Battle Minikit 5": minikit_data(
            R_CONTROL_SHIP_BATTLE,
            pickup_name="m_pup5",
        ),
    },
    power_brick=LocationData(R_BEHIND_FIRST_FORCE_FIELD),
)
