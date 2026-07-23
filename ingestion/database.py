import duckdb
import pandas as pd
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "bcra.duckdb"


def get_connection() -> duckdb.DuckDBPyConnection:
    """
    Crea la carpeta data si no existe y devuelve una conexión a DuckDB.
    """
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(DB_PATH))


def init_tables(conn: duckdb.DuckDBPyConnection) -> None:
    """
    Crea las tablas si no existen.
    """
    conn.execute("""
        CREATE TABLE IF NOT EXISTS raw_bcra (
            variable     VARCHAR,
            fecha        DATE,
            valor        DOUBLE,
            ingested_at  TIMESTAMP DEFAULT current_timestamp
        )
    """)
    print("Tablas inicializadas.")


def upsert_variable(
    conn: duckdb.DuckDBPyConnection,
    nombre: str,
    df: pd.DataFrame
) -> None:
    """
    Inserta registros nuevos para una variable, evitando duplicados.

    Args:
        conn: conexión activa a DuckDB
        nombre: nombre de la variable (ej: 'reservas_internacionales')
        df: DataFrame con columnas [fecha, valor]
    """
    df = df.copy()
    df["variable"] = nombre

    conn.execute("""
        INSERT INTO raw_bcra (variable, fecha, valor)
        SELECT variable, fecha, valor
        FROM df
        WHERE NOT EXISTS (
            SELECT 1 FROM raw_bcra r
            WHERE r.variable = df.variable
            AND r.fecha = df.fecha
        )
    """)

    print(f"  {nombre}: datos insertados correctamente.")


def load_variable(
    conn: duckdb.DuckDBPyConnection,
    nombre: str
) -> pd.DataFrame:
    """
    Devuelve todos los registros de una variable como DataFrame.

    Args:
        conn: conexión activa a DuckDB
        nombre: nombre de la variable

    Returns:
        DataFrame con columnas [variable, fecha, valor, ingested_at]
    """
    return conn.execute("""
        SELECT variable, fecha, valor, ingested_at
        FROM raw_bcra
        WHERE variable = ?
        ORDER BY fecha
    """, [nombre]).df()