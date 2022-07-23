from sqlmodel import Session, select

from database.model import Holding


def get_all_holdings(session: Session, tickers: list[str] = []) -> list[Holding]:
    """
    Get all holdings from the database
    """
    if len(tickers) == 0:
        return session.query(Holding).all()

    statement = select(Holding).where(Holding.ticker.in_(tickers))

    results = session.execute(statement).fetchall()

    holdings = []

    for result in results:
        holdings.append(result[0])

    return holdings


def get_most_recent_holding(session: Session, ticker: str) -> Holding | None:
    """
    Get the most recent holding from the database
    """
    statement = select(Holding).where(
        Holding.ticker == ticker).order_by(Holding.buy_date.desc())

    results = session.execute(statement).first()

    if results is None:
        return None

    return results[0]


def add_holding(session: Session, holding: Holding):
    """
    Add a holding to the database
    """
    session.add(holding)
    session.commit()


if __name__ == "__main__":
    from sqlmodel import create_engine, SQLModel
    engine = create_engine("sqlite:///test.db")
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        holdings = get_all_holdings(session)
        for holding in holdings:
            print(holding)
