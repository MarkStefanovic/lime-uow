import pyodbc

import lime_uow as lu


def test_pyodbc_connection_open(postgres_db_uri: str) -> None:
    pc = lu.PyodbcConnection(db_uri=postgres_db_uri, autocommit=False, read_only=False)
    con = pc.open()
    assert isinstance(con, pyodbc.Connection)
