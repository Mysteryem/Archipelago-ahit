import math

from BaseClasses import CollectionState, Entrance, Item, Region, Tutorial, MultiWorld

from worlds.AutoWorld import WebWorld, World, LogicMixin

from .Items import JigsawItem, item_table
from .Locations import JigsawLocation, location_table

from .Options import JigsawOptions, OrientationOfImage
from .Rules import set_jigsaw_rules, PuzzleBoard
from worlds.generic.Rules import set_rule


class JigsawWeb(WebWorld):
    tutorials = [
        Tutorial(
            "Multiworld Setup Guide",
            "A guide to setting up Jigsaw. This guide covers single-player, multiworld, and website.",
            "English",
            "setup_en.md",
            "setup/en",
            ["Spineraks"],
        )
    ]


class JigsawMixin(LogicMixin):
    def init_mixin(self, parent: MultiWorld):
        self._jigsaw_boards = {}

    def copy_mixin(self, ret: CollectionState) -> CollectionState:
        ret._jigsaw_boards = {player: board.copy() for player, board in self._jigsaw_boards.items()}
        return ret


class JigsawWorld(World):
    """
    Make a Jigsaw puzzle! But first you'll have to find your pieces.
    Connect the pieces to unlock more. Goal: solve the puzzle of course!
    """

    game: str = "Jigsaw"
    options_dataclass = JigsawOptions

    web = JigsawWeb()

    item_name_to_id = {name: data.code for name, data in item_table.items()}

    location_name_to_id = {name: data.id for name, data in location_table.items()}
    
    ap_world_version = "0.0.2"

    def _get_jigsaw_data(self):
        return {
            # "world_seed": self.multiworld.per_slot_randoms[self.player].getrandbits(32),
            "seed_name": self.multiworld.seed_name,
            "player_name": self.multiworld.get_player_name(self.player),
            "player_id": self.player,
            "race": self.multiworld.is_race,
        }
        
    def calculate_optimal_nx_and_ny(self, number_of_pieces, orientation):
        def mround(x):
            return int(round(x))

        def msqrt(x):
            return math.sqrt(x)

        def mabs(x):
            return abs(x)
        
        height = 1
        width = orientation

        nHPieces = mround(msqrt(number_of_pieces * width / height))
        nVPieces = mround(number_of_pieces / nHPieces)
        
        errmin = float('inf')
        optimal_nx, optimal_ny = nHPieces, nVPieces

        for ky in range(5):
            ncv = nVPieces + ky - 2
            for kx in range(5):
                nch = nHPieces + kx - 2
                err = nch * height / ncv / width
                err = (err + 1 / err) - 2  # error on pieces dimensions ratio
                err += mabs(1 - nch * ncv / number_of_pieces)  # adds error on number of pieces

                if err < errmin:  # keep smallest error
                    errmin = err
                    optimal_nx, optimal_ny = nch, ncv

        return optimal_nx, optimal_ny

    def generate_early(self):
        self.orientation = 1
        if self.options.orientation_of_image == OrientationOfImage.option_landscape:
            self.orientation = 1.5
        if self.options.orientation_of_image == OrientationOfImage.option_portrait:
            self.orientation = 0.8
        self.nx, self.ny = self.calculate_optimal_nx_and_ny(self.options.number_of_pieces.value, self.orientation)
        self.npieces = self.nx * self.ny
        self.base_board = PuzzleBoard(self.nx, self.ny)
        
        self.pool_pieces = [i for i in range(1, self.npieces + 1)]
        self.multiworld.random.shuffle(self.pool_pieces)

        board = PuzzleBoard(self.nx, self.ny)

        start_pieces = []
        max_merges = max(3, math.pow(self.nx * self.ny, 0.4))
        while board.merges_count < max_merges:
            p = self.pool_pieces.pop(0)
            start_pieces.append(p)
            board.add_piece(p - 1)

        self.pool_pieces = [f"Puzzle Piece {i}" for i in self.pool_pieces]

        for i in start_pieces:
            self.multiworld.push_precollected(self.create_item(f"Puzzle Piece {i}"))
            
        self.pool_pieces += ["Squawks"] * (self.npieces - len(self.pool_pieces) - 2)

            

    def create_items(self):
        self.multiworld.itempool += [self.create_item(name) for name in self.pool_pieces]

    def create_regions(self):

        # simple menu-board construction
        menu = Region("Menu", self.player, self.multiworld)
        board = Region("Board", self.player, self.multiworld)

        # add locations to board, one for every location in the location_table
        board.locations = [
            JigsawLocation(self.player, f"Connect {i} Pieces", i, 234782000+i, board)
            for i in range(2, self.npieces)
        ]

        # add the regions
        connection = Entrance(self.player, "New Board", menu)
        menu.exits.append(connection)
        connection.connect(board)
        self.multiworld.regions += [menu, board]

    def get_filler_item_name(self) -> str:
        return "Squawks"

    def set_rules(self):
        """
        set rules per location, and add the rule for beating the game
        """

        set_jigsaw_rules(self.multiworld, self.player)

        self.multiworld.completion_condition[self.player] = lambda state: all(
            state.has(f"Puzzle Piece {i}", self.player) for i in range(1, self.npieces + 1)
        )

    def create_item(self, name: str) -> Item:
        item_data = item_table[name]
        item = JigsawItem(name, item_data.classification, item_data.code, self.player, item_data.piece_nr)
        return item

    def fill_slot_data(self):
        """
        make slot data, which consists of jigsaw_data, options, and some other variables.
        """
        slot_data = self._get_jigsaw_data()
        
        slot_data["orientation"] = self.orientation
        slot_data["nx"] = self.nx
        slot_data["ny"] = self.ny
        return slot_data
    
    # We overwrite these function to monitor when states have changed. See also dice_simulation in Rules.py
    def collect(self, state: CollectionState, item: Item) -> bool:
        change = super().collect(state, item)
        if change:
            if state.prog_items[self.player][item.name] == 1:
                # The piece is new, so add it to the board.
                board = state._jigsaw_boards.get(self.player)
                if board is None:
                    # Initialize board if it has not been initialized yet.
                    board = self.base_board.copy()
                    state._jigsaw_boards[self.player] = board

                board.add_piece(item.piece_nr)
        return change

    def remove(self, state: CollectionState, item: Item) -> bool:
        change = super().remove(state, item)
        if change:
            if state.prog_items[self.player][item.name] == 0:
                # The piece has been removed, so remove it from the board.
                board = state._jigsaw_boards.get(self.player)
                if board is None:
                    raise RuntimeError("Removed a piece, but there is no board???")
                    # # Initialize board if it has not been initialized yet.
                    # board = self.base_board.copy()
                    # state._jigsaw_boards[self.player] = board

                board.remove_piece(item.piece_nr)
        return change
