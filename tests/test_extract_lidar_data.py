"""Test extract_lidar_data.py file."""
import geopandas as gpd
import pandas as pd
from neonwranglerpy.lib.extract_lidar_data import extract_lidar_data


def test_extract_lidar_data():
    """Test extract_lidar_data function."""
    savepath = 'tests/raw_data'
    vst_data = pd.read_csv('tests/raw_data/vst_data.csv')

    rgb_data = gpd.read_file("tests/raw_data/dataframe.shp")

    result = extract_lidar_data(rgb_data=rgb_data,
                                vst_data=vst_data,
                                year="2018",
                                savepath=savepath,
                                dpID="DP1.30003.001",
                                site="DELA")

    assert (vst_data.shape[0] > 0) & (vst_data.shape[1] > 0)
    assert len(result) > 0
