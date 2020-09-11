import os
import yaml
from collections import namedtuple
from pkg_resources import resource_string

DEFAULT_CONFIG_PATH = 'cptools.local_data', 'default_config.yml'
DEFAULT_EXECUTORS_PATH = 'cptools.local_data', 'default_executors.yml'
DEFAULT_STRESS_TEST_PATH = 'cptools.local_data', 'default_stress_test.yml'

DATA_DIR = '.cptools'
CONFIG_PATH = f'{DATA_DIR}/config.yml'
EXECUTORS_PATH = f'{DATA_DIR}/executors.yml'
RESULTS_LIST_PATH = f'{DATA_DIR}/results_list.yml'
RESULTS_DIR = f'{DATA_DIR}/results'

Result = namedtuple('Result', 'id src_name input_name checker cases')
Case = namedtuple('Case', 'inp out expected_out err')


# pkg_resources.resource_string but with some small fixes (such as removing \r)
def get_resource_string_fix(*args):
    return str(resource_string(*args), 'utf8').replace('\r', '')


def get_default_stress_test_file():
    """
    Get the default content of the stress test file for cptools-stress-test --make-file
    """
    return get_resource_string_fix(*DEFAULT_STRESS_TEST_PATH)


def reset_config(force=False):
    if force or not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'w') as f:
            f.write(get_resource_string_fix(*DEFAULT_CONFIG_PATH))


def reset_executors(force=False):
    if force or not os.path.exists(EXECUTORS_PATH):
        with open(EXECUTORS_PATH, 'w') as f:
            f.write(get_resource_string_fix(*DEFAULT_EXECUTORS_PATH))


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


def get_executors():
    """
    Returns a list of all executors
    """

    __verify_folder_exists()
    reset_executors(False)
    with open(EXECUTORS_PATH) as f:
        return yaml.unsafe_load(f.read())


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


"""
VALIDATORS
"""

v_int = lambda x: type(x) == int, 'expected int'
v_float = lambda x: type(x) == float, 'expected float'
v_str = lambda x: type(x) == str, 'expected string'
v_exist_file = lambda x: type(x) == str and os.path.exists(x), 'expected file (path specified does not exist)'
v_dict = lambda x: type(x) == dict, 'expected dict'
v_list_str = lambda x: type(x) == list and all((type(xx) == str for xx in x)), 'expected list of strings'
v_list_node = lambda x: type(x) == list and all((type(xx) == dict for xx in x)), 'expected list of dict'

CONFIG_VALIDATORS = {
    'timeout': v_float,
    'char_limit': v_int,
    'default_checker': v_str,  # Whether the checker string is valid is handled in checker.py :)
    'template_path': v_str,
    'saved_files_dir': v_str
}


def validate_keys(validator_dict, obj, pre=None):
    pre = f'in path "{pre}" ' if pre else ''
    for k, v in validator_dict.items():
        fun, msg = v
        if k not in obj:
            return f'Config key "{k}"" not found {pre}'
        if not fun(obj[k]):
            return f'Invalid value "{obj[k]}" for config key "{k}" {pre}({msg})'
    return None


def validate_config_object(obj):
    """
    Returns an error message if the config is invalid, and None otherwise
    :param obj: The config object in question
    """
    return validate_keys(CONFIG_VALIDATORS, obj)


EXECUTOR_VALIDATORS = {
    'ext': v_list_str,
    'command': v_list_str
}

COMPILED_EXECUTOR_VALIDATORS = {
    'command': v_list_str,
    'exe_format': v_str
}


def validate_executors_object(obj):
    """
    Returns an error message if the executor list is invalid, and None otherwise
    :param obj: The object
    """

    for k, v in obj.items():
        if not v_dict[0](v):
            return f'Executor {k} not a node'
        res_base = validate_keys(EXECUTOR_VALIDATORS, v, k)
        if res_base: return res_base
        if 'compiled' in v:
            if not v_dict[0](v):
                return f'Compiled key of executor {k} not a node'
            res_base = validate_keys(COMPILED_EXECUTOR_VALIDATORS, v['compiled'], f'{k}.compiled')
            if res_base: return res_base
    return None


DATA_VALIDATORS = {
    'checker': v_str,  # Validity is checked when parsing string
    'cases': v_list_node
}

CASE_VALIDATORS = {
    'in': v_str,
    'out': v_str
}


def validate_data_object(obj):
    """
    Returns an error message if the executor list is invalid, and None otherwise
    :param obj: The object
    """
    res_base = validate_keys(DATA_VALIDATORS, obj)
    if res_base: return res_base
    for idx, node in enumerate(obj['cases']):
        res_base = validate_keys(CASE_VALIDATORS, node, f'[{idx}]')
        if res_base: return res_base
    return None


STRESS_TEST_VALIDATORS = {
    'checker': v_str,
    'gen': v_exist_file,
    'fast': v_exist_file
}


def validate_stress_test_object(obj):
    """
    Returns an error message if the stress testing info object is invalid, and None otherwise
    :param obj: The object
    """
    return validate_keys(STRESS_TEST_VALIDATORS, obj)

