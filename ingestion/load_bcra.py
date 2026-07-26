import argparse
from ingestion.bcra_client import load_historical, load_incremental
from ingestion.database import get_connection, init_tables, upsert_variable, load_variable


def main():
    parser = argparse.ArgumentParser(description="Pipeline de ingesta BCRA")
    parser.add_argument(
        "--mode",
        choices=["historical", "incremental"],
        default="incremental",
        help="historical: carga 5 años (solo primera vez). incremental: carga últimos 45 días (uso diario)."
    )
    args = parser.parse_args()

    print("Conectando a DuckDB...")
    conn = get_connection()
    init_tables(conn)

    if args.mode == "historical":
        datos = load_historical()
    else:
        datos = load_incremental()

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