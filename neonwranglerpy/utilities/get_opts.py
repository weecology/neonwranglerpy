"""Argument Parser."""
import argparse
from neonwranglerpy.utilities.defaults import VERSION

parser = argparse.ArgumentParser(prog="neonwranglerpy")
parser.add_argument('-v', '--version', action='version', version=VERSION)
parser.add_argument('-q', '--quiet', help='suppress output', action='store_true')

# neonwranglerpy help
subparsers = parser.add_subparsers(help='sub command help', dest='command')
