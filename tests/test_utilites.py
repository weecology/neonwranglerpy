"""Tests for neonwranglerpy.utilities Package."""
import os
import subprocess
import pytest

from neonwranglerpy.utilities.loadByProduct import load_by_product
from neonwranglerpy.utilities.tools import get_api
from neonwranglerpy.utilities import __version__
from neonwranglerpy.utilities.zipsByProduct import zips_by_product
from neonwranglerpy.utilities.utils import get_recent_publications, get_variables

# Main Paths
file_location = os.path.dirname(os.path.realpath(__file__))
neonwranglerpy_root_dir = os.path.abspath(os.path.join(file_location, os.pardir))

# Paths of the raw data files used
raw_dir_files = os.path.normpath(os.path.join(neonwranglerpy_root_dir, 'raw_data'))

# tests examples
test_urls = [
    ('test_neon_url', 'https://data.neonscience.org/api/v0/products/DP1.10098.001'),
]

test_recent_pub = [("test_get_recent_publication", [
    'NEON.D08.DELA.DP1.10098.001.variables.20220104T182335Z.csv',
    'NEON.D08.DELA.DP1.10098.001.variables.20220104T175959Z.csv'
], 'NEON.D08.DELA.DP1.10098.001.variables.20220104T182335Z.csv')]

test_loadByProduct = [
    ("VST_DELA_2021_2022", "DP1.10098.001", "DELA", "2021-01", "2022-01", [False, True], {
        'columns': [
            'uid', 'namedLocation', 'date', 'eventID', 'domainID', 'siteID', 'plotID',
            'subplotID', 'nestedSubplotID', 'pointID', 'stemDistance', 'stemAzimuth',
            'recordType', 'individualID', 'supportingStemIndividualID',
            'previouslyTaggedAs', 'samplingProtocolVersion', 'taxonID', 'scientificName',
            'taxonRank', 'identificationReferences', 'morphospeciesID',
            'morphospeciesIDRemarks', 'identificationQualifier', 'remarks', 'measuredBy',
            'recordedBy', 'dataQF'
        ],
        'data': [
            '45603b3d-ea0b-4022-a4a0-6168e6ceb647', 'DELA_046.basePlot.vst', '2015-06-08',
            'vst_DELA_2015', 'D08', 'DELA', 'DELA_046', 21.0, 2.0, 41.0, 11.1, 201.5, 0,
            'NEON.PLA.D08.DELA.04068', 0, 0, 'NEON.DOC.000987vE', 'ACRU',
            'Acer rubrum L.', 'species', 0, 0, 0, 0, 0, 'mwiegmann@neoninc.org',
            'calvis@field-ops.org', 0
        ]
    }),
]

test_checks = [
    ("DPID_CHECK", "DP1.1098.001", "DELA", "2021-01", "2022-01", [False, True],
     'not a properly formatted data product ID'),
    ("AOP_PRODUCT_CHECK", "DP3.30005.006", "DELA", "2021-01", "2022-01", [False, True],
     'remote sensing data product and cannot be loaded'),
    ("START_DATE_CHECK", "DP1.10098.001", "DELA", "202-01", "2022-01", [False, True],
     'startdate and enddate must be either NA or valid dates'),
    ("END_DATE_CHECK", "DP1.10098.001", "DELA", "2021-01", "202-01", [False, True],
     'startdate and enddate must be either NA or valid dates'),
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


def test_version():
    """Test import version."""
    assert __version__.startswith("v")


@pytest.mark.parametrize("test_name, url", test_urls)
def test_get_api(test_name, url):
    """Test get_api function."""
    assert get_api(url).status_code == 200


@pytest.mark.parametrize("test_name, file_list, expected", test_recent_pub)
def test_get_recent_publications(test_name, file_list, expected):
    """Test get_recent_publications function."""
    re_pub = get_recent_publications(file_list)
    assert re_pub == expected


@pytest.mark.parametrize("test_name, dpID, site, start_date, end_date, args, expected",
                         test_loadByProduct)
def test_load_by_product(test_name, dpID, site, start_date, end_date, args, expected):
    setup_functions()
    path = raw_dir_files
    save_files = args[0]
    stacked_df = args[1]
    data_frame = load_by_product(dpID,
                                 site,
                                 start_date,
                                 end_date,
                                 path=path,
                                 save_files=save_files,
                                 stacked_df=stacked_df)
    print(data_frame.keys())
    columns_values = list(data_frame['vst_mappingandtagging'].dtypes.index)
    first_row_data = list(data_frame['vst_mappingandtagging'].fillna(0).iloc[0])

    assert columns_values == expected['columns']
    assert first_row_data == expected['data']


@pytest.mark.parametrize("test_name, dpID, site, start_date, end_date, args, expected",
                         test_checks)
def test_load_by_product_checks(test_name, dpID, site, start_date, end_date, args,
                                expected):
    setup_functions()
    path = raw_dir_files
    save_files = args[0]
    stacked_df = args[1]
    out = load_by_product(dpID,
                          site,
                          start_date,
                          end_date,
                          path=path,
                          save_files=save_files,
                          stacked_df=stacked_df)
    assert expected in out


@pytest.mark.parametrize("test_name, dpID, site, start_date, end_date, args, expected",
                         test_checks)
def test_zips_by_product_checks(test_name, dpID, site, start_date, end_date, args,
                                expected):
    setup_functions()
    path = raw_dir_files
    out = zips_by_product(dpID, site, start_date, end_date, savepath=path)
    assert expected in out
