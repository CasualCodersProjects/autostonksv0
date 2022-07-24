import os
from threading import Thread
from multiprocessing import Process, Queue
import time

import arrow
from alpaca_trade_api.rest import REST, TimeFrame, TimeFrameUnit
from sqlmodel import Session, select

from database.models import Instance, Holding


class BaseAlgorithm:
    '''
    The base algorithm that all other algorithms will inherit from.

    Contains the base code needed to buy and sell stocks. This code keeps the holdings up to date with the database.

    This also contains the needed code to resume the algorithm if the program is interrupted. The database should be queried to find the algorithm to be matched with the instance.
    '''

    def __init__(self, API_KEY: str | None = None, API_SECRET: str | None = None, base_url: str = 'https://paper-api.alpaca.markets', api_version: str = 'v2', expiration: arrow.Arrow | None = None, budget=0.0, session: Session | None = None, database_uri: str | None = None, instance: Instance | None = None):

        if session is None and database_uri is None:
            raise ValueError('Either session or database_uri must be provided')

        if API_KEY is None:
            API_KEY = os.getenv('ALPACA_API_KEY')
        if API_SECRET is None:
            API_SECRET = os.getenv('ALPACA_API_SECRET')

        self.api = REST(API_KEY, API_SECRET, base_url=base_url,
                        api_version=api_version)

        if instance:
            self.instance = instance
        else:
            self.instance = Instance(
                expiration=expiration, budget=budget, balance=0)

        if session is None:
            self.session = Session(database_uri)
        else:
            self.session = session

        if not instance:
            self.session.add(self.instance)
            self.session.commit()

    def __del__(self):
        '''
        Close the session when the algorithm is deleted from memory.
        '''
        self.session.close()

    def start(self):
        '''
        Starts the algorithm in a separate process.
        '''
        self.kill_queue = Queue()
        self.process = Process(target=self.run, args=())
        self.process.start()
        return self

    def kill(self):
        self.kill_queue.put(True)

    def run(self):
        '''
        Example run method.
        '''
        while True:
            if not self.kill_queue.empty():
                print('Killing thread')
                break
            time.sleep(1)
            print("Running....")

    def _update_instance(self):
        '''
        Update the instance in the database.
        '''
        self.session.add(self.instance)
        self.session.commit()

    def _process_order(self, order):
        '''
        Takes the order, gets the ID, waits until the order is filled, then subtracts the average buy price from the bot balance.
        '''
        order_id = order.id

        def _wait_for_order():
            while True:
                order = self.api.get_order(order_id)
                if order.status == 'filled':
                    break
                else:
                    time.sleep(1)
            avg_price = float(order.filled_avg_price)
            qty = float(order.filled_qty)
            self.instance.balance -= avg_price * qty
            holding = Holding(
                created_at=arrow.get(order.filled_at).datetime,
                ticker=order.symbol,
                shares=qty,
                buy_price=avg_price,
                owner=self.instance.id)
            self.session.add(holding)
            # there's a commit in this function, so we don't need to commit here
            self._update_instance()

        thread = Thread(target=_wait_for_order)
        thread.start()

    def get_instance(self):
        return self.instance

    def get_session(self):
        return self.session

    def get_number_of_shares(self, symbol: str):
        statement = select(Holding).where(Holding.ticker == symbol)
        results = self.session.exec(statement)
        return sum([holding.shares for holding in results])

    def get_holdings(self):
        statement = select(Holding).where(
            Holding.owner == self.instance.id)
        results = self.session.exec(statement)
        return results

    def get_portfolio(self):
        return self.get_holdings()

    def add_holding(self, holding: Holding):
        self.session.add(holding)
        self.session.commit()

    def get_holdings_by_ticker(self, ticker: str):
        statement = select(Holding).where(
            Holding.owner == self.instance.id).where(Holding.ticker == ticker)
        results = self.session.exec(statement)
        return results

    def get_holdings_by_date(self, start: arrow.Arrow | None = None, end: arrow.Arrow | None = None):
        # convert from arrow.Arrow to datetime
        start_time = start.datetime
        end_time = end.datetime
        if start is None and end is None:
            raise ValueError('Either start or end must be provided')

        if start and end is None:
            statement = select(Holding).where(
                Holding.owner == self.instance.id).where(Holding.created_at >= start_time)

        if start is None and end:
            statement = select(Holding).where(
                Holding.owner == self.instance.id).where(Holding.created_at <= end_time)

        if start and end:
            statement = select(Holding).where(
                Holding.owner == self.instance.id).where(Holding.created_at >= start_time).where(Holding.created_at <= end_time)

        results = self.session.exec(statement)
        return results

    def get_current_price(self, symbol: str):
        return float(self.api.get_bars(symbol, TimeFrame.Minute, limit=1)[0].c)

    def get_current_crypto_price(self, symbol: str, exchange: str = 'CBSE'):
        q = self.api.get_latest_crypto_quote(symbol + 'USD', exchange)
        return float(q.ap)

    def get_yesterday_price(self, symbol: str):
        return self.api.get_bars(symbol, TimeFrame(23, TimeFrameUnit.Hour), limit=1)[0].c

    def get_account_value(self):
        return float(self.api.get_account().portfolio_value)

    def get_account_cash(self):
        return float(self.api.get_account().cash)

    def get_account_buying_power(self):
        return float(self.api.get_account().buying_power)

    def get_account_equity(self):
        return float(self.api.get_account().equity)

    def get_account_portfolio(self, raw: bool = False):
        self.api._use_raw_data = raw
        positions = self.api.list_positions()
        self.api._use_raw_data = False
        return positions

    def has_account_traded_today(self):
        # get the now timestamp
        now = arrow.now().format('YYYY-MM-DD')
        # get all orders after the now timestamp
        orders = self.api.list_orders(after=now, status='closed', limit=500)

        clock = self.api.get_clock()

        return len(orders) > 0 and clock.is_open

    def place_buy_order(self, symbol: str, qty: float | int, crypto: bool = False):
        if crypto:
            symbol += 'USD'

        # get the current price of the symbol
        price = self.get_current_price(symbol)
        buy_price = price * qty
        # check to make sure we have enough money.
        if self.instance.balance - buy_price < 0:
            # should there be an error here?
            return None  # not enough money to buy

        order = self.api.submit_order(
            symbol=symbol,
            qty=float(qty),
            side='buy',
            type='market',
            time_in_force='day'
        )
        self._process_order(order)
        return order

    def place_sell_order(self, symbol: str, qty: float | int, crypto: bool = False):
        if crypto:
            symbol += 'USD'

        # check to make sure we have the shares.
        if self.get_number_of_shares(symbol) < qty:
            # should there be an error here?
            return None

        order = self.api.submit_order(
            symbol=symbol,
            qty=float(qty),
            side='sell',
            type='market',
            time_in_force='day'
        )
        self._process_order(order)
        return order

    # These should all be added later. For now we'll focus on market buy and sell.
    # def place_limit_buy_order(self, symbol: str, qty: float | int, limit_price: float):
    #     return self.api.submit_order(
    #         symbol=symbol,
    #         qty=float(qty),
    #         side='buy',
    #         type='limit',
    #         time_in_force='day',
    #         limit_price=limit_price
    #     )

    # def place_limit_sell_order(self, symbol: str, qty: float | int, limit_price: float):
    #     return self.api.submit_order(
    #         symbol=symbol,
    #         qty=float(qty),
    #         side='sell',
    #         type='limit',
    #         time_in_force='day',
    #         limit_price=limit_price
    #     )

    # def place_stop_buy_order(self, symbol: str, qty: float | int, stop_price: float):
    #     return self.api.submit_order(
    #         symbol=symbol,
    #         qty=float(qty),
    #         side='buy',
    #         type='stop',
    #         time_in_force='day',
    #         stop_price=stop_price
    #     )

    # def place_stop_sell_order(self, symbol: str, qty: float | int, stop_price: float):
    #     return self.api.submit_order(
    #         symbol=symbol,
    #         qty=float(qty),
    #         side='sell',
    #         type='stop',
    #         time_in_force='day',
    #         stop_price=stop_price
    #     )

    # def sell_notional_order(self, symbol: str, price: float):
    #     return self.api.submit_order(
    #         symbol=symbol,
    #         notional=price,
    #         side='sell',
    #         type='market',
    #         time_in_force='day'
    #     )

    # def place_notional_order(self, symbol: str, price: float):
    #     return self.api.submit_order(
    #         symbol=symbol,
    #         notional=price,
    #         side='buy',
    #         type='market',
    #         time_in_force='day'
    #     )
