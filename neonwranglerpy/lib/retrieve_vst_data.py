"""Retrieve Vegetation Structure Data from NEON."""
import os.path

import pandas as pd
from neonwranglerpy.utilities.loadByProduct import load_by_product
from neonwranglerpy.lib.retrieve_coords_itc import retrieve_coords_itc


def retrieve_vst_data(dpId="DP1.10098.001",
                      site="all",
                      start_date=None,
                      end_date=None,
                      method="shp",
                      savepath="",
                      attributes=None,
                      save_files=False,
                      stacked_df=True):
    """Retrieve Vegetation Structure Data From NEON and Add Individual ID coordinates.

    Parameters
    ------------
    dpID: str, optional
        The NEON Data Product ID to be downloaded, in the form DPL.PRNUM.REV
        e.g. DP1.10098.001.

    site : str, list, optional
        The 4 Letter NEON site code for NEON sites or 'all' for data from all sites
        e.g. DELA, ['DELA','ABBY'].

    start_date : str, optional
        Date to search data in the form YYYY-MM or None for all available dates,
        e.g. 2017-01.

    end_date : str, optional
        Date to search data in the form YYYY-MM or None for all available dates,
        e.g. 2017-01.

    method : str, optional
        Indicating which method should be used for calculating the individual trees
        location.

    savepath : str, optional
        The full path to the folder in which the files would be placed locally.

    save_files : bool, optional
        Whether to save the downloaded files after downloading them.

    stacked_df: str, optional
        Whether to return the stacked dataframes after stacking the files.
    """
    vst = load_by_product(dpId,
                          site,
                          start_date,
                          end_date,
                          path=savepath,
                          save_files=save_files,
                          stacked_df=stacked_df)
    vst_mappingandtagging = vst["vst_mappingandtagging"]
    vst_apparentindividual = vst["vst_apparentindividual"]

    if method == "shp":
        # Adds the UTM coordinates of vst entries based on azimuth and distance
        vst["vst_mappingandtagging"] = retrieve_coords_itc(vst_mappingandtagging)

    if attributes is None:
        attributes = vst_apparentindividual[[
            'uid', 'individualID', 'eventID', 'tagStatus', 'growthForm', 'plantStatus',
            'stemDiameter', 'measurementHeight', 'height', 'baseCrownHeight', 'breakHeight',
            'breakDiameter', 'maxCrownDiameter', 'ninetyCrownDiameter', 'canopyPosition',
            'shape', 'basalStemDiameter', 'basalStemDiameterMsrmntHeight',
            'maxBaseCrownDiameter', 'ninetyBaseCrownDiameter'
        ]]
    vst['vst_mappingandtagging'].rename(columns={'eventID': 'tagEventID'}, inplace=True)
    csv_vst = pd.merge(attributes,
                       vst["vst_mappingandtagging"],
                       how="left",
                       on="individualID")
    csv_vst.drop_duplicates(inplace=True)
    if save_files:
        csv_vst.to_csv(os.path.join(vst['stackedpath'], 'vst.csv'), index=False)

    return dict([('vst', csv_vst), ('raw_dat', vst)])
