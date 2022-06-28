from neonwranglerpy.lib.tools import get_api


def get_zip_urls(month_urls, package, dpID, release, token=None):
    """
    returns the total no. of files , their urls, files names, size
    """
    print("finding available files")
    temp = []
    # get all the file names
    for i in month_urls:
        temp.append(get_api(i).json()['data'])
    # TODO: check for no response from API
    # TODO : add progress bar

    # TODO: subset for a release
    # TODO: check for no files
    # TODO: return name and size
    return temp
