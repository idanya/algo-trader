import yfinance as yf

class YahooFinanceHistoryProvider:
    def __init__(self):
        pass

    def get_symbol_history(self, symbol: str):
        ticker = yf.Ticker(symbol)



