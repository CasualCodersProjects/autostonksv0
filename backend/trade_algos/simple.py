import time
import datetime

from . import BaseAlgorithm
class SimpleAlgorithm(BaseAlgorithm):
    '''
    Buys given stock or crypto. Set a max loss and a min gained. When min gained is hit, sell. When max loss is hit, sell.
    '''
    def set_min_gain(self, symbol: str, min_gain: float) -> None:
        self.symbols[symbol]['min_gain'] = min_gain

    def set_max_loss(self, symbol: str, max_loss: float) -> None:
        self.symbols[symbol]['max_loss'] = max_loss

    def get_min_gain(self, symbol: str) -> float:
        return self.symbols[symbol]['min_gain']

    def get_max_loss(self, symbol: str) -> float:
        return self.symbols[symbol]['max_loss']

    def get_buy_price(self, symbol: str) -> float:
        orders = self.api.list_orders(status="closed", symbols=[symbol])
        if orders:
            for order in orders:
                if order.side == 'buy':
                    return float(order.filled_avg_price)
        return 0

    def run(self):
        while True:
            clock = self.api.get_clock()

            if not clock.is_open:
                time.sleep(60)
                continue
            
            # clear existing orders
            self.clear_account_orders()

            closingTime = clock.next_close.replace(tzinfo=datetime.timezone.utc).timestamp()
            # get symbols
            symbols = self.get_symbols()

            # iterate through symbols
            for symbol in symbols:
                # check if we are holding any of this symbol
                buy_price = self.get_buy_price(symbol)
                # if we are holding any of this symbol
                if buy_price != 0:
                    # don't buy any more
                    print(f'Holding {symbol} at {buy_price}')
                    self.holding_count += 1
                    continue
                print(f"Buying {symbol}....")
                # buy the symbol at current market price
                order = self.place_buy_order(symbol, self.symbols[symbol].get('qty', 1))
                self.holding_count += 1
                print(f'{symbol} bought at {order.filled_avg_price}')

            while self.holding_count > 0:
                currTime = clock.timestamp.replace(tzinfo=datetime.timezone.utc).timestamp()
                if currTime > closingTime:
                    break
                # iterate through symbols
                for symbol in symbols:
                    print('-' * 20)
                    # get current price
                    current_price = self.get_current_price(symbol)
                    buy_price = self.get_buy_price(symbol)
                    min_gain = self.get_min_gain(symbol)
                    max_loss = self.get_max_loss(symbol)
                    difference = (current_price - buy_price) * self.symbols[symbol].get('qty', 1)
                    print(f'{symbol} current price: {current_price}')
                    print(f'{symbol} buy price: {buy_price}')
                    print(f'{symbol} difference: {round(difference, 2)}')
                    if difference > min_gain:
                        # sell the symbol at current market price
                        self.place_sell_order(symbol, symbols.get('qty', 1))
                        self.holding_count -= 1
                        print(f'{symbol} sold at {current_price}')
                    elif difference < max_loss:
                        # sell the symbol at current market price
                        self.place_sell_order(symbol, symbols.get('qty', 1))
                        self.holding_count -= 1
                        print(f'{symbol} sold at {current_price}')

                # wait a second
                time.sleep(1)