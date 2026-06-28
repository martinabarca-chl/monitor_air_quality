# ============================================================
# config.py - Configuración visual y constantes del dashboard
# ============================================================
# Contiene la paleta de colores, estilos de línea y las
# opciones fijas de los selectores (meses).
# ============================================================

# --- Paleta de colores CB (Color Blind friendly) ---
# Colores diseñados para ser distinguibles por personas
# con daltonismo (Color Universal Design).
CB = {
    'blue':    '#0077BB',
    'cyan':    '#33BBEE',
    'teal':    '#009988',
    'orange':  '#EE7733',
    'red':     '#CC3311',
    'magenta': '#EE3377',
    'grey':    '#BBBBBB',
    'dark':    '#333333',
}

# --- Estilos de línea para gráficos multi-traza ---
# Permite diferenciar series aunque compartan color.
DASH_STYLES = ['solid', 'dash', 'dot', 'dashdot']

# --- Opciones del selector de mes ---
# Incluye "Todos" como opción por defecto; el resto sigue
# el orden calendario estándar con nombre en español.
MONTHS = [
    {'label': 'Todos', 'value': 'all'},
    {'label': 'Enero',    'value': 1}, {'label': 'Febrero',  'value': 2},
    {'label': 'Marzo',    'value': 3}, {'label': 'Abril',    'value': 4},
    {'label': 'Mayo',     'value': 5}, {'label': 'Junio',    'value': 6},
    {'label': 'Julio',    'value': 7}, {'label': 'Agosto',   'value': 8},
    {'label': 'Septiembre','value': 9}, {'label': 'Octubre', 'value': 10},
    {'label': 'Noviembre', 'value': 11}, {'label': 'Diciembre','value': 12},
]
