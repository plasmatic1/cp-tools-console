import argparse
import cptools.util as cptools_util

parser = argparse.ArgumentParser()


def main():
    cptools_util.init_common(parser)
    args = parser.parse_args()
    cptools_util.init_common_options(args, False)
