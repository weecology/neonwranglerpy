"""Tests the neonwrangler.lib package."""
import os
import subprocess
import pytest

from neonwranglerpy.lib.retrieve_vst_data import retrieve_vst_data

# Main Paths
file_location = os.path.dirname(os.path.realpath(__file__))
neonwranglerpy_root_dir = os.path.abspath(os.path.join(file_location, os.pardir))

# Paths of the raw data files used
raw_dir_files = os.path.normpath(os.path.join(neonwranglerpy_root_dir, 'raw_data'))

test_retrieve_vst = [('VST_DELA', 'DP1.10098.001', 'DELA', '2021-01', '2022-01', [
    True, True
], {
    'cols': [
        'uid_x', 'individualID', 'eventID', 'tagStatus', 'growthForm', 'plantStatus',
        'stemDiameter', 'measurementHeight', 'height', 'baseCrownHeight', 'breakHeight',
        'breakDiameter', 'maxCrownDiameter', 'ninetyCrownDiameter', 'canopyPosition',
        'shape', 'basalStemDiameter', 'basalStemDiameterMsrmntHeight',
        'maxBaseCrownDiameter', 'ninetyBaseCrownDiameter', 'uid_y', 'namedLocation',
        'date', 'tagEventID', 'domainID', 'siteID', 'plotID', 'subplotID',
        'nestedSubplotID', 'pointID', 'stemDistance', 'stemAzimuth', 'recordType',
        'supportingStemIndividualID', 'previouslyTaggedAs', 'samplingProtocolVersion',
        'taxonID', 'scientificName', 'taxonRank', 'identificationReferences',
        'morphospeciesID', 'morphospeciesIDRemarks', 'identificationQualifier', 'remarks',
        'measuredBy', 'recordedBy', 'dataQF', 'plotType', 'subtype', 'latitude',
        'longitude', 'datum', 'utmZone', 'easting', 'northing', 'horzUncert', 'crdSource',
        'elevation', 'vertUncert', 'nlcdClass', 'appMods', 'geometry', 'itcEasting',
        'itcNorthing'
    ],
    'data':['09af9259-e01e-4a08-9f77-236c3d205ab4', 'NEON.PLA.D08.DELA.04240', 'vst_DELA_2021', 'ok', 'single bole tree', 'Live', 21.7, 130.0, 17.6, 0, 0, 0, 8.3, 7.6, 'Full sun', 0, 0, 0, 0, 0, 'd83b1872-e247-4439-be37-2727c2c22ad4', 'DELA_053.basePlot.vst', '2015-09-15', 'vst_DELA_2015', 'D08', 'DELA', 'DELA_053', 39.0, 0, '59', 4.8, 185.8, 0, 0, 0, 'NEON.DOC.000987vE', 'FRPE', 'Fraxinus pennsylvanica Marshall', 'species', 0, 0, 0, 'cf. species', 0, 'mrichards@field-ops.org', 'hshirley@field-ops.org', 0, 'tower', 'basePlot', 32.537652, -87.804167, 'WGS84', '16N', 424487.656, 3600317.947, 0.12, 'GeoXH 6000', 27.96, 0.13, 'deciduousForest', 'bbc|cdw|cfc|dhp|hbp|ltr|vst' ]})]


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


@pytest.mark.parametrize("test_name, dpID, site, start_date, end_date, args, expected",
                         test_retrieve_vst)
def test_retrieve_vst_data(test_name, dpID, site, start_date, end_date, args, expected):
    """Tests retrieve_vst_data function."""
    setup_functions()
    path = raw_dir_files
    save_files = args[0]
    stacked_df = args[1]
    data_frame = retrieve_vst_data(dpID,
                                   site,
                                   start_date,
                                   end_date,
                                   savepath=path,
                                   save_files=save_files,
                                   stacked_df=stacked_df)
    columns_values = list(data_frame['vst'].dtypes.index)
    first_row_data = list(data_frame['vst'].iloc[0, :-3].fillna(0))
    assert columns_values == expected['cols']
    assert first_row_data == expected['data']
