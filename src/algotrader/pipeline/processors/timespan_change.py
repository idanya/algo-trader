from datetime import datetime
from typing import Optional

from algotrader.entities.candle import Candle
from algotrader.entities.event import Event
from algotrader.entities.timespan import TimeSpan
from algotrader.pipeline.processor import Processor
from algotrader.pipeline.shared_context import SharedContext


class TimeSpanChangeProcessor(Processor):
    """
    Event emitter.
    Keeps track of processed candles timestamps and emits a Event.TimeSpanChange upon a TimeSpan change.
    """
    def __init__(self, timespan: TimeSpan, next_processor: Optional[Processor]) -> None:
        """
        @param timespan: What TimeSpan we are tracking
        """
        super().__init__(next_processor)
        self.timespan = timespan
        self.latest_candle: Optional[Candle] = None

    def process(self, context: SharedContext, candle: Candle):
        if self.latest_candle and candle.time_span == self.timespan and \
                self._is_diff(candle.timestamp, self.latest_candle.timestamp):

            self.next_processor.event(context, Event.TimeSpanChange)

        self.latest_candle = candle

        super().process(context, candle)

    def _is_diff(self, one: datetime, other: datetime) -> bool:
        if self.timespan == TimeSpan.Day:
            return one.date() != other.date()
        else:
            return True
