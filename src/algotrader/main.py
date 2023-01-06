import json
import pathlib

from algotrader.cli.main import initiate_cli
# from logger import setup_default_logger
from algotrader.pipeline.builders.backtest import BacktestPipelines
from algotrader.pipeline.builders.loaders import LoadersPipelines
from algotrader.pipeline.pipeline import Pipeline

BIN_COUNT = 10

EXAMPLE_TEMPLATES_DIR = pathlib.Path(__file__).parent.joinpath('examples/pipeline-templates').resolve()
'''
Main entry point, you can use the LoadersPipelines or the BacktestPipelines in order to run an example pipeline.
This should eventually be the CLI entrypoint. For now, it's for running examples.
'''


def save_pipeline_spec(filename: str, pipeline: Pipeline):
    if not pathlib.Path.exists(EXAMPLE_TEMPLATES_DIR):
        pathlib.Path.mkdir(EXAMPLE_TEMPLATES_DIR)

    with open(pathlib.Path(EXAMPLE_TEMPLATES_DIR).joinpath(filename), 'w') as output_file:
        output_file.write(json.dumps(pipeline.serialize(), indent=2, default=str))


def generate_example_templates():
    save_pipeline_spec('build_realtime_binance.json', LoadersPipelines.build_realtime_binance())
    save_pipeline_spec('build_daily_binance_loader.json', LoadersPipelines.build_daily_binance_loader())
    save_pipeline_spec('build_daily_yahoo_loader.json', LoadersPipelines.build_daily_yahoo_loader())
    save_pipeline_spec('backtest_mongo_source_rsi_strategy.json', BacktestPipelines.build_mongodb_backtester())
    save_pipeline_spec('backtest_history_buckets_backtester.json',
                       BacktestPipelines.build_mongodb_history_buckets_backtester(
                           f'{EXAMPLE_TEMPLATES_DIR}/bins.json'))

    save_pipeline_spec('backtest_technicals_with_buckets_calculator.json',
                       LoadersPipelines.build_technicals_with_buckets_calculator(
                           f'{EXAMPLE_TEMPLATES_DIR}/bins.json', BIN_COUNT,
                           f'{EXAMPLE_TEMPLATES_DIR}/correlation.json'))

    save_pipeline_spec('loader_simple_technicals_calculator.json', LoadersPipelines.build_technicals_calculator())
    save_pipeline_spec('loader_simple_returns_calculator.json', LoadersPipelines.build_returns_calculator())
    save_pipeline_spec('loader_technicals_with_buckets_matcher.json',
                       LoadersPipelines.build_technicals_with_buckets_matcher(f'{EXAMPLE_TEMPLATES_DIR}/bins.json',
                                                                              f'{EXAMPLE_TEMPLATES_DIR}/correlation.json'))

    save_pipeline_spec('backtest_history_similarity_backtester.json',
                       BacktestPipelines.build_mongodb_history_similarity_backtester(
                           f'{EXAMPLE_TEMPLATES_DIR}/bins.json'))

    # depends on a running IB gateway
    # save_pipeline_spec('loader_simple_daily_loader.json', LoadersPipelines.build_daily_ib_loader())


if __name__ == '__main__':
    # setup_default_logger()

    # generate_example_templates()

    initiate_cli()
