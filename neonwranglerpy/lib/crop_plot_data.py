"""Create a shapefile out of vegetation structure data with lat/lon coordinates."""
from glob import glob
import pandas as pd
import numpy as np

from neonwranglerpy.lib.clip_plot import clip_plot


def list_files(path):
    """List all the files in a path of given format."""
    mask = path + '**/*.[th][i5][f ]'
    files = glob(mask, recursive=True)
    return files


def crop_data_to_plot(plt,
                      dpID='DP3.30006.001',
                      path="",
                      target_year=2018,
                      bff=520,
                      tasks=1,
                      parallelized=False):
    """Create shapefiles out of a vegetation structure data with lat/lon coordinates."""
    full_files = list_files(path)
    files = [file for file in full_files if dpID in file]
    files = [file for file in files if str(target_year) in file]

    # TODO: add check if files for targeted year and product is not present
    plots = plt[['plotID', 'subplotID', 'siteID', 'utmZone', 'easting', 'northing']]

    plots = plots.groupby(['plotID', 'subplotID', 'siteID',
                           'utmZone']).mean().reset_index()
    drop_subset = ['siteID', 'plotID', 'subplotID', 'utmZone', 'easting', 'northing']
    plots = plots.drop_duplicates(subset=drop_subset).reset_index(drop=True)
    plots.dropna(axis=0, how='any', inplace=True)
    plots['plt_e'] = (plots[['easting']] / 1000).astype(int) * 1000
    plots['plt_n'] = (plots[['northing']] / 1000).astype(int) * 1000

    plots["check_e"] = (plots["easting"] - plots['plt_e']).apply(np.floor)
    plots["check_n"] = (plots["northing"] - plots['plt_n']).apply(np.floor)

    tile_ep = plots.loc[plots['check_e'] < bff]
    tile_ep.loc[:, ['plt_e']] = tile_ep['plt_e'] - 1000
    tile_ep.loc[:, ['plotID']] = tile_ep['plotID'] + 'pl'
    tile_ep.loc[:, ['easting']] = tile_ep['easting'] - bff - tile_ep['check_e']

    tile_em = plots.loc[plots['check_e'] > 1000 - bff]
    tile_em.loc[:, ['plt_e']] = tile_em['plt_e'] + 1000
    tile_em.loc[:, ['plotID']] = tile_em['plotID'] + 'mn'
    tile_em.loc[:, ['easting']] = tile_em['easting'] + bff - tile_em['check_e'] + 1000

    tile_np = plots.loc[plots['check_n'] < bff]
    tile_np.loc[:, ['plt_n']] = tile_np['plt_n'] - 1000
    tile_np.loc[:, ['plotID']] = tile_np['plotID'] + 'pl'
    tile_np.loc[:, ['northing']] = tile_np['northing'] - bff - tile_np['check_n']

    tile_nm = plots.loc[plots['check_n'] > 1000 - bff]
    tile_nm.loc[:, ['plt_n']] = tile_nm['plt_n'] + 1000
    tile_nm.loc[:, ['plotID']] = tile_nm['plotID'] + 'mn'
    tile_nm.loc[:, ['northing']] = tile_nm['northing'] - bff - tile_nm['check_n']

    plots.loc[:, ['easting']] = plots['plt_e'] + np.maximum(bff, plots['check_e'])
    plots.loc[:, ['northing']] = plots['plt_n'] + np.maximum(bff, plots['check_n'])

    # get borders
    border_e = (plots.loc[plots['check_e'] > 1000 - bff, 'easting'] / 1000).apply(
        np.floor) * 1000
    plots.loc[plots['check_e'] > 1000 - bff, ["easting"]] = border_e + 1000 - bff

    border_n = (plots.loc[plots['check_n'] > 1000 - bff, 'northing'] / 1000).apply(
        np.floor) * 1000
    plots.loc[plots['check_n'] > 1000 - bff, ["northing"]] = border_n + 1000 - bff

    plots = pd.concat([plots, tile_ep, tile_em, tile_np, tile_nm]).reset_index(drop=True)
    # list_data = [site for site in plots['siteID'].unique().tolist() if site in files]
    files_list = []
    sites = plots['siteID'].unique().tolist()
    for site in sites:
        list_data = [file for file in files if site in file]
        files_list.extend(list_data)

    plots = plots.apply(lambda p: clip_plot(p, list_data), axis=1, result_type='expand')
