"""Tools functions."""
import re
import requests
import os
import shutil
from tempfile import mkdtemp
from datetime import datetime
from neonwranglerpy import get_data


def get_api(api_url, token=None):
    """Return the api response."""
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
    """Return the year-month of files."""
    return datetime.strptime(date, '%Y-%m').date()


def get_month_year_urls(date, all_urls, date_type):
    """Return the urls for files for specificed year-month."""
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
    """Return the list of files for a directory."""
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
    """Create temporary directory."""
    if not os.path.exists(dst):
        print(f'{dst} does not exists')
        return None
    tempdir = mkdtemp(dir=dst)
    return tempdir


def copy_zips(src, dst):
    """Copy zip files to a temp dir."""
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
    """Copy a files to directory."""
    dir_path, file_name = os.path.split(dst)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    if not os.path.isfile(src):
        print('This function only works for zip or file')

    shutil.copy2(src, dst)
    return
