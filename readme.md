# CP-Tools Console Version

!!! Module has not been published to PyPl !!!

Run `python3 setup.py develop` to install the module in development mode.

Module has been tested with Python 3.7 on both Windows and Linux based systems.

# Introduction

CP-Tools supports both manually made test data along with data retrieved from `jmerle/competitive-companion`

Test data is stored in `.yml` files, which can be easily modified to add/remove test cases.  Example:

```
checker: tokens
cases:
  - in: |
      5 5
      1 3 -8 -2 4
    out: |
      8
  - in: |
      6 2
      0 1 8 1 5 5
    out: |
      10
```

For the checker field, the currently available checkers are:

- `identical`: Identical
- `tokens` (the default): Compares tokenized versions of the expected and actual outputs
- `float:<eps>`: Tokenizes the strings, and then attempts to convert them to floating-point numbers and compare them with a given epsilon value.  Example: `float:1e-4`
- `custom:<path_to_source>`: Custom checker that allows the use of custom code to check the solution.  Path should be absolute
or relative to the current working directory.  File extension should be supported by an executor (i.e. `.cpp` files are supported by default)
    - Custom checker programs will be passed the input in `argv[1]`, the expected output in `argv[2]`, and the actual output in
    `argv[3]`
    - The checker also supports a feedback system: the solution is treated as accepted if only `OK` is outputted to `stdout` (after removing leading/trailing whitespace).
    If anything else is outputted, the verdict is treated as `Wrong Answer` and the feedback is given as the `stdout` content.
    
These files can be written manually, or auto-generated using the Competitive Companion listener.

# Commands/Scripts

## `cptools-run`
Aliases: `cprun`, `cpr`

```
usage: cptools-run [-h] [-e {cpp,cpp-fast,cpp-debug,py}] [-a] [-o ONLY_CASE]
                   [-pwd] [-v]
                   data_file src_file

Compiles and executes a source file on a set of cases

positional arguments:
  data_file             The test cases, as a .yml file
  src_file              The source file to use

optional arguments:
  -h, --help            show this help message and exit
  -e {cpp,cpp-fast,cpp-debug,py}, --executor {cpp,cpp-fast,cpp-debug,py}
                        The executor to use (will use first listed available
                        executor for the file extension if this option is not
                        specified)
  -a, --list-all        Always display output, even if the case was correct
  -o ONLY_CASE, --only-case ONLY_CASE
                        Only run a single case
  -pwd, --pause-when-done
                        Asks the user to press enter before terminating
  -v, --verbose         Verbose mode: shows DEBUG level log messages
```

## `cptools-companion-server`
Aliases: `cpserv`

```
usage: cptools-companion-server [-h] [-p PORT] [-ss] [-pwd] [-v]

Opens a HTTP server to listen for requests from competitive-companion,
automatically creating data files for sample cases along with a source file
from a template (optional). Note: If on linux, shebangs for the input files
are added and they are `chmod`ed so that they are directly executable

optional arguments:
  -h, --help            show this help message and exit
  -p PORT, --port PORT  Port to listen on (default 4244)
  -ss, --skip-source-file
                        Don't autogenerate source file from template
  -pwd, --pause-when-done
                        Asks the user to press enter before terminating
  -v, --verbose         Verbose mode: shows DEBUG level log messages
```

## `cptools-make-file`
Aliases: `cpm`

```
usage: cptools-make-file [-h] [-ms] [-cc CASE_COUNT] [-c CHECKER] [-pwd] [-v]
                         cases_file_name

Autogenerate test case (YML) and source files

positional arguments:
  cases_file_name       File name of the YML file to generate. Note that this
                        should not include the file extension

optional arguments:
  -h, --help            show this help message and exit
  -ms, --make-source    Also generate a source file from the template file
                        path specified in the config. Note that the extension
                        of the source file will be thesame as that of the
                        template
  -cc CASE_COUNT, --case_count CASE_COUNT
                        Adds the specified amount of test cases to the YML
                        file, with placeholders being used as the input and
                        output (foo and bar respectively)
  -c CHECKER, --checker CHECKER
                        The checker for the cases file
  -pwd, --pause-when-done
                        Asks the user to press enter before terminating
  -v, --verbose         Verbose mode: shows DEBUG level log messages
```

## Stress Testing

Automatic stress-testing is also available with the ...

TODO
   
# Configuration

Workspace-level configuration is available at `.cptools/config.yml` in the current workspace.  This file is automatically generated 
when a command is run if the file does not exist already.

To reset the config, simply delete the file and run a command.

Default Configuration:

```
# ==[ Build and Run ]==
# Timeout for running programs (seconds)
timeout: 5.

# Char limit for displayed stdin/stdout/stderr (WIP)
char_limit: 1000000

# ==[ Companion Listener ]==
# Default checker for test sets generated by competitive companion listener or cptools-make-file
default_checker: tokens

# Path to the template file for generating source files as well as input files
template_path: .template.cpp

# Path to save
saved_files_dir: '.'
```

## Executors

Executors are defined in a `.cptools/executors.yml` file in the current workspace.  If it does not exist, a default one will be generated
and used.  The default executors file can be seen in the repository under `cptools/local_data/default_executors.yml`.

Note: Leaving `compiled.exe_format` as `{src_name}.exe` still works fine on Linux based systems.

The executor format is as follows:

### For Compiled Languages

```
cpp-debug:
  ext: ['cpp', 'cxx', 'cc']
  compiled:
    command: ['g++', '-DLOCAL', '-Wall', '-Wshift-overflow=2', '-D_GLIBCXX_DEBUG', '-D_GLIBCXX_DEBUG_PEDANTIC', '-D_FORTIFY_SOURCE=2', '-fsanitize=address', '-fsanitize=undefined', '-fno-sanitize-recover', '-fstack-protector', '-o', '{exe_path}', '{src_path}']
    exe_format: '{src_name}.exe'
  command: ['./{exe_path}']
```

- `ext`: File extensions that this executor supports
    - Also used when determining the default executor for a source file
- `compiled`:
    - `command`: Compilation command
    - `exe_format`: Format for the 
- `command`: Command used to run the source file

### For Interpreted Languages

```
py:
  ext: ['py']
  command: ['python3', '{src_path}']
```

- `ext`: File extensions that this executor supports
    - Also used when determining the default executor for a source file
- `command`: Command used to run the source file

### Format Substitutions

Substitutions are also available for the `compiled.command`, `command`, and `compiled.exe_format` options.  These substitutions
use the `str.format` method with the following keyword substitutions.

- `src_path`: Path to the source file
- `src_name`: `src_path` but without the file extension
- `exe_path`: Path to the executable file
    - Value of the `compiled.exe_format` option after performing substitutions
    - Equal to `src_path` for interpreted languages

## TODO List

- Retrieving previous results
    - `cptools-view`
        - Options:
            - `-p --prev`: Look at previous result only
            - `-l --list`: List all results stored
            - `-c --clear`: Clear previous results
            - `-i --id <id>`: ID
- Allowing both user-wide and local configuration
- Finish stress testing things q:
