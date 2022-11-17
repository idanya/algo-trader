import logging
import pathlib
import time

def setup_logger():
    log_dir = pathlib.Path(__file__).parent.parent.joinpath('logs')

    if not pathlib.Path.exists(log_dir):
        pathlib.Path.mkdir(log_dir)

    recfmt = '(%(threadName)s) %(asctime)s.%(msecs)03d %(levelname)s %(filename)s:%(lineno)d %(message)s'

    timefmt = '%y%m%d_%H:%M:%S'

    logging.basicConfig(
        filename=f'{log_dir}/{time.strftime("algo-trader.%y%m%d_%H%M%S.log")}',
        filemode="w",
        level=logging.INFO,
        format=recfmt, datefmt=timefmt)
    logger = logging.getLogger()
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logger.addHandler(console)

    logging.getLogger('ibapi.wrapper').setLevel(logging.WARNING)
