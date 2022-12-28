import json
from typing import Optional, List, Dict

from scipy import spatial

from algotrader.entities.candle import Candle
from algotrader.entities.event import Event
from algotrader.entities.generic_candle_attachment import GenericCandleAttachment
from algotrader.pipeline.processor import Processor
from algotrader.pipeline.processors.candle_cache import CandleCache
from algotrader.pipeline.processors.technicals import IndicatorValue
from algotrader.pipeline.shared_context import SharedContext

CORRELATIONS_ATTACHMENT_KEY = 'correlations'
CORRELATION_ELEMENTS_COUNT = 4


class AssetCorrelation(GenericCandleAttachment[IndicatorValue]):
    pass


AssetCorrelation()


class CorrelationConfig:
    def __init__(self, groups: List[List[str]]) -> None:
        self.groups: List[List[str]] = groups


class AssetCorrelationProcessor(Processor):
    """
    Calculates correlations between groups of symbols
    """
    def __init__(self, config_path: str, next_processor: Optional[Processor]) -> None:
        """
        @param config_path: path to the correlation's config file
        @param next_processor: the next processor in chain
        """
        with open(config_path, 'r') as config_content:
            c: Dict = json.loads(config_content.read())
            self.config = CorrelationConfig(c.get('groups', []))

        super().__init__(next_processor)

    def process(self, context: SharedContext, candle: Candle):
        super().process(context, candle)

    def event(self, context: SharedContext, event: Event):
        if event == event.TimeSpanChange:
            self._calculate_correlations(context)

        super().event(context, event)

    def _calculate_correlations(self, context: SharedContext):
        cache_reader = CandleCache.context_reader(context)
        symbols = cache_reader.get_symbols_list()

        for symbol in symbols:
            self._calculate_symbol_correlations(context, symbol)

    def _calculate_symbol_correlations(self, context: SharedContext, symbol: str):
        cache_reader = CandleCache.context_reader(context)
        asset_correlation = AssetCorrelation()

        group_symbols = self._get_symbol_group(symbol)

        if group_symbols:
            current_symbol_candles = cache_reader.get_symbol_candles(symbol) or []
            current_symbol_values = self._get_correlation_measurable_values(current_symbol_candles)

            for paired_symbol in group_symbols:
                if paired_symbol == symbol:
                    continue

                symbol_candles = cache_reader.get_symbol_candles(paired_symbol) or []
                symbol_values = self._get_correlation_measurable_values(symbol_candles)

                if len(symbol_values) != len(current_symbol_values) or len(current_symbol_values) <= CORRELATION_ELEMENTS_COUNT:
                    continue

                correlation = spatial.distance.correlation(current_symbol_values[-CORRELATION_ELEMENTS_COUNT:],
                                                           symbol_values[-CORRELATION_ELEMENTS_COUNT:])
                asset_correlation.set(paired_symbol, correlation)

            latest_candle = current_symbol_candles[-1]
            latest_candle.attachments.add_attachement(CORRELATIONS_ATTACHMENT_KEY, asset_correlation)

            self.reprocess(context, latest_candle)

    def _get_symbol_group(self, symbol: str) -> Optional[List[str]]:
        for group in self.config.groups:
            if symbol in group:
                return group

    @staticmethod
    def _get_correlation_measurable_values(candles: List[Candle]) -> List[float]:
        return [c.close for c in candles]
