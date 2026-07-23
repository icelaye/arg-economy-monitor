from ingestion.bcra_client import get_all_variables, get_dolar_blue
from ingestion.database import get_connection, init_tables, upsert_variable, load_variable


def main():
    print("Conectando a DuckDB...")
    conn = get_connection()
    init_tables(conn)

    print("\nObteniendo datos del BCRA...")
    datos = get_all_variables()

    print("\nObteniendo dólar blue...")
    datos["dolar_blue"] = get_dolar_blue()

    print("\nPersistiendo en DuckDB...")
    for nombre, df in datos.items():
        upsert_variable(conn, nombre, df)

    print("\nVerificando datos guardados:")
    for nombre in datos.keys():
        df_check = load_variable(conn, nombre)
        print(f"  {nombre}: {len(df_check)} registros")

    conn.close()
    print("\nListo.")


if __name__ == "__main__":
    main()