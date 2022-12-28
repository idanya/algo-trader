from typing import Dict, Optional, TypeVar, Generic

T = TypeVar('T')


class SharedContext(Generic[T]):
    def __init__(self) -> None:
        self._kv_store: Dict[str, object] = {}

    def put_kv_data(self, key: str, value: T):
        self._kv_store[key] = value

    def get_kv_data(self, key: str, default: object = None) -> Optional[T]:
        if key in self._kv_store:
            return self._kv_store[key]

        return default
