import asyncio
import copy
import contextlib
import logging
import sys
import typing

import Utils
from BaseClasses import ItemClassification
from CommonClient import (
    CommonContext,
    server_loop,
    gui_enabled,
    get_base_parser,
    handle_url_arg,
    ClientCommandProcessor,
    logger
)
from NetUtils import NetworkItem, JSONMessagePart


# Duck-typing for ctx.ui set as ctx.suppressible_logging because the actual class cannot be referred to due to weird
# kvui import order issues.
class Suppressible(typing.Protocol):
    def suppress(self, do_suppress: bool) -> typing.ContextManager[None]:
        ...


# Default value for ctx.suppressible_logging when not set yet. `Suppressible` is easier to work with than
# `Suppressible | None`.
class NullSuppress:
    @staticmethod
    def suppress(do_suppress: bool):
        return contextlib.nullcontext()


class FilteredTextCommandProcess(ClientCommandProcessor):
    # This is a crap way to let the user toggle options on and off, but I'm not learning kivy in an evening.
    # These options don't persist either, so will have to be set again each time.

    def _cmd_toggle_chat(self):
        """Toggle chat messages on/off"""
        ctx = self.ctx
        if isinstance(ctx, FilteredTextContext):
            ctx.chat_enabled = not ctx.chat_enabled
            if ctx.chat_enabled:
                logger.info("Chat messages enabled")
            else:
                logger.info("Chat messages disabled")

    def _cmd_toggle_connections(self):
        """Toggle connection (join/leave) messages on/off"""
        ctx = self.ctx
        if isinstance(ctx, FilteredTextContext):
            ctx.connections_enabled = not ctx.connections_enabled
            if ctx.connections_enabled:
                logger.info("Connection messages enabled")
            else:
                logger.info("Connection messages disabled")

    def _cmd_toggle_items(self):
        """Toggle item send/receive messages on/off"""
        ctx = self.ctx
        if isinstance(ctx, FilteredTextContext):
            ctx.items_enabled = not ctx.items_enabled
            if ctx.items_enabled:
                logger.info("Item send/receive messages globally enabled")
            else:
                logger.info("Item send/receive messages globally disabled")

    def _cmd_toggle_other_player_items(self):
        """Toggle displaying item send/receive messages for players other than yourself"""
        ctx = self.ctx
        if isinstance(ctx, FilteredTextContext):
            ctx.other_player_items_enabled = not ctx.other_player_items_enabled
            if ctx.other_player_items_enabled:
                logger.info("Other player item send/receive messages enabled")
            else:
                logger.info("Other player item send/receive messages disabled")

    def _cmd_toggle_progression_only(self):
        """Toggle showing only progression items in send/receive messages"""
        ctx = self.ctx
        if isinstance(ctx, FilteredTextContext):
            ctx.progression_only_enabled = not ctx.progression_only_enabled
            if ctx.progression_only_enabled:
                logger.info("Only progression items will be shown in item send/receive messages")
            else:
                logger.info("All classifications of items will be shown in item send/receive messages")

    def _cmd_toggle_deathlink(self):
        """Toggle showing deathlink death messages"""
        ctx = self.ctx
        if isinstance(ctx, FilteredTextContext):
            ctx.deathlink_messages_enabled = not ctx.deathlink_messages_enabled
            if ctx.deathlink_messages_enabled:
                logger.info("Showing DeathLink death messages enabled")
            else:
                logger.info("Showing DeathLink death messages disabled")


