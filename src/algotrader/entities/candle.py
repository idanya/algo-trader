from __future__ import annotations

from datetime import datetime
from typing import Optional, Annotated, Literal

from pydantic import Field

from algotrader.entities.base_dto import BaseEntity
from algotrader.entities.candle_attachments import CandleAttachment
from algotrader.entities.timespan import TimeSpan


def timestamp_to_str(d: datetime) -> str:
    return d.strftime("%Y%m%d %H:%M:%S.%f")


def str_to_timestamp(d: str) -> datetime:
    return datetime.strptime(d, "%Y%m%d %H:%M:%S.%f")


class Candle(BaseEntity):
    type: Literal["Candle"] = "Candle"
    symbol: str
    timestamp: datetime
    time_span: TimeSpan

    open: float
    close: float
    high: float
    low: float
    volume: float

    attachments: Optional[dict[str, Annotated[CandleAttachment, Field(discriminator="type")]]] = None

    def add_attachment(self, key: str, entity: BaseEntity):
        if not self.attachments:
            self.attachments = {}

        self.attachments[key] = entity

    def get_attachment(self, key: str) -> Optional[CandleAttachment]:
        if self.attachments:
            return self.attachments.get(key)
