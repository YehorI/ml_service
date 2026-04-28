import logging
from typing import Iterable


class EndpointLogFilter(logging.Filter):
    def __init__(self, excluded_endpoints: Iterable[str] = ()):
        self._excluded_endpoints = frozenset(excluded_endpoints)

        super().__init__()

    def filter(self, record: logging.LogRecord) -> bool:
        return bool(
            record.args and
            len(record.args) >= 3 and
            record.args[2] not in self._excluded_endpoints
        )
