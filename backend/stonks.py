from typing import List, Union
import json
import os

import arrow
import fire
from dotenv import load_dotenv
from alpaca_trade_api.rest import TimeFrame

from ark_wrapper import Ark
from trade_algos import BaseAlgorithm
from trade_algos.copycat import CopyCatAlgorithm
from trade_algos.simple import SimpleAlgorithm
from trade_algos.mean_reversion import MeanReversionAlgorithm
from utils import get_all_ark_holdings

load_dotenv()

API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')


def simple(symbol: str, qty: int = 1, gain: float = 1, loss: float = 1):
    '''Executes the simple algorithm.'''
    simple_algo = SimpleAlgorithm(API_KEY, API_SECRET)

    simple_algo.add_symbol(symbol, qty=qty)

    simple_algo.set_max_loss(symbol, loss)
    simple_algo.set_min_gain(symbol, gain)

    simple_algo.run()


def copycat(symbol: str, daily_budget_percentage: float, min_bal: float):
    '''Executes the copycat algorithm.'''
    copycat = CopyCatAlgorithm(API_KEY, API_SECRET)

    copycat.set_etf_symbol(symbol)
    copycat.set_daily_budget_percent(daily_budget_percentage)
    copycat.set_min_balance(min_bal)

    copycat.run()


def ark(symbol: str, mode: str, start_date: str = None, end_date: str = None, limit: int = 100):
    '''Prints the ARK holdings for the given ARK ticker.'''
    ark = Ark()
    if mode == 'holdings':
        print(json.dumps(ark.get_etf_holdings(
            symbol, start_date, end_date, limit), indent=4))

    elif mode == 'trades':
        print(json.dumps(ark.get_etf_trades(
            symbol, start_date, end_date, limit), indent=4))

    else:
        print('Invalid mode')


def historical(symbol: str, timeframe: str = 'day', limit: int = 100):
    '''Prints the historical price of the given ticker.'''
    base = BaseAlgorithm(API_KEY, API_SECRET)

    timeframe_table = {
        'minute': TimeFrame.Minute,
        'hour': TimeFrame.Hour,
        'day': TimeFrame.Day,
        'week': TimeFrame.Week,
        'month': TimeFrame.Month,
    }

    # 15 minutes ago
    end = arrow.now().shift(hours=-1)
    end_str = end.isoformat()
    print(end_str)

    # 100 days ago
    start = end.shift(days=-100)
    start_str = start.isoformat()
    print(start_str)

    bars = base.api.get_bars(
        symbol, timeframe_table[timeframe], start=start_str, end=end_str, limit=limit)
    for bar in bars:
        timestamp = arrow.get(bar.t)
        print(f'Date: {timestamp.format("YYYY-MM-DD hh:mm:ss")} Open: {bar.o} Close: {bar.c} High: {bar.h} Low: {bar.l} Volume: {bar.v}')


def current(symbol: str):
    '''Prints the current price of the given ticker.'''
    base = BaseAlgorithm(API_KEY, API_SECRET)
    barset = base.api.get_bars(symbol, TimeFrame.Minute, limit=1)
    print(barset[0].c)


def yesterday(symbol: str):
    '''Prints yesterday's stock price of the given ticker.'''
    base = BaseAlgorithm(API_KEY, API_SECRET)
    print(base.get_yesterday_price(symbol))


def mean(symbol: str, timeframe: str = 'month'):
    '''Gets the average rate of change for the given ticker.'''
    mean_reversion = MeanReversionAlgorithm(API_KEY, API_SECRET)
    print(mean_reversion.mean([symbol], timeframe)[symbol])


def mean_reversion(symbols: Union[List[str], None] = None, ticker_file: str = './tickers.txt', cache_means: bool = False, cache_filename: str = './mean_reversion.json', budget: float = 0.0, testing: bool = False, timeframe: str = 'month'):
    '''Executes the mean reversion algorithm.'''
    mean_reversion = MeanReversionAlgorithm(API_KEY, API_SECRET)
    ticker_file_exists = os.path.exists(ticker_file)
    if symbols is None and not ticker_file_exists:
        symbols = get_all_ark_holdings()
        for symbol in symbols:
            with open(ticker_file, 'a') as f:
                f.write(f'{symbol}\n')
    with open(ticker_file, 'r') as f:
        symbols = [line.strip() for line in f.readlines()]

    if testing:
        cache_means = True

    mean_reversion.set_budget(budget)
    mean_reversion.run(symbols, cache_means, timeframe,
                       cache_filename, testing)


def test():
    '''Used for testing.'''
    # print(f'{symbol} {qty} {gain} {loss}')
    # print(API_KEY)
    # print(API_SECRET)
    base = BaseAlgorithm(API_KEY, API_SECRET)
    print(base.get_current_crypto_price('ETH'))


def portfolio():
    '''Prints your current portfolio.'''
    base = BaseAlgorithm(API_KEY, API_SECRET)
    print(json.dumps(base.get_portfolio(raw=True), indent=4))


if __name__ == "__main__":
    fire.Fire()
