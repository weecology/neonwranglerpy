"""Test extract_training_data.py file."""
import geopandas as gpd
from shapely.geometry import Point
from neonwranglerpy.lib.retrieve_vst_data import retrieve_vst_data
from neonwranglerpy.lib.extract_training_data import extract_training_data


def test_extract_training_data():
    """Test extract_training_data function."""
    savepath = 'tests/raw_data'
    vst = retrieve_vst_data('DP1.10098.001', 'DELA', "2018-01", "2022-01",
                            savepath=savepath, save_files=True, stacked_df=True)

    vst_data = vst['vst']
    columns_to_drop_na = ['plotID', 'siteID', 'utmZone', 'easting', 'northing']
    vst_data = vst_data.dropna(subset=columns_to_drop_na)

    geometry = [Point(easting, northing) for easting, northing in
                zip(vst_data['itcEasting'], vst_data['itcNorthing'])]
    epsg_codes = (vst_data['utmZone'].map(lambda x: (326 * 100) +
                                          int(x[:-1]))).astype(str)
    geo_data_frame = gpd.GeoDataFrame(vst_data, geometry=geometry, crs=epsg_codes.iloc[0])

    result = extract_training_data(vst_data.iloc[1:10, :], geo_data_frame, year='2018',
                                   dpID='DP3.30010.001', savepath=savepath, site='DELA')

    assert (vst_data.shape[0] > 0) & (vst_data.shape[1] > 0)
    assert len(result) > 0
    assert "geometry" in result.columns
    assert isinstance(result, gpd.GeoDataFrame)
    assert ~result[['xmin', 'ymin', 'xmax', 'ymax']].duplicated().any()
    assert 'Polygon' in result['geometry'].geom_type.values