# Mostly copied from CommonClient.run_as_textclient
class FilteredTextContext(CommonContext):
    # Also using the DeathLink tag so the client can see (and optionally filter out) DeathLink messages.
    # The client does not have the capability to send deaths.
    tags = CommonContext.tags | {"TextOnly", "DeathLink"}
    command_processor = FilteredTextCommandProcess
    game = ""
    items_handling = 0b111
    want_slot_data = False

    suppressible_logging: Suppressible = NullSuppress()

    chat_enabled: bool = True
    connections_enabled: bool = True
    items_enabled: bool = True
    other_player_items_enabled: bool = True
    progression_only_enabled: bool = False
    deathlink_messages_enabled: bool = True

    async def server_auth(self, password_requested: bool = False):
        if password_requested and not self.password:
            await super().server_auth(password_requested)
        await self.get_username()
        await self.send_connect(game="")

    def on_package(self, cmd: str, args: dict):
        if cmd == "Connected":
            self.game = self.slot_info[self.slot].game

    async def disconnect(self, allow_autoreconnect: bool = False):
        self.game = ""
        await super().disconnect(allow_autoreconnect)

    def _print_json_filter(self, args: dict):
        if "type" in args:
            message_type = args["type"]

            if message_type == "ItemSend":
                if not self.items_enabled:
                    # Item sending/receiving messages are disabled.
                    return False

                item: NetworkItem = args["item"]
                if self.progression_only_enabled and ItemClassification.progression not in ItemClassification(
                        item.flags):
                    # Skip displaying non-progression.
                    return False

                recipient = args["receiving"]
                if (not self.other_player_items_enabled
                        and not self.slot_concerns_self(recipient)
                        and not self.slot_concerns_self(item.player)):
                    # Skip displaying an item not for ourself or from ourself.
                    return False
            elif message_type == "Join":
                if not self.connections_enabled:
                    return False
            elif message_type == "Part":
                if not self.connections_enabled:
                    return False
            elif message_type == "Chat":
                if not self.chat_enabled:
                    return False
        return True

    def on_print_json(self, args: dict):
        args2 = copy.deepcopy(args)

        with self.suppressible_logging.suppress(not self._print_json_filter(args2)):
            super().on_print_json(args)

    def on_deathlink(self, data: typing.Dict[str, typing.Any]) -> None:
        with self.suppressible_logging.suppress(not self.deathlink_messages_enabled):
            super().on_deathlink(data)

    def run_gui(self):
        from kvui import GameManager, UILog
        from kivy.uix.layout import Layout

        class SuppressibleUiLog(UILog):
            """Ignores received messages when suppressed"""
            suppressed: bool = False

            def on_log(self, record: str) -> None:
                if not self.suppressed:
                    super().on_log(record)

            def on_message_markup(self, text: str):
                if not self.suppressed:
                    super().on_message_markup(text)

        class FilteredTextGameManager(GameManager):

            base_title = "Archipelago Filtered Text Client"

            def build(self) -> Layout:
                filtered_panel = SuppressibleUiLog(logging.getLogger("Client"))
                layout = super().build()
                self.log_panels["Filtered"] = filtered_panel
                self.add_client_tab("Filtered", filtered_panel, index=1)
                return layout

            def print_json(self, data: typing.List[JSONMessagePart]):
                text = self.json_to_kivy_parser(data)
                self.log_panels["Archipelago"].on_message_markup(text)
                self.log_panels["All"].on_message_markup(text)
                self.log_panels["Filtered"].on_message_markup(text)

            @contextlib.contextmanager
            def suppress(self, do_suppress: bool):
                try:
                    if do_suppress:
                        self.log_panels["Filtered"].suppressed = True
                    yield
                finally:
                    if do_suppress:
                        self.log_panels["Filtered"].suppressed = False

        new_ui = FilteredTextGameManager(self)
        self.ui = new_ui
        self.suppressible_logging = new_ui
        self.ui_task = asyncio.create_task(self.ui.async_run(), name="UI")


def run(*args):
    async def main(args):
        ctx = FilteredTextContext(args.connect, args.password)
        ctx.auth = args.name
        ctx.server_task = asyncio.create_task(server_loop(ctx), name="server loop")

        if gui_enabled:
            ctx.run_gui()
        ctx.run_cli()

        await ctx.exit_event.wait()
        await ctx.shutdown()

    Utils.init_logging("FilterableTextClient", exception_logger="Client")

    import colorama

    parser = get_base_parser(description="Gameless Archipelago Client, for text interfacing.")
    parser.add_argument('--name', default=None, help="Slot Name to connect as.")
    parser.add_argument("url", nargs="?", help="Archipelago connection url")
    args = parser.parse_args(args)

    args = handle_url_arg(args, parser=parser)

    # use colorama to display colored text highlighting on windows
    colorama.just_fix_windows_console()

    asyncio.run(main(args))
    colorama.deinit()


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)  # force log-level to work around log level resetting to WARNING
    run(*sys.argv[1:])  # default value for parse_args
