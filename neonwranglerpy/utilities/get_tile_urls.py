"""Get tile_urls, size, name"""

from neonwranglerpy.utilities.tools import get_api


def get_tile_urls(month_url, easting, northing, ):
    """Get tile urls"""
    file_urls = []
    for i in range(len(month_url)):
        temp = get_api(month_url[i]).json()

        if not len(temp):
            print(f"No files found for site {temp['data']['siteCode']} and year {temp['data']['month']}.")
            continue

        temp_ = temp['data']['files']
        # temp_ = json.dumps(temp['data']['files'])
        # df = pd.read_json(temp_)
        # # get the files for easting and northing
        for j in range(len(easting)):
            urls = [x for x in temp_ if f'_{easting[j]}_{northing[j]}' in x['name']]

            #     df1 = df.loc[df['name'].str.contains(str(easting[j]))]
            #     df2 = df.loc[df['name'].str.contains(str(northing[j]))]
            #     s1 = pd.merge(df1, df2, how='inner')
            #
            #     if not s1.shape[0] :
            #         print(f"no tiles found for {easting[j]} and {northing[j]}")

            if not len(urls):
                print(f"no tiles found for {easting[j]} and {northing[j]}")
            file_urls.extend(urls)
    print(f'{len(file_urls)} files found')
    return file_urls
