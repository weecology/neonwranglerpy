"""Downloads the AOP data from NEON API."""
import math
import os
import re
from urllib.error import HTTPError
from urllib.request import urlretrieve
import pandas as pd
import geopandas as gpd

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


def by_tile_aop(dpID, site, year, easting, northing, buffer=0, savepath=None):
    """Download the AOP data for given tiles coordinates.

    Parameters
    ----------
    dpID: str
        The NEON Data Product ID to be downloaded, in the form DPL.PRNUM.REV
        e.g. DP3.30006.001

    site : str
        The NEON site code for a single NEON site e.g. DELA

    year : str
        The single year to search data e.g 2017

    easting : int, list of int, pandas dataframe of int
        The easting UTM coordinates of the locations to be downloaded

    northing : int, list of int, pandas dataframe of int
        The northing UTM coordinates of the locations to be downloaded

    savepath : str, optional
        The full path to the folder in which the files would be placed locally.

    buffer : int
        The buffer around cooordinates to be taken while downloading the tiles.
    """
    if not re.match("DP[1-4]{1}.[0-9]{5}.00[0-9]{1}", dpID):
        return f"{dpID} is not a properly formatted data product ID. The correct format" \
               f" is DP#.#####.00#, where the first placeholder must be between 1 and 4."

    api_url = NEON_API_BASE_URL + 'products/' + dpID
    response = get_api(api_url).json()
    all_urls = []

    if 'error' in response:
        return f"status: {response['error']['status'], {response['error']['detail']}}"

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
    year_pattern = re.compile(str(year))
    month_urls = [x for x in all_urls if re.search(year_pattern, x)]
    if not len(month_urls):
        print(f"There is no data for site {site} and year {year}")

    if isinstance(easting, (int, float)):
        easting = [easting]
        northing = [northing]
    # convert the easting and northing for BLAN site
    if site == "BLAN":
        if isinstance(easting, (int, list)):
            easting = pd.DataFrame({'easting': easting}).reset_index(drop=True)
            northing = pd.DataFrame({'northing': northing}).reset_index(drop=True)

        df18N_mask = easting <= 250000
        df17N_mask = easting > 250000
        if df18N_mask['easting'].any:
            # df17N dataframe
            df17N_easting = easting.loc[df17N_mask['easting']].reset_index(drop=True)
            df17N_northing = northing.loc[df17N_mask['easting']].reset_index(drop=True)
            df17N = pd.concat([df17N_easting, df17N_northing],
                              axis=1).reset_index(drop=True)
            df17N.columns = ['easting', 'northing']

            # df18N dataframe
            df18N_easting = easting.loc[df18N_mask['easting']].reset_index(drop=True)
            df18N_northing = northing.loc[df18N_mask['easting']].reset_index(drop=True)
            df18N = pd.concat([df18N_easting, df18N_northing],
                              axis=1).reset_index(drop=True)
            df18N.columns = ['easting', 'northing']

            # convert the 18N to 17N
            gdf18N = gpd.GeoDataFrame(df18N,
                                      geometry=gpd.points_from_xy(
                                          df18N.easting, df18N.northing),
                                      crs=32618)
            df18N_in17nm = gdf18N.to_crs(32617)

            # update the easting and northing for 18N with 17N
            df18N_in17nm = pd.concat(
                [df18N_in17nm['geometry'].x, df18N_in17nm['geometry'].y],
                axis=1).reset_index(drop=True)
            df18N_in17nm.columns = ['easting', 'northing']

            # append df18N and df17N
            _df = pd.concat([df18N_in17nm, df17N])
            easting, northing = _df.easting, _df.northing

    tile_easting = [math.floor(float(x / 1000)) * 1000 for x in easting]
    tile_northing = [math.floor(float(x / 1000)) * 1000 for x in northing]
    file_urls = get_tile_urls(month_urls, tile_easting, tile_northing)

    if not savepath:
        savepath = os.path.normpath(os.path.join(os.getcwd(), dpID))
    else:
        savepath = os.path.normpath(os.path.join(savepath, dpID))

    if not os.path.isdir(savepath):
        os.makedirs(savepath)

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
