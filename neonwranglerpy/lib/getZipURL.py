from neonwranglerpy.lib.tools import get_api


def get_zip_url(month_urls, package, dpID, release, token=None):
    """
    returns the total no. of files , files names, size
    """
    print("finding available files")
    temp = []
    # get all the file names
    for i in range(len(month_urls)):
        temp.append(get_api(month_urls).json())

    # TODO: check for no response from API
