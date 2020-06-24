import coloredlogs

LOG_FORMAT = '[%(asctime)s/%(name)s] %(levelname)s %(message)s'
TIME_FORMAT = '%H:%M:%S'


def init_log():
    coloredlogs.install(fmt=LOG_FORMAT, datefmt=TIME_FORMAT)

