from log import setup_logger
from pipeline.builders.backtest import BacktestPipelines
from pipeline.builders.loaders import LoadersPipelines

if __name__ == '__main__':
    setup_logger()
    # LoadersPipelines.build_daily_loader().run()
    # BacktestPipelines.build_mongodb_backtester().run()
    # LoadersPipelines.build_technicals_calculator().run()
    # LoadersPipelines.build_returns_calculator().run()

    # LoadersPipelines.build_technicals_with_buckets_calculator('bins.json').run()
    # LoadersPipelines.build_technicals_with_buckets_matcher('bins.json').run()
    # BacktestPipelines.build_mongodb_history_buckets_backtester('bins.json').run()
    BacktestPipelines.build_mongodb_history_similarity_backtester('bins.json').run()

