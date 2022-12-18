from os import path
from typing import List

SP500_SYMBOLS = 'sp500.symbols'
CRYPTO_SYMBOLS = 'crypto.symbols'


class AssetsProvider:

    @staticmethod
    def get_sp500_symbols() -> List[str]:
        return AssetsProvider._get_file_lines(SP500_SYMBOLS)

    @staticmethod
    def get_crypto_symbols() -> List[str]:
        return AssetsProvider._get_file_lines(CRYPTO_SYMBOLS)

    @staticmethod
    def _get_file_lines(filename: str) -> List[str]:
        symbols_file = path.join(path.dirname(__file__), filename)
        with open(symbols_file, 'r') as file:
            return [line.rstrip('\n') for line in file]
