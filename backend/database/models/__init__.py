from datetime import datetime
from typing import Optional

import arrow
from sqlmodel import Field, SQLModel, create_engine, Session, select


class Instance(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default=datetime.now())
    expiration: Optional[datetime] = Field(default=None)
    budget: float
    balance: float


class Holding(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    ticker: str
    shares: float
    buy_price: float
    created_at: datetime = Field(default=datetime.now())
    owner: int = Field(foreign_key='instance.id')

    def get_date(self) -> arrow.Arrow:
        return arrow.get(self.created_at)


class Mods(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default=datetime.now)
    user: str = Field(foreign_key='users.id')


if __name__ == "__main__":
    holding_one = Holding(ticker="AAPL", shares=100, buy_price=100.00)
    # generate an arrow time from two weeks ago
    two_weeks_ago = arrow.now().shift(weeks=-2)
    holding_two = Holding(ticker="MSFT", shares=100, buy_price=100.00)
    # holding three is AAPL but double the shares at half the price
    holding_three = Holding(ticker="AAPL", shares=200,
                            buy_price=50.00, buy_date=two_weeks_ago.isoformat())

    engine = create_engine("sqlite:///test.db")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        session.add(holding_one)
        session.add(holding_two)
        session.add(holding_three)
        session.commit()

    # get all AAPL holdings
    with Session(engine) as session:
        statement = select(Holding).where(Holding.ticker == "AAPL")
        results = session.execute(statement).fetchall()
        for result in results:
            print(result[0])
