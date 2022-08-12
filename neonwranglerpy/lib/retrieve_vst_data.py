"""Retrieve Vegetation Structure Data from NEON."""
import os.path

import pandas as pd
from neonwranglerpy.utilities.loadByProduct import load_by_product
from neonwranglerpy.lib.retrieve_coords_itc import retrieve_coords_itc


def retrieve_vst_data(dpId="DP1.10098.001",
                      site="all",
                      start_date="",
                      end_date="",
                      method="shp",
                      savepath="",
                      save_files=False,
                      stacked_df=False):
    """Retrieve Vegetation Structure Data From NEON and Add Individual ID coordinates."""
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
    if len(savepath):
        csv_vst.to_csv(os.path.join(vst['stackedpath'], 'vst.csv'), index=False)

    return dict([('vst', csv_vst), ('raw_dat', vst)])
