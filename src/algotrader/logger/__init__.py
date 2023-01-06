import logging
import os
import pathlib
import time


def setup_default_logger():
    log_dir = pathlib.Path(__file__).parent.parent.joinpath('logs').resolve()
    level = logging.DEBUG if os.environ.get('DEBUG') else logging.INFO

    if not pathlib.Path.exists(log_dir):
        pathlib.Path.mkdir(log_dir)

    recfmt = '(%(threadName)s) %(asctime)s.%(msecs)03d %(levelname)s %(filename)s:%(lineno)d %(message)s'

    timefmt = '%y%m%d_%H:%M:%S'

    logging.basicConfig(
        filename=f'{log_dir}/{time.strftime("algo-trader.%y%m%d_%H%M%S.log")}',
        filemode="w",
        level=level,
        format=recfmt, datefmt=timefmt)
    logger = logging.getLogger()
    console = logging.StreamHandler()
    console.setLevel(level)
    logger.addHandler(console)
