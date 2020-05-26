import os
import setuptools
from setuptools import setup

# Getting dependencies
requirements_path = os.path.dirname(os.path.realpath(__file__)) + '/requirements.txt'
assert os.path.isfile(requirements_path)
with open(requirements_path) as f:
    install_requires = f.readlines()

setup(
    name='cp-tools-console',
    version='1.0.0',
    install_requires=install_requires,
    packages=setuptools.find_packages('cptools.*', exclude='cptools.tests.*'),
    url='',
    license='GPL 3.0',
    author='Plasmatic',
    author_email='',
    description='Competitive Programming Tools- in console form',

    package_data={
        '': '*.yml'
    },
    entry_points={
        'console_scripts': [
            'cpr = cptools.scripts.run:main'
        ]
    }
)
