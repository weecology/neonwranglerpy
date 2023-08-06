import geopandas as gpd
import cv2
import os
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import Point
import rasterio
from deepforest import main
from deepforest import utilities
from neonwranglerpy.lib.retrieve_aop_data import retrieve_aop_data


def extract_training_data(vst_data,
                          geo_data_frame,
                     year, dpID='DP3.30010.001',
                     savepath='/content',
                     site='DELA'):
    """
    Extracting training data with geo_data_frame and image predictions.

    Parameters
    ------------
    savepath = '/content'
    vst = retrieve_vst_data('DP1.10098.001', 'DELA', "2018-01", "2022-01",
                            savepath=savepath, save_files=True, stacked_df=True)

    vst_data = vst['vst']
    columns_to_drop_na = ['plotID', 'siteID', 'utmZone', 'easting', 'northing']
    vst_data = vst_data.dropna(subset=columns_to_drop_na)
    vst_data.iloc[1:10, :]

    geometry = [Point(easting, northing) for easting, northing in
                zip(vst_data['itcEasting'], vst_data['itcNorthing'])]
    epsg_codes = (vst_data['utmZone'].map(lambda x: (326 * 100) +
                                        int(x[:-1]))).astype(str)
    geo_data_frame = gpd.GeoDataFrame(vst_data, geometry=geometry, crs=epsg_codes.iloc[0])

    extract_training_data(vst_data=vst_data, geo_data_frame=geo_data_frame, year='2018', dpID='DP3.30010.001',
                    savepath='/content', site='DELA')
    """
    retrieve_aop_data(vst_data, year, dpID, savepath)
    site_level_data = vst_data[vst_data.plotID.str.contains(site)]
    get_tiles = ((site_level_data.easting/1000).astype(int) * 1000).astype(str) + "_" + ((site_level_data.northing/1000).astype(int) * 1000).astype(str)
    print("get_tiles")
    print(get_tiles.unique())

    pattern = fr"{year}_{site}_.*_{get_tiles.unique()[0]}"

    model = main.deepforest()
    model.use_release()

    all_predictions = []

    section_files = {}

    for root, dirs, files in os.walk(savepath):
        for file in files:
            if re.match(pattern, file):
                image_file = os.path.join(root, file)
                print(image_file)

                # Load the image using OpenCV
                image = cv2.imread(image_file)

                affine = None

                # Open the raster file
                with rasterio.open(image_file) as src:
                    # Get the bounding box coordinates
                    affine = src.transform

                    ras_extent = str(int(affine[2])) + "_" + str(int(affine[5]))

                    print(affine)

                    row = site_level_data.loc[get_tiles == ras_extent]
                    row

                    output_folder = os.path.join(savepath, "data", "rgb")
                    os.makedirs(output_folder, exist_ok=True)

                    for _, row in vst_data.iterrows():
                        easting = row.easting
                        northing = row.northing

                        x_min = int(affine[2] + 10/affine[0] - easting)
                        y_min = int(affine[5] + 10/affine[0] - northing)
                        x_max = int(affine[2] - 10/affine[0] - easting)
                        y_max = int(affine[5] - 10/affine[0] - northing)

                        section_file = os.path.join(output_folder, f"section_{x_min}_{y_min}_{x_max}_{y_max}.tif")


                        if section_file not in section_files:

                          section = image[y_max:y_min, x_max:x_min, :]
                          print("Section shape:", section.shape)

                          section_meta = src.meta.copy()
                          section_meta['width'], section_meta['height'] = (affine[2] + x_min) - (affine[2] + x_max), (affine[5] + y_min) - (affine[5] + y_max)
                          section_meta['transform'] = rasterio.Affine(affine[0], 0, (affine[2] - x_min), 0, affine[4], (affine[5] - y_min))


                          section_np = np.moveaxis(section, -1, 0)

                          with rasterio.open(section_file, 'w', **section_meta) as dst:
                              dst.write(section_np)
                              section_affine = dst.transform

                          section_files[section_file] = section_affine

                          print("Crop affine: ")
                          print(section_affine)

                          print("Expected file path:", section_file)

                        prediction = model.predict_image(path=section_file)

                        gdf = utilities.boxes_to_shapefile(prediction, root_dir=os.path.dirname(section_file), projected=True)

                        all_predictions.append(gdf)

    all_predictions_df = pd.concat(all_predictions)

    merged_data = gpd.sjoin(geo_data_frame, all_predictions_df, how="inner", op="within")


    return merged_data
