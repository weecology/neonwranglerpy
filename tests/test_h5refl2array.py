import unittest
import numpy as np
import subprocess
import os
import pytest

from neonwranglerpy.lib.extract_hsi_to_tif import h5refl2array

# Main Paths
file_location = os.path.dirname(os.path.realpath(__file__))
neonwranglerpy_root_dir = os.path.abspath(os.path.join(file_location, os.pardir))

# Paths of the raw data files used
raw_dir_files = os.path.normpath(os.path.join(neonwranglerpy_root_dir, 'raw_data'))

test_reflection2array_data = [
    ('test_reflection2array', "h5_data/DP3.30006.001/2017/FullSite/D16/2017_ABBY_1/L3/Spectrometer/Reflectance"
                              "/NEON_D16_ABBY_DP3_559000_5070000_reflectance.h5")
]


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


@pytest.mark.parametrize("test_name, path", test_reflection2array_data)
def test_reflection2array(test_name, path):
    setup_functions()
    path = os.path.join(raw_dir_files, path)
    reflArray, metadata, sol_az, sol_zn, sns_az, sns_zn = h5refl2array(path)

    # Test the type of the returned objects
    assert (isinstance(reflArray, np.ndarray))
    assert (isinstance(metadata, dict))
    assert (isinstance(sol_az,  np.ndarray))
    assert (isinstance(sol_zn,  np.ndarray))
    assert (isinstance(sns_az, np.ndarray))
    assert (isinstance(sns_zn, np.ndarray))
