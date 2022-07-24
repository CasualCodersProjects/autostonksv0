import os
from typing import Optional

from sqlmodel import create_engine, Session, select
from fastapi import FastAPI

from database.models import Instance, Holding
from api.models import NewInstance
from trade_algorithms import BaseAlgorithm  # this doesn't actually do anything

algorithms = {
    "base": BaseAlgorithm
}

app = FastAPI()

DB_URI = os.getenv("DB_URI", "sqlite:///test.db")
engine = create_engine(DB_URI)


@app.get("/")
async def root():
    return {"status": "ok"}


@app.get("/instances")
async def instances():
    with Session(engine) as session:
        statement = select(Instance)
        results = session.execute(statement).fetchall()
        return results


@app.post("/new/instance")
async def new_instance(instance: NewInstance):
    selected_algo = algorithms[instance.algorithm]
    algo = selected_algo(
        expiration=instance.expiration,
        tickers=instance.tickers,
        budget=instance.budget,
    ).start()

    return algo.instance


@app.get("/holdings")
async def holdings(ticker: Optional[str] = None):
    if not ticker:
        with Session(engine) as session:
            statement = select(Holding)
            results = session.execute(statement).fetchall()
            return results

    with Session(engine) as session:
        statement = select(Holding).where(Holding.ticker == ticker)
        results = session.execute(statement).fetchall()
        return results
