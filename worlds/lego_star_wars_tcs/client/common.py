import abc
from typing import Any

from .type_aliases import TCSContext


class StaticUChar(int):
    def get(self, ctx: TCSContext) -> int:
        return ctx.read_uchar(self)

    def set(self, ctx: TCSContext, value: int):
        ctx.write_byte(self, value)


class StaticFloat(int):
    def get(self, ctx: TCSContext) -> float:
        return ctx.read_float(self)

    def set(self, ctx: TCSContext, value: float):
        ctx.write_float(self, value)


class FloatField(int):
    def get(self, ctx: TCSContext, raw_address: int) -> float:
        return ctx.read_float(raw_address + self, raw=True)

    def set(self, ctx: TCSContext, raw_address: int, value: float):
        ctx.write_float(raw_address + self, value, raw=True)


class ClientComponent(abc.ABC):
    @abc.abstractmethod
    def init_from_slot_data(self, ctx: TCSContext, slot_data: dict[str, Any]) -> None: ...
