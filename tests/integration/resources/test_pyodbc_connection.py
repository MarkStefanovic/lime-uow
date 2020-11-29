import pyodbc

from lime_uow import pyodbc_resources as lpa


def test_pyodbc_connection_open(postgres_db_uri: str) -> None:
    pc = lpa.PyodbcConnection(db_uri=postgres_db_uri, autocommit=False, read_only=False)
    con = pc.open()
    assert isinstance(con, pyodbc.Connection)
