from ..types import make_legacy_chapter, LegacyMinikitData

REBEL_ATTACK = make_legacy_chapter(
    short_name="4-6",
    minikits={
        "First TIE Gate Minikit": LegacyMinikitData.new("deathstarbattle_a", "m_pup3"),
        "First Spinner Minikit": LegacyMinikitData.new("deathstarbattle_a", "m_pup1"),
        "First Hidden Alcove Minikit": LegacyMinikitData.new("deathstarbattle_a", "m_pup2"),
        "Second Spinner Minikit By Second TIE Gate": LegacyMinikitData.new("deathstarbattle_b", "m_pup4"),
        "Second TIE Gate Green Tiles Minikit": LegacyMinikitData.new("deathstarbattle_b", "m_pup5"),
        "Second Hidden Alcove Minikit": LegacyMinikitData.new("deathstarbattle_b", "m_pup6"),
        "Third TIE Gate Behind Force Field Minikit": LegacyMinikitData.new("deathstarbattle_b", "m_pup7"),
        "Third Spinner Minikit": LegacyMinikitData.new("deathstarbattle_c", "m_pup8"),
        "Third Alcove Minikit Before Trench Run": LegacyMinikitData.new("deathstarbattle_c", "m_pup9"),
        "Fourth Spinner Minikit By Exhaust Port": LegacyMinikitData.new("deathstarbattle_d", "m_pup10"),
    },
)
