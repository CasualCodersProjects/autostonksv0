import requests
import arrow


class Ark:
    def __init__ (self, BASE_URL='https://arkfunds.io/api', VERSION='v2'):
        self.BASE_URL = BASE_URL
        self.VERSION = VERSION
        self.API_URL = BASE_URL + '/' + VERSION

    def get_etf_trades(self, symbol, start_date=None, end_date=None, limit=None):
        if start_date is None:
            start_date = arrow.utcnow().shift(days=-1).format('YYYY-MM-DD')
        if end_date is None:
            end_date = arrow.utcnow().format('YYYY-MM-DD')
        if limit is None:
            limit = 100
        url = self.API_URL + '/etf/trades'
        params = {'symbol': symbol, 'start_date': start_date, 'end_date': end_date, 'limit': limit}
        r = requests.get(url, params=params)
        return r.json()

    def get_etf_holdings(self, symbol, start_date=None, end_date=None, limit=None):
        if start_date is None:
            start_date = arrow.utcnow().shift(days=-1).format('YYYY-MM-DD')
        if end_date is None:
            end_date = arrow.utcnow().format('YYYY-MM-DD')
        if limit is None:
            limit = 100
        url = self.API_URL + '/etf/holdings'
        params = {'symbol': symbol, 'start_date': start_date, 'end_date': end_date, 'limit': limit}
        r = requests.get(url, params=params)
        return r.json()

if __name__ == '__main__':
    ark = Ark()
    print(ark.get_etf_holdings('PRNT'))
    print(ark.get_etf_trades('ARKW'))

''' Output of ETF trades:
{
  "symbol": "ARKK",
  "date_from": "2021-10-08",
  "date_to": "2021-10-08",
  "trades": [
    {
      "fund": "ARKK",
      "date": "2021-10-08",
      "ticker": "NTLA",
      "company": "INTELLIA THERAPEUTICS INC",
      "direction": "Buy",
      "cusip": "45826J105",
      "shares": 269179,
      "etf_percent": 0.1608
    },
    {
      "fund": "ARKK",
      "date": "2021-10-08",
      "ticker": "CRSP",
      "company": "CRISPR THERAPEUTICS AG",
      "direction": "Buy",
      "cusip": "H17182108",
      "shares": 268472,
      "etf_percent": 0.1293
    },
    {
      "fund": "ARKK",
      "date": "2021-10-08",
      "ticker": "DOCU",
      "company": "DOCUSIGN INC",
      "direction": "Sell",
      "cusip": "256163106",
      "shares": 78867,
      "etf_percent": 0.103
    }
  ]
}
'''