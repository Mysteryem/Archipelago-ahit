from ...rules import HasAbility
from ...types import minikit_data, ExitData, Chapter, LocationData

from .....character_ability import VEHICLE_TIE

MOS_ESPA_POD_RACE = Chapter(
    name="Mos Espa Pod Race",
    episode_number=1,
    chapter_number=4,
    start_region="Racetrack",
    start_level="podsprint_a",
    vehicle_level=True,
    regions={
        "Racetrack": (
            ExitData("Chapter Completion", new_level="podsprint_status"),
        ),
        "Chapter Completion": (),
    },
    minikits={
        "TIE Service Ramp Minikit": minikit_data(
            "Racetrack",
            # todo: I'm pretty sure it is possible to clip through the TIE gate, or to squeeze behind it on the left,
            #  using character swapping.
            HasAbility(VEHICLE_TIE),
            pickup_name="m_pup3"
        ),
        "Cave Minikit": minikit_data(
            "Racetrack",
            pickup_name="m_pup4"
        ),
        "Tusken Canyon Minikit": minikit_data(
            "Racetrack",
            pickup_name="m_pup5"
        ),
        "Corner After Tusken Canyon Minikit": minikit_data(
            "Racetrack",
            pickup_name="m_pup6"
        ),
        "Beneath Rock Arches Minikit": minikit_data(
            "Racetrack",
            pickup_name="m_pup7"
        ),
        "After Rock Arches Minikit": minikit_data(
            "Racetrack",
            pickup_name="m_pup8",
        ),
        "Finish Straight Minikit": minikit_data(
            "Racetrack",
            pickup_name="m_pup9"
        ),
        "Before Finish Line Minikit": minikit_data(
            "Racetrack",
            pickup_name="m_pup10"
        ),
        "Lap 2 Center Path Minikit": minikit_data(
            "Racetrack",
            pickup_name="m_pup1"
        ),
        "Lap 3 End Of Right Path Minikit": minikit_data(
            "Racetrack",
            pickup_name="m_pup2"
        ),
    },
    power_brick=LocationData(
        "Racetrack",
    )
)
