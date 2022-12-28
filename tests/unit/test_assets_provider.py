from unittest import TestCase

from algotrader.assets.assets_provider import AssetsProvider


class TestAssestProvider(TestCase):
    def test_get_sp500(self):
        symbols = AssetsProvider.get_sp500_symbols()
        self.assertEqual(495, len(symbols))
        self.assertTrue('AAPL' in symbols)
        self.assertTrue('AMD' in symbols)
        self.assertTrue('WYNN' in symbols)
