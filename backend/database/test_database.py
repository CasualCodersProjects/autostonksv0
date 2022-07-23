import os

import arrow
import pytest
from sqlmodel import Session, SQLModel, create_engine

from database import get_all_holdings, get_most_recent_holding, add_holding
from database.model import Holding


@pytest.fixture(autouse=True)
def setup_db():
    engine = create_engine("sqlite:///test.db")
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        holding = Holding(ticker="AAPL", shares=100, buy_price=100.00)
        add_holding(session, holding)

        holding = Holding(ticker="MSFT", shares=100, buy_price=100.00)
        add_holding(session, holding)

        holding = Holding(ticker="AAPL", shares=200,
                          buy_price=50.00, buy_date=arrow.now().shift(weeks=-2).isoformat())
        add_holding(session, holding)

    yield

    os.remove("test.db")


def test_get_all_holdings():
    engine = create_engine("sqlite:///test.db")
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        holdings = get_all_holdings(session)
        assert len(holdings) != 0
        holdings = get_all_holdings(session, tickers=["AAPL"])
        assert len(holdings) == 2


def test_get_most_recent_holding():
    engine = create_engine("sqlite:///test.db")
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        holding = get_most_recent_holding(session, ticker="AAPL")
        assert holding is not None
        holding = get_most_recent_holding(session, ticker="TSLA")
        assert holding is None
