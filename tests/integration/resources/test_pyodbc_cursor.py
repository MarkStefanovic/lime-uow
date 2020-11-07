import pyodbc

import lime_uow as lu


def test_pyodbc_connection_open(postgres_db_uri: str) -> None:
    with pyodbc.connect(postgres_db_uri) as con:
        p_cur = lu.PyodbcCursor(con=con, fast_executemany=True)
        assert isinstance(p_cur, lu.PyodbcCursor)
