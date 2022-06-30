from utils import get_all_ark_holdings, get_ark_tickers


def test_get_ark_tickers():
    tickers = get_ark_tickers()
    assert len(tickers)


def test_get_all_ark_holdings():
    tickers = get_all_ark_holdings()
    assert len(tickers)
