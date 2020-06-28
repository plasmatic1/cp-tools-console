import argparse
import json
import logging
import os
import string
import sys
import textwrap
from http.server import HTTPServer, BaseHTTPRequestHandler

from cptools.data import get_option
from cptools.util import init_log

# Default host ports: https://github.com/jmerle/competitive-companion/blob/master/src/hosts/hosts.ts
DEFAULT_PORT = 4244  # It's the hightail port but whatever.  I asked jmerle and he said it was fine


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


# Fixes a problem name
def fix_name(name: str):
    TO_REMOVE = ''.join(ch for ch in string.punctuation if ch not in '-')
    return name.lower() \
        .replace(' - ', '-') \
        .replace(' ', '-') \
        .translate(str.maketrans('', '', TO_REMOVE))


# Source: https://gist.github.com/mdonkers/63e115cc0c79b4f6b8b3a6b797e485c7
class RequestHandler(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])  # <--- Gets the size of data
        problem = json.loads(self.rfile.read(content_length))  # <--- Gets the data itself

        name = fix_name(problem['name'].strip())
        logging.info(f'Received problem "{name}" from {problem["group"]}.  Contains {len(problem["tests"])} sample cases')

        self._set_response()
        self.wfile.write("POST request for {}".format(self.path).encode('utf-8'))

        # Make name unique
        src_lang = os.path.splitext(get_option('template_path'))[1]

        fname = name
        ctr = 1
        while not fname or os.path.exists(fname + '.yml') or os.path.exists(fname + src_lang):
            fname = name + str(ctr)
            ctr += 1

        # Write case file
        is_linux = sys.platform == 'linux' or sys.platform == 'linux2'

        with open(fname + '.yml', 'w') as f:  # Writing cases manually for a bit more flexibility when formatting YAML
            # Shebang
            if is_linux:
                f.write('#!cptools-run\n')

            f.write(f'checker: {get_option("default_checker")}\n')
            f.write('cases:\n')
            for case in problem['tests']:
                inp = case['input'] + ('\n' if case['input'][-1] != '\n' else '')
                out = case['output'] + ('\n' if case['output'][-1] != '\n' else '')

                f.write('  - in: |\n')
                f.write(textwrap.indent(inp, ' ' * 6))
                f.write('    out: |\n')
                f.write(textwrap.indent(out, ' ' * 6))

        if is_linux:
            os.chmod(fname + '.yml', 0o777)  # Help

        # Write source file
        if not args.skip_source_file:
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

    # Source: https://stackoverflow.com/questions/3389305/how-to-silent-quiet-httpserver-and-basichttprequesthandlers-stderr-output
    # Silences pesky log messages
    def log_message(self, format, *args):
        return


parser = argparse.ArgumentParser()
parser.add_argument('-p', '--port', help='Port to listen on (default 4244)',
                    type=int)
parser.add_argument('-ss', '--skip-source-file', help='Don\'t autogenerate source file from template',
                    action='store_true')
parser.add_argument('-v', '--verbose', help='Verbose mode: shows DEBUG level log messages',
                    action='store_true')
args = parser.parse_args()


def main():
    init_log(args.verbose)

    logging.info('Started Competitive Companion Listener')
    logging.info(f'Files will be saved in {os.getcwd()}')

    port = args.port or DEFAULT_PORT
    logging.info(f'Starting HTTP server on port {port}...')
    server = HTTPServer(('localhost', port), RequestHandler)
    server.serve_forever()

