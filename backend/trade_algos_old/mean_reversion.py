from collections import OrderedDict
import os
import time
from typing import List
import json
from datetime import timedelta

import arrow
from alpaca_trade_api import TimeFrame, TimeFrameUnit
import requests

from . import BaseAlgorithm

# chunk a list into n evenly sized chunks


def chunk(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def create_blacklist(path: str, symbols: List[str] = []):
    values = {}
    for symbol in symbols:
        values[symbol] = arrow.now().shift(months=1).timestamp
    with open(path, 'w') as f:
        json.dump(values, f)


def create_cache_file(data: dict, filename: str):
    # get the date now
    now = arrow.utcnow()
    output_data = {
        'date': now.isoformat(),
        'data': data
    }
    with open(filename, 'w') as f:
        json.dump(output_data, f, indent=4)


def load_cache_file(filename: str) -> dict:
    with open(filename, 'r') as f:
        data = json.load(f)
    date = arrow.get(data['date'])

    # check if the cache file is older than 12 hours
    # if it is, return empty data and delete the file
    now = arrow.utcnow()
    if now - date > timedelta(hours=12):
        os.remove(filename)
        return {}

    return data['data']


class MeanReversionAlgorithm(BaseAlgorithm):
    budget = 0.0
    blacklist_path = 'blacklist.json'

    def set_tickers(self, tickers: List[str]):
        self.tickers = list(set(tickers))

    def set_budget(self, budget: float):
        self.budget = budget

    def add_to_blacklist(self, ticker: str):
        # check if blacklist exists
        if os.path.exists(self.blacklist_path):
            # append the ticker to the blacklist
            with open(self.blacklist_path, 'r') as f:
                blacklist = json.load(f)
            blacklist[ticker] = arrow.now().shift(months=1).timestamp
            with open(self.blacklist_path, 'w') as f:
                json.dump(blacklist, f)
        else:
            # create the blacklist
            create_blacklist(self.blacklist_path, [ticker])

    def remove_from_blacklist(self, ticker: str):
        # check if blacklist exists
        if os.path.exists(self.blacklist_path):
            # append the ticker to the blacklist
            with open(self.blacklist_path, 'r') as f:
                blacklist = json.load(f)
            if ticker in blacklist:
                del blacklist[ticker]
                with open(self.blacklist_path, 'w') as f:
                    json.dump(blacklist, f)
        # otherwise, do nothing

    def get_blacklist(self) -> dict:
        if os.path.exists(self.blacklist_path):
            with open(self.blacklist_path, 'r') as f:
                blacklist = json.load(f)
        else:
            blacklist = {}
        return blacklist

    # def stop_loss(self):
    #     positions = self.get_owned_positions()
    #     for symbol, position in positions.items():
    #         if position['market_value'] < position['avg_entry_price'] * 0.95:
    #             self.sell_all(symbol)

    def get_owned_positions(self) -> dict:
        positions = self.get_portfolio(raw=True)
        owned_positions = {}
        for position in positions:
            symbol = position['symbol']
            shares = float(position['qty'])
            market_value = float(position['market_value'])
            avg_entry_price = float(position['avg_entry_price'])
            owned_positions[symbol] = {
                'shares': shares,  # shares the user owns
                'market_value': market_value,  # market value of the shares
                'avg_entry_price': avg_entry_price  # average buy price of the shares
            }
        return owned_positions

    def mean(self, symbols: List[str], timeframe: str = 'month') -> dict:
        alpaca_timeframe = TimeFrame(1, TimeFrameUnit.Hour)
        start_date = arrow.now().shift(months=-1)
        if timeframe == 'day':
            start_date = arrow.now().shift(days=-1)
        if timeframe == 'week':
            start_date = arrow.now().shift(weeks=-1)
        today = arrow.now().shift(minutes=-30)
        try:
            bars = self.api.get_bars(symbols, alpaca_timeframe, start=start_date.isoformat(
            ), end=today.isoformat(), limit=10000)
        except requests.exceptions.HTTPError as e:
            print('HTTPError: {}'.format(e))
            return {}
        # bars for multiple symbols are grouped in the same list
        # create an object with each symbol as a key
        # and the list of bars as the value
        # e.g. {'TSLA': [bar1, bar2, bar3], 'AAPL': [bar1, bar2, bar3]}
        bars_by_symbol = {}
        changes_by_symbol = {}
        for bar in bars:
            if bar.S in bars_by_symbol:
                bars_by_symbol[bar.S].append(bar)
            else:
                bars_by_symbol[bar.S] = [bar]

        # sort the bars by time
        for symbol in bars_by_symbol:
            bars_by_symbol[symbol].sort(key=lambda bar: bar.t)
            changes_by_symbol[symbol] = []
            for i in range(1, len(bars_by_symbol[symbol])):
                changes_by_symbol[symbol].append(
                    bars_by_symbol[symbol][i].c - bars_by_symbol[symbol][i-1].c)

        # calculate the mean of the changes
        means = {}
        for symbol in changes_by_symbol:
            means[symbol] = sum(changes_by_symbol[symbol]) / \
                len(changes_by_symbol[symbol])

        return means

    def calculate_buy_amounts(self, tickers: List[str], testing: bool = False) -> dict:

        budget = self.budget
        cash = self.get_account_cash()
        if budget == 0:
            budget = cash

        if cash < budget and not testing:
            print('Not enough cash in budget, skipping today....')
            return {}

        # get the current market price of each ticker in buy
        prices = {}
        buy_amounts = {}
        for ticker in tickers:
            prices[ticker] = self.get_current_price(ticker)
            buy_amounts[ticker] = 0

        current_cost = 0.0

        while True:
            for ticker in tickers:
                if current_cost + prices[ticker] <= budget:
                    buy_amounts[ticker] += 1
                    current_cost += prices[ticker]
                else:
                    return buy_amounts

    def run(self, symbols: List[str], cache_means: bool = False, timeFrame: str = 'month', cache_filename: str = 'mean_reversion.json', testing: bool = False) -> dict:

        print('Initialzing Mean Reversion Algorithm')
        print('Waiting for market open....')

        waitTime = 60
        waitCount = 0
        try:
            while True:
                clock = None
                if not testing:
                    clock = self.api.get_clock()

                    if not clock.is_open:
                        time.sleep(60)
                        continue

                sell = []

                print('-' * 20)
                print('Market Open! Good morning!')
                # pretty print the current local time to console
                print('The date and time is currently', end=' ')
                print(arrow.now().format('YYYY-MM-DD HH:mm:ss'))

                print(f"Using {timeFrame} timeframe.")

                print('Getting tickers...')
                owned_positions = self.get_owned_positions()
                owned_tickers = list(owned_positions.keys())
                self.set_tickers(symbols + owned_tickers)

                if not testing:
                    print('Clearing orders...')
                    # clear existing orders
                    self.clear_account_orders()

                values = {}
                cache_invalid = False

                print('Running analysis.....')

                if cache_means and os.path.isfile(cache_filename):
                    print('Loading cached means from {}'.format(cache_filename))
                    values = load_cache_file(cache_filename)

                if not values:
                    cache_invalid = True
                    print('Calculating means.....')
                    chunks = chunk(self.tickers, 10)
                    for ticker_chunk in chunks:
                        chunk_values = self.mean(ticker_chunk, timeFrame)
                        # combine values and chunk_values
                        values.update(chunk_values)
                        if not values:
                            print(
                                'There was an issue getting data in bulk. Trying again...')
                            for t in ticker_chunk:
                                roc = self.mean([t], timeFrame)
                                if roc:
                                    values[ticker] = roc[ticker]

                sorted_values = OrderedDict(
                    sorted(values.items(), key=lambda x: x[1], reverse=True))

                if cache_means and cache_invalid:
                    # output to json file
                    create_cache_file(sorted_values, cache_filename)

                # get all tickers with a mean reversion greater than 0
                tickers = []
                for ticker in sorted_values:
                    if sorted_values[ticker] > 0:
                        tickers.append(ticker)

                for ticker in self.tickers:
                    if not ticker in tickers and ticker in owned_tickers:
                        sell.append(ticker)

                print(f'Selling tickers: {sell}')
                for ticker in sell:
                    qty = owned_positions[ticker]['shares']
                    print(f'Selling {qty} shares of {ticker}')
                    if not testing:
                        self.place_sell_order(ticker, qty)

                print('Waiting for positions to sell...')
                while len(self.api.list_orders(status='open')) > 0:
                    time.sleep(3)

                print('Calculating buy amounts...')

                # if there are more than 10 tickers, only buy the top 10
                if len(tickers) > 10:
                    tickers = tickers[:10]
                    print(
                        f"More than 10 top stocks, only buying top 10: {tickers}")

                buy_amounts = self.calculate_buy_amounts(tickers, testing)

                # print(buy_amounts)

                print('Buying tickers...')
                for ticker in buy_amounts:
                    if buy_amounts[ticker] > 0:
                        print(
                            f'Buying {buy_amounts[ticker]} shares of {ticker}')
                        if not testing:
                            self.place_buy_order(ticker, buy_amounts[ticker])

                # done for the day, sleeping until market close
                print('Done for the day, sleeping until market close.')
                if not clock is None:
                    while clock.is_open:
                        time.sleep(120)
                        clock = self.api.get_clock()

                print('Market Closed! Good Night!')
                if testing:
                    return
        except Exception as e:
            print(e)
            print('Error occurred, waiting and retrying...')
            time.sleep(waitTime * waitCount)
            waitCount += 1
            if waitCount > 10:
                print('Exceeded wait count, exiting...')
                return
