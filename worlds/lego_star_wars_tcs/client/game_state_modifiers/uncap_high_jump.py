from ..common import ClientComponent, StaticFloat
from ..events import subscribe_event, OnAreaChangeEvent, OnReceiveSlotDataEvent
from ..type_aliases import TCSContext
from ...options import UncapOriginalTrilogyHighJump

_HIGH_JUMP_CAP = StaticFloat(0x802d94)


class UncapHighJump(ClientComponent):
    uncap_high_jump: bool = False

    def adjust_high_jump_cap(self, ctx: TCSContext):
        if self.uncap_high_jump:
            _HIGH_JUMP_CAP.set(ctx, 1.14)

    @subscribe_event
    def on_receive_slot_data(self, event: OnReceiveSlotDataEvent):
        self.uncap_high_jump = bool(event.get_slot_data_option(UncapOriginalTrilogyHighJump))
        self.adjust_high_jump_cap(event.context)

    @subscribe_event
    def on_area_change(self, event: OnAreaChangeEvent):
        self.adjust_high_jump_cap(event.context)
