# ============================================================
# app.py - Punto de entrada del Dashboard
# ============================================================
# Crea la instancia de Dash, registra los callbacks, define
# el layout completo y ejecuta el servidor de desarrollo.
#
# Módulos del proyecto:
#   config.py      → Almacena datos de configuración pura sin lógica; la Paleta de Colores, estilos de líneas.
#   components.py  → Componentes UI reutilizables (cards, tablas, etc)
#   charts.py      → Constructures de figuras Plotly.
#   tabs.py        → Lógica Visual: df_raw, YEARS, build_tab_resumen, build_tab_dispersion
#   callbacks.py   → Lógica de interacción en el sistema.
#   data/          → carga y filtrado de datos CSV
#   assets/        → CSS e imágenes estáticas
# ============================================================

# --- Librerías externas ---
import dash                      # Framework principal
from dash import dcc, html       # Componentes Dash

# --- Módulos locales ---
from config import MONTHS        # Opciones fijas del selector de mes
from tabs import YEARS           # Años disponibles (derivado de los datos)
from callbacks import register_callbacks  # Registrador de callbacks


# ============================================================
# INICIALIZACIÓN DE LA APLICACIÓN
# ============================================================

app = dash.Dash(
    __name__,
    title='Monitor Calidad del Aire',
    suppress_callback_exceptions=True,
    update_title=None,
)


# ============================================================
# REGISTRO DE CALLBACKS
# ============================================================

register_callbacks(app)


# ============================================================
# LAYOUT - Estructura visual completa
# ============================================================

app.layout = html.Div([

    # --- Encabezado con logo y título ---
    html.Header([
        html.Div([
            html.Img(
                src='/assets/Escudo_Universidad_Aysén.png',
                className='header-logo',
            ),
            html.Div([
                html.H1('Monitor de Calidad del Aire'),
                html.P(
                    'Temperatura · Humedad · MP2.5 · Velocidad del Viento  |  2015 – 2026'
                ),
            ], className='header-text'),
            html.A(
                html.Img(
                    src='/assets/github-mark.svg',
                    className='header-gh-icon',
                ),
                href='https://github.com/martinabarca-chl/monitor_air_quality',
                target='_blank',
                title='Ver repositorio en GitHub',
                className='header-gh-link',
            ),
        ], className='header-content'),
    ], className='header'),

    # --- Filtros (año y mes) ---
    html.Section([
        html.Div([
            html.Div([
                html.Label('Año', className='filter-label'),
                dcc.Dropdown(
                    id='year-selector',
                    options=[{'label': 'Todos', 'value': 'all'}] +
                            [{'label': str(y), 'value': y} for y in YEARS],
                    value='all',
                    clearable=False,
                    className='filter-dropdown',
                ),
            ], className='filter-group'),

            html.Div([
                html.Label('Mes', className='filter-label'),
                dcc.Dropdown(
                    id='month-selector',
                    options=MONTHS,
                    value='all',
                    clearable=False,
                    className='filter-dropdown',
                ),
            ], className='filter-group'),
        ], className='filters-row'),
    ], className='filters-section'),

    # --- Barra de navegación con pestañas ---
    html.Nav([
        dcc.Tabs(
            id='main-tabs',
            value='tab-resumen',
            children=[
                dcc.Tab(
                    label='Resumen General',
                    value='tab-resumen',
                    className='tab',
                    selected_className='tab-selected',
                ),
                dcc.Tab(
                    label='Dispersión',
                    value='tab-dispersion',
                    className='tab',
                    selected_className='tab-selected',
                ),
            ],
        ),
    ], className='nav-bar'),

    # --- Contenido principal (se renderiza según pestaña activa) ---
    html.Main(
        [html.Div(id='tab-content')],
        className='main-content',
    ),

    # --- Pie de página ---
    html.Footer([
        html.P(
            'Datos: Sistema de Información Nacional de Calidad del Aire (SINCA) · '
            'Estación Los Andes, Región de Valparaíso'
        ),
        html.A(
            'sinca.mma.gob.cl',
            href='https://sinca.mma.gob.cl/index.php/estacion/index/id/238',
            target='_blank',
            className='footer-link',
        ),
    ], className='footer'),

], className='app-container')


# ============================================================
# PUNTO DE ENTRADA
# ============================================================

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8050)
