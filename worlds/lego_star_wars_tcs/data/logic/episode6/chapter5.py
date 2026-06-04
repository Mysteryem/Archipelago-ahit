from ..types import make_legacy_chapter, LegacyMinikitData

JEDI_DESTINY = make_legacy_chapter(
    short_name="6-5",
    minikits={
        "Silver Brick Panels And Red Buttons Minikit": LegacyMinikitData.new("emperorfight_a", "MINI_3"),
        "Grapple Platform Right Of Spawn Minikit": LegacyMinikitData.new("emperorfight_a", "pup1"),
        "Spawn Left Alcove Minikit": LegacyMinikitData.new("emperorfight_a", "mk_0"),
        "Below Electric Floor Minikit": LegacyMinikitData.new("emperorfight_a", "mk_1"),
        "Protocol Panel Walkway Room Minikit": LegacyMinikitData.new("emperorfight_a", "MINI_PI"),
        "Four Lights Force Field Minikit": LegacyMinikitData.new("emperorfight_a", "M_RED"),
        "Silver Bricks Central Column Minikit": LegacyMinikitData.new("emperorfight_a", "m_pup1"),

        "Red Room Access Hatch Minikit": LegacyMinikitData.new("emperorfight_b", "m_pup1"),
        "Red Room Left Force Field Minikit": LegacyMinikitData.new("emperorfight_b", "mk_0"),
        "Red Room Grate Force Field Minikit": LegacyMinikitData.new("emperorfight_b", "mk_1"),
    },
    extra_toggle_characters=(
        "Mouse Droid",
        "Imperial Engineer",
    ),
)
