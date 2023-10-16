from datetime import datetime
from unittest import TestCase

from algotrader.entities.attachments.nothing import NothingClass
from algotrader.entities.bucket import Bucket
from algotrader.entities.bucketscontainer import BucketsContainer
from algotrader.entities.candle import Candle
from algotrader.entities.timespan import TimeSpan
from unit import generate_candle_with_price


class TestSerializations(TestCase):
    def test_candle(self):
        candle = generate_candle_with_price(TimeSpan.Day, datetime.now(), 888)
        data = candle.model_dump_json()

        new_candle = Candle.model_validate_json(data)

        self.assertEqual(candle.symbol, new_candle.symbol)
        self.assertEqual(candle.timestamp, new_candle.timestamp)
        self.assertEqual(candle.time_span, new_candle.time_span)
        self.assertEqual(candle.close, new_candle.close)
        self.assertEqual(candle.high, new_candle.high)
        self.assertEqual(candle.low, new_candle.low)
        self.assertEqual(candle.volume, new_candle.volume)
        self.assertEqual(candle.open, new_candle.open)

    def test_candle_attachments(self):
        candle = generate_candle_with_price(TimeSpan.Day, datetime.now(), 888)
        candle.add_attachment("key1", NothingClass())

        data = candle.model_dump_json()
        new_candle = Candle.model_validate_json(data)

        self.assertEqual(candle.symbol, new_candle.symbol)
        original_attachment = candle.get_attachment("key1")
        new_attachment = new_candle.get_attachment("key1")
        self.assertEqual(original_attachment.__class__, new_attachment.__class__)

    def test_bins(self):
        bins = BucketsContainer()
        bins.add("x", [Bucket(ident=1, start=1, end=2)])
        bins.add("list", [[Bucket(ident=0, start=1, end=2)], [Bucket(ident=1, start=3, end=4)]])

        serialized_data = bins.model_dump_json()
        new_bins = BucketsContainer.model_validate_json(serialized_data)

        x = new_bins.get("x")
        self.assertIsNotNone(x)
        self.assertEqual(1, x[0].start)
        self.assertEqual(2, x[0].end)

        lst = new_bins.get("list")
        self.assertIsNotNone(lst)
        self.assertTrue(isinstance(lst[0], list))
        self.assertEqual(1, lst[0][0].start)
        self.assertEqual(2, lst[0][0].end)
        self.assertEqual(3, lst[1][0].start)
        self.assertEqual(4, lst[1][0].end)
