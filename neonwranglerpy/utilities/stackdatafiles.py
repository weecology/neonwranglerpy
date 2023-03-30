"""Stack the data files according to table_types."""
import os.path
import pandas as pd
from neonwranglerpy import get_data
import neonwranglerpy.utilities.tools as tl
import neonwranglerpy.utilities.utils as ut


def load_table_types(dpID: str):
    """Return the dataframe about the table types of Data Products."""
    stream = get_data('table_types.csv')
    df = pd.read_csv(stream)
    table_types = df[df['productID'] == dpID]
    table = table_types.reset_index(drop=True)
    return table


def stackdatafiles(folder_path, dst, dpID, stack_df=False):
    """Stack the data files according to table_types."""
    if not os.path.exists(folder_path):
        print(f"{folder_path} does not exists")
        return None

    filenames = tl.get_all_files(folder_path)
    filepaths = tl.get_all_files(folder_path, dir_name=True)
    variables_list = [_ for _ in filepaths if "variables.20" in _]
    validation_list = [s for s in filepaths if "validation" in s]
    codes_list = [s for s in filepaths if "categoricalCodes" in s]
    stackedpath = os.path.join(dst, 'stackedFiles')

    # getting the table types from table_types.csv
    table_types = load_table_types(dpID)

    # getting the table types from files
    a_names = set([s.split('.')[6] for s in filenames])
    t_names = [s for s in a_names if '_' in s]
    t_filter = table_types['tableName'].isin(t_names)
    tables = table_types[t_filter]
    table_names = tables.tableName

    # copy varibles and validation files to /stackedfiles using the most
    # recent publication date
    if variables_list:
        # get most recent variable file
        varpath = ut.get_recent_publications(variables_list)
        # get variables from the files
        variables = ut.get_variables(varpath)

    if not os.path.exists(stackedpath):
        print('creating stackedFiles directory')
        os.makedirs(stackedpath)

    if validation_list:
        valpath = ut.get_recent_publications(validation_list)
        validation_dst = os.path.join(stackedpath, f"validation_{dpID}.csv")
        tl.copy_zip(valpath, validation_dst)
        print("copying the most recent publication of validation file to /stackedFiles")

    if codes_list:
        codepath = ut.get_recent_publications(codes_list)
        code_dst = os.path.join(stackedpath, f"categoricalCodes_{dpID}.csv")
        tl.copy_zip(codepath, code_dst)
        print("copying the most recent publication of categoricalCodes file to"
              "/stackedFiles")
    out = {}
    # stacking the files
    for i in range(len(table_names)):
        file_list = sorted([file for file in filepaths if table_names[i] in file])
        temp_files = []
        stacking_list = []

        if tables.tableType[i] == "site-date":
            temp_files = file_list

        if tables.tableType[i] == "site-all":
            base_files = [os.path.basename(name) for name in file_list]
            sites = set([s.split(".")[2] for s in base_files])
            for _ in sites:
                site_list = [s for s in file_list if _ in s]
                site = ut.get_recent_publications(site_list)
                temp_files.append(site)

        for _ in temp_files:
            df = pd.read_csv(_)
            stacking_list.append(df)

        stacked_df = pd.concat(stacking_list, axis=0)
        df_save_path = os.path.join(stackedpath, f"{table_names[i]}_{dpID}.csv")

        if stack_df:
            out[table_names[i]] = stacked_df
        stacked_df.to_csv(df_save_path, index=False)

    out['variables'] = variables
    out['stackedpath'] = stackedpath

    return out
