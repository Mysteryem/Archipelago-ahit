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


class StaticUint(int):
    def get(self, ctx: TCSContext) -> int:
        return ctx.read_uint(self)

    def set(self, ctx: TCSContext, value: int):
        ctx.write_uint(self, value)


class StaticBOOL(StaticUint):
    """Microsoft 4-byte BOOL"""
    def get(self, ctx: TCSContext) -> bool:
        return super().get(ctx) != 0


class FloatField(int):
    def get(self, ctx: TCSContext, raw_address: int) -> float:
        return ctx.read_float(raw_address + self, raw=True)

    def set(self, ctx: TCSContext, raw_address: int, value: float):
        ctx.write_float(raw_address + self, value, raw=True)


class UintField(int):
    def get(self, ctx: TCSContext, raw_address: int) -> int:
        return ctx.read_uint(raw_address + self, raw=True)

    def set(self, ctx: TCSContext, raw_address: int, value: int):
        ctx.write_uint(raw_address + self, value, raw=True)


class ClientComponent(abc.ABC):
    @abc.abstractmethod
    def init_from_slot_data(self, ctx: TCSContext, slot_data: dict[str, Any]) -> None: ...
