# ============================================================
# tabs.py - Constructores de pestañas del dashboard
# ============================================================
# Define el contenido completo de cada pestaña (Resumen General
# y Dispersión). Carga los datos al importar el módulo y
# exporta las funciones constructoras y el mapa TAB_BUILDERS.
# ============================================================

import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html

from config import CB, MONTHS
from components import kpi_card, narrative_box, section_title
from charts import build_line_fig, scatter_with_trend
from data.load_data import load_all_data, filter_by_year_month, resample_by


# ============================================================
# CARGA DE DATOS (una sola vez al importar el módulo)
# ============================================================

df_raw = load_all_data()


# ============================================================
# CONSTANTES DERIVADAS DE LOS DATOS
# ============================================================

YEARS = sorted(df_raw['year'].unique())


# ============================================================
# PESTAÑA: RESUMEN GENERAL
# ============================================================

def build_tab_resumen(year, month):
    """
    Construye el contenido de la pestaña 'Resumen General'.
    Incluye KPIs, gráfico MP2.5 por hora, tabla de información
    del medidor con Google Maps, y gráficos de evolución temporal.
    """
    # --- Filtro según selector de año y mes ---
    df = filter_by_year_month(df_raw, year, month)

    # --- Nombres cortos de meses para etiquetas ---
    month_names = {
        1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr', 5: 'May', 6: 'Jun',
        7: 'Jul', 8: 'Ago', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic',
    }

    # --- Etiqueta del período para la caja narrativa ---
    if year == 'all':
        period_label = 'Todos los años'
    else:
        period_label = f'{year}'
    if month and month != 'all':
        period_label += f' · {month_names[month]}'

    # --- Estadísticas descriptivas para KPIs ---
    temp_mean = df['temperatura'].mean()
    temp_min  = df['temperatura'].min()
    temp_max  = df['temperatura'].max()
    hum_mean  = df['humedad'].mean()
    mp_mean   = df['mp2_5'].mean()
    mp_max    = df['mp2_5'].max()
    vv_mean   = df['vel_viento'].mean()

    # --- Tarjetas KPI ---
    kpis = html.Div([
        kpi_card(
            'Temp. Promedio',
            f'{temp_mean:.1f} °C' if pd.notna(temp_mean) else '—',
            f'Mín: {temp_min:.1f} · Máx: {temp_max:.1f}',
            CB['red'],
        ),
        kpi_card(
            'Humedad Promedio',
            f'{hum_mean:.1f} %' if pd.notna(hum_mean) else '—',
            '',
            CB['blue'],
        ),
        kpi_card(
            'MP2.5 Promedio',
            f'{mp_mean:.1f} µg/m³' if pd.notna(mp_mean) else '—',
            f'Máx: {mp_max:.1f}',
            CB['orange'],
        ),
        kpi_card(
            'Viento Promedio',
            f'{vv_mean:.2f} m/s' if pd.notna(vv_mean) else '—',
            f'{len(df):,} registros',
            CB['teal'],
        ),
    ], className='kpi-grid')

    # --- Gráfico: MP2.5 promedio por hora ---
    if not df.empty:
        peak_hour = df.groupby('hour')['mp2_5'].mean().idxmax()
        peak_hour_val = df.groupby('hour')['mp2_5'].mean().max()

        hourly = df.groupby('hour')['mp2_5'].mean().reset_index()
        colors_hour = [CB['orange'] if h == peak_hour else CB['grey'] for h in hourly['hour']]

        fig_hourly = go.Figure()
        fig_hourly.add_trace(go.Bar(
            x=hourly['hour'],
            y=hourly['mp2_5'],
            marker_color=colors_hour,
            hovertemplate='%{x}:00 h · %{y:.1f} µg/m³<extra></extra>',
            showlegend=False,
        ))
        fig_hourly.update_layout(
            title=dict(
                text=(
                    f'MP2.5 Promedio por Hora · Pico a las {peak_hour}:00 h '
                    f'({peak_hour_val:.1f} µg/m³)'
                ),
                font=dict(size=13, color=CB['dark']),
            ),
            xaxis=dict(
                tickmode='array',
                tickvals=list(range(0, 24, 3)),
                ticktext=[f'{h}:00' for h in range(0, 24, 3)],
            ),
            yaxis_title='MP2.5 (µg/m³)',
            yaxis=dict(rangemode='tozero'),
            hovermode='x',
            margin=dict(l=50, r=20, t=40, b=40),
            font_family='Segoe UI, Arial, sans-serif',
            plot_bgcolor='#f8f9fa',
        )
        fig_hourly.update_xaxes(showgrid=True, gridcolor='#d0d5db')
        fig_hourly.update_yaxes(showgrid=True, gridcolor='#d0d5db')
        fig_hourly.update_traces(marker_line_width=0)
        hourly_graph = dcc.Graph(figure=fig_hourly, config={'displayModeBar': False})
    else:
        hourly_graph = html.Div(
            html.P('Sin datos para el período seleccionado.',
                   style={'text-align': 'center', 'padding': '40px', 'color': '#6c757d'}),
        )

    # --- Información General del Medidor ---
    info_data = [
        ('Propietario', 'Ministerio del Medio Ambiente'),
        ('Operador', 'Algoritmos y Mediciones Ambientales SpA'),
        ('Región', 'Aysén del General Carlos Ibáñez del Campo'),
        ('Comuna', 'Coyhaique'),
        ('Coordenadas UTM', '729281 E  4948421 N'),
        ('Recepción de datos', 'en línea'),
        ('Inicio de operación', '2007-03-01'),
    ]

    info_rows = []
    for label, value in info_data:
        info_rows.append(html.Tr([
            html.Td(label, className='info-label'),
            html.Td(value, className='info-value'),
        ]))

    info_table = html.Table(info_rows, className='info-table')

    # --- Ensamblaje del layout de la pestaña ---
    return html.Div([
        narrative_box(
            f'Resumen del período {period_label}. Los indicadores y gráficos se actualizan '
            'automáticamente al cambiar el año o mes en los filtros superiores.'
        ),
        kpis,
        html.Div([
            html.Div([hourly_graph], className='card'),
            html.Div([
                section_title('Información General'),
                info_table,
                html.Iframe(
                    src='https://www.google.com/maps?q=-45.5795528,-72.0619082&z=14&output=embed',
                    width='100%',
                    height='300',
                    style={'border': 0, 'margin-top': '14px', 'border-radius': '8px'},
                ),
            ], className='card'),
        ], className='two-column'),
        html.Div([
            html.Div([
                html.Label('Agregación:', className='control-label'),
                dcc.Dropdown(
                    id='agg-selector',
                    options=[
                        {'label': 'Horario',  'value': 'H'},
                        {'label': 'Diario',   'value': 'D'},
                        {'label': 'Semanal',  'value': 'W'},
                        {'label': 'Mensual',  'value': 'M'},
                    ],
                    value='D',
                    clearable=False,
                    className='control-dropdown',
                ),
            ], className='control-group'),
        ], className='controls-row'),
        html.Div([
            html.Div([
                section_title('Temperatura y MP2.5'),
                dcc.Graph(id='evol-temp-mp', config={'displayModeBar': False}),
            ], className='card'),
            html.Div([
                section_title('Humedad y Viento'),
                dcc.Graph(id='evol-hum-vv', config={'displayModeBar': False}),
            ], className='card'),
        ], className='two-column'),
    ])


