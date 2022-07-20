import pandas as pd
import re


def get_recent_publications(filelist):
    # TODO : add some checks
    pattern = re.compile("[0-9]{8}T[0-9]{6}Z")
    path_dates = []
    for x in filelist:
        path_dates.append(re.search(pattern, x).group())
    path_dates.sort()
    return list(filter(lambda s: path_dates[-1] in s, filelist))[0]


def get_variables(varfile):
    df = pd.read_csv(varfile)
    df['colClass'] = 'numeric'
    cond = ("string" == df['dataType']) | \
           ("date" == df['dataType']) | \
           ("dateTime" == df['dataType']) | \
           ("uri" == df['dataType'])
    df['colClass'].mask(cond, 'character', inplace=True)

    if 'table' in df.columns:
        return df[['table', 'fieldName', 'colClass']]

    return df[['fieldName', 'colClass']]
    # take out "