"""Extract training data from NEON AOP data."""
import geopandas as gpd
import os
import re
from shapely.geometry import box
from shapely.geometry import Point
import numpy as np
import pandas as pd
import torch
import rasterio
from deepforest import main
from deepforest import utilities
from neonwranglerpy.lib.clip_raster import mask_raster
from neonwranglerpy.lib.retrieve_aop_data import retrieve_aop_data


def extract_training_data(vst_data,
                          year,
                          dpID='DP3.30010.001',
                          savepath='/content',
                          site='DELA'):
    """
    Extract training data with geo_data_frame and image predictions.

    Parameters
    ------------
    savepath = '/content'
    vst = retrieve_vst_data('DP1.10098.001', 'DELA', "2018-01", "2022-01",
                            savepath=savepath, save_files=True, stacked_df=True)

    vst_data = vst['vst']
    columns_to_drop_na = ['plotID', 'siteID', 'utmZone', 'easting', 'northing']
    vst_data = vst_data.dropna(subset=columns_to_drop_na)
    """
    retrieve_aop_data(vst_data, year, dpID, savepath)
    geometry = [
        Point(easting, northing)
        for easting, northing in zip(vst_data['itcEasting'], vst_data['itcNorthing'])
    ]
    epsg_codes = (
        vst_data['utmZone'].map(lambda x: (326 * 100) + int(x[:-1]))).astype(str)
    geo_data_frame = gpd.GeoDataFrame(vst_data, geometry=geometry, crs=epsg_codes.iloc[0])
    site_level_data = vst_data[vst_data.plotID.str.contains(site)]
    get_tiles = (((site_level_data.easting / 1000).astype(int) * 1000).astype(str) + "_" +
                 ((site_level_data.northing / 1000).astype(int) * 1000).astype(str))
    print("get_tiles")
    print(get_tiles.unique())

    pattern = fr"{year}_{site}_.*_{get_tiles.unique()[0]}"

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model = main.deepforest()
    model.use_release()

    model.to(device)

    all_predictions = []

    directory_path = ""

    for root, dirs, files in os.walk(savepath):
        for file in files:
            if re.match(pattern, file):
                image_file = os.path.join(root, file)
                directory_path = os.path.dirname(image_file) + '/'
                print(image_file)

                predictions = model.predict_tile(image_file,
                                                 return_plot=False,
                                                 patch_size=300,
                                                 patch_overlap=0.05)

                gdf = utilities.boxes_to_shapefile(predictions,
                                                   root_dir=os.path.dirname(image_file),
                                                   projected=True)

                all_predictions.append(gdf)

    all_predictions_df = pd.concat(all_predictions)

    merged_data = gpd.sjoin(all_predictions_df, geo_data_frame, how="inner")

    canopy_position_mapping = {
        np.nan: 0,
        'Full shade': 1,
        'Mostly shaded': 2,
        'Partially shaded': 3,
        'Full sun': 4,
        'Open grown': 5
    }

    predictions = merged_data

    predictions_copy = predictions.copy()

    cp = 'canopyPosition'

    predictions_copy[cp] = predictions_copy[cp].replace(canopy_position_mapping)

    duplicate_mask = predictions_copy.duplicated(subset=['xmin', 'ymin', 'xmax', 'ymax'],
                                                 keep=False)

    duplicate_entries = predictions[duplicate_mask]

    print(duplicate_entries)

    predictions_sorted = predictions.sort_values(by=['height', cp, 'stemDiameter'],
                                                 ascending=[False, False, False])

    duplicates_mask = predictions_sorted.duplicated(
        subset=['xmin', 'ymin', 'xmax', 'ymax'], keep='first')

    clean_predictions = predictions_sorted[~duplicates_mask]

    # destination_root = "/data/rgb"

    for index, row in merged_data.iterrows():
        plant_status = row['plantStatus']
        image_path = directory_path + row['image_path']
        geometry = row['geometry']

        with rasterio.open(image_path) as dataset:
            affine = dataset.transform

            print(affine)
            print("bbox", geometry.bounds)

            bbox = box(geometry.bounds[0], geometry.bounds[1], geometry.bounds[2],
                       geometry.bounds[3])

            print("bbox", bbox)

            dat = rasterio.open(image_path)
            # creates mask and clips raster
            out_img, out_meta = mask_raster(dat, bbox)

            destination_folder = os.path.join(savepath, "data", "rgb")
            os.makedirs(destination_folder, exist_ok=True)

            new_image_path = os.path.join(destination_folder,
                                          f"{plant_status}_tree_{index}.tif")

            with rasterio.open(new_image_path, "w", **out_meta) as dest:
                dest.write(out_img)

            print(f"Tree image {index} saved as '{new_image_path}'")

    return clean_predictions
