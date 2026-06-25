import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

FILE_HR = BASE_DIR / "hR_150101_260624.csv"
FILE_TC = BASE_DIR / "tC_150101_260624.csv"
FILE_MP = BASE_DIR / "mp2.5_150101_260624.csv"
FILE_VV = BASE_DIR / "vV_150101_260624.csv"

QC_LIMITS = {
    'temperatura':  (None, 45),
    'humedad':      (0, 100),
    'vel_viento':   (None, 30),
    'mp2_5':        (0, 500),
}

qc_counts = {}


def _apply_qc(df, col, limits):
    lo, hi = limits
    mask = pd.Series(False, index=df.index)
    if lo is not None:
        mask |= (df[col] < lo)
    if hi is not None:
        mask |= (df[col] > hi)
    n = mask.sum()
    if n:
        qc_counts[col] = qc_counts.get(col, 0) + n
        df.loc[mask, col] = None
    return df


def get_qc_summary():
    return {k: v for k, v in qc_counts.items() if v > 0}


def load_time_series(filepath, col_name):
    df = pd.read_csv(
        filepath, sep=';', encoding='utf-8', header=0,
        usecols=[0, 1, 2], names=['FECHA', 'HORA', col_name],
        skiprows=1, dtype=str
    )
    df[col_name] = df[col_name].str.replace(',', '.').str.strip()
    df[col_name] = pd.to_numeric(df[col_name], errors='coerce')
    df['FECHA'] = df['FECHA'].str.strip()
    df['HORA'] = df['HORA'].str.strip()
    df['datetime'] = pd.to_datetime(df['FECHA'] + df['HORA'], format='%y%m%d%H%M', errors='coerce')
    df = df.dropna(subset=['datetime', col_name]).reset_index(drop=True)
    df = _apply_qc(df, col_name, QC_LIMITS.get(col_name, (None, None)))
    return df[['datetime', col_name]]


def load_mp2_5():
    df = pd.read_csv(
        FILE_MP, sep=';', encoding='utf-8', header=0,
        usecols=[0, 1, 2, 3, 4],
        names=['FECHA', 'HORA', 'validado', 'preliminar', 'no_validado'],
        skiprows=1, dtype=str
    )
    for col in ['validado', 'preliminar', 'no_validado']:
        df[col] = df[col].str.replace(',', '.').str.strip()
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df['FECHA'] = df['FECHA'].str.strip()
    df['HORA'] = df['HORA'].str.strip()
    df['datetime'] = pd.to_datetime(df['FECHA'] + df['HORA'], format='%y%m%d%H%M', errors='coerce')
    df['mp2_5'] = df['validado'].fillna(df['preliminar'].fillna(df['no_validado']))
    df = df.dropna(subset=['datetime']).reset_index(drop=True)
    df = _apply_qc(df, 'mp2_5', QC_LIMITS['mp2_5'])
    return df[['datetime', 'mp2_5']]


def load_all_data():
    hr = load_time_series(FILE_HR, 'humedad')
    tc = load_time_series(FILE_TC, 'temperatura')
    vv = load_time_series(FILE_VV, 'vel_viento')
    mp = load_mp2_5()
    merged = pd.merge(hr, tc, on='datetime', how='outer')
    merged = pd.merge(merged, vv, on='datetime', how='outer')
    merged = merged.set_index('datetime').join(mp.set_index('datetime'), how='outer').reset_index()
    merged = merged.sort_values('datetime').reset_index(drop=True)
    merged['year'] = merged['datetime'].dt.year
    merged['month'] = merged['datetime'].dt.month
    merged['day'] = merged['datetime'].dt.day
    merged['hour'] = merged['datetime'].dt.hour
    merged['month_name'] = merged['datetime'].dt.month_name().str.slice(0, 3)
    return merged


def filter_by_year_month(df, year, month=None):
    conditions = []
    if year != 'all':
        conditions.append(f'year == {year}')
    if month is not None and month != 'all':
        conditions.append(f'month == {month}')
    if conditions:
        return df.query(' and '.join(conditions)).copy().reset_index(drop=True)
    return df.copy().reset_index(drop=True)


def resample_by(df, freq):
    if freq == 'H':
        return df
    elif freq == 'D':
        return df.resample('D', on='datetime').mean(numeric_only=True).reset_index()
    elif freq == 'W':
        return df.resample('W', on='datetime').mean(numeric_only=True).reset_index()
    elif freq == 'M':
        return df.resample('ME', on='datetime').mean(numeric_only=True).reset_index()
    elif freq == 'Y':
        return df.resample('YE', on='datetime').mean(numeric_only=True).reset_index()
    return df
