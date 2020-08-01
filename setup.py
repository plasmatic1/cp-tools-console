import string
import os
import setuptools
from setuptools import setup


# Removes non-printable ASCII characters
def fix(s):
    res = ''
    for ch in s:
        if ch in string.printable:
            res += ch
    return res


# Getting dependencies
requirements_path = os.path.dirname(os.path.realpath(__file__)) + '/requirements.txt'
assert os.path.isfile(requirements_path)
with open(requirements_path) as f:
    # Windows doesn't want to read files properly for some reason
    install_requires = list(filter(lambda x: len(x) > 0, map(lambda x: fix(x).strip(), f.readlines())))

setup(
    name='cp-tools-console',
    version='1.0.0',
    install_requires=install_requires,
    python_requires='>=3.7',
    packages=setuptools.find_packages('cptools.*', exclude='cptools.tests.*'),
    url='',
    license='GPL 3.0',
    author='Plasmatic',
    author_email='',
    description='Competitive Programming Tools-in console form',

    package_data={
        '': ['*.yml']
    },
    entry_points={
        'console_scripts': [
            'cpr = cptools.scripts.run:main',
            'cprun = cptools.scripts.run:main',
            'cptools-run = cptools.scripts.run:main',

            'cpserv = cptools.scripts.companion_listener:main',
            'cptools-companion-server = cptools.scripts.companion_listener:main',
            
            'cps = cptools.scripts.stress:main',
            'cpstress = cptools.scripts.stress:main',
            'cptools-stress-test = cptools.scripts.stress:main',

            'cpm = cptools.scripts.make_tester:main',
            'cptools-make-file = cptools.scripts.make_tester:main',
        ]
    }
)
