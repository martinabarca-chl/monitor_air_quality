# ============================================================
# data/load_data.py - Carga, limpieza y transformación de datos
# ============================================================

import pandas as pd               # Manipulación y análisis de datos
from pathlib import Path          # Manejo portable de rutas de archivos


# ============================================================
# RUTAS DE ARCHIVOS
# ============================================================

# Directorio raíz del proyecto (data/.. → raíz)
BASE_DIR = Path(__file__).resolve().parent.parent

# Archivos CSV con datos horarios de cada variable meteorológica
FILE_HR = BASE_DIR / "hR_150101_260624.csv"     # Humedad Relativa (%)
FILE_TC = BASE_DIR / "tC_150101_260624.csv"     # Temperatura (°C)
FILE_MP = BASE_DIR / "mp2.5_150101_260624.csv"  # MP2.5 (µg/m³)
FILE_VV = BASE_DIR / "vV_150101_260624.csv"     # Velocidad del Viento (m/s)


# ============================================================
# CONTROL DE CALIDAD (QC) - Límites físicos por variable
# ============================================================

QC_LIMITS = {
    'temperatura':  (None, 45),    # Sin mínimo; máximo 45 °C
    'humedad':      (0, 100),      # Rango 0-100 %
    'vel_viento':   (None, 30),    # Sin mínimo; máximo 30 m/s
    'mp2_5':        (0, 500),      # Rango 0-500 µg/m³
}

# Acumulador global de valores rechazados por variable (para auditoría)
qc_counts = {}


# ============================================================
# _apply_qc - Marca como NaN valores fuera de límites
# ============================================================

def _apply_qc(df, col, limits):
    """
    Reemplaza por NaN los valores de df[col] que estén fuera
    de los límites (lo, hi). Acumula el conteo en qc_counts.
    """
    lo, hi = limits                            # Límite inferior y superior
    mask = pd.Series(False, index=df.index)    # Máscara inicial: nada se rechaza

    if lo is not None:                         # Si hay cota inferior...
        mask |= (df[col] < lo)                 #   ...marca valores menores
    if hi is not None:                         # Si hay cota superior...
        mask |= (df[col] > hi)                 #   ...marca valores mayores

    n = mask.sum()                             # Total de valores fuera de rango
    if n:                                      # Si hay al menos uno...
        qc_counts[col] = qc_counts.get(col, 0) + n  # ...acumula en el registro global
        df.loc[mask, col] = None               # ...y los convierte en NaN

    return df


# ============================================================
# get_qc_summary - Resumen de valores rechazados por QC
# ============================================================

def get_qc_summary():
    """Retorna solo las variables que tuvieron valores fuera de rango."""
    return {k: v for k, v in qc_counts.items() if v > 0}


# ============================================================
# load_time_series - Carga serie temporal simple (3 columnas)
# ============================================================

def load_time_series(filepath, col_name):
    """
    Lee un CSV con formato: FECHA | HORA | VALOR.
    - Concatena fecha+hora → datetime
    - Convierte valor string → float (coma → punto)
    - Descarta filas inválidas y aplica control de calidad
    """
    # Lectura del archivo: separador punto y coma, encoding UTF-8
    df = pd.read_csv(
        filepath, sep=';', encoding='utf-8', header=0,
        usecols=[0, 1, 2],                          # Toma solo las 3 primeras columnas
        names=['FECHA', 'HORA', col_name],          # Renombra columnas
        skiprows=1, dtype=str                       # Salta encabezado original; lee como texto
    )

    # Limpieza: coma decimal → punto, elimina espacios
    df[col_name] = df[col_name].str.replace(',', '.').str.strip()
    # Conversión a numérico (errores → NaN)
    df[col_name] = pd.to_numeric(df[col_name], errors='coerce')

    # Elimina espacios en fecha y hora
    df['FECHA'] = df['FECHA'].str.strip()
    df['HORA'] = df['HORA'].str.strip()

    # Combina FECHA + HORA y parsea como datetime con formato YYMMDDHHMM
    df['datetime'] = pd.to_datetime(
        df['FECHA'] + df['HORA'],
        format='%y%m%d%H%M',
        errors='coerce'
    )

    # Descarta filas sin datetime o sin valor numérico válido
    df = df.dropna(subset=['datetime', col_name]).reset_index(drop=True)

    # Aplica control de calidad (valores fuera de rango → NaN)
    df = _apply_qc(df, col_name, QC_LIMITS.get(col_name, (None, None)))

    # Retorna solo las columnas de interés
    return df[['datetime', col_name]]


# ============================================================
# load_mp2_5 - Carga MP2.5 con prioridad de columnas
# ============================================================

