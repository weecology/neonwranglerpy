"""Downloads the AOP data from NEON API."""
import math
import os
import re
from urllib.error import HTTPError
from urllib.request import urlretrieve
import pandas as pd

from neonwranglerpy import get_data
from neonwranglerpy.utilities.tools import get_api
from neonwranglerpy.utilities.defaults import NEON_API_BASE_URL
from neonwranglerpy.utilities.get_tile_urls import get_tile_urls


def load_shared_flights():
    """Return the dataframe about the table types of Data Products."""
    stream = get_data('shared_flights.csv')
    df = pd.read_csv(stream)
    df.reset_index(drop=True, inplace=True)
    return df


def by_tile_aop(dpID, site, year, easting, northing, savepath=None):
    """Download the AOP data for given tiles coordinates."""
    if not re.match("DP[1-4]{1}.[0-9]{5}.00[0-9]{1}", dpID):
        return f"{dpID} is not a properly formatted data product ID. The correct format" \
               f" is DP#.#####.00#, where the first placeholder must be between 1 and 4."

    # TODO: convert to int if dataframe
    # easting = int(easting)
    # northing = int(northing)

    api_url = NEON_API_BASE_URL + 'products/' + dpID
    response = get_api(api_url).json()
    all_urls = []
    # TODO: check for product not found

    # check for shared sites
    shared_flights = load_shared_flights()
    flight_site = shared_flights['site'].str.contains(site)

    if flight_site.any():
        flight_site = shared_flights['flightSite'][flight_site].item()
        site = flight_site
        print(f'{site} is part of shared flights, changing the {site} to {flight_site}')

    for i in range(len(response['data']['siteCodes'])):
        if response['data']['siteCodes'][i]['siteCode'] == site:
            all_urls = response['data']['siteCodes'][i]['availableDataUrls']
        if not len(all_urls):
            return f"There is no data for {site}"
    month_urls = [x for x in all_urls if re.search(year, x)]
    if not len(month_urls):
        print(f"There is no data for site {site} and year {year}")

    # TODO : use vectorized operation instead
    tile_easting = [math.floor(float(x / 1000)) * 1000 for x in easting]
    tile_northing = [math.floor(float(x / 1000)) * 1000 for x in northing]
    file_urls = get_tile_urls(month_urls, tile_easting, tile_northing)

    if not savepath:
        savepath = os.path.normpath(os.path.join(os.getcwd(), dpID))
    else:
        savepath = os.path.normpath(os.path.join(savepath, dpID))

    if not os.path.isdir(savepath):
        os.makedirs(savepath)

    # TODO: progress bar
    for i in range(len(file_urls)):
        split_path = file_urls[i]['url'].split('/')
        dir_path = '/'.join(split_path[4:len(split_path) - 1])
        save_dir_path = os.path.join(savepath, dir_path)
        save_file_path = os.path.join(save_dir_path, file_urls[i]['name'])
        if not os.path.exists(save_dir_path):
            os.makedirs(save_dir_path)

        try:
            file_path, _ = urlretrieve(file_urls[i]['url'], save_file_path)
        except HTTPError as e:
            print("HTTPError :", e)
            return None

    return savepath
