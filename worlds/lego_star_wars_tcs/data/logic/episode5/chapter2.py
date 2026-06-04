from ..types import make_legacy_chapter, LegacyMinikitData

ESCAPE_FROM_ECHO_BASE = make_legacy_chapter(
    short_name="5-2",
    minikits={
        "Spawn Room Consoles Minikit": LegacyMinikitData.new("hothescape_a", "m_pup2"),
        "Four Buttons Thaw Skeletons Minikit": LegacyMinikitData.new("hothescape_a", "m_pup1"),
        "Double Score Zone Alcove Above Track Minikit": LegacyMinikitData.new("hothescape_a", "m_pup3"),
        "Stormtrooper Fishing Minikit": LegacyMinikitData.new("hothescape_b", "pup1"),
        "Hidden Minikit In Snowmobile Room Wall": LegacyMinikitData.new("hothescape_b", "pup2"),
        "High Minikit In Snowmobile Room": LegacyMinikitData.new("hothescape_b", "pup4"),
        "Fan Minikit In Blocked Off Room": LegacyMinikitData.new("hothescape_b", "m_pup1"),
        "Minikit In Double Score Zone Tube": LegacyMinikitData.new("hothescape_c", "pup1"),
        "Minikit Inside Green-Yellow Shutter": LegacyMinikitData.new("hothescape_c", "pup2"),
        "Access Hatch Snow Canopy Minikit": LegacyMinikitData.new("hothescape_d", "pup1"),
    },
    extra_toggle_characters=(
        "Skeleton",
        "Rebel Engineer",
    ),
)
