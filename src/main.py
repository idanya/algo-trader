from log import setup_logger
from pipeline.builders.backtest import BacktestPipelines
from pipeline.builders.loaders import LoadersPipelines

if __name__ == '__main__':
    setup_logger()
    # LoadersPipelines.build_daily_loader().run()
    BacktestPipelines.build_mongodb_backtester().run()

