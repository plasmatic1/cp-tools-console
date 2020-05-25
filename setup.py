import setuptools
from setuptools import setup

setup(
    name='cp-tools-console',
    version='1.0.0',
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
