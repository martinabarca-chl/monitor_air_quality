# ============================================================
# charts.py - Constructores de gráficos Plotly
# ============================================================
# Funciones que crean figuras Plotly reutilizables:
#   - build_line_fig:    gráfico de líneas con 1+ series
#   - scatter_with_trend: dispersión con recta de regresión
# ============================================================

import numpy as np
import plotly.graph_objects as go

from config import CB, DASH_STYLES


def build_line_fig(df, y_cols, title, y_label, colors=None):
    """
    Construye un gráfico de líneas con una o más series temporales.
    - df:      DataFrame con columna 'datetime' y las columnas en y_cols
    - y_cols:  lista de nombres de columnas a graficar
    - title:   texto del título del gráfico
    - y_label: etiqueta del eje Y
    - colors:  lista de colores (opcional, usa CB por defecto)
    """
    fig = go.Figure()

    if colors is None:
        colors = [CB['blue'], CB['red'], CB['teal'], CB['orange']]

    for i, col in enumerate(y_cols):
        fig.add_trace(go.Scatter(
            x=df['datetime'],
            y=df[col],
            mode='lines',
            name=col,
            line=dict(
                color=colors[i % len(colors)],
                width=2,
                dash=DASH_STYLES[i % len(DASH_STYLES)],
            ),
            hovertemplate=f'%{{y:.2f}}<extra>{col}</extra>',
        ))

    fig.update_layout(
        title=title,
        xaxis_title='',
        yaxis_title=y_label,
        hovermode='x unified',
        margin=dict(l=50, r=20, t=40, b=40),
        font_family='Segoe UI, Arial, sans-serif',
        plot_bgcolor='#f8f9fa',
        legend=dict(
            orientation='v',
            y=0.98, x=1.02,
            xanchor='left', yanchor='top',
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='#d0d5db', borderwidth=1,
        ),
    )

    fig.update_xaxes(showgrid=True, gridcolor='#d0d5db')
    fig.update_yaxes(showgrid=True, gridcolor='#d0d5db')

    return fig


def scatter_with_trend(df, x, y, xlabel, ylabel, color):
    """
    Gráfico de dispersión con línea de tendencia lineal.
    - Muestra hasta 3000 puntos aleatorios si hay más (rendimiento).
    - Calcula correlación de Pearson (r) y pendiente (polyfit).
    """
    df = df[[x, y]].dropna()

    if len(df) > 3000:
        df = df.sample(n=3000, random_state=42)

    fig = go.Figure()

    fig.add_trace(go.Scattergl(
        x=df[x], y=df[y],
        mode='markers',
        marker=dict(color=color, size=4, opacity=0.35),
        name='Datos',
        hovertemplate=f'%{{x:.2f}}<br>%{{y:.2f}}<extra></extra>',
    ))

    if len(df) > 5:
        slope, intercept = np.polyfit(df[x], df[y], 1)
        x_range = np.linspace(df[x].min(), df[x].max(), 50)
        fig.add_trace(go.Scatter(
            x=x_range,
            y=slope * x_range + intercept,
            mode='lines',
            name='Tendencia',
            line=dict(color=CB['dark'], width=2, dash='dash'),
        ))
        r_val = df[x].corr(df[y])
        annotation = f'r = {r_val:.3f}'
    else:
        annotation = ''

    fig.update_layout(
        title=f'{ylabel} vs {xlabel}',
        xaxis_title=xlabel,
        yaxis_title=ylabel,
        yaxis=dict(rangemode='tozero'),
        hovermode='closest',
        margin=dict(l=50, r=20, t=40, b=40),
        font_family='Segoe UI, Arial, sans-serif',
        plot_bgcolor='#f8f9fa',
        annotations=[
            dict(
                x=0.02, y=0.98, xref='paper', yref='paper',
                text=annotation,
                showarrow=False,
                font=dict(size=13, color=CB['dark']),
                bgcolor='white',
                bordercolor='#adb5bd',
                borderwidth=1,
            )
        ] if annotation else [],
    )

    fig.update_xaxes(showgrid=True, gridcolor='#d0d5db')
    fig.update_yaxes(showgrid=True, gridcolor='#d0d5db')

    return fig
