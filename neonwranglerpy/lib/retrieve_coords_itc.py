"""Get Individual ID coordinates."""
import geopandas as gp
from neonwranglerpy import get_data
from neonwranglerpy.lib.retrieve_dist_to_utm import retrieve_dist_to_utm


def load_plots():
    """Return the dataframe of the all_neon_tos_plots.shp."""
    stream = get_data('All_NEON_TOS_Plots_V9/All_NEON_TOS_Plot_Points_V9.shp')
    df = gp.read_file(stream)
    return df


def retrieve_coords_itc(dat):
    """Calcualte the coordinates for each individual tree in the vegetation structure."""
    # getting the vst columns from ALL NEON TOS Plots
    plots = load_plots()
    vst_rows = list(plots['appMods'].str.contains('vst'))
    plots_df = plots.loc[vst_rows]

    convert_dict = {
        'pointID': 'string',
    }
    # converting the pointID dtype from float to character
    plots_df = plots_df.astype({'pointID': 'Int64'}).astype(convert_dict)
    data = dat.astype({'pointID': 'Int64'}).astype(convert_dict)

    vst_df = data.merge(plots_df, how='inner', on=['plotID', 'pointID', 'siteID'])
    na_values = vst_df['stemAzimuth'].isnull().values.any()

    if na_values:
        print(
            f"{len(na_values)} entries could not be georeferenced and will be discarded.")
        vst_df.dropna(subset=['stemAzimuth'], axis=0, inplace=True)
        vst_df.reset_index(drop=True, inplace=True)
    # if retrieve_dist_to_utm doesn't work add p[0] as an extra argument to
    # retrieve_dist_to_utm function and append individualID to results
    dat_apply = vst_df[['uid', 'stemDistance', 'stemAzimuth', 'easting', 'northing']]
    coords = dat_apply.apply(lambda p: retrieve_dist_to_utm(p[0], p[1], p[2], p[3], p[4]),
                             axis=1,
                             result_type='expand')
    coords.reset_index(drop=True, inplace=True)
    coords.rename(columns={0: 'uid', 1: 'itcEasting', 2: 'itcNorthing'}, inplace=True)
    # merging the coords and vst_df dataframes, taking indivodualID as reference
    field_tag = vst_df.merge(coords, on=['uid'])
    # dropping nan itcEasting
    # na_values = np.where(field_tag['itcEasting'].isnull() == True)[0]
    field_tag.dropna(subset=['itcEasting'], axis=0, inplace=True)
    field_tag.reset_index(drop=True, inplace=True)
    return field_tag
