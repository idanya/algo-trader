from datetime import datetime, timedelta
from unittest import TestCase

from algotrader.entities.timespan import TimeSpan
from algotrader.market.async_query_result import AsyncQueryResult
from algotrader.providers.ib.query_subscription import QuerySubscription
from unit import generate_candle


class TestAsyncQueryResult(TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.from_ts = datetime.now() - timedelta(days=10)
        self.to_ts = datetime.now()
        self.result = AsyncQueryResult(self.from_ts, self.to_ts)

    def test_candles_out_of_range(self):
        subscription = QuerySubscription(1, 'X', TimeSpan.Day)
        self.result.attach_query_subscription(subscription)
        subscription.push_candles([generate_candle(TimeSpan.Day, self.from_ts),
                                   generate_candle(TimeSpan.Day, self.to_ts),
                                   generate_candle(TimeSpan.Day, self.from_ts - timedelta(days=1))])

        subscription.done()

        self.assertEqual(2, len(self.result.result()))

    def test_multiple_subscriptions(self):
        subscription1 = QuerySubscription(1, 'X', TimeSpan.Day)
        self.result.attach_query_subscription(subscription1)

        subscription2 = QuerySubscription(2, 'X', TimeSpan.Day)
        self.result.attach_query_subscription(subscription2)

        subscription1.push_candles([generate_candle(TimeSpan.Day, self.from_ts),
                                    generate_candle(TimeSpan.Day, self.to_ts),
                                    generate_candle(TimeSpan.Day, self.from_ts - timedelta(days=1))])

        subscription2.push_candles([generate_candle(TimeSpan.Day, self.from_ts),
                                    generate_candle(TimeSpan.Day, self.to_ts),
                                    generate_candle(TimeSpan.Day, self.from_ts - timedelta(days=1))])

        subscription1.done()
        subscription2.done()

        self.assertEqual(4, len(self.result.result()))

    def test_multiple_subscriptions_with_error(self):
        subscription1 = QuerySubscription(1, 'X', TimeSpan.Day)
        self.result.attach_query_subscription(subscription1)

        subscription2 = QuerySubscription(2, 'X', TimeSpan.Day)
        self.result.attach_query_subscription(subscription2)

        subscription1.push_candles([generate_candle(TimeSpan.Day, self.from_ts),
                                    generate_candle(TimeSpan.Day, self.to_ts),
                                    generate_candle(TimeSpan.Day, self.from_ts - timedelta(days=1))])

        subscription2.push_candles([generate_candle(TimeSpan.Day, self.from_ts),
                                    generate_candle(TimeSpan.Day, self.to_ts),
                                    generate_candle(TimeSpan.Day, self.from_ts - timedelta(days=1))])

        subscription1.done()
        subscription2.done(True)

        with self.assertRaises(Exception):
            self.result.result()
