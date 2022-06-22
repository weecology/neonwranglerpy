import re
from neonwranglerpy.lib.tools import get_api, get_month_year_urls
from neonwranglerpy.lib.defaults import NEON_API_BASE_URL
from neonwranglerpy.lib.getZipURL import get_zip_url

DATE_PATTERN = re.compile('20[0-9]{2}-[0-9]{2}')


def zips_by_product(
        dpID, site='all',
        start_date=None,
        end_date=None,
        package="basic",
        release="current", path='./', token=None
):
    if package != 'basic' or package != 'extended':
        print(f"{package} is not a valid package name. Package must be basic or expanded")
        return

    # TODO: add a check for correct format of product ID
    # TODO: add a check for AOP data product

    if not start_date:
        if not re.match(DATE_PATTERN, start_date):
            return 'startdate and enddate must be either NA or valid dates in the form YYYY-MM'

    if not end_date:
        if not re.match(DATE_PATTERN, end_date):
            return 'startdate and enddate must be either NA or valid dates in the form YYYY-MM'

    if release == 'current':
        api_url = NEON_API_BASE_URL + 'products/' + dpID
        product_req = get_api(api_url, token)
    else:
        api_url = NEON_API_BASE_URL + 'products/' + dpID + '?release' + release
        product_req = get_api(api_url, token)

    api_response = product_req.json()

    if api_response['error']['status']:
        print('No data found for product')

    # TODO: check for rate-limit

    # extracting URLs for specific sites
    month_urls = []
    all_urls = []
    for i in range(len(api_response['data']['siteCodes'])):
        all_urls.extend(api_response['data']['siteCodes'][i]['availableDataUrls'])

    if site == 'all':
        month_urls = all_urls
    else:
        month_urls = [x for x in month_urls if re.search(site, x)]

    if len(month_urls) == 0:
        print(f"There is no data for site {site}")

    # extracting urls for specified start and end dates
    if len(start_date) != 0:
        month_urls = get_month_year_urls(start_date, month_urls, 'start')

    if len(month_urls) == 0:
        print("There is no data for selected dates")

    if len(end_date) != 0:
        month_urls = get_month_year_urls(end_date, month_urls, 'end')

    if len(month_urls) == 0:
        print("There is no data for selected dates")


