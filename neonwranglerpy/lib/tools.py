import re
import requests
import os
import shutil
from tempfile import mkdtemp
from datetime import datetime
import rpy2.robjects as robjects
from rpy2.robjects.conversion import localconverter
from rpy2.robjects import pandas2ri


def get_tables():
    """
    convert table_types.rda to table_types.csv
    """
    rda_file = robjects.r.load("table_types.rda")
    df = robjects.globalenv['table_types']
    with localconverter(robjects.default_converter + pandas2ri.converter):
        table_types_df = robjects.conversion.rpy2py(df)
    table_types_df.to_csv('neonwranglerpy/data/table_types.csv',
                          index=False,
                          columns=['productID', 'tableName', 'tableType'])
    return


def get_api(api_url, token=None):
    """
    returns the api response
    """
    try:
        response = requests.get(api_url,
                                headers={
                                    'X-API-Token': token,
                                    'accept': 'application/json'
                                })
        return response
    except Exception as e:
        print(e)

    # TODO : check for rate-limit


def get_year_month(date):
    """ returns the year-month of files"""
    return datetime.strptime(date, '%Y-%m').date()


def get_month_year_urls(date, all_urls, date_type):
    """returns the urls for files for specificed year-month"""
    date_urls = []
    pattern = re.compile('20[0-9]{2}-[0-9]{2}')
    y_m = get_year_month(date)
    for x in all_urls:
        year_month = re.search(pattern, x).group()
        a_y_m = get_year_month(year_month)
        if date_type == 'start':
            if a_y_m > y_m:
                date_urls.append(x)
        elif date_type == 'end':
            if a_y_m < y_m:
                date_urls.append(x)
    return date_urls


def get_all_files(folder_path, dir_name=False):
    """returns the list of files for a directory"""
    files = []
    if not os.path.exists(folder_path):
        print(f"{folder_path} does not exits.")
        return None

    for dr in os.listdir(folder_path):
        dir_path = os.path.join(folder_path, dr)
        for file in os.listdir(dir_path):
            if dir_name:
                all_path = os.path.join(dir_path, file)
                files.append(all_path)
            else:
                files.append(file)
    return files


def create_temp(dst):
    """ creates temporary directory"""
    if not os.path.exists(dst):
        print(f'{dst} does not exists')
        return None
    tempdir = mkdtemp(dir=dst)
    return tempdir


def copy_zips(src, dst):
    """ Copies zip files to a temp dir """
    if not os.path.exists(dst):
        os.makedirs(dst)

    lst = os.listdir(src)

    for item in lst:
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            copy_zips(s, d)
        else:
            shutil.copy2(s, d)
    return


def copy_zip(src, dst):
    """ Copies a files to dir """
    dir_path, file_name = os.path.split(dst)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    if not os.path.isfile(src):
        print('This function only works for zip or file')

    shutil.copy2(src, dst)
    return
