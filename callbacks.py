# ============================================================
# callbacks.py - Lógica de interacción (callbacks Dash)
# ============================================================
# Define todos los @app.callback del dashboard dentro de la
# función register_callbacks(app), que recibe la instancia de
# la aplicación y vincula los callbacks a los componentes.
# ============================================================

from dash import html, Input, Output

from config import CB
from charts import build_line_fig, scatter_with_trend
from data.load_data import filter_by_year_month, resample_by


def register_callbacks(app):
    """
    Registra todos los callbacks de la aplicación en la
    instancia `app` de Dash. Se invoca desde app.py.
    """

    # ----------------------------------------------------------
    # Callback: Renderizado de pestaña activa
    # ----------------------------------------------------------
    @app.callback(
        Output('tab-content', 'children'),
        Input('main-tabs', 'value'),
        Input('year-selector', 'value'),
        Input('month-selector', 'value'),
    )
    def render_tab(tab_value, year, month):
        """
        Actualiza el contenido de la página al cambiar de
        pestaña o al modificar los filtros de año/mes.
        """
        # Import tardío para evitar ciclos: tabs.py importa df_raw
        # solo cuando se necesita, y callbacks.py no lo necesita
        # hasta que se ejecuta este callback.
        from tabs import TAB_BUILDERS

        builder = TAB_BUILDERS.get(tab_value)
        if builder:
            return builder(year, month)
        return html.Div()

    # ----------------------------------------------------------
    # Callback: Gráfico de evolución Temperatura + MP2.5
    # ----------------------------------------------------------
    @app.callback(
        Output('evol-temp-mp', 'figure'),
        Input('agg-selector', 'value'),
        Input('year-selector', 'value'),
        Input('month-selector', 'value'),
    )
    def update_evol_temp_mp(agg, year, month):
        """
        Actualiza el gráfico de temperatura y MP2.5 al cambiar
        los filtros o la frecuencia de agregación.
        """
        from tabs import df_raw

        df = filter_by_year_month(df_raw, year, month)
        df = resample_by(df, agg)

        fig = build_line_fig(
            df,
            ['temperatura', 'mp2_5'],
            'Temperatura y MP2.5',
            'Valor',
            [CB['blue'], CB['red']],
        )

        fig.update_traces(
            selector=dict(name='temperatura'),
            hovertemplate='%{y:.1f} °C<extra>Temperatura</extra>',
        )
        fig.update_traces(
            selector=dict(name='mp2_5'),
            hovertemplate='%{y:.1f} µg/m³<extra>MP2.5</extra>',
        )

        return fig

    # ----------------------------------------------------------
    # Callback: Gráfico de evolución Humedad + Viento
    # ----------------------------------------------------------
    @app.callback(
        Output('evol-hum-vv', 'figure'),
        Input('agg-selector', 'value'),
        Input('year-selector', 'value'),
        Input('month-selector', 'value'),
    )
    def update_evol_hum_vv(agg, year, month):
        """
        Actualiza el gráfico de humedad y velocidad del viento.
        """
        from tabs import df_raw

        df = filter_by_year_month(df_raw, year, month)
        df = resample_by(df, agg)

        fig = build_line_fig(
            df,
            ['humedad', 'vel_viento'],
            'Humedad y Velocidad del Viento',
            'Valor',
            [CB['blue'], CB['orange']],
        )

        fig.update_traces(
            selector=dict(name='humedad'),
            hovertemplate='%{y:.1f} %<extra>Humedad</extra>',
        )
        fig.update_traces(
            selector=dict(name='vel_viento'),
            hovertemplate='%{y:.2f} m/s<extra>Viento</extra>',
        )

        return fig

    # ----------------------------------------------------------
    # Callback: Dispersión MP2.5 vs Temperatura
    # ----------------------------------------------------------
    @app.callback(
        Output('disp-temp', 'figure'),
        Input('year-selector', 'value'),
        Input('month-selector', 'value'),
    )
    def update_disp_temp(year, month):
        """Gráfico de dispersión: Temperatura vs MP2.5."""
        from tabs import df_raw

        df = filter_by_year_month(df_raw, year, month)
        return scatter_with_trend(
            df, 'temperatura', 'mp2_5',
            'Temperatura (°C)', 'MP2.5 (µg/m³)', '#CC3311',
        )

    # ----------------------------------------------------------
    # Callback: Dispersión MP2.5 vs Humedad
    # ----------------------------------------------------------
    @app.callback(
        Output('disp-hum', 'figure'),
        Input('year-selector', 'value'),
        Input('month-selector', 'value'),
    )
    def update_disp_hum(year, month):
        """Gráfico de dispersión: Humedad vs MP2.5."""
        from tabs import df_raw

        df = filter_by_year_month(df_raw, year, month)
        return scatter_with_trend(
            df, 'humedad', 'mp2_5',
            'Humedad Relativa (%)', 'MP2.5 (µg/m³)', CB['blue'],
        )

    # ----------------------------------------------------------
    # Callback: Dispersión MP2.5 vs Velocidad del Viento
    # ----------------------------------------------------------
    @app.callback(
        Output('disp-viento', 'figure'),
        Input('year-selector', 'value'),
        Input('month-selector', 'value'),
    )
    def update_disp_viento(year, month):
        """Gráfico de dispersión: Velocidad del Viento vs MP2.5."""
        from tabs import df_raw

        df = filter_by_year_month(df_raw, year, month)
        return scatter_with_trend(
            df, 'vel_viento', 'mp2_5',
            'Velocidad del Viento (m/s)', 'MP2.5 (µg/m³)', CB['teal'],
        )
