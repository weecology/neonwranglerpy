"""Test predict_aop_data.py file."""
import pandas as pd
from neonwranglerpy.lib.predict_aop_data import predict_aop_data


def test_predict_aop_data():
    """Test predict_aop_data function."""
    savepath = 'tests/raw_data'
    vst_data = pd.read_csv('tests/raw_data/vst_data.csv')

    result = predict_aop_data(vst_data=vst_data.iloc[1:10, :], year='2018',
                              dpID='DP3.30010.001', savepath=savepath, site='DELA',
                              plot_crop=False)

    assert (vst_data.shape[0] > 0) & (vst_data.shape[1] > 0)
    assert len(result) > 0
    assert isinstance(result, pd.DataFrame)
    assert result[['xmin', 'ymin', 'xmax', 'ymax']].duplicated().any()
