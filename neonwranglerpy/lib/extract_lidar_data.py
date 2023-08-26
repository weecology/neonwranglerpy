"""Function to extract lidar data using RGB data and vst data."""
import laspy
import numpy as np
import os
import re
from neonwranglerpy.lib.retrieve_aop_data import retrieve_aop_data


def extract_lidar_data(rgb_data,
                       vst_data,
                       year,
                       savepath="/content",
                       dpID="DP1.30003.001",
                       site="DELA"):
    """
    Extract LiDAR data using RGB data and vst data.

    Arguments:
    ------------
        rgb_data: GeoDataFrame containing the plot data
        vst_data: DataFrame containing the plot data
        year: Year of the data
        savepath: Path to save the data
        dpID: LiDAR data product ID
        site: Site name
    """
    retrieve_aop_data(vst_data, year, dpID, savepath)

    site_level_data = vst_data[vst_data.plotID.str.contains(site)]
    get_tiles = (((site_level_data.easting / 1000).astype(int) * 1000).astype(str) + "_" +
                 ((site_level_data.northing / 1000).astype(int) * 1000).astype(str))

    pattern = fr"{get_tiles.unique()}_classified_point_cloud.laz"

    saveFile = savepath + "/" + dpID

    filtered_data_list = []

    for root, dirs, files in os.walk(saveFile):
        for file in files:
            if re.search(pattern, file):
                lidar_file = os.path.join(root, file)
                # directory_path = os.path.dirname(lidar_file) + '/'
                file_name = os.path.basename(lidar_file)
                print(lidar_file)

                lidar = laspy.read(lidar_file)

                x = lidar.x
                y = lidar.y
                z = lidar.z

                data = np.vstack((x, y, z)).transpose()

                lidar_dir = savepath + "/data/lidar"
                os.makedirs(lidar_dir, exist_ok=True)

                for index, row in rgb_data.iterrows():
                    geometry = row['geometry']

                    minx, miny, maxx, maxy = geometry.bounds

                    filtered_data = data[(data[:, 0] >= minx) & (data[:, 0] <= maxx) &
                                         (data[:, 1] >= miny) & (data[:, 1] <= maxy)]

                    if len(filtered_data) > 0:
                        filtered_data_list.append(filtered_data)

                        filename = os.path.join(lidar_dir,
                                                f"lidar_{file_name}_{index}.npy")
                        np.save(filename, filtered_data)

                        print(f"LiDAR data for index {index} saved as '{filename}'")
                    else:
                        print(f"No LiDAR data for index {index}")

    filtered_data_array = np.concatenate(filtered_data_list, axis=0)

    return filtered_data_array
