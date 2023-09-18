"""Test predict_aop_data.py file."""
import pandas as pd
import os
import subprocess
from neonwranglerpy.lib.predict_aop_data import predict_aop_data

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
def test_predict_aop_data():
    """Test predict_aop_data function."""
    vst_path = os.path.normpath(os.path.join(raw_dir_files, 'vst_data.csv'))
    vst_data = pd.read_csv(vst_path)

    result = predict_aop_data(vst_data=vst_data.iloc[1:10, :], year='2018',
                              dpID='DP3.30010.001', savepath=raw_dir_files, site='DELA',
                              plot_crop=False)

    assert (vst_data.shape[0] > 0) & (vst_data.shape[1] > 0)
    assert len(result) > 0
    assert isinstance(result, pd.DataFrame)
    assert result[['xmin', 'ymin', 'xmax', 'ymax']].duplicated().any()
