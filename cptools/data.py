import os
import yaml
from collections import namedtuple
from pkg_resources import resource_string

DEFAULT_CONFIG_PATH = 'cptools.local_data', 'default_config.yml'
DEFAULT_EXECUTORS_PATH = 'cptools.local_data', 'default_executors.yml'

DATA_DIR = '.cptools'
CONFIG_PATH = f'{DATA_DIR}/config.yml'
EXECUTORS_PATH = f'{DATA_DIR}/executors.yml'
RESULTS_LIST_PATH = f'{DATA_DIR}/results_list.yml'
RESULTS_DIR = f'{DATA_DIR}/results'

Result = namedtuple('Result', 'id src_name input_name checker cases')
Case = namedtuple('Case', 'in out expected_out err')


def reset_config(force=False):
    if force or not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'w') as f:
            f.write(resource_string(*DEFAULT_CONFIG_PATH))


def reset_executors(force=False):
    if force or not os.path.exists(EXECUTORS_PATH):
        with open(EXECUTORS_PATH, 'w') as f:
            f.write(resource_string(*DEFAULT_EXECUTORS_PATH))


def reset_results(force=False):
    if force or not os.path.exists(RESULTS_LIST_PATH):
        with open(RESULTS_LIST_PATH, 'w') as f:
            f.write('[]')
    if force:
        os.rmdir(RESULTS_DIR)
    if not os.path.exists(RESULTS_DIR):
        os.mkdir(RESULTS_DIR)


def __verify_folder_exists():
    if not os.path.exists(DATA_DIR):
        os.mkdir(DATA_DIR)


def reset_all(force=False):
    if force and os.path.exists(DATA_DIR):
        os.rmdir(DATA_DIR)
    if not os.path.exists(DATA_DIR):
        os.mkdir(DATA_DIR)

    reset_config(force)
    reset_executors(force)
    reset_results(force)


def get_config():
    """
    Returns the entire config file as a dict
    """

    __verify_folder_exists()
    reset_config(False)
    with open(CONFIG_PATH) as f:
        return yaml.unsafe_load(f)


def get_option(key):
    """
    Returns the value of the config option specified by key.  Nested options should be separated by periods
    :param key: The config key.  Note that the correctness of key is not checked for.
    """

    config = get_config()
    for part in key.split('.'):
        if part not in config:
            raise ValueError(f'Invalid config option {key}')
        config = config[part]
    return config


def get_executor(name):
    """
    Returns the executor with the specified name
    :param name: The name of the executor to return.  Note that the correctness of name is not checked for
    """

    __verify_folder_exists()
    reset_executors(False)
    with open(EXECUTORS_PATH) as f:
        executors = yaml.unsafe_load(f.read())
        if name not in executors:
            raise ValueError(f'Invalid executor {name}')
        return executors[name]


def get_executors_list():
    """
    Returns a list of all executors
    """

    __verify_folder_exists()
    reset_executors(False)
    with open(EXECUTORS_PATH) as f:
        return yaml.unsafe_load(f.read()).keys()


def get_result_list():
    """
    Returns a list of currently saved execution results
    """

    __verify_folder_exists()
    reset_results(False)
    with open(RESULTS_LIST_PATH) as f:
        return yaml.unsafe_load(f.read())


def get_result(result_id):
    """
    Returns the execution result with the given id
    :param result_id: The id of the result to save
    """

    __verify_folder_exists()
    reset_results(False)
    with open(RESULTS_LIST_PATH) as f:
        results_info = yaml.full_load(f.read())
        if result_id not in results_info:
            raise ValueError(f'Invalid result id {result_id}')
        with open(results_info[result_id]['path']) as ff:
            return yaml.full_load(ff.read())  # Since its auto generated loading unsafe is not needed


def add_result(result_obj: Result):
    """
    Adds a result to the results file
    :param result_obj: The result object to add
    """

    __verify_folder_exists()
    reset_results(False)
    path = f'{RESULTS_DIR}/{result_obj.id}.yml'
    with open(RESULTS_LIST_PATH) as f:
        result_list = yaml.full_load(f.read())
    result_list.append({
        'path': path,
        'src_name': result_obj.src_name,
        'input_name': result_obj.input_name
    })
    with open(path, 'w') as f:
        f.write(yaml.dump(result_list))

