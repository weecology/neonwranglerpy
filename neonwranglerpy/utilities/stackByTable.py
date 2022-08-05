import re
from os import path
from re import match
from shutil import rmtree
from neonwranglerpy.utilities.stackdatafiles import stackdatafiles
from neonwranglerpy.utilities.tools import create_temp, copy_zips


def stack_by_table(filepath="filesTostack", savepath=".", dpID=None, package=None, stack_df=False):
    if not path.exists(filepath):
        return f"{filepath} doesn't exists "

    if not re.match("DP[1-4]{1}.[0-9]{5}.00[0-9]{1}", dpID):
        return f"{dpID} is not a properly formatted data product ID. The correct format is DP#.#####.00#, " \
               f"where the first placeholder must be between 1 and 4."

    # TODO: add check for data should be stacked
    if not match("DP[1-4]{1}.[0-9]{5}.00[0-9]{1}", dpID):
        return f"{dpID} is not a properly formatted data product ID. The correct format is DP#.#####.00#, " \
               f"where the first placeholder must be between 1 and 4."

    if dpID[4:5] == 3 and dpID != "DP1.30012.001":
        return f'{dpID}, "is a remote sensing data product and cannot be loaded directly to R with this function.Use ' \
               f'the byFileAOP() or byTileAOP() function to download locally." '

    # copies the downloaded files to a temp dir
    tempdir = create_temp(savepath)
    copy_zips(filepath, dst=tempdir)

    # pass the path of files to stackdatafiles function
    out = stackdatafiles(tempdir, savepath, dpID,stack_df=stack_df)

    rmtree(tempdir)
    return out
