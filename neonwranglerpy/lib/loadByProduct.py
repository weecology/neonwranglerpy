import os.path
from tempfile import mkdtemp
from shutil import rmtree
from neonwranglerpy.lib.zipsByProduct import zips_by_product
from neonwranglerpy.lib.stackByTable import stack_by_table


def load_by_product(dpID,
                    site='all',
                    start_date=None,
                    end_date=None,
                    package="basic",
                    release="current",
                    path='./'):
    """
    :param path:
    :param dpID: productID
    :param site: site ID
    :param start_date:
    :param end_date:
    :param package:
    :param release:
    :return:
    """
    if package != "basic" or package != "expanded":
        print(f"{package} is not a valid package name. Package must be basic or expanded")
        return

    # TODO: add a check for correct format of product ID
    # TODO: add a check for AOP data product
    # TODO: add a check for start and end date

    args = {
        "dpID": dpID,
        "site": site,
        "start_date": start_date,
        "end_date": end_date,
        "package": package,
        "release": release
    }

    # creates a temp dir.
    tempdir = mkdtemp(dir=os.path.dirname(path))

    # pass the request to zipsByProduct() to download
    zips_by_product(dpID, site, start_date, end_date, package, release, path=tempdir)
    # stack the tables by using stackByTable\
    out = stack_by_table(filepath=tempdir)
    # removes temp dir
    rmtree(tempdir)
    return out
