from typing import Optional

from pydantic import BaseModel

# start algorithm
# end algorithm
# buy a stock
# sell a stock
# get current price of a stock
# get all holdings
# get all algorithm instances
# get price history of a stock


class NewInstance(BaseModel):
    tickers: str
    budget: float
    expiration: Optional[str] = None
    algorithm: str
