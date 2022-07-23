import os
import requests
from dotenv import load_dotenv

load_dotenv()

ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

URL = 'https://www.alphavantage.co/query'


def lookup_ticker(query: str, region: str = 'United States') -> str | None:
    '''
    Lookup a ticker on Alpha Vantage
    '''
    query_params = {
        'function': 'SYMBOL_SEARCH',
        'keywords': query,
        'apikey': ALPHA_VANTAGE_API_KEY,
    }
    response = requests.get(URL, params=query_params)
    response.raise_for_status()
    data = response.json()
    for ticker in data['bestMatches']:
        if ticker['4. region'] == region:
            return ticker['1. symbol']
    return None


if __name__ == '__main__':

    print(lookup_ticker('Apple'))
