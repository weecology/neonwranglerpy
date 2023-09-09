"""Get tile_urls, size, name."""

from neonwranglerpy.utilities.tools import get_api
import numpy as np


def get_tile_urls(
    month_url,
    easting,
    northing,
):
    """Get tile urls."""
    file_urls = []
    for i in range(len(month_url)):
        temp = get_api(month_url[i]).json()['data']

        if not len(temp):
            print(f"No files found for site {temp['data']['siteCode']} and "
                  f"year {temp['data']['month']}.")
            continue

        temp_ = temp['files']
        dataSiteMonth = {
            "data": {
                "productCode": temp['productCode'],
                "siteCode": temp['siteCode'],
                "month": temp['month'],
                "release": temp['release'],
                "packages": temp['packages'],
                "files": []
            }
        }

        if isinstance(easting.astype(str), str) and isinstance(northing.astype(str), str):
            dataSiteMonth['data']['files'] = [x for x in temp_ if f'_{easting}_{northing}' in x['name']]
            file_urls.append(dataSiteMonth)

        elif isinstance(easting, np.ndarray) and isinstance(northing, np.ndarray):
            for j in range(len(easting)):
                urls = [
                    x for x in temp_
                    if f'_{easting.iloc[j]}_{northing.iloc[j]}' in x['name']
                ]

                #     df1 = df.loc[df['name'].str.contains(str(easting[j]))]
                #     df2 = df.loc[df['name'].str.contains(str(northing[j]))]
                #     s1 = pd.merge(df1, df2, how='inner')
                #
                #     if not s1.shape[0] :
                #         print(f"no tiles found for {easting[j]} and {northing[j]}")

                if not len(urls):
                    print(f"no tiles found for {easting[j]} and {northing[j]}")
                dataSiteMonth['data']['files'].append(urls)
            file_urls.append(dataSiteMonth)

    print(f'{len(file_urls)} files found')
    return file_urls
