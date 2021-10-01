from log import setup_logger
from pipeline.builders.loader import LoadersPipelines

if __name__ == '__main__':
    setup_logger()
    LoadersPipelines.build_daily_loader().run()

