"""Shared database engine for the homework solution.

Reads PG_DSN from the environment, e.g.
    PG_DSN=postgresql://postgres:postgres@localhost:5432/langgraph_db
"""
import os

from sqlmodel import create_engine
from dotenv import load_dotenv

load_dotenv()


def get_engine():
    dsn = os.getenv("PG_DSN")
    if not dsn:
        raise RuntimeError(
            "PG_DSN environment variable not set "
            "(e.g. postgresql://postgres:postgres@localhost:5432/langgraph_db)"
        )
    return create_engine(dsn, echo=False)