# ============================================================
# PESTAÑA: DISPERSIÓN
# ============================================================

def build_tab_dispersion(year, month):
    """
    Construye el contenido de la pestaña 'Dispersión'.
    Muestra gráficos de dispersión con línea de tendencia
    entre MP2.5 y cada variable meteorológica.
    """
    df = filter_by_year_month(df_raw, year, month)

    # --- Etiqueta del período ---
    if year == 'all':
        period_label = 'Todos los años'
    else:
        period_label = f'{year}'
    if month and month != 'all':
        month_names = {
            1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr', 5: 'May', 6: 'Jun',
            7: 'Jul', 8: 'Ago', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic',
        }
        period_label += f' · {month_names[month]}'

    return html.Div([
        narrative_box(
            'Gráficos de dispersión que relacionan el MP2.5 con temperatura, humedad y '
            'velocidad del viento. Cada punto representa una medición horaria. '
            'La línea de tendencia ayuda a visualizar la correlación entre variables.'
        ),
        html.Div([
            html.Div([
                dcc.Graph(id='disp-temp', config={'displayModeBar': False}),
            ], className='card'),
            html.Div([
                dcc.Graph(id='disp-hum', config={'displayModeBar': False}),
            ], className='card'),
        ], className='two-column'),
        html.Div([
            dcc.Graph(id='disp-viento', config={'displayModeBar': False}),
        ], className='card'),
    ])


# ============================================================
# MAPA DE PESTAÑAS A FUNCIONES CONSTRUCTORAS
# ============================================================

TAB_BUILDERS = {
    'tab-resumen':    build_tab_resumen,
    'tab-dispersion': build_tab_dispersion,
}
