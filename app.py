import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

from data.load_data import load_all_data, filter_by_year_month, resample_by

CB = {
    'blue': '#0077BB',
    'cyan': '#33BBEE',
    'teal': '#009988',
    'orange': '#EE7733',
    'red': '#CC3311',
    'magenta': '#EE3377',
    'grey': '#BBBBBB',
    'dark': '#333333',
}

df_raw = load_all_data()

YEARS = sorted(df_raw['year'].unique())
MONTHS = [
    {'label': 'Todos', 'value': 'all'},
    {'label': 'Enero', 'value': 1}, {'label': 'Febrero', 'value': 2},
    {'label': 'Marzo', 'value': 3}, {'label': 'Abril', 'value': 4},
    {'label': 'Mayo', 'value': 5}, {'label': 'Junio', 'value': 6},
    {'label': 'Julio', 'value': 7}, {'label': 'Agosto', 'value': 8},
    {'label': 'Septiembre', 'value': 9}, {'label': 'Octubre', 'value': 10},
    {'label': 'Noviembre', 'value': 11}, {'label': 'Diciembre', 'value': 12},
]

app = dash.Dash(
    __name__,
    title='Monitor Calidad del Aire',
    suppress_callback_exceptions=True,
    update_title=None,
)

app.layout = html.Div([
    html.Header([
        html.Div([
            html.Img(src='/assets/Escudo_Universidad_Aysén.png', className='header-logo'),
            html.Div([
                html.H1('Monitor de Calidad del Aire'),
                html.P('Temperatura · Humedad · MP2.5 · Velocidad del Viento  |  2015 – 2026'),
            ], className='header-text'),
        ], className='header-content'),
    ], className='header'),
    html.Section([
        html.Div([
            html.Div([
                html.Label('Año', className='filter-label'),
                dcc.Dropdown(
                    id='year-selector',
                    options=[{'label': 'Todos', 'value': 'all'}] + [{'label': str(y), 'value': y} for y in YEARS],
                    value='all', clearable=False, className='filter-dropdown',
                ),
            ], className='filter-group'),
            html.Div([
                html.Label('Mes', className='filter-label'),
                dcc.Dropdown(
                    id='month-selector', options=MONTHS,
                    value='all', clearable=False, className='filter-dropdown',
                ),
            ], className='filter-group'),
        ], className='filters-row'),
    ], className='filters-section'),
    html.Nav([
        dcc.Tabs(id='main-tabs', value='tab-resumen', children=[
            dcc.Tab(label='Resumen General', value='tab-resumen',
                    className='tab', selected_className='tab-selected'),
            dcc.Tab(label='Dispersión', value='tab-dispersion',
                    className='tab', selected_className='tab-selected'),
        ]),
    ], className='nav-bar'),
    html.Main([html.Div(id='tab-content')], className='main-content'),
    html.Footer([
        html.P('Datos: Sistema de Información Nacional de Calidad del Aire (SINCA) · '
               'Estación Los Andes, Región de Valparaíso'),
        html.A('sinca.mma.gob.cl', href='https://sinca.mma.gob.cl/index.php/estacion/index/id/238',
               target='_blank', className='footer-link'),
    ], className='footer'),
], className='app-container')

def kpi_card(title, value, subtitle='', color=CB['blue']):
    return html.Div([
        html.H4(title, className='kpi-title'),
        html.P(value, className='kpi-value', style={'color': color}),
        html.Small(subtitle, className='kpi-subtitle'),
    ], className='kpi-card')

def narrative_box(text):
    return html.Div([
        html.Div([
            html.Span('i', className='narrative-icon'),
            html.P(text, className='narrative-text'),
        ], className='narrative-inner'),
    ], className='narrative-box')

def section_title(text):
    return html.H3(text, className='section-title')

DASH_STYLES = ['solid', 'dash', 'dot', 'dashdot']


