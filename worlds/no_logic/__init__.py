import Utils
from BaseClasses import MultiWorld
from Generate import main as generate_main, mystery_argparse
from Options import Accessibility
from worlds.AutoWorld import World
from worlds.LauncherComponents import components, Component, Type, launch_subprocess


# __main__ copied from Generate.py
def _generate___main__(*args):
    # Commented out the atexit stuff because the input gets an EOF and I don't want to figure out how to get this to
    # run in a window without a full CommonContext subclass.
    #import atexit
    #confirmation = atexit.register(input, "Press enter to close.")
    # args added so you can 'python Launcher.py "Generate No-Logic" -- --seed 1234' without generate_main complaining.
    erargs, seed = generate_main(mystery_argparse(list(args)))
    from Main import main as ERmain
    multiworld = ERmain(erargs, seed)
    if __debug__:
        import gc
        import sys
        import weakref
        weak = weakref.ref(multiworld)
        del multiworld
        gc.collect()  # need to collect to deref all hard references
        assert not weak(), f"MultiWorld object was not de-allocated, it's referenced {sys.getrefcount(weak())} times." \
                           " This would be a memory leak."
    # in case of error-free exit should not need confirmation
    #atexit.unregister(confirmation)


def generate_no_logic_wrapper(*args):
    original_has_beaten_game = MultiWorld.has_beaten_game
    try:
        MultiWorld.has_beaten_game = lambda *_args: True
        Accessibility.value = property(
            fget=lambda *_args: Accessibility.option_minimal,
            fset=lambda *_args: None,
            fdel=lambda *_args: None,
        )
        # Generate.py only calls Utils.init_logging when __name__ == "__main__", so we need to initialize logging
        # ourselves.
        Utils.init_logging(f"NoLogicGenerate")
        # Call normal generation.
        _generate___main__(*args)
    finally:
        # Since we're launching a subprocess, restoring the original values is probably not necessary, but I cba
        # removing this now.
        MultiWorld.has_beaten_game = original_has_beaten_game
        del Accessibility.value


def launch(*launch_args: str):
    generate_no_logic_wrapper(*launch_args)


def launch_generate(*args: str):
    launch_subprocess(launch, name="GenerateNoLogic", args=args)


components.append(
    Component(
        "Generate No-Logic",
        func=launch_generate,
        description="Generate a No-Logic multiworld with the YAMLs in the players folder."
                    "\nForces `accessibility: minimal` and acts like goaling is always possible."
    )
)


# Need a World defined or "Build APWorlds" won't acknowledge our existence.
class NoLogicWorld(World):
    game = "No Logic Generator"
    hidden = True
    item_name_to_id = {}
    location_name_to_id = {}
