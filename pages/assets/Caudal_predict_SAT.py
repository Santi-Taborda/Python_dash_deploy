from dash import Dash, html, dcc, callback, Output, Input, register_page
import plotly.express as px
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import geoglows
import pytz
import zarr

def caudal_predict(fecha_inicio, fecha_fin, id_tramo, nombre_tramo):
    reach_id = id_tramo  # tramo bocatoma

    sf = geoglows.data.forecast(reach_id)
    geoglows.plots.forecast(sf)

    stats = geoglows.data.forecast_stats(reach_id)
    geoglows.plots.forecast_stats(stats)

    sf_modified = sf

    # Definir la zona horaria de Colombia
    colombia_tz = pytz.timezone("America/Bogota")

    # Convertir la columna datetime de UTC+0 a UTC-5 y cambiar a formato de string
    sf_modified = sf_modified.copy()
    sf_modified.index = sf_modified.index.tz_convert(colombia_tz).strftime('%Y-%m-%d %H:%M:%S')

    # Generar el gráfico base
    fig = geoglows.plots.forecast(sf_modified)

    # Modificar el nombre de la leyenda de "streamflow (median)" a "Caudal (mediana)"
    for trace in fig.data:
        if "median" in trace.name.lower():  # Identificar la traza de la mediana
            trace.name = "Caudal (mediana)"

    # Extraer los datos de incertidumbre con el índice ya en formato de string
    x_values = sf_modified.index
    upper_bound = sf_modified["flow_uncertainty_upper"]
    lower_bound = sf_modified["flow_uncertainty_lower"]

    # Eliminar cualquier traza existente de incertidumbre para evitar superposición incorrecta
    fig.data = [trace for trace in fig.data if "uncertainty" not in trace.name.lower()]

    # Crear la banda de incertidumbre correctamente sombreada
    fig.add_trace(go.Scatter(
        x=list(x_values) + list(x_values[::-1]),  # Para cerrar la sombra correctamente
        y=list(upper_bound) + list(lower_bound[::-1]),  # Definir el área sombreada
        fill='toself',  # Rellenar el área entre los límites
        fillcolor='rgba(173, 216, 230, 0.4)',  # Color azul claro semitransparente
        line=dict(color='rgba(255,255,255,0)'),  # Sin bordes visibles
        name="Rango de incertidumbre"
    ))

    # Modificar los nombres de los ejes
    fig.update_layout(
        yaxis_title="Caudal (%)",
        xaxis_title="Fecha",
        hovermode="x unified"  # Permite ver todos los valores al pasar el cursor
    )

    # Crear un nuevo dataframe con los valores transformados
    stats_modified = (stats * 100 / 395.11)

    # Convertir la columna datetime de UTC+0 a UTC-5
    stats_modified = stats_modified.copy()  # Evitar modificar el original directamente
    stats_modified.index = stats_modified.index.tz_convert(colombia_tz)

    start_date = fecha_inicio
    end_date = fecha_fin
    filtered_stats = stats_modified.loc[start_date:end_date]

    # Graficar usando GeoGLOWS
    geoglows.plots.forecast_stats(filtered_stats)

    stats_modified = stats_modified.loc[:end_date]
    geoglows.plots.forecast_stats(stats_modified)

    fig = geoglows.plots.forecast_stats(stats_modified)

    # Modificar el nombre del eje X
    fig.update_layout(
        yaxis_title="Caudal (%)",
        xaxis_title="Fecha",
        title=f"Predicción de caudal para {nombre_tramo}",
        hovermode="x unified"  # Permite ver todos los valores al pasar el cursor
    )

    min_date = stats_modified['flow_avg'].idxmin()
    min_value = stats_modified['flow_avg'].min()

    max_date = stats_modified['flow_avg'].idxmax()
    max_value = stats_modified['flow_avg'].max()
    return fig, min_date, min_value, max_date, max_value

# Definir la zona horaria de Colombia
colombia_tz = pytz.timezone("America/Bogota")

# Convertir las fechas a la zona horaria de Colombia
max_actualized = (datetime.now(colombia_tz) + timedelta(days=7))
min_actualized = datetime.now(colombia_tz)
figura, min_date, min_value, max_date, max_value = caudal_predict(min_actualized, max_actualized, '610_408_927', 'Río Risaralda desembocadura')

register_page(__name__, name="Predicción de caudales Bocatoma Nuevo Libaré", path='/SAT/caudal_predict')


layout = dbc.Container(children=[
    html.Div(
        children=[
            html.H1("Predicción caudales Bocatoma Nuevo Libaré", style={'textAlign': 'left', 'color': '#0d6efd', 'margin-left': '20px', 'padding': '10px'}),
            html.Hr()
        ],
        style={'background-color': 'AliceBlue'},
    ),

    dbc.Row(children=[
        dcc.Interval(
            id='interval_component',
            interval=30 * 60 * 1000,  # in milliseconds
            n_intervals=0),
        
        dcc.Dropdown(
            id='tramo_button',
            options=[
                {'label': 'Río Risaralda desembocadura', 'value': '610_408_927'},
                {'label': 'Río Cauca sin Risaralda', 'value': '610_448_527'},
                {'label': 'Río San Eugenio', 'value': '610_283_090'},
                {'label': 'Río Monos', 'value': '610_232_920'},
                {'label': 'Río San Juan Santa Cecilia', 'value': '670_016_532'},
                {'label': 'Río Totuí', 'value': '610_254_042'},
                {'label': 'Río Mapa', 'value': '610_342_917'},
                {'label': 'Río Otún', 'value': '610_363_173'},
                {'label': 'Río Consota', 'value': '610_300_693'},
                {'label': 'Quebrada Dosquebradas', 'value': '610_252_290'},
            ],
            value='610_408_927',
            multi=False,
            style={'width': '50%', 'margin-left': '20px', 'margin-top': '10px'},
        ),

        dbc.Col( id='dates',
            children=[
                html.H3("Valores extremos"),
                html.Hr(),
                html.H5("Fecha del valor mínimo:"),
                html.H6(min_date.date(), style={'color': 'black'}),
                html.H5("Valor mínimo:"),
                html.H6(round(min_value,2), style={'color': 'black'}),
                html.H5("Fecha del valor máximo:"),
                html.H6(max_date.date(), style={'color': 'black'}),
                html.H5("Valor máximo:"),
                html.H6(round(max_value,2), style={'color': 'black'}),
                html.Hr(),
            ],
            style={'overflowY': 'scroll', 'height': '100%'},
            width=3),
        dbc.Col(
            children=[
                dcc.Graph(id='monitor_oferta_caudal_predict_aya', figure=figura),
            ],
            style={'overflowY': 'scroll', 'height': '100%'},
            width=9)

    ]),
    html.Hr(),
], fluid=True)


@callback(
    [Output('monitor_oferta_caudal_predict_aya', 'figure'),
     Output('dates', 'children')],
    [Input('interval_component', 'n_intervals'),
     Input('tramo_button', 'value'),
     Input('tramo_button', 'options')],

)
def update_graph(n, id_tramo,nombre_tramo):
    options = [option['label'] for option in nombre_tramo if option['value'] == id_tramo]
    max_actualized = (datetime.now(colombia_tz) + timedelta(days=7))
    min_actualized = datetime.now(colombia_tz)
    figura, min_date, min_value, max_date, max_value = caudal_predict(min_actualized, max_actualized, id_tramo, options[0])

    dates_children = [
    html.H3("Valores extremos"),
    html.Hr(),
    html.H5("Fecha del valor mínimo:"),
    html.H6(min_date.date(), style={'color': 'black'}),
    html.H5("Valor mínimo:"),
    html.H6(round(min_value, 2), style={'color': 'black'}),
    html.H5("Fecha del valor máximo:"),
    html.H6(max_date.date(), style={'color': 'black'}),
    html.H5("Valor máximo:"),
    html.H6(round(max_value, 2), style={'color': 'black'}),
    html.Hr(),
    ]

    return figura, dates_children
