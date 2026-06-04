from ..types import make_legacy_chapter, LegacyMinikitData

DEATH_STAR_ESCAPE = make_legacy_chapter(
    short_name="4-5",
    minikits={
        "Minikit Behind Silver Bricks": LegacyMinikitData.new("deathstarescape_a", "m_pup1"),
        "Access Hatch Minikit": LegacyMinikitData.new("deathstarescape_a", "mk_0"),
        "Window Washing Minikit": LegacyMinikitData.new("deathstarescape_b", "pup1"),
        "Minikit Behind Sith Force Bricks": LegacyMinikitData.new("deathstarescape_b", "pup2"),
        "High Minikit In Cylindrical Room": LegacyMinikitData.new("deathstarescape_b", "pup3"),
        "Hangar Right Minikit": LegacyMinikitData.new("deathstarescape_c", "pup1"),
        "Minikit By Vader": LegacyMinikitData.new("deathstarescape_c", "pup2"),
        "Stormtrooper Reinforcements Room Minikit": LegacyMinikitData.new("deathstarescape_c", "pup3"),
        "Corridor Start Minikit": LegacyMinikitData.new("deathstarescape_c", "pup4"),
        "Reveal Three Berry Tiles Minikit": LegacyMinikitData.new("deathstarescape_c", "m_pup1"),
    },
    extra_toggle_characters=(
        "Mouse Droid",
        "Imperial Engineer",
    )
)
