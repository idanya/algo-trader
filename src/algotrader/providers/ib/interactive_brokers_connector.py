import logging
import math
import threading
from datetime import datetime
from typing import Optional, Dict

from ibapi.client import EClient
from ibapi.common import TickerId, BarData
from ibapi.contract import Contract
from ibapi.order import Order
from ibapi.wrapper import EWrapper, iswrapper

from algotrader.entities.candle import Candle
from algotrader.entities.timespan import TimeSpan
from algotrader.market.async_market_provider import AsyncMarketProvider, AsyncQueryResult
from algotrader.providers.ib.ib_interval import timespan_to_api_str, datetime_to_api_string
from algotrader.providers.ib.query_subscription import QuerySubscription


class InteractiveBrokersConnector(AsyncMarketProvider, EWrapper, EClient):

    def __init__(self, host: str = '127.0.0.1', port: int = 7497, client_id: int = 100) -> None:
        EWrapper.__init__(self)
        EClient.__init__(self, wrapper=self)
        self.done = False
        self.query_subscriptions_by_id: Dict[int, QuerySubscription] = {}

        self.nextValidOrderId = 1
        self.connect(host, port, clientId=client_id)

        print(f"serverVersion:{self.serverVersion()} connectionTime:{self.twsConnectionTime()}")
        self.reqIds(-1)
        self.tick_last_query_id = 14000

        thread = threading.Thread(target=self.run)
        thread.daemon = True
        thread.start()

    def next_order_id(self):
        oid = self.nextValidOrderId
        self.nextValidOrderId += 1
        return oid

    def request_symbol_history(self, symbol: str, candle_timespan: TimeSpan, from_time: datetime,
                               to_time: datetime) -> AsyncQueryResult:
        logging.info(f'request_symbol_history :: {symbol} ...')
        async_query_result = AsyncQueryResult(from_time, to_time)
        self.tick_last_query_id += 1
        subscription = self._add_subscription(self.tick_last_query_id, symbol, candle_timespan)

        async_query_result.attach_query_subscription(subscription)

        self.reqHistoricalData(self.tick_last_query_id,
                               self._get_contract(symbol),
                               datetime_to_api_string(to_time),
                               self._calculate_query_duration(candle_timespan, from_time, to_time),
                               timespan_to_api_str(candle_timespan), 'TRADES', 1, 1, False, [])

        return async_query_result

    def _calculate_query_duration(self, candle_timespan: TimeSpan, from_time: datetime, to_time: datetime) -> str:
        if candle_timespan == TimeSpan.Day:
            days = (to_time - from_time).days + 1
            if days > 365:
                return f'{math.ceil(days / 365)} Y'
            else:
                return f'{math.ceil(days / 7)} W'

    def _add_subscription(self, query_id: int, symbol: str, candle_timespan: TimeSpan) -> QuerySubscription:
        subscription = QuerySubscription(query_id, symbol, candle_timespan)
        self.query_subscriptions_by_id[query_id] = subscription
        return subscription

    def _resolve_subscription(self, query_id: int) -> Optional[QuerySubscription]:
        if query_id in self.query_subscriptions_by_id:
            return self.query_subscriptions_by_id[query_id]

    @iswrapper
    def historicalData(self, reqId: int, bar: BarData):
        super().historicalData(reqId, bar)

        subscription = self._resolve_subscription(reqId)

        try:
            bar_time = datetime.strptime(bar.date, "%Y%m%d")
        except Exception:
            bar_time = datetime.strptime(bar.date, "%Y%m%d %H:%M:%S")

        c = Candle(subscription.symbol,
                   subscription.candle_timespan,
                   bar_time,
                   bar.open, bar.close, bar.high, bar.low,
                   bar.volume * bar.average)

        subscription.push_candles([c])

    @iswrapper
    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)
        self.nextValidOrderId = orderId

    @iswrapper
    def error(self, reqId: TickerId, errorCode: int, errorString: str):
        super().error(reqId, errorCode, errorString)
        sub = self._resolve_subscription(reqId)
        if sub:
            sub.done(True)

    @iswrapper
    def historicalDataEnd(self, reqId: int, start: str, end: str):
        super().historicalDataEnd(reqId, start, end)
        self._resolve_subscription(reqId).done()

    def kill(self):
        self.done = True

    def _get_contract(self, symbol: str, exchange: str = 'SMART') -> Contract:
        contract = Contract()
        contract.symbol = symbol
        contract.secType = "STK"
        contract.exchange = exchange
        contract.currency = "USD"

        return contract

    def _generate_moc_order(self, action: str, quantity: float):
        order = Order()
        order.action = action
        order.orderType = "MOC"
        order.totalQuantity = quantity
        return order

    def _generate_moo_order(self, action: str, quantity: float):
        order = Order()
        order.action = action
        order.orderType = "MKT"
        order.totalQuantity = quantity
        order.tif = "OPG"
        return order

    def _generate_trailing_order(self, action: str, quantity: float, trailing_percent: float):
        order = Order()
        order.action = action
        order.orderType = "TRAIL"
        order.totalQuantity = quantity
        order.trailingPercent = trailing_percent
        return order

    def _generate_stop_order(self, action: str, quantity: float, price: float):
        order = Order()
        order.action = action
        order.orderType = "STP"
        order.auxPrice = price
        order.totalQuantity = quantity

        return order

    def _generate_mkt_order(self, action: str, quantity: float):
        order = Order()
        order.action = action
        order.orderType = "MKT"
        order.totalQuantity = quantity
        return order

    def _generate_lmt_order(self, action: str, quantity: float, price: float):
        order = Order()
        order.action = action
        order.orderType = "LMT"
        order.totalQuantity = quantity
        order.lmtPrice = price
        return order
