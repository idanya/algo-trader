from algotrader.calc.calculations import TechnicalCalculation
from algotrader.pipeline.configs.indicator_config import IndicatorConfig
from algotrader.pipeline.configs.technical_processor_config import TechnicalsProcessorConfig

TECHNICAL_PROCESSOR_CONFIG = TechnicalsProcessorConfig([
    IndicatorConfig('sma5', TechnicalCalculation.SMA, [5]),
    IndicatorConfig('sma20', TechnicalCalculation.SMA, [20]),
    IndicatorConfig('cci7', TechnicalCalculation.CCI, [7]),
    IndicatorConfig('cci14', TechnicalCalculation.CCI, [14]),
    IndicatorConfig('macd', TechnicalCalculation.MACD, [2, 5, 9]),
    IndicatorConfig('rsi7', TechnicalCalculation.CCI, [7]),
    IndicatorConfig('rsi14', TechnicalCalculation.CCI, [14]),
    IndicatorConfig('adxr5', TechnicalCalculation.ADXR, [5]),
    IndicatorConfig('stddev5', TechnicalCalculation.STDDEV, [5]),
    IndicatorConfig('ema5', TechnicalCalculation.EMA, [5]),
    IndicatorConfig('ema20', TechnicalCalculation.EMA, [20]),
    IndicatorConfig('mom5', TechnicalCalculation.MOM, [5]),
    IndicatorConfig('natr5', TechnicalCalculation.NATR, [5]),
    IndicatorConfig('meandev5', TechnicalCalculation.MEANDEV, [5]),
    IndicatorConfig('obv', TechnicalCalculation.OBV, []),
    IndicatorConfig('var5', TechnicalCalculation.VAR, [5]),
    IndicatorConfig('vosc', TechnicalCalculation.VOSC, [2, 5]),
]
)
