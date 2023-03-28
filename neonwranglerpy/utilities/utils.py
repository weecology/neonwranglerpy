"""Utilities functions."""
import pandas as pd
import re


def get_recent_publications(filelist):
    """Return the most recent version of file from a list of files."""
    pattern = re.compile("[0-9]{8}T[0-9]{6}Z")
    path_dates = []
    for x in filelist:
        path_dates.append(re.search(pattern, x).group())
    path_dates.sort()
    return list(filter(lambda s: path_dates[-1] in s, filelist))[0]


def get_variables(varfile):
    """Return the table, fieldName, colClass columns from variables files."""
    df = pd.read_csv(varfile)
    df["colClass"] = "numeric"
    cond = (("string" == df["dataType"]) | ("date" == df["dataType"]) |
            ("dateTime" == df["dataType"]) | ("uri" == df["dataType"]))
    df["colClass"].mask(cond, "character", inplace=True)

    if "table" in df.columns:
        return df[["table", "fieldName", "colClass"]]
    return df[["fieldName", "colClass"]]
