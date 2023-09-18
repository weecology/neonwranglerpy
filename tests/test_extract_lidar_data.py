"""Test extract_lidar_data.py file."""
import geopandas as gpd
import pandas as pd
import os
import subprocess
from neonwranglerpy.lib.extract_lidar_data import extract_lidar_data

file_location = os.path.dirname(os.path.realpath(__file__))
neonwranglerpy_root_dir = os.path.abspath(os.path.join(file_location, os.pardir))

# Paths of the raw data files used
raw_dir_files = os.path.normpath(os.path.join(neonwranglerpy_root_dir, 'raw_data'))

def setup_module():
    """Automatically sets up the environment before the module runs."""
    os.chdir(neonwranglerpy_root_dir)
    subprocess.call(['cp', '-r', 'tests/raw_data', neonwranglerpy_root_dir])


def teardown_module():
    """Automatically clean up after the module."""
    os.chdir(neonwranglerpy_root_dir)
    subprocess.call(['rm', '-r', 'raw_data'])


def setup_functions():
    """Set up functions."""
    teardown_module()
    setup_module()

def test_extract_lidar_data():
    """Test extract_lidar_data function."""
    setup_functions()
    vst_path = os.path.normpath(os.path.join(raw_dir_files, 'vst_data.csv'))
    rgb_path = os.path.normpath(os.path.join(raw_dir_files, 'dataframe.shp'))

    vst_data = pd.read_csv(vst_path)
    rgb_data = gpd.read_file(rgb_path)

    result = extract_lidar_data(rgb_data=rgb_data,
                                vst_data=vst_data,
                                year="2018",
                                savepath=raw_dir_files,
                                dpID="DP1.30003.001",
                                site="DELA")

    assert (vst_data.shape[0] > 0) & (vst_data.shape[1] > 0)
    assert len(result) > 0
