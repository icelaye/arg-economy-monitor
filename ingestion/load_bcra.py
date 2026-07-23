from ingestion.bcra_client import get_all_variables
from ingestion.database import get_connection, init_tables, upsert_variable, load_variable


def main():
    print("Conectando a DuckDB...")
    conn = get_connection()
    init_tables(conn)

    print("\nObteniendo datos del BCRA...")
    datos = get_all_variables()

    print("\nPersistiendo en DuckDB...")
    for nombre, df in datos.items():
        upsert_variable(conn, nombre, df)

    print("\nVerificando datos guardados:")
    df_check = load_variable(conn, "reservas_internacionales")
    print(f"  reservas_internacionales: {len(df_check)} registros")
    print(df_check.tail(3))

    conn.close()
    print("\nListo.")


if __name__ == "__main__":
    main()