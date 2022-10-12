"""Clip Plots around NEON vegetation structure."""
import os
from neonwranglerpy.lib.clip_raster import clip_raster


def clip_plot(plt, list_data, bff=12, savepath=""):
    """Clip Plots around Vegetation Structure."""
    # convert the type of easting and northing to numeric
    # plt['easting'] = plt['easting'].astype(int)
    # plt['northing'] = plt['northing'].astype(int)
    # tile = plt["plt_e"].values.astype(str) + "_" + plt["plt_n"].values.astype(str)
    tiles = str(plt["plt_e"]) + "_" + str(plt["plt_n"])
    tiles = [f for f in list_data if tiles in f]
    missed_plots = []

    for tile in tiles:
        try:
            file_args = tile.split(sep='/FullSite')[1]
            file_args = file_args.split(sep='/')
            # year = file_args[1].split("_")[0]

            if ".tif" in file_args[-1]:
                # site = file_args[1].split('_')[1]
                file_name = os.path.basename(tile)
                savepath = os.path.join(savepath, file_name)
                clip_raster(plt, tile, bff, savepath)
        except Exception:
            missed_plots.append(tile)
