import requests
import pandas as pd
from datetime import datetime, timedelta
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://api.bcra.gob.ar/estadisticas/v4.0"

VARIABLES = {
    "reservas_internacionales": 1,
    "tipo_cambio_minorista": 4,
    "tasa_politica_monetaria": 7,
    "base_monetaria": 15,
}


def get_variable(id_variable: int, dias: int = 365) -> pd.DataFrame:
    """
    Obtiene una serie temporal de una variable del BCRA.

    Args:
        id_variable: ID de la variable según la API del BCRA
        dias: cantidad de días hacia atrás a consultar

    Returns:
        DataFrame con columnas [fecha, valor]
    """
    fecha_desde = (datetime.today() - timedelta(days=dias)).strftime("%Y-%m-%d")
    fecha_hasta = datetime.today().strftime("%Y-%m-%d")

    url = f"{BASE_URL}/monetarias/{id_variable}"
    params = {"desde": fecha_desde, "hasta": fecha_hasta}

    response = requests.get(url, params=params, timeout=10, verify=False)
    response.raise_for_status()

    data = response.json()
    df = pd.DataFrame(data["results"][0]["detalle"])
    df["fecha"] = pd.to_datetime(df["fecha"])
    df = df.sort_values("fecha").reset_index(drop=True)

    return df


def get_all_variables() -> dict[str, pd.DataFrame]:
    """
    Obtiene todas las variables definidas en VARIABLES.

    Returns:
        Diccionario con nombre de variable -> DataFrame
    """
    resultados = {}

    for nombre, id_var in VARIABLES.items():
        print(f"Obteniendo {nombre}...")
        resultados[nombre] = get_variable(id_var)

    return resultados

def get_dolar_blue(dias: int = 365) -> pd.DataFrame:
    """
    Obtiene la evolución del dólar blue desde bluelytics.com.ar

    Args:
        dias: cantidad de días hacia atrás a consultar

    Returns:
        DataFrame con columnas [fecha, valor] para el precio de venta blue
    """
    url = "https://api.bluelytics.com.ar/v2/evolution.json"
    response = requests.get(url, timeout=10)
    response.raise_for_status()

    df = pd.DataFrame(response.json())
    df["fecha"] = pd.to_datetime(df["date"])

    fecha_desde = datetime.today() - timedelta(days=dias)
    df = df[
        (df["source"] == "Blue") &
        (df["fecha"] >= fecha_desde)
    ].copy()

    df = df.rename(columns={"value_sell": "valor"})
    df = df[["fecha", "valor"]].sort_values("fecha").reset_index(drop=True)

    return df

if __name__ == "__main__":
    datos = get_all_variables()

    for nombre, df in datos.items():
        print(f"\n{nombre}: {len(df)} registros")
        print(df.tail(3))

    print("\nObteniendo dólar blue...")
    df_blue = get_dolar_blue()
    print(f"dolar_blue: {len(df_blue)} registros")
    print(df_blue.tail(3))