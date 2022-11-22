import json
import os
from os import path

from logger import setup_logger
from pipeline.builders.backtest import BacktestPipelines
from pipeline.builders.loaders import LoadersPipelines
from pipeline.runner import PipelineSpecificationRunner
from pipeline.specification import PipelineSpecification
from serialization.store import DeserializationService

BIN_COUNT = 10

'''
Main entry point, you can use the LoadersPipelines or the BacktestPipelines in order to run an example pipeline.
This should eventually be the CLI entrypoint. For now, it's for running examples.
'''
EXAMPLE_TEMPLATES_DIR = 'examples/pipeline-templates'


def save_pipeline_spec(filename: str, spec: PipelineSpecification):
    if not path.exists(EXAMPLE_TEMPLATES_DIR):
        os.mkdir(EXAMPLE_TEMPLATES_DIR)

    with open(path.join(EXAMPLE_TEMPLATES_DIR, filename), 'w') as output_file:
        output_file.write(json.dumps(spec.serialize(), indent=2, default=str))


def load_pipeline_spec(filename: str) -> PipelineSpecification:
    with open(path.join(EXAMPLE_TEMPLATES_DIR, filename), 'r') as input_file:
        return DeserializationService.deserialize(json.loads(input_file.read()))


def generate_example_templates():
    save_pipeline_spec('backtest_mongo_source_rsi_strategy.json', BacktestPipelines.build_mongodb_backtester())
    save_pipeline_spec('backtest_history_buckets_backtester.json',
                       BacktestPipelines.build_mongodb_history_buckets_backtester(
                           'examples/pipeline-templates/bins.json'))

    save_pipeline_spec('backtest_technicals_with_buckets_calculator.json',
                       LoadersPipelines.build_technicals_with_buckets_calculator(
                           'examples/pipeline-templates/bins.json', BIN_COUNT,
                           'examples/pipeline-templates/correlation.json'))

    save_pipeline_spec('loader_simple_technicals_calculator.json', LoadersPipelines.build_technicals_calculator())
    save_pipeline_spec('loader_simple_returns_calculator.json', LoadersPipelines.build_returns_calculator())
    save_pipeline_spec('loader_technicals_with_buckets_matcher.json',
                       LoadersPipelines.build_technicals_with_buckets_matcher('examples/pipeline-templates/bins.json',
                                                                              'examples/pipeline-templates/correlation.json'))

    save_pipeline_spec('backtest_history_similarity_backtester.json',
                       BacktestPipelines.build_mongodb_history_similarity_backtester(
                           'examples/pipeline-templates/bins.json'))

    # depends on a running IB gateway
    # save_pipeline_spec('loader_simple_daily_loader.json', LoadersPipelines.build_daily_ib_loader())


if __name__ == '__main__':
    setup_logger()

    # generate_example_templates()

    # LOAD SAVED JSON PIPELINE AND RUN IT
    spec = load_pipeline_spec('backtest_history_similarity_backtester.json')
    PipelineSpecificationRunner(spec).run()
