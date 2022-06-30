
import string
from ark_wrapper import Ark
from cnbc_article_parser import get_article_data, get_article_html
from lookup_ticker import lookup_ticker


def parse_cnbc_article(url):
    html = get_article_html(url)
    return get_article_data(html)


def get_ark_tickers(fund='ARKK'):
    ark = Ark()
    holdings = ark.get_etf_holdings(fund)
    tickers = []
    for holding in holdings['holdings']:
        ticker = holding.get('ticker')
        if ticker is not None:
            tickers.append(ticker)

    return tickers


def get_all_ark_holdings():
    funds = ['ARKK', 'ARKW', 'ARKQ', 'ARKG',
             'ARKF', 'ARKX', 'PRNT', 'IZRL', 'CTRU']
    invalid_chars = string.punctuation + string.whitespace + string.digits
    tickers = []
    print('Getting ARK Holdings', end='')
    for fund in funds:
        print('.', end='')
        tickers += get_ark_tickers(fund)
    print('')
    print('Filtering and sorting')
    # remove duplicates
    tickers = list(set(tickers))
    filtered_tickers = []
    for ticker in tickers:
        if any(digit in ticker for digit in invalid_chars):
            continue
        filtered_tickers.append(ticker)
    filtered_tickers.sort()
    print('Done')
    return filtered_tickers


if __name__ == '__main__':

    print(get_all_ark_holdings())
