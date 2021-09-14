from typing import Dict, Optional


class SharedContext:
    def __init__(self) -> None:
        self._kv_store: Dict[str, object] = {}

    def put_kv_data(self, key: str, value: object):
        self._kv_store[key] = value

    def get_kv_data(self, key: str) -> Optional[object]:
        if key in self._kv_store:
            return self._kv_store[key]
