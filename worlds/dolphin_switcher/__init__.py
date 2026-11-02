import logging
import os

from worlds.LauncherComponents import components, Component, Type
from Utils import messagebox, gui_enabled, is_kivy_running


ENV_VAR = "DME_DOLPHIN_PROCESS_NAME"
"""Dolphin Memory Engine attempts to find the Dolphin process by matching against process names. By default, this
matches against Dolphin.exe and some variations.

By overriding this environment variable"""


def _get_current_override_str() -> str:
    """Get a human-readable string of the current override value, intended for displaying in UI."""
    current_override = os.environ.get(ENV_VAR)
    if current_override is None:
        current_override_text = "No override set"
    elif isinstance(current_override, str):
        current_override_text = f"'{current_override}'"
    else:
        current_override_text = f"Error. Got '{current_override}' for current DME Dolphin process name."
    return current_override_text


def set_dolphin_exe_name(name: str):
    """Set the Dolphin process name override, or remove it if given an empty string."""
    title = "DME Dolphin Switcher"
    if name:
        os.environ[ENV_VAR] = name
        messagebox(title, f"Dolphin process name override set to '{name}'")
        logging.info("Set dolphin process name override to '%s'", name)
    else:
        if ENV_VAR in os.environ:
            del os.environ[ENV_VAR]
            text = "Dolphin process name override removed"
        else:
            text = "There was no Dolphin process name override to remove"
        messagebox(title, text)
        logging.info("Cleared dolphin process name")


def set_dolphin_name_override_popup(*_args: str):
    if not gui_enabled or not is_kivy_running():
        messagebox("No Kivy GUI available:",
                   "Cannot set the dolphin name without GUI or kivy. You can set the DME_DOLPHIN_PROCESS_NAME "
                   "environment variable before starting the Archipelago Launcher to change the Dolphin process name "
                   "override manually.",
                   error=True)
        return

    # kivy imports, at the module-level, are a mess that I don't want to deal with, so they are all lazy imports within
    # the function for now.
    from kivy.app import App
    from kivy.uix.gridlayout import GridLayout
    from kivy.uix.button import Button
    from kivy.uix.label import Label
    from kivy.uix.popup import Popup
    from kivy.uix.textinput import TextInput

    layout = GridLayout(cols=1, padding=10)

    label = Label(text=f"Current override: {_get_current_override_str()}\nSet to empty to remove override")

    # According to what I understand from the documentation, this should work. But when I try it, it is not possible
    # to type text into the input field, and I don't know why.
    # dolphin_name_override_input = TextInput(text="", multiline=False, focus=True)

    # Instead, make our own TextInput subclass that grabs focus in on_parent.
    class FocusTextInput(TextInput):
        def on_parent(self, widget, parent):
            self.focus = True

    dolphin_name_override_input = FocusTextInput(text="", multiline=False)

    button_sub_layout = GridLayout(cols=2, padding=10)
    apply_button = Button(text="Set")
    cancel_button = Button(text="Cancel")
    button_sub_layout.add_widget(apply_button)
    button_sub_layout.add_widget(cancel_button)

    layout.add_widget(label)
    layout.add_widget(dolphin_name_override_input)
    layout.add_widget(button_sub_layout)

    popup = Popup(title="DME Dolphin process name override",
                  content=layout,
                  size_hint=(None, None),
                  size=(300, 250),
                  )

    # Cancel button simply closes the popup, which the user can also do by clicking off the popup. The button just
    # gives users a more obvious option.
    cancel_button.bind(on_press=popup.dismiss)

    def on_press_apply(*args):
        set_dolphin_exe_name(dolphin_name_override_input.text)
        popup.dismiss()

    apply_button.bind(on_press=on_press_apply)
    # Hitting the Enter key in the Text Field should also set.
    dolphin_name_override_input.bind(on_text_validate=on_press_apply)

    # The Launcher class in Launcher.run_gui overrides _on_keyboard to always give focus to the search bar, meaning
    # that the user cannot type into any kind of popup box. We'll just monkeypatch this behaviour away, and restore
    # it when the popup box is closed.
    orig_on_keyboard = None
    def on_open_popup(*args):
        nonlocal orig_on_keyboard
        running_app = App.get_running_app()
        orig_on_keyboard = running_app._on_keyboard
        running_app._on_keyboard = lambda *args: None
    def on_dismiss_popup(*args):
        running_app = App.get_running_app()
        if orig_on_keyboard is not None:
            running_app._on_keyboard = orig_on_keyboard
    popup.bind(on_open=on_open_popup)
    popup.bind(on_dismiss=on_dismiss_popup)
    popup.open()


components.append(
    Component(
        "DME Dolphin Switcher",
        func=set_dolphin_name_override_popup,
        component_type=Type.TOOL,
        description="Set/Check the current override of the Dolphin process name."
                    "\nClients opened from this Launcher will use the current override value."
                    "\nChanging the override will not affect already opened clients."
    )
)