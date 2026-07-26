import requests
import pandas as pd
from datetime import datetime, timedelta
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://api.bcra.gob.ar/estadisticas/v4.0"

VARIABLES = {
    "reservas_internacionales": 1,
    "tipo_cambio_minorista": 4,
    "tipo_cambio_mayorista": 5,
    "tasa_badlar": 7,
    "tasa_prestamos_personales": 14,
    "base_monetaria": 15,
    "prestamos_sector_privado": 26,
    "expectativas_inflacion_rem": 29,
    "m2": 109,
    "prestamos_adelantos_cuenta": 110,
    "prestamos_documentos": 111,
    "prestamos_hipotecarios": 112,
    "prestamos_prendarios": 113,
    "prestamos_personales": 114,
    "prestamos_tarjeta_credito": 115,
    "prestamos_otros": 116,
}


def get_variable(id_variable: int, dias: int = 365) -> pd.DataFrame:
    """
    Obtiene una serie temporal de una variable del BCRA con paginación.

    Args:
        id_variable: ID de la variable según la API del BCRA
        dias: cantidad de días hacia atrás a consultar

    Returns:
        DataFrame con columnas [fecha, valor]
    """
    fecha_desde = (datetime.today() - timedelta(days=dias)).strftime("%Y-%m-%d")
    fecha_hasta = datetime.today().strftime("%Y-%m-%d")

    url = f"{BASE_URL}/monetarias/{id_variable}"
    todos = []
    offset = 0
    limit = 1000

    while True:
        params = {
            "desde": fecha_desde,
            "hasta": fecha_hasta,
            "offset": offset,
            "limit": limit,
        }

        response = requests.get(url, params=params, timeout=10, verify=False)
        response.raise_for_status()

        data = response.json()
        detalle = data["results"][0]["detalle"]
        todos.extend(detalle)

        total = data["metadata"]["resultset"]["count"]
        offset += limit

        if offset >= total:
            break

    df = pd.DataFrame(todos)
    df["fecha"] = pd.to_datetime(df["fecha"])
    df = df.sort_values("fecha").reset_index(drop=True)

    return df


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


def load_historical(dias: int = 1825) -> dict[str, pd.DataFrame]:
    """
    Carga histórica inicial. Correr solo una vez para poblar la base.

    Args:
        dias: años hacia atrás a consultar (default: 5 años)

    Returns:
        Diccionario con nombre de variable -> DataFrame
    """
    print(f"Carga histórica: últimos {dias} días ({dias // 365} años aprox)")
    resultados = {}
    for nombre, id_var in VARIABLES.items():
        print(f"  Obteniendo {nombre}...")
        resultados[nombre] = get_variable(id_var, dias=dias)

    print("  Obteniendo dólar blue...")
    resultados["dolar_blue"] = get_dolar_blue(dias=dias)

    return resultados


def load_incremental(dias: int = 45) -> dict[str, pd.DataFrame]:
    """
    Carga incremental diaria. Trae los últimos N días con overlap
    para capturar datos publicados con retraso por el BCRA.

    Args:
        dias: ventana de días a traer (default: 45 para tener overlap)

    Returns:
        Diccionario con nombre de variable -> DataFrame
    """
    print(f"Carga incremental: últimos {dias} días")
    resultados = {}
    for nombre, id_var in VARIABLES.items():
        print(f"  Obteniendo {nombre}...")
        resultados[nombre] = get_variable(id_var, dias=dias)

    print("  Obteniendo dólar blue...")
    resultados["dolar_blue"] = get_dolar_blue(dias=dias)

    return resultados