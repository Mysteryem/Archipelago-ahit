from ..types import make_legacy_chapter, LegacyMinikitData

RESCUE_THE_PRINCESS = make_legacy_chapter(
    short_name="4-4",
    minikits={
        "Minikit Inside Protocol Droid Door": LegacyMinikitData.new("deathstarrescue_a", "mk_0"),
        "Defeat Imperials With Crane Minikit": LegacyMinikitData.new("deathstarrescue_a", "m_pup1"),
        "Minikit Above Bridge Levers": LegacyMinikitData.new("deathstarrescue_b", "pup1"),
        "Right Corridor High Minikit": LegacyMinikitData.new("deathstarrescue_b", "mk_0"),
        "Right Corridor Alcove Minikit": LegacyMinikitData.new("deathstarrescue_b", "mk_1"),
        "Right Corridor Access Hatch Minikit": LegacyMinikitData.new("deathstarrescue_b", "mk_2"),
        "Turntable Room Minikit": LegacyMinikitData.new("deathstarrescue_c", "mk_0"),
        "Imperial Phones Room Minikit": LegacyMinikitData.new("deathstarrescue_c", "m_pup1"),
        "Caged Minikit": LegacyMinikitData.new("deathstarrescue_c", "mk_1"),
        "Holding Cell Minikit": LegacyMinikitData.new("deathstarrescue_c", "mk_2"),
    },
    extra_toggle_characters=(
        "Skeleton",
        "Mouse Droid",
        "Imperial Engineer",
    ),
)
