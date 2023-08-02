"""Return the total no. of files , their urls, files names, size."""
from neonwranglerpy.utilities.tools import get_api
import time
import concurrent.futures

def get_zip_urls(month_urls, package, dpID, release, token=None):
    """Return the total no. of files , their urls, files names, size."""
    print("finding available files")
    temp = []
    # get all the file names
    with concurrent.futures.ThreadPoolExecutor() as executor:
        temp = list(filter(None, executor.map(fetch_data, month_urls)))


    # TODO : add progress bar

    # TODO: subset for a release
    # TODO: check for no files
    # TODO: return name and size
    return temp


def fetch_data(month_url):
    try:
        return get_api(month_url).json()['data']
    except Exception as e:
        print(f"no response from API for {month_url}")
        return None

