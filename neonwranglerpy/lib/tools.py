import re
import requests
import os
import shutil
import stat
from tempfile import mkdtemp
from datetime import datetime


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
    return datetime.strptime(date, '%Y-%m').date()


def get_month_year_urls(date, all_urls, date_type):
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


def create_temp(dst):
    if not os.path.exists(dst):
        print(f'{dst} does not exists')
        return None
    tempdir = mkdtemp(dir=dst)
    return tempdir


def get_all_files(path):
    files = []
    for dr in os.listdir(path):
        dir_path = os.path.join(path, dr)
        for file in os.listdir(dir_path):
            files.append(os.path.join(dir_path, file))
    return files


def copy_zips(src, dst, symlinks=False, ignore=None):
    """ Copies zip files to a temp dir """
    if not os.path.exists(dst):
        os.makedirs(dst)
        shutil.copystat(src, dst)
    lst = os.listdir(src)
    if ignore:
        excl = ignore(src, lst)
        lst = [x for x in lst if x not in excl]
    for item in lst:
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if symlinks and os.path.islink(s):
            if os.path.lexists(d):
                os.remove(d)
            os.symlink(os.readlink(s), d)
            try:
                st = os.lstat(s)
                mode = stat.S_IMODE(st.st_mode)
                os.lchmod(d, mode)
            except Exception as e:
                print(e)
        elif os.path.isdir(s):
            copy_zips(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)

    return