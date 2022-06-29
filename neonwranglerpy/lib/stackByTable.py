import pandas as pd
import numpy as np
from os import path

def stack_by_table(filepath="./stack", savepath=".", dpID=None, package=None):

    if not path.exists(filepath):
        return f"{filepath} doesn't exists "


    # TODO: add check for data should be stacked
    # TODO: add check for dpID and Package of files
