"""Download the Files from the NEON API, stacks them and returns dataframe."""
import os.path
from tempfile import mkdtemp
from shutil import rmtree
from re import match, compile
from neonwranglerpy.utilities.zipsByProduct import zips_by_product
from neonwranglerpy.utilities.stackByTable import stack_by_table

DATE_PATTERN = compile('20[0-9]{2}-[0-9]{2}')


def load_by_product(dpID,
                    site='all',
                    start_date=None,
                    end_date=None,
                    package="basic",
                    release="current",
                    path='./',
                    save_files=False,
                    stacked_df=False):
    """Download the Files from the NEON API, stacks them and returns dataframe."""
    if not match("DP[1-4]{1}.[0-9]{5}.00[0-9]{1}", dpID):
        return f"{dpID} is not a properly formatted data product ID. The correct format" \
               f" is DP#.#####.00#, where the first placeholder must be between 1 and 4."

    if dpID[4:5] == 3 and dpID != "DP1.30012.001":
        return f'{dpID}, "is a remote sensing data product and cannot be loaded ' \
               f'directly to R with this function.Use the byFileAOP() or ' \
               f'byTileAOP() function to download locally." '

    if len(start_date):
        if not match(DATE_PATTERN, start_date):
            return 'startdate and enddate must be either NA or valid dates in' \
                   ' the form YYYY-MM'

    if len(end_date):
        if not match(DATE_PATTERN, end_date):
            return 'startdate and enddate must be either NA or valid dates in' \
                   ' the form YYYY-MM'

    # creates a temp dir.
    tempdir = mkdtemp(dir=os.path.dirname(path))

    # pass the request to zipsByProduct() to download
    path = zips_by_product(dpID,
                           site,
                           start_date,
                           end_date,
                           package,
                           release,
                           savepath=tempdir)
    # stack the tables by using stackByTable\
    out = stack_by_table(filepath=path, dpID=dpID, savepath=tempdir, stack_df=stacked_df)
    # removes temp dir
    if not save_files:
        rmtree(tempdir)
    return out
