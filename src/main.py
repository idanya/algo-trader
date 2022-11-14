import json

from log import setup_logger
from pipeline.builders.backtest import BacktestPipelines
from pipeline.runner import PipelineSpecificationRunner
from pipeline.specification import PipelineSpecification
from serialization.store import DeserializationService

BIN_COUNT = 10

'''
Main entry point, you can use the LoadersPipelines or the BacktestPipelines in order to run an example pipeline. 
This should eventually be the CLI entrypoint. For now, it's for running examples.
'''
if __name__ == '__main__':
    setup_logger()

    ## RUN PIPELINE FROM CODE USING SPECIFICATION RUNNER

    # specs = LoadersPipelines.build_daily_loader()
    # spec_obj = specs.serialize()
    # PipelineSpecificationRunner(specs).run()

    # specs = LoadersPipelines.build_technicals_with_buckets_calculator('bins.json', BIN_COUNT, 'correlation.json')
    # spec_obj = specs.serialize()
    # PipelineSpecificationRunner(specs).run()

    ## RUN PIPELINE FROM CODE

    # BacktestPipelines.build_mongodb_backtester().run()
    # LoadersPipelines.build_technicals_calculator().run()
    # LoadersPipelines.build_returns_calculator().run()
    # LoadersPipelines.build_technicals_with_buckets_matcher('bins.json', 'correlation.json').run()
    # BacktestPipelines.build_mongodb_history_buckets_backtester('bins.json').run()

    # SERIALIZE AND SAVE CONSTRUCTED PIPELINE TO JSON FILE
    # specs = BacktestPipelines.build_mongodb_history_similarity_backtester('bins.json')
    # spec_obj = specs.serialize()
    #
    # with open('pipeline.json', 'w') as output_file:
    #     output_file.write(json.dumps(spec_obj, indent=2, default=str))

    # RUN SAVED JSON PIPELINE AND RUN IT
    # with open('pipeline.json', 'r') as input_file:
    #     specs: PipelineSpecification = DeserializationService.deserialize(json.loads(input_file.read()))
    # PipelineSpecificationRunner(specs).run()
