import re
from os import path

from neonwranglerpy.lib.tools import create_temp, copy_zips


def stack_by_table(filepath="./stack", savepath=".", dpID=None, package=None):
    if not path.exists(filepath):
        return f"{filepath} doesn't exists "

    if not re.match("DP[1-4]{1}.[0-9]{5}.00[0-9]{1}", dpID):
        return f"{dpID} is not a properly formatted data product ID. The correct format is DP#.#####.00#, " \
               f"where the first placeholder must be between 1 and 4."

    # TODO: add check for data should be stacked
    # TODO: add check for dpID and Package of files
    # TODO: add check for AOP data

    tempdir = create_temp(savepath)

    if tempdir:
        copy_zips(filepath, dst=savepath)
