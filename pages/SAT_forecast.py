from dash import Dash, html, dcc, callback, Output, Input, register_page
import plotly.express as px
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
import pandas as pd
from sqlalchemy import create_engine
import pymysql
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from os import environ as env


env['DB_URL_2']="mysql+pymysql://{user}:{password}@{host}:{port}/{name}".format(
    user=env['DB_USER_2'],
    password=env['DB_PASSWORD_2'],
    host=env['DB_HOST_2'],
    port=env['DB_PORT_2'],
    name=env['DB_NAME_SATMA']
    )
 
def obtener_datos():
    
    # Conexión a la base de datos MySQL
    engine2 = create_engine(env.get('DB_URL_2'), echo=True)
    # Consultas SQL
    query1 = "SELECT IdRegistro, idPunto, Lugar, IdTiempoRegistro, Temperatura, Precipitacion FROM forecast"

    datos_tabla = pd.read_sql(query1, engine2)

    datos_tabla["IdTiempoRegistro"] = pd.to_datetime(datos_tabla["IdTiempoRegistro"])
    datos_tabla["timestamp"] = datos_tabla['IdTiempoRegistro'].apply(lambda x: x.timestamp())
    datos_tabla.sort_values(by="IdTiempoRegistro", inplace=True)

    return (datos_tabla)

datos_tabla = obtener_datos()

global min_actualized, max_actualized
min_actualized = datos_tabla["timestamp"].min()
max_actualized = datos_tabla["timestamp"].max()

register_page(__name__, name="Forecast", path='/SAT/forecast' )

layout= dbc.Container(children=[
    html.Div(
        children=[
    html.H1("Forecast SAT", style={'textAlign': 'left', 'color': '#0d6efd', 'margin-left':'20px', 'padding':'10px'}),
    html.Hr()],
    style={'background-color':'AliceBlue'},
    ),

    dbc.Row(children=[
        dbc.Col(children=[dbc.Card(children=[
                    dbc.CardBody(children=[
                    html.H4("Controles", className="card-title"),
                    html.H6("Seleccione los puntos que desea visualizar:", className="card-text" ),
                    dcc.Dropdown(
                        id='lugar-dropdown_forecast_SAT',
                        options=pd.unique(datos_tabla["Lugar"]),
                        value='Pereira',
                        multi=True,
                        className='mb-3'),
                        
                    html.H6("Seleccione la variable que desea visualizar:", className="card-text", style={'margin-top':'1em'}),

                    dcc.Dropdown(id='variable-button_forecast_SAT',
                                    options=[{'label': 'Temperatura', 'value': 'Temperatura'},
                                              {'label': 'Precipitacion', 'value': 'Precipitacion'}],
                                    value='Temperatura', multi=False, className='mb-3'),
                    html.H6("Seleccione el rango de fechas que desea visualizar:", className="card-text" ),

                    dbc.Card(children=[
                    dcc.RangeSlider(id='datetime-range-slider_forecast_SAT',
                                    min=min_actualized,
                                    max=max_actualized, 
                                    value=[min_actualized,max_actualized],
                                    marks=None,
                                    step=1,
                                    allowCross=False,
                                    tooltip={"placement": "top", "always_visible": False, "transform": "Hora_legible"},
                                    className='mt-3')
                                    ],className="shadow-none p-1 mb-2 rounded", color="#D3F1FF"),

                    html.H6(id='actualizador-slider'),

                    dcc.Interval(
                    id='interval-component',
                    interval=60*60*1000, # in milliseconds
                    n_intervals=0),

                    ])], 
                    className="shadow p-3 mb-5 bg-white rounded"
            )], width=3
        ),
        dbc.Col(
            dcc.Graph(id='Monitor_forecast_SAT'),style={'overflowY': 'scroll', 'height': '100%'},
                width=9)
    ]),
    html.Hr(),
    ], fluid=True)

@callback(
   [Output('datetime-range-slider_forecast_SAT', 'min'),
    Output('datetime-range-slider_forecast_SAT', 'max'),
    Output('datetime-range-slider_forecast_SAT', 'value')],
   Input('interval-component', 'n_intervals') 
)

def update_slider(n):
    datos_tabla = obtener_datos()
    global min_actualized, max_actualized

    min_actualized = datos_tabla["timestamp"].min()
    max_actualized = datos_tabla["timestamp"].max()

    return (min_actualized, max_actualized,[min_actualized,max_actualized])


@callback(
    Output('Monitor_forecast_SAT', 'figure'),
    Input('datetime-range-slider_forecast_SAT', 'value'),
    Input('lugar-dropdown_forecast_SAT', 'value'),
    Input ('variable-button_forecast_SAT', 'value'),
    Input('interval-component', 'n_intervals')
    )

def update_monitor(date_time, lugares, variable,n):
    datos_tabla = obtener_datos()

    if isinstance(lugares, str):
        lugares = [lugares]

    datos_tabla_filtrados= datos_tabla[datos_tabla["Lugar"].isin(lugares)]
    if variable == 'Temperatura':
        datos_tabla_filtrados = datos_tabla_filtrados[datos_tabla_filtrados["Temperatura"].notna()]
        datos_tabla_filtrados = datos_tabla_filtrados.rename(columns={"Temperatura": "Valor"})
    elif variable == 'Precipitacion':
        datos_tabla_filtrados = datos_tabla_filtrados[datos_tabla_filtrados["Precipitacion"].notna()]
        datos_tabla_filtrados = datos_tabla_filtrados.rename(columns={"Precipitacion": "Valor"})

    start_time = pd.to_datetime(date_time[0], unit='s')
    end_time = pd.to_datetime(date_time[1], unit='s')
    datos_tabla_filtrados = datos_tabla_filtrados[
        (datos_tabla_filtrados["IdTiempoRegistro"] >= start_time) &
        (datos_tabla_filtrados["IdTiempoRegistro"] <= end_time)
    ]

    cant_figures=pd.unique(datos_tabla_filtrados["Lugar"])

    if len(cant_figures)==0:
        fig= make_subplots(rows=1, cols=1, subplot_titles="")
        fig.add_trace(go.Scatter(x=None, y=None),
            row=1, col=1)
            
        fig.update_layout(autosize=True, title_text="NINGUNO DE LOS LUGARES PREDICE LA VARIABLE ESTABLECIDA")
    else: 
        fig= make_subplots(rows=len(cant_figures), cols=1, subplot_titles=cant_figures, vertical_spacing=0.1)
        for index, figure in enumerate(cant_figures):
            datos= datos_tabla_filtrados[datos_tabla_filtrados['Lugar']==figure]
            fig.add_trace( {
                'type': 'scatter',
                'x': datos['IdTiempoRegistro'],
                'y': datos['Valor'],
                'mode': 'none',
                'fill': 'tozeroy',
                'name': figure
            },
            row=index+1, col=1)
            fig.update_yaxes(title_text=variable, range=[min(datos['Valor']), max(datos['Valor'])+max(datos['Valor'])*0.1], row=index+1, col=1)

        fig.update_layout(autosize=True, height=len(cant_figures)*300, paper_bgcolor="LightSteelBlue", margin=dict(l=30, r=30, t=30, b=30))
    return fig
 
