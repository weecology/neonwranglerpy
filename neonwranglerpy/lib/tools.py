import re
import requests


def get_api(api_url, token=None):
    """
    returns the api response
    """
    try:
        response = requests.get(
            api_url,
            headers={
                'X-API-Token': token,
                'accept': 'application/json'}
        )
        return response.json()
    except Exception as e:
        print(e)

    # TODO : check for rate-limit


def get_year_month(date):
    return int(date.split("-")[0]), int(date.split("-")[1])


def get_month_year_urls(date, all_urls, date_type):
    date_urls = []
    pattern = re.compile('20[0-9]{2}-[0-9]{2}')
    s_y, s_m = get_year_month(date)
    for x in all_urls:
        year_month = re.search(pattern, x).group()
        year, month = get_year_month(year_month)
        if date_type == 'start':
            if year >= s_y and month >= s_m:
                date_urls.append(x)
        elif date_type == 'end':
            if year <= s_y and month <= s_m:
                date_urls.append(x)
    return date_urls
