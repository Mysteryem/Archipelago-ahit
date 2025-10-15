import inspect
import logging
from dataclasses import dataclass, field
from typing import Callable, TypeVar, Any, ClassVar, Self, Protocol
from types import MethodType

from ..common import ClientComponent
from ..type_aliases import TCSContext


debug_logger = logging.getLogger("TCS Debug")


@dataclass
class Event:
    _subclasses: ClassVar[dict[str, type[Self]]] = {}
    context: TCSContext

    def __init_subclass__(cls, **kwargs):
        Event._subclasses[cls.__name__] = cls

    @staticmethod
    def get_subclass(subclass_name: str):
        return Event._subclasses.get(subclass_name)


_Subscriber = TypeVar("_Subscriber", covariant=True)


@dataclass
class EventManager:
    subscriptions: dict[type[Event], list[Callable[[Event], None]]] = field(default_factory=dict)

    def fire_event(self, event: Event):
        debug_logger.info("Firing event %s", event)
        for subscriber in self.subscriptions.get(type(event), ()):
            subscriber(event)

    def subscribe_events(self, instance: _Subscriber) -> _Subscriber:
        for _method_name, method in inspect.getmembers(instance, inspect.ismethod):
            func = getattr(method, "__func__", None)
            if func is None:
                continue
            event_type = getattr(func, "_event_subscription", None)
            if event_type is None:
                continue
            self.subscriptions.setdefault(event_type, []).append(method)
        return instance

    def subscribe_method(self, method, event_type: type[Event]):
        # todo: Validate the method.
        if not issubclass(event_type, Event):
            raise ValueError("event_type should be an Event subclass")
        self.subscriptions.setdefault(event_type, []).append(method)


# Some of the generics for subscribe_event are probably wrong, due to inexperience, but seem to work OK enough.
EVENT = TypeVar("EVENT", bound=Event, contravariant=True)


class EventSubscriberFun(Protocol[_Subscriber, EVENT]):
    def __call__(self: _Subscriber, event: EVENT) -> None:
        ...

    def __get__(self, instance, owner) -> MethodType:
        ...


def subscribe_event(fun: EventSubscriberFun[_Subscriber, EVENT]) -> EventSubscriberFun[_Subscriber, EVENT]:
    params = inspect.signature(fun).parameters
    params_iter = iter(params.values())
    # Skip the 'self' argument.
    next(params_iter)
    event_type = next(params_iter).annotation
    if issubclass(event_type, Event):
        pass
    elif isinstance(event_type, str):
        event_type = Event.get_subclass(event_type)
    else:
        raise ValueError(f"Invalid function to subscribe to events, the second argument should have an Event type"
                         f" annotation, but got {event_type}")

    class EventSubscriber:
        _event_subcription: type[EVENT]
        fun: EventSubscriberFun[_Subscriber, EVENT]

        def __init__(self, event_type: type[EVENT], fun: EventSubscriberFun[_Subscriber, EVENT]):
            self._event_subscription = event_type
            self.fun = fun

        # __set_name__ is used to check that the owner of the decorated method is a valid target for subscribing to
        # events.
        # If it worked, it would have been much simpler to set `fun.__set_name__` and then just return `fun`.
        def __set_name__(self, owner, name):
            if not issubclass(owner, ClientComponent):
                raise TypeError(
                    f"{subscribe_event.__name__} can only be used in classes that inherit from ClientComponent."
                    f"Use on {owner.__qualname__} is not allowed.")
            else:
                debug_logger.info("@subscribe_event{%s} usage on %s",
                                  self._event_subscription.__name__, owner.__qualname__)

        def __get__(self, instance, owner):
            return self.fun.__get__(instance, owner)

        def __call__(self, *args, **kwargs):
            return self.fun(*args, **kwargs)

    return EventSubscriber(event_type, fun)


@dataclass
class OnLevelChangeEvent(Event):
    old_level_id: int
    new_level_id: int

    def __str__(self):
        return f"{type(self).__name__}({self.old_level_id} -> {self.new_level_id})"


@dataclass
class OnAreaChangeEvent(Event):
    old_p_area_data: int
    new_p_area_data: int

    def __str__(self):
        return f"{type(self).__name__}(0x{self.old_p_area_data:x} -> 0x{self.new_p_area_data:x})"


@dataclass
class OnReceiveSlotDataEvent(Event):
    slot_data: dict[str, Any]
    generator_version: tuple[int, int, int] = field(init=False)
    """The version of the Lego Star Wars: TCS apworld that generated the multiworld"""

    def __post_init__(self):
        # Setting the version is structured this way to satisfy type checking.
        major, minor, patch = self.slot_data["apworld_version"]
        assert isinstance(major, int)
        assert isinstance(minor, int)
        assert isinstance(patch, int)
        self.generator_version = (major, minor, patch)
