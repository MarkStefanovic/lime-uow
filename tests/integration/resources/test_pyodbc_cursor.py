import pyodbc

from lime_uow import pyodbc_resources as lpa


def test_pyodbc_connection_open(postgres_db_uri: str) -> None:
    with pyodbc.connect(postgres_db_uri) as con:
        p_cur = lpa.PyodbcCursor(con=con, fast_executemany=True)
        assert isinstance(p_cur, lpa.PyodbcCursor)
