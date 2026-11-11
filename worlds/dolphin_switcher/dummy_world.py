"""Note: This file is not included in .apworld distribution. This file's existence is purely to load a world so that the
"Build APWorlds" Launcher Component can build this tool into a .apworld."""
import json
from pkgutil import get_data

_MANIFEST = json.loads(get_data(__name__, "archipelago.json"))

from worlds.AutoWorld import World

class DummyDMESwitcherWorld(World):
    game = _MANIFEST["game"]
    hidden = True
    item_name_to_id = {}
    location_name_to_id = {}
