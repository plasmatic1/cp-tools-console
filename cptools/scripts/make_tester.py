import logging
import os.path as path
import argparse
import cptools.util as cptools_util
from cptools.data import get_option
from cptools.gen import write_cases_file, try_write_source_file

parser = argparse.ArgumentParser(description='Autogenerate test case (YML) and source files')
parser.add_argument('cases_file_name', type=str, help='File name of the YML file to generate.  Note that this should '
                                                      'not include the file extension')
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


def main():
    cptools_util.init_common(parser)
    args = parser.parse_args()
    cptools_util.init_common_options(args, False)

    tests_obj = {'tests': [{'input': 'foo', 'output': 'bar'} for _ in range(args.case_count)]}
    write_cases_file(args.cases_file_name + '.yml', tests_obj, args.checker)
    logging.info(f'Generating cases file {args.cases_file_name}.yml with {args.case_count} sample cases and checker "{args.checker}"')
    if args.make_source:
        fname = args.cases_file_name
        ext = path.splitext(get_option('template_path'))[1]
        logging.info(f'Generating source file {fname}{ext}')
        try_write_source_file(fname, ext)