def build_line_fig(df, y_cols, title, y_label, colors=None):
    fig = go.Figure()
    if colors is None:
        colors = [CB['blue'], CB['red'], CB['teal'], CB['orange']]
    for i, col in enumerate(y_cols):
        fig.add_trace(go.Scatter(
            x=df['datetime'], y=df[col], mode='lines',
            name=col, line=dict(color=colors[i % len(colors)], width=2,
                                dash=DASH_STYLES[i % len(DASH_STYLES)]),
            hovertemplate=f'%{{y:.2f}}<extra>{col}</extra>',
        ))
    fig.update_layout(
        title=title, xaxis_title='', yaxis_title=y_label,
        hovermode='x unified', margin=dict(l=50, r=20, t=40, b=40),
        font_family='Segoe UI, Arial, sans-serif', plot_bgcolor='#f8f9fa',
        legend=dict(orientation='v', y=0.98, x=1.02, xanchor='left', yanchor='top',
                    bgcolor='rgba(255,255,255,0.8)', bordercolor='#d0d5db', borderwidth=1),
    )
    fig.update_xaxes(showgrid=True, gridcolor='#d0d5db')
    fig.update_yaxes(showgrid=True, gridcolor='#d0d5db')
    return fig


def build_tab_resumen(year, month):
    df = filter_by_year_month(df_raw, year, month)
    month_names = {1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr', 5: 'May', 6: 'Jun',
                   7: 'Jul', 8: 'Ago', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'}
    if year == 'all':
        period_label = 'Todos los años'
    else:
        period_label = f'{year}'
    if month and month != 'all':
        period_label += f' · {month_names[month]}'

    temp_mean = df['temperatura'].mean()
    temp_min = df['temperatura'].min()
    temp_max = df['temperatura'].max()
    hum_mean = df['humedad'].mean()
    mp_mean = df['mp2_5'].mean()
    mp_max = df['mp2_5'].max()
    vv_mean = df['vel_viento'].mean()

    kpis = html.Div([
        kpi_card('Temp. Promedio', f'{temp_mean:.1f} °C' if pd.notna(temp_mean) else '—',
                 f'Mín: {temp_min:.1f} · Máx: {temp_max:.1f}', CB['red']),
        kpi_card('Humedad Promedio', f'{hum_mean:.1f} %' if pd.notna(hum_mean) else '—',
                 '', CB['blue']),
        kpi_card('MP2.5 Promedio', f'{mp_mean:.1f} µg/m³' if pd.notna(mp_mean) else '—',
                 f'Máx: {mp_max:.1f}', CB['orange']),
        kpi_card('Viento Promedio', f'{vv_mean:.2f} m/s' if pd.notna(vv_mean) else '—',
                 f'{len(df):,} registros', CB['teal']),
    ], className='kpi-grid')

    peak_hour = df.groupby('hour')['mp2_5'].mean().idxmax()
    peak_hour_val = df.groupby('hour')['mp2_5'].mean().max()

    hourly = df.groupby('hour')['mp2_5'].mean().reset_index()
    colors_hour = [CB['orange'] if h == peak_hour else CB['grey'] for h in hourly['hour']]
    fig_hourly = go.Figure()
    fig_hourly.add_trace(go.Bar(
        x=hourly['hour'], y=hourly['mp2_5'],
        marker_color=colors_hour,
        hovertemplate='%{x}:00 h · %{y:.1f} µg/m³<extra></extra>',
        showlegend=False,
    ))
    fig_hourly.update_layout(
        title=dict(
            text=f'MP2.5 Promedio por Hora · Pico a las {peak_hour}:00 h ({peak_hour_val:.1f} µg/m³)',
            font=dict(size=13, color=CB['dark']),
        ),
        xaxis=dict(tickmode='array', tickvals=list(range(0, 24, 3)),
                   ticktext=[f'{h}:00' for h in range(0, 24, 3)]),
        yaxis_title='MP2.5 (µg/m³)',
        yaxis=dict(rangemode='tozero'),
        hovermode='x', margin=dict(l=50, r=20, t=40, b=40),
        font_family='Segoe UI, Arial, sans-serif', plot_bgcolor='#f8f9fa',
    )
    fig_hourly.update_xaxes(showgrid=True, gridcolor='#d0d5db')
    fig_hourly.update_yaxes(showgrid=True, gridcolor='#d0d5db')
    fig_hourly.update_traces(marker_line_width=0)

    monthly = df.groupby('month')['mp2_5'].mean().reset_index()
    colors_month = [CB['blue'], CB['cyan'], CB['teal'], CB['orange'], CB['red'], CB['magenta']]
    fig_monthly = go.Figure()
    fig_monthly.add_trace(go.Bar(
        x=monthly['month'], y=monthly['mp2_5'],
        marker_color=[colors_month[(m - 1) % len(colors_month)] for m in monthly['month']],
        hovertemplate='%{x} · %{y:.1f} µg/m³<extra></extra>',
        showlegend=False,
    ))
    fig_monthly.update_layout(
        title=dict(
            text='MP2.5 Promedio por Mes',
            font=dict(size=13, color=CB['dark']),
        ),
        xaxis=dict(tickmode='array',
                   tickvals=list(range(1, 13)),
                   ticktext=[month_names[m] for m in range(1, 13)]),
        yaxis_title='MP2.5 (µg/m³)',
        yaxis=dict(rangemode='tozero'),
        hovermode='x', margin=dict(l=50, r=20, t=40, b=40),
        font_family='Segoe UI, Arial, sans-serif', plot_bgcolor='#f8f9fa',
    )
    fig_monthly.update_xaxes(showgrid=True, gridcolor='#d0d5db')
    fig_monthly.update_yaxes(showgrid=True, gridcolor='#d0d5db')
    fig_monthly.update_traces(marker_line_width=0)

    return html.Div([
        narrative_box(
            f'Resumen del período {period_label}. Los indicadores y gráficos se actualizan '
            'automáticamente al cambiar el año o mes en los filtros superiores.'
        ),
        kpis,
        html.Div([
            html.Div([dcc.Graph(figure=fig_hourly, config={'displayModeBar': False})], className='card'),
            html.Div([dcc.Graph(figure=fig_monthly, config={'displayModeBar': False})], className='card'),
        ], className='two-column'),
        html.Div([
            html.Div([
                html.Label('Agregación:', className='control-label'),
                dcc.Dropdown(
                    id='agg-selector',
                    options=[
                        {'label': 'Horario', 'value': 'H'},
                        {'label': 'Diario', 'value': 'D'},
                        {'label': 'Semanal', 'value': 'W'},
                        {'label': 'Mensual', 'value': 'M'},
                    ],
                    value='D', clearable=False, className='control-dropdown',
                ),
            ], className='control-group'),
        ], className='controls-row'),
        html.Div([
            html.Div([section_title('Temperatura y MP2.5'), dcc.Graph(id='evol-temp-mp', config={'displayModeBar': False})], className='card'),
            html.Div([section_title('Humedad y Viento'), dcc.Graph(id='evol-hum-vv', config={'displayModeBar': False})], className='card'),
        ], className='two-column'),
    ])


def build_tab_dispersion(year, month):
    df = filter_by_year_month(df_raw, year, month)
    if year == 'all':
        period_label = 'Todos los años'
    else:
        period_label = f'{year}'
    if month and month != 'all':
        month_names = {1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr', 5: 'May', 6: 'Jun',
                       7: 'Jul', 8: 'Ago', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'}
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


TAB_BUILDERS = {
    'tab-resumen': build_tab_resumen,
    'tab-dispersion': build_tab_dispersion,
}


@app.callback(
    Output('tab-content', 'children'),
    Input('main-tabs', 'value'),
    Input('year-selector', 'value'),
    Input('month-selector', 'value'),
)
def render_tab(tab_value, year, month):
    builder = TAB_BUILDERS.get(tab_value)
    if builder:
        return builder(year, month)
    return html.Div()


@app.callback(
    Output('evol-temp-mp', 'figure'),
    Input('agg-selector', 'value'),
    Input('year-selector', 'value'),
    Input('month-selector', 'value'),
)
def update_evol_temp_mp(agg, year, month):
    df = filter_by_year_month(df_raw, year, month)
    df = resample_by(df, agg)
    fig = build_line_fig(
        df, ['temperatura', 'mp2_5'], 'Temperatura y MP2.5',
        'Valor', [CB['red'], CB['orange']]
    )
    fig.update_traces(selector=dict(name='temperatura'), hovertemplate='%{y:.1f} °C<extra>Temperatura</extra>')
    fig.update_traces(selector=dict(name='mp2_5'), hovertemplate='%{y:.1f} µg/m³<extra>MP2.5</extra>')
    return fig


@app.callback(
    Output('evol-hum-vv', 'figure'),
    Input('agg-selector', 'value'),
    Input('year-selector', 'value'),
    Input('month-selector', 'value'),
)
def update_evol_hum_vv(agg, year, month):
    df = filter_by_year_month(df_raw, year, month)
    df = resample_by(df, agg)
    fig = build_line_fig(
        df, ['humedad', 'vel_viento'], 'Humedad y Velocidad del Viento',
        'Valor', [CB['blue'], CB['teal']]
    )
    fig.update_traces(selector=dict(name='humedad'), hovertemplate='%{y:.1f} %<extra>Humedad</extra>')
    fig.update_traces(selector=dict(name='vel_viento'), hovertemplate='%{y:.2f} m/s<extra>Viento</extra>')
    return fig


def scatter_with_trend(df, x, y, xlabel, ylabel, color):
    df = df[[x, y]].dropna()
    if len(df) > 3000:
        df = df.sample(n=3000, random_state=42)
    fig = go.Figure()
    fig.add_trace(go.Scattergl(
        x=df[x], y=df[y], mode='markers',
        marker=dict(color=color, size=4, opacity=0.35),
        name='Datos',
        hovertemplate=f'%{{x:.2f}}<br>%{{y:.2f}}<extra></extra>',
    ))
    if len(df) > 5:
        slope, intercept = np.polyfit(df[x], df[y], 1)
        x_range = np.linspace(df[x].min(), df[x].max(), 50)
        fig.add_trace(go.Scatter(
            x=x_range, y=slope * x_range + intercept,
            mode='lines', name='Tendencia',
            line=dict(color=CB['dark'], width=2, dash='dash'),
        ))
        r_val = df[x].corr(df[y])
        annotation = f'r = {r_val:.3f}'
    else:
        annotation = ''

    fig.update_layout(
        title=f'{ylabel} vs {xlabel}',
        xaxis_title=xlabel, yaxis_title=ylabel,
        yaxis=dict(rangemode='tozero'),
        hovermode='closest', margin=dict(l=50, r=20, t=40, b=40),
        font_family='Segoe UI, Arial, sans-serif', plot_bgcolor='#f8f9fa',
        annotations=[
            dict(x=0.02, y=0.98, xref='paper', yref='paper', text=annotation,
                 showarrow=False, font=dict(size=13, color=CB['dark']),
                 bgcolor='white', bordercolor='#adb5bd', borderwidth=1)
        ] if annotation else [],
    )
    fig.update_xaxes(showgrid=True, gridcolor='#d0d5db')
    fig.update_yaxes(showgrid=True, gridcolor='#d0d5db')
    return fig


@app.callback(
    Output('disp-temp', 'figure'),
    Input('year-selector', 'value'),
    Input('month-selector', 'value'),
)
def update_disp_temp(year, month):
    df = filter_by_year_month(df_raw, year, month)
    return scatter_with_trend(df, 'temperatura', 'mp2_5',
                              'Temperatura (°C)', 'MP2.5 (µg/m³)', CB['red'])


@app.callback(
    Output('disp-hum', 'figure'),
    Input('year-selector', 'value'),
    Input('month-selector', 'value'),
)
def update_disp_hum(year, month):
    df = filter_by_year_month(df_raw, year, month)
    return scatter_with_trend(df, 'humedad', 'mp2_5',
                              'Humedad Relativa (%)', 'MP2.5 (µg/m³)', CB['blue'])


@app.callback(
    Output('disp-viento', 'figure'),
    Input('year-selector', 'value'),
    Input('month-selector', 'value'),
)
def update_disp_viento(year, month):
    df = filter_by_year_month(df_raw, year, month)
    return scatter_with_trend(df, 'vel_viento', 'mp2_5',
                              'Velocidad del Viento (m/s)', 'MP2.5 (µg/m³)', CB['teal'])


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8050)
