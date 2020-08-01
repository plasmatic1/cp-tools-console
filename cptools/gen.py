import logging
import textwrap
import os
import sys
from cptools.data import get_option

# dict of file ext -> comment prefix
COMMENT_MAP = {
    '.c': '//',
    '.cpp': '//',
    '.cxx': '//',
    '.cc': '//',
    '.java': '//',

    '.py': '#',
    '.rb': '#'
}


def write_cases_file(path, problem, checker=get_option("default_checker")):
    is_linux = sys.platform == 'linux' or sys.platform == 'linux2'
    with open(path, 'w') as f:  # Writing cases manually for a bit more flexibility when formatting YAML
        # Shebang
        if is_linux:
            f.write('#!cptools-run\n')

        f.write(f'checker: {checker}\n')
        f.write('cases:\n')

        # Number of cases is 0
        if len(problem['tests']) == 0:
            problem['tests'].append({'input': 'foo', 'output': 'bar'})  # Any sample sequence

        for case in problem['tests']:
            inp = case['input'] + ('\n' if case['input'][-1] != '\n' else '')
            out = case['output'] + ('\n' if case['output'][-1] != '\n' else '')

            f.write('  - in: |\n')
            f.write(textwrap.indent(inp, ' ' * 6))
            f.write('    out: |\n')
            f.write(textwrap.indent(out, ' ' * 6))
    if is_linux:
        os.chmod(path, 0o777)  # Help


def try_write_source_file(fname, src_lang):
    is_linux = sys.platform == 'linux' or sys.platform == 'linux2'
    if not os.path.exists(get_option('template_path')):
        logging.warning('Template file does not exist.  Skipping generation of source file')
    else:
        with open(fname + src_lang, 'w') as f:
            # Some sort of indicator to denote the associated data file
            f.write(f'{COMMENT_MAP[src_lang]} {fname}.yml\n')

            with open(get_option('template_path')) as ff:
                f.write(ff.read().replace('\r', ''))

        if is_linux:
            os.chmod(fname + src_lang, 0o777)

