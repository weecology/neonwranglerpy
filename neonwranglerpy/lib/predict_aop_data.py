"""Download data using retrive_aop_data and predict the tiles using deepforest model."""
import geopandas as gpd
import cv2
import os
import re
import matplotlib.pyplot as plt
from shapely.geometry import Point
import rasterio
from deepforest import main
from neonwranglerpy.lib.retrieve_aop_data import retrieve_aop_data


def predict_aop_data(vst_data,
                     year, dpID='DP3.30010.001',
                     savepath='/content',
                     site='DELA',
                     plot_crop=True):
    """
    Download the dataframe using retrive_vst_data function.

    Parameters
    ------------
    savepath = '/content'
    vst = retrieve_vst_data('DP1.10098.001', 'DELA', "2018-01", "2022-01",
                            savepath=savepath, save_files=True, stacked_df=True)

    vst_data = vst['vst']
    columns_to_drop_na = ['plotID', 'siteID', 'utmZone', 'easting', 'northing']
    vst_data = vst_data.dropna(subset=columns_to_drop_na)
    vst_data.iloc[1:10, :]

    predict_aop_data(vst_data=vst_data, year='2018', dpID='DP3.30010.001',
                    savepath='/content', site='DELA')
    """
    retrieve_aop_data(vst_data, year, dpID, savepath)
    geometry = [Point(easting, northing) for easting, northing in
                zip(vst_data['easting'], vst_data['northing'])]
    epsg_codes = (vst_data['utmZone'].map(lambda x: (326 * 100) +
                                          int(x[:-1]))).astype(str)
    geo_data_frame = gpd.GeoDataFrame(vst_data, geometry=geometry, crs=epsg_codes.iloc[0])
    site_level_data = vst_data[vst_data.plotID.str.contains(site)]
    get_tiles = ((site_level_data.easting/1000).astype(int) * 1000).astype(str) + "_"
    + ((site_level_data.northing/1000).astype(int) * 1000).astype(str)
    print(get_tiles.unique())

    pattern = fr"{year}_{site}_.*_{get_tiles.unique()[0]}"

    for root, dirs, files in os.walk(savepath):
        for file in files:
            if re.match(pattern, file):
                image_file = os.path.join(root, file)
                print(image_file)

                # Load the image using OpenCV
                image = cv2.imread(image_file)

                print(geo_data_frame)

                # Open the raster file
                with rasterio.open(image_file) as src:
                    # Get the bounding box coordinates
                    affine = src.transform

                    ras_extent = str(int(affine[2])) + "_" + str(int(affine[5]) - 1000)

                    print(affine)

                    row = site_level_data.loc[get_tiles == ras_extent]
                    row

                    for _, row in vst_data.iterrows():
                        easting = row.easting
                        northing = row.northing

                        x_min = int(affine[2] + 10/affine[0] - easting)
                        y_min = int(affine[5] + 10/affine[0] - northing)
                        x_max = int(affine[2] - 10/affine[0] - easting)
                        y_max = int(affine[5] - 10/affine[0] - northing)

                        print(x_min, y_min, x_max, y_max)
                        section = image[y_max:y_min, x_max:x_min, :]
                        section.shape

                        model = main.deepforest()
                        model.use_release()
                        prediction = model.predict_image(section, return_plot=plot_crop)
                        if plot_crop is True:
                            plt.imshow(prediction)
                            plt.axis('off')
                            plt.show()

    return prediction
