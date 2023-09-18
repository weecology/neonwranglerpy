"""Test extract_training_data.py file."""
import geopandas as gpd
import pandas as pd
from neonwranglerpy.lib.extract_training_data import extract_training_data


def test_extract_training_data():
    """Test extract_training_data function."""
    savepath = 'tests/raw_data'
    vst_data = pd.read_csv('tests/raw_data/vst_data.csv')
    vst_data = vst_data[:500]
    result = extract_training_data(vst_data=vst_data[:500], year='2018',
                                   dpID='DP3.30010.001', savepath=savepath, site='DELA')

    assert (vst_data.shape[0] > 0) & (vst_data.shape[1] > 0)
    assert len(result) > 0
    assert "geometry" in result.columns
    assert isinstance(result, gpd.GeoDataFrame)
    assert ~result[['xmin', 'ymin', 'xmax', 'ymax']].duplicated().any()
    assert 'Polygon' in result['geometry'].geom_type.values
