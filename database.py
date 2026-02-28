import os
import psycopg2
import psycopg2.extras
from psycopg2 import pool
from dotenv import load_dotenv

load_dotenv()

_connection_pool: pool.ThreadedConnectionPool | None = None


def _get_pool() -> pool.ThreadedConnectionPool:
    global _connection_pool
    if _connection_pool is None:
        _connection_pool = pool.ThreadedConnectionPool(
            minconn=1,
            maxconn=10,
            dsn=os.getenv("DATABASE_URL"),
            cursor_factory=psycopg2.extras.RealDictCursor,
        )
    return _connection_pool


def get_connection():
    return _get_pool().getconn()


def return_connection(conn):
    _get_pool().putconn(conn)
