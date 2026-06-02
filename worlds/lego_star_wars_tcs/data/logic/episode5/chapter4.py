from ..types import make_legacy_chapter, LegacyMinikitData

DAGOBAH = make_legacy_chapter(
    short_name="5-4",
    start_level="dagobah_a",
    minikits={
        "Spawn Tree Minikit": LegacyMinikitData.new("dagobah_a", "m_pup2"),
        "Snake Central Island Minikit": LegacyMinikitData.new("dagobah_a", "m_pup1"),

        "Yoda's TV Minikit": LegacyMinikitData.new("dagobah_e", "m_pup2"),

        "Open Three Hatches Minikit": LegacyMinikitData("dagobah_e", ("m_pup1", "m_pup3", "m_pup4")),

        "Silver Brick Cave Minikit": LegacyMinikitData.new("dagobah_b", "m_pup3"),
        "Grapple Minikit After Hut": LegacyMinikitData.new("dagobah_b", "m_pup2"),

        "Sith Force Bridge Minikit": LegacyMinikitData.new("dagobah_d", "m_pup1"),
        "Caged Minikit": LegacyMinikitData.new("dagobah_d", "m_pup2"),
        "Many Collapsing Platforms Minikit": LegacyMinikitData.new("dagobah_d", "m_pup4"),

        "Final Area Lever Minikit": LegacyMinikitData.new("dagobah_c", "m_pup1"),
    },
    extra_toggle_characters=(
        "Skeleton",
    )
)
