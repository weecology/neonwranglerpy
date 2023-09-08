"""Download the Files from the NEON API, stacks them and returns dataframe."""
import os.path
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
                    stacked_df=True):
    """Download the Files from the NEON API, stacks them and returns dataframe.

    Parameters
    ------------
    dpID: str
        The NEON Data Product ID to be downloaded, in the form DPL.PRNUM.REV
        e.g. DP1.10098.001.

    site : str, list, optional
        The 4 Letter NEON site code for NEON sites or 'all' for data from all sites
        e.g. DELA, ['DELA','ABBY'].

    start_date : str, optional
        Date to search data in the form YYYY-MM or None for all available dates,
        e.g. 2017-01.

    end_date : str, optional
        Date to search data in the form YYYY-MM or None for all available dates,
        e.g. 2017-01.

    package : str, optional
        Indicating which data package to download, either 'basic' or 'expanded'.

    release : str, optional
        The data release to be downloaded; either 'current' or the name of a release,
        e.g. 'RELEASE-2021'.

    path : str, optional
        The full path to the folder in which the files would be placed locally.

    save_files : bool, optional
        Whether to save the downloaded files after downloading them.

    stacked_df: str, optional
        Whether to return the stacked dataframes after stacking the files.

    Returns
    --------
    dict
        A Python dictionary having stacked dataframes and path of saved files
        e.g.
        ``{
        'vst_mappingandtagging' : pandas.DataFrame,
        'stackedpath' : '/test/vst.csv'
        }``
    """
    if not match("DP[1-4]{1}.[0-9]{5}.00[0-9]{1}", dpID):
        return f"{dpID} is not a properly formatted data product ID. The correct format" \
               f" is DP#.#####.00#, where the first placeholder must be between 1 and 4."

    if dpID[4:5] == '3' and dpID != "DP1.30012.001":
        return f'{dpID}, "is a remote sensing data product and cannot be loaded ' \
               f'directly to R with this function.Use the byFileAOP() or ' \
               f'byTileAOP() function to download locally." '

    if start_date is not None:
        if not match(DATE_PATTERN, start_date):
            return 'startdate and enddate must be either NA or valid dates in' \
                   ' the form YYYY-MM'

    if end_date is not None:
        if not match(DATE_PATTERN, end_date):
            return 'startdate and enddate must be either NA or valid dates in' \
                   ' the form YYYY-MM'

    # creates a temp dir.
    # tempdir = mkdtemp(dir=os.path.dirname(path))

    if not path:
        savepath = os.path.normpath(os.path.join(os.getcwd()))
    else:
        savepath = os.path.normpath(path)

    if not os.path.isdir(savepath):
        print(f"{path} doesn't exist")
        return
    # pass the request to zipsByProduct() to download
    files_to_stack_path = zips_by_product(dpID, site, start_date, end_date, package,
                                          release, savepath)
    # stack the tables by using stackByTable\
    savepath = os.path.join(savepath, dpID)
    out = stack_by_table(files_to_stack_path, savepath, dpID, stack_df=stacked_df)
    # removes temp dir
    if not save_files:
        rmtree(savepath)
    return out
