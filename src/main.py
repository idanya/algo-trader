import json
import pathlib

from logger import setup_logger
from pipeline.builders.backtest import BacktestPipelines
from pipeline.builders.loaders import LoadersPipelines
from pipeline.runner import PipelineRunner
from pipeline.pipeline import Pipeline
from serialization.store import DeserializationService

BIN_COUNT = 10

'''
Main entry point, you can use the LoadersPipelines or the BacktestPipelines in order to run an example pipeline. 
This should eventually be the CLI entrypoint. For now, it's for running examples.
'''
EXAMPLE_TEMPLATES_DIR = pathlib.Path(__file__).parent.joinpath('examples/pipeline-templates').resolve()
ASSETS_DIR = pathlib.Path(__file__).parent.joinpath('assets').resolve()


def save_pipeline_spec(filename: str, pipeline: Pipeline):
    if not pathlib.Path.exists(EXAMPLE_TEMPLATES_DIR):
        pathlib.Path.mkdir(EXAMPLE_TEMPLATES_DIR)

    with open(pathlib.Path(EXAMPLE_TEMPLATES_DIR).joinpath(filename), 'w') as output_file:
        output_file.write(json.dumps(pipeline.serialize(), indent=2, default=str))


def load_pipeline_spec(filename: str) -> Pipeline:
    with open(pathlib.Path(EXAMPLE_TEMPLATES_DIR).joinpath(filename), 'r') as input_file:
        return DeserializationService.deserialize(json.loads(input_file.read()))


def generate_example_templates():
    save_pipeline_spec('backtest_mongo_source_rsi_strategy.json', BacktestPipelines.build_mongodb_backtester())
    save_pipeline_spec('backtest_history_buckets_backtester.json',
                       BacktestPipelines.build_mongodb_history_buckets_backtester(
                           f'{ASSETS_DIR}/bins.json'))

    save_pipeline_spec('backtest_technicals_with_buckets_calculator.json',
                       LoadersPipelines.build_technicals_with_buckets_calculator(
                           f'{ASSETS_DIR}/bins.json', BIN_COUNT,
                           f'{ASSETS_DIR}/correlation.json'))

    save_pipeline_spec('loader_simple_technicals_calculator.json', LoadersPipelines.build_technicals_calculator())
    save_pipeline_spec('loader_simple_returns_calculator.json', LoadersPipelines.build_returns_calculator())
    save_pipeline_spec('loader_technicals_with_buckets_matcher.json',
                       LoadersPipelines.build_technicals_with_buckets_matcher(f'{ASSETS_DIR}/bins.json',
                                                                              f'{ASSETS_DIR}/correlation.json'))

    save_pipeline_spec('backtest_history_similarity_backtester.json',
                       BacktestPipelines.build_mongodb_history_similarity_backtester(
                           f'{ASSETS_DIR}/bins.json'))

    # depends on a running IB gateway
    # save_pipeline_spec('loader_simple_daily_loader.json', LoadersPipelines.build_daily_ib_loader())


if __name__ == '__main__':
    setup_logger()

    # generate_example_templates()

    # LOAD SAVED JSON PIPELINE AND RUN IT
    pipeline = load_pipeline_spec('backtest_history_similarity_backtester.json')
    PipelineRunner(pipeline).run()