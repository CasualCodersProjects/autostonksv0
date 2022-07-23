from . import Ark

def test_init():
    ark = Ark()
    assert ark.BASE_URL == 'https://arkfunds.io/api'
    assert ark.VERSION == 'v2'
    assert ark.API_URL == 'https://arkfunds.io/api/v2'

def test_get_etf_trades():
    ark = Ark()
    trades = ark.get_etf_trades('ARKK')
    assert trades['symbol'] == 'ARKK'
    
def test_get_etf_holdings():
    ark = Ark()
    holdings = ark.get_etf_holdings('ARKK')
    assert holdings['symbol'] == 'ARKK'