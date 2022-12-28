import logging
from datetime import datetime
from typing import List, Optional, Dict, Callable

from binance.spot import Spot
from binance.websocket.spot.websocket_client import SpotWebsocketClient as WebsocketClient

from entities.candle import Candle
from entities.serializable import Deserializable, Serializable
from entities.timespan import TimeSpan

StreamedCandleCallback = Callable[[Candle], None]


class BinanceProvider(Serializable, Deserializable):
    logger = logging.getLogger('BinanceProvider')

    def __init__(self, api_key: Optional[str] = '', api_secret: Optional[str] = '', enable_websocket: bool = False):
        self.api_key = api_key
        self.api_secret = api_secret
        self.enable_websocket = enable_websocket
        self.client = Spot(api_key, api_secret)

        self.wsManager = WebsocketClient()
        if enable_websocket:
            self.logger.info('Starting websocket manager...')
            self.wsManager.start()

    def stop(self):
        if self.is_socket_alive():
            self.logger.info('Stopping websocket manager...')
            self.wsManager.stop()

    def is_socket_alive(self) -> bool:
        return self.wsManager.is_alive()

    def start_kline_socket(self, symbol: str, interval: TimeSpan, handler: StreamedCandleCallback):
        self.logger.info(f'Starting kline socket for {symbol}...')
        self.wsManager.kline(symbol=symbol, id=1,
                             interval=self._timespan_to_interval(interval),
                             callback=self._generate_kline_msg_handler(interval, handler))

    def _generate_kline_msg_handler(self, interval: TimeSpan, handler: StreamedCandleCallback) -> Callable:
        def _handle_kline_msg(msg: Dict):
            try:
                if msg['e'] == 'kline':
                    handler(self._deserialize_websocket_candle(msg['k'], interval))
            except Exception as e:
                self.logger.error(f'Error while handling kline message: {e}')

        return _handle_kline_msg

    def _deserialize_websocket_candle(self, data: Dict, interval: TimeSpan) -> Candle:
        timestamp = self._timestamp_to_datetime(data['T'])
        open = float(data['o'])
        high = float(data['h'])
        low = float(data['l'])
        close = float(data['c'])
        volume = float(data['v'])

        return Candle(data['s'], interval, timestamp, open, close, high, low, volume)

    def _deserialize_candle(self, symbol: str, interval: TimeSpan, data: Dict) -> Candle:
        timestamp = self._timestamp_to_datetime(data[0])
        open = float(data[1])
        high = float(data[2])
        low = float(data[3])
        close = float(data[4])
        volume = float(data[5])

        return Candle(symbol, interval, timestamp, open, close, high, low, volume)

    def get_symbol_history(self, symbol: str, interval: TimeSpan, start_time: datetime,
                           end_time: datetime = datetime.now()) -> List[Candle]:
        self.logger.info(f'Getting {symbol} history from {start_time} to {end_time}...')

        candles: List[Candle] = []
        lines = self.client.klines(symbol,
                                   self._timespan_to_interval(interval),
                                   startTime=int(start_time.timestamp() * 1000),
                                   endTime=int(end_time.timestamp() * 1000))

        for line in lines:
            candles.append(self._deserialize_candle(symbol, interval, line))

        return candles

    def serialize(self) -> Dict:
        return {
            'apiKey': self.api_key,
            'apiSecret': self.api_secret,
            'enableWebsocket': self.enable_websocket,
        }

    @classmethod
    def deserialize(cls, data: Dict):
        return cls(data.get('apiKey'), data.get('apiSecret'), data.get('enableWebsocket'))

    @staticmethod
    def _timestamp_to_datetime(timestamp: int) -> datetime:
        return datetime.fromtimestamp(timestamp / 1000)

    @staticmethod
    def _timespan_to_interval(timespan: TimeSpan) -> str:
        if timespan == TimeSpan.Second:
            return '1s'
        elif timespan == TimeSpan.Minute:
            return '1m'
        elif timespan == TimeSpan.Hour:
            return '1h'
        elif timespan == TimeSpan.Day:
            return '1d'
        else:
            raise ValueError('Unsupported timespan')
