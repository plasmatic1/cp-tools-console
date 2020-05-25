import os
import yaml
from pkg_resources import resource_string

DEFAULT_CONFIG_PATH = 'cptools.local_data', 'default_config.yml'
DEFAULT_EXECUTORS_PATH = 'cptools.local_data', 'default_executors.yml'

DATA_DIR = '.cptools'
CONFIG_PATH = f'{DATA_DIR}/config.yml'
EXECUTORS_PATH = f'{DATA_DIR}/executors.yml'
PREVIOUS_RESULTS_PATH = f'{DATA_DIR}/previous_results.yml'


def reset():
    os.mkdir(DATA_DIR)
    with open(CONFIG_PATH, 'w') as f:
        f.write(resource_string(*DEFAULT_CONFIG_PATH))
    with open(EXECUTORS_PATH, 'w') as f:
        f.write(resource_string(*DEFAULT_EXECUTORS_PATH))
    with open()


