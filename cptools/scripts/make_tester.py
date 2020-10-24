import logging
import os.path as path
import argparse
import cptools.common as common
import cptools.data as data
from cptools.data import get_option
from cptools.gen import write_cases_file, try_write_source_file

parser = argparse.ArgumentParser(description='Autogenerate test case (YML), source files, and stress-testing config'
                                             'files')
parser.add_argument('file_name', type=str, help='File name (without extension) of the YML file to generate.')
parser.add_argument('-ms', '--make-source', help='Also generate a source file from the template file path specified in '
                                                 'the config.  Note that the extension of the source file will be the'
                                                 'same as that of the template',
                    action='store_true')
parser.add_argument('-cc', '--case_count', help='Adds the specified amount of test cases to the YML file, with '
                                               'placeholders being used as the input and output (foo and bar '
                                               'respectively)',
                    type=int, default=1)
parser.add_argument('-c', '--checker', help='The checker for the cases file.  If not specified, it defaults to the'
                                            'default_checker option in the config.yml file',
                                            type=str, default=get_option('default_checker'))

parser.add_argument('-S', '--stress-test', help='Instead of generating test case and source files, it creates a stress'
                                                '-testing config file instead.  Specify the name of the file (without '
                                                'xtension) in the file_name argument',
                                            action='store_true')


def main():
    common.init_common(parser)
    args = parser.parse_args()
    common.init_common_options(args, False)

    if args.stress_test:
        args.file_name += '.yml'
        logging.info(f'Making info file {args.file_name}...')
        with open(args.file_name, 'w') as f:
            f.write(data.get_default_stress_test_file())
    else:
        tests_obj = {'tests': [{'input': 'foo', 'output': 'bar'} for _ in range(args.case_count)]}
        write_cases_file(args.file_name + '.yml', tests_obj, args.checker)
        logging.info(f'Generating cases file {args.file_name}.yml with {args.case_count} sample cases and checker "{args.checker}"')
        if args.make_source:
            fname = args.file_name
            ext = path.splitext(get_option('template_path'))[1]
            logging.info(f'Generating source file {fname}{ext}')
            try_write_source_file(fname, ext)
