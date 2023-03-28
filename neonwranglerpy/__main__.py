"""CLI entry point."""

import logging
import sys

from neonwranglerpy.utilities.get_opts import parser

_logger = logging.getLogger(__name__)


def setup_logging(loglevel):
    """Set basic logging."""
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(level=loglevel,
                        stream=sys.stdout,
                        format=logformat,
                        datefmt="%Y-%m-%d %H:%M:%S")


def main():
    """CLI main function."""
    if len(sys.argv) == 1:
        # if no command line args are passed, show the help options
        parser.parse_args(["-h"])
    else:
        # parse args for CLI interface
        args = parser.parse_args()
        print(args)


if __name__ == "__main__":
    main()
