# ============================================================
# components.py - Componentes UI reutilizables
# ============================================================
# Funciones que generan fragmentos de layout Dash (tarjetas
# KPI, caja narrativa, títulos de sección). Se usan desde
# los constructores de pestañas (tabs.py).
# ============================================================

from dash import html

from config import CB


def kpi_card(title, value, subtitle='', color=CB['blue']):
    """
    Crea una tarjeta KPI (indicador) con título, valor y subtítulo.
    - title:    etiqueta del indicador (ej. 'Temp. Promedio')
    - value:    valor numérico formateado (ej. '12.5 °C')
    - subtitle: texto secundario (mín/máx, cantidad de registros)
    - color:    color del valor (por defecto azul CB)
    """
    return html.Div([
        html.H4(title, className='kpi-title'),
        html.P(value, className='kpi-value', style={'color': color}),
        html.Small(subtitle, className='kpi-subtitle'),
    ], className='kpi-card')


def narrative_box(text):
    """
    Crea una caja de texto informativo con ícono 'i' circular.
    - text: contenido explicativo en una sola línea o párrafo.
    """
    return html.Div([
        html.Div([
            html.Span('i', className='narrative-icon'),
            html.P(text, className='narrative-text'),
        ], className='narrative-inner'),
    ], className='narrative-box')


def section_title(text):
    """
    Crea un título de sección con línea decorativa inferior
    (borde azul). Ideal para encabezar gráficos o tablas.
    """
    return html.H3(text, className='section-title')
