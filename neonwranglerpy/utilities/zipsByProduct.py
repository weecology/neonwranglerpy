"""Download the data files from NEON API."""
import re
import os.path
from urllib.request import urlretrieve
from urllib.error import HTTPError
from neonwranglerpy.utilities.tools import get_api, get_month_year_urls
from neonwranglerpy.utilities.defaults import NEON_API_BASE_URL
from neonwranglerpy.utilities.getzipurls import get_zip_urls
import neonwranglerpy.fetcher.fetcher as fetcher

DATE_PATTERN = re.compile('20[0-9]{2}-[0-9]{2}')


def zips_by_product(dpID,
                    site='all',
                    start_date=None,
                    end_date=None,
                    package="basic",
                    release="current",
                    savepath='',
                    token=None):
    """Download the data files from NEON API.

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

    savepath : str, optional
        The full path to the folder in which the files would be placed locally.


    Returns
    --------
    str
        The path to /filestostack directory
    """
    if dpID[4:5] == '3' and dpID != "DP1.30012.001":
        return f'{dpID}, "is a remote sensing data product and cannot be loaded' \
               f'directly to R with this function.Use the byFileAOP() or ' \
               f'byTileAOP() function to download locally." '

    global zip_dir_path

    if not re.match("DP[1-4]{1}.[0-9]{5}.00[0-9]{1}", dpID):
        return f"{dpID} is not a properly formatted data product ID. The correct format" \
               f" is DP#.#####.00#, where the first placeholder must be between 1 and 4."

    if start_date is not None:
        if not re.match(DATE_PATTERN, start_date):
            return 'startdate and enddate must be either NA or valid dates in the form '\
                   'YYYY-MM'

    if end_date is not None:
        if not re.match(DATE_PATTERN, end_date):
            return 'startdate and enddate must be either NA or valid dates in the form ' \
                   'YYYY-MM'

    if release == 'current':
        api_url = NEON_API_BASE_URL + 'products/' + dpID
        product_req = get_api(api_url, token)
    else:
        api_url = NEON_API_BASE_URL + 'products/' + str(dpID) + '?release' + str(release)
        product_req = get_api(api_url, token).json()

    api_response = product_req.json()

    if 'error' in api_response:
        return f"status: {api_response['error']['status']},"
        f" {api_response['error']['detail']}"

    # TODO: check for rate-limit

    # extracting URLs for specific sites
    month_urls = []
    all_urls = []
    for i in range(len(api_response['data']['siteCodes'])):
        all_urls.extend(api_response['data']['siteCodes'][i]['availableDataUrls'])

    if site == 'all':
        month_urls = all_urls
    else:
        if isinstance(site, str):
            site = list(site.split(' '))
        for package in site:
            month_site = [x for x in all_urls if re.search(package, x)]
            month_urls.extend(month_site)

    if not len(month_urls):
        print(f"There is no data for site {site}")

    # extracting urls for specified start and end dates
    if start_date is not None:
        month_urls = get_month_year_urls(start_date, month_urls, 'start')

    if not len(month_urls):
        print("There is no data for selected dates")

    if end_date is not None:
        month_urls = get_month_year_urls(end_date, month_urls, 'end')

    if not len(month_urls):
        print("There is no data for selected dates")

    # TODO: calculate download size
    # TODO: user input for downloading or not
    if not savepath:
        savepath = os.path.normpath(os.path.join(os.getcwd(), dpID))
    else:
        savepath = os.path.normpath(os.path.join(savepath, dpID))

    if not os.path.isdir(savepath):
        os.makedirs(savepath)

    files_to_stack_path = os.path.join(savepath, "filesToStack")
    if not os.path.isdir(files_to_stack_path):
        os.mkdir(files_to_stack_path)

    if files_to_stack_path:
        fetcher.run_threaded_batches(month_urls,
                                     'vst',
                                     rate_limit=2,
                                     headers=None,
                                     savepath=files_to_stack_path)
    # returns the path to /filestostack directory
    return files_to_stack_path
