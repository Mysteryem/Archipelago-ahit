from ..types import make_legacy_chapter, LegacyMinikitData

HOTH_BATTLE = make_legacy_chapter(
    short_name="5-1",
    minikits={
        "Minikit Behind Wall In First Area": LegacyMinikitData.new("hothbattle_a", "m_pup1"),
        "First TIE Gate Behind Rock Minikit": LegacyMinikitData.new("hothbattle_a", "m_pup2"),
        "First Area Trip AT-STs Minikit": LegacyMinikitData.new("hothbattle_a", "m_pup3"),
        "Rescue Rebels In Cave Minikit": LegacyMinikitData.new("hothbattle_b", "m_pup4"),
        "Second Area Trip AT-STs Minikit": LegacyMinikitData.new("hothbattle_c", "m_pup7"),
        "Second Area Minikit Right Of Last Wall": LegacyMinikitData.new("hothbattle_c", "m_pup8"),
        "Second TIE Gate Cave Minikit": LegacyMinikitData.new("hothbattle_d", "m_pup5"),
        "Second TIE Gate Rock After Cave Minikit": LegacyMinikitData.new("hothbattle_d", "m_pup6"),
        "Final Battle Behind Rock Minikit 1": LegacyMinikitData.new("hothbattle_e", "m_pup9"),
        "Final Battle Behind Rock Minikit 2": LegacyMinikitData.new("hothbattle_e", "m_pup10"),
    },
)
