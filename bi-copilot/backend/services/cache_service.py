from collections import OrderedDict
from collections.abc import Callable
from copy import deepcopy
from typing import Generic, TypeVar

T = TypeVar("T")


class LRUCache(Generic[T]):
    def __init__(self, max_size: int = 128):
        self.max_size = max_size
        self._items: OrderedDict[str, T] = OrderedDict()

    def get_or_set(self, key: str, factory: Callable[[], T]) -> T:
        if key in self._items:
            value = self._items.pop(key)
            self._items[key] = value
            return deepcopy(value)

        value = factory()
        self._items[key] = deepcopy(value)
        if len(self._items) > self.max_size:
            self._items.popitem(last=False)
        return deepcopy(value)

    def clear(self) -> None:
        self._items.clear()