def load_mp2_5():
    """
    El archivo MP2.5 contiene 3 columnas de datos:
      validado > preliminar > no_validado
    Toma el primer valor disponible en ese orden de prioridad.
    """
    # Lectura: 5 columnas (FECHA, HORA + 3 tipos de dato)
    df = pd.read_csv(
        FILE_MP, sep=';', encoding='utf-8', header=0,
        usecols=[0, 1, 2, 3, 4],
        names=['FECHA', 'HORA', 'validado', 'preliminar', 'no_validado'],
        skiprows=1, dtype=str
    )

    # Limpieza y conversión numérica de las 3 columnas de datos
    for col in ['validado', 'preliminar', 'no_validado']:
        df[col] = df[col].str.replace(',', '.').str.strip()
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df['FECHA'] = df['FECHA'].str.strip()
    df['HORA'] = df['HORA'].str.strip()

    # Construye datetime combinando fecha y hora
    df['datetime'] = pd.to_datetime(
        df['FECHA'] + df['HORA'],
        format='%y%m%d%H%M',
        errors='coerce'
    )

    # Prioridad: validado → preliminar → no_validado (fillna encadena)
    df['mp2_5'] = df['validado'].fillna(df['preliminar'].fillna(df['no_validado']))

    # Descarta registros sin datetime
    df = df.dropna(subset=['datetime']).reset_index(drop=True)

    # Aplica control de calidad
    df = _apply_qc(df, 'mp2_5', QC_LIMITS['mp2_5'])

    return df[['datetime', 'mp2_5']]


# ============================================================
# load_all_data - Carga y combina todas las variables
# ============================================================

def load_all_data():
    """
    Carga humedad, temperatura, viento y MP2.5 y las fusiona
    en un único DataFrame con outer join por datetime.
    Agrega columnas derivadas: year, month, day, hour, month_name.
    """
    hr = load_time_series(FILE_HR, 'humedad')      # Humedad relativa
    tc = load_time_series(FILE_TC, 'temperatura')  # Temperatura
    vv = load_time_series(FILE_VV, 'vel_viento')   # Velocidad del viento
    mp = load_mp2_5()                               # Material particulado 2.5

    # Merge secuencial (outer join para no perder registros)
    merged = pd.merge(hr, tc, on='datetime', how='outer')
    merged = pd.merge(merged, vv, on='datetime', how='outer')

    # Join con MP2.5 usando datetime como índice
    merged = merged.set_index('datetime').join(
        mp.set_index('datetime'), how='outer'
    ).reset_index()

    # Ordena cronológicamente
    merged = merged.sort_values('datetime').reset_index(drop=True)

    # Columnas derivadas de la fecha
    merged['year'] = merged['datetime'].dt.year            # Año
    merged['month'] = merged['datetime'].dt.month          # Mes (1-12)
    merged['day'] = merged['datetime'].dt.day              # Día del mes
    merged['hour'] = merged['datetime'].dt.hour            # Hora (0-23)
    merged['month_name'] = merged['datetime'].dt.month_name().str.slice(0, 3)  # Ene, Feb...

    return merged


# ============================================================
# filter_by_year_month - Filtra DataFrame por año y mes
# ============================================================

def filter_by_year_month(df, year, month=None):
    """
    Filtra filas según año y mes.
    - year='all' omite filtro de año
    - month='all' o month=None omite filtro de mes
    """
    conditions = []                                    # Acumula condiciones de filtro
    if year != 'all':                                  # Si hay año específico...
        conditions.append(f'year == {year}')           #   ...agrega condición
    if month is not None and month != 'all':           # Si hay mes específico...
        conditions.append(f'month == {month}')         #   ...agrega condición

    if conditions:                                     # Aplica filtro con query()
        return df.query(' and '.join(conditions)).copy().reset_index(drop=True)

    return df.copy().reset_index(drop=True)            # Sin filtro: copia sin modificar


# ============================================================
# resample_by - Remuestrea a frecuencia mayor (agregación)
# ============================================================

def resample_by(df, freq):
    """
    Agrupa datos por frecuencia temporal:
      H = Horario (sin cambio)
      D = Diario
      W = Semanal
      M = Mensual
      Y = Anual
    Promedia las columnas numéricas en cada ventana.
    """
    if freq == 'H':                                    # Horario → retorna igual
        return df
    elif freq == 'D':                                  # Diario
        return df.resample('D', on='datetime').mean(numeric_only=True).reset_index()
    elif freq == 'W':                                  # Semanal
        return df.resample('W', on='datetime').mean(numeric_only=True).reset_index()
    elif freq == 'M':                                  # Mensual
        return df.resample('ME', on='datetime').mean(numeric_only=True).reset_index()
    elif freq == 'Y':                                  # Anual
        return df.resample('YE', on='datetime').mean(numeric_only=True).reset_index()
    return df
