from __future__ import annotations

from typing import Optional, List, Dict, Union, Tuple

from algotrader.calc.technicals import TechnicalCalculator
from algotrader.entities.candle import Candle
from algotrader.entities.generic_candle_attachment import GenericCandleAttachment
from algotrader.pipeline.configs.technical_processor_config import TechnicalsProcessorConfig
from algotrader.pipeline.processor import Processor
from algotrader.pipeline.processors.candle_cache import CandleCache
from algotrader.pipeline.shared_context import SharedContext

INDICATORS_ATTACHMENT_KEY = 'indicators'
TechnicalsData = Dict[str, Dict[str, List[float]]]

IndicatorValue = Union[List[float], float]


class Indicators(GenericCandleAttachment[IndicatorValue]):
    pass


Indicators()

MAX_CANDLES_FOR_CALC = 50


class TechnicalsProcessor(Processor):
    """
    Technical indicators processor. Using Tulip indicators to calculate and attach technicals to the processed candles.
    Make use of the SharedContext to keep track of earlier candles.
    """

    def __init__(self, config: TechnicalsProcessorConfig, next_processor: Optional[Processor]) -> None:
        super().__init__(next_processor)
        self.config = config

    def process(self, context: SharedContext, candle: Candle):
        cache_reader = CandleCache.context_reader(context)
        symbol_candles = cache_reader.get_symbol_candles(candle.symbol) or []
        calculator = TechnicalCalculator(symbol_candles[-MAX_CANDLES_FOR_CALC:] + [candle])

        candle_indicators = Indicators()
        self._calculate(calculator, candle_indicators)
        candle.attachments.add_attachement(INDICATORS_ATTACHMENT_KEY, candle_indicators)

        super().process(context, candle)

    def _calculate(self, calculator: TechnicalCalculator, candle_indicators: Indicators):

        for technicalConfig in self.config.technicals:
            results = calculator.execute(technicalConfig.type, technicalConfig.params)
            candle_indicators.set(technicalConfig.name, TechnicalsProcessor._get_last_value(results))

    @staticmethod
    def _get_last_value(values: Union[Tuple[List[float]], List[float]]) -> Optional[IndicatorValue]:
        if isinstance(values, tuple):
            return [v[-1] for v in values]
        elif isinstance(values, list) and values:
            return values[-1]

    def serialize(self) -> Dict:
        obj = super().serialize()
        obj.update({
            'config': self.config.serialize()
        })
        return obj

    @classmethod
    def deserialize(cls, data: Dict) -> Optional[Processor]:
        config = TechnicalsProcessorConfig.deserialize(data['config'])
        return cls(config, cls._deserialize_next_processor(data))
