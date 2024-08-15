from dash import Dash, html, dcc, callback, Output, Input, register_page
import plotly.express as px
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import statistics
from sqlalchemy import create_engine
import pymysql
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from os import environ as env

env['DB_USER']='utpmon'
env['DB_PASSWORD']='UtpM0n1t0r'
env['DB_HOST']='194.163.137.37'
env['DB_PORT']='3306'
env['DB_NAME']='upt_monestaciones'

env['DB_URL']="mysql+pymysql://{user}:{password}@{host}:{port}/{name}".format(
    user=env['DB_USER'],
    password=env['DB_PASSWORD'],
    host=env['DB_HOST'],
    port=env['DB_PORT'],
    name=env['DB_NAME']
    )

def obtener_datos():
    fecha_actual= datetime.now().replace(tzinfo=pd.Timestamp.now().tz)
    fecha_40_dias_atras=fecha_actual - timedelta(days=2)
    hora_actual_str = fecha_actual.strftime('%Y-%m-%d %H:%M:%S')
    hace_40_dias_str = fecha_40_dias_atras.strftime('%Y-%m-%d %H:%M:%S')
# Conexión a la base de datos MySQL
    engine = create_engine(env.get('DB_URL'), echo=True)
    # Consultas SQL
    
    query1 = "SELECT IdTiempoRegistro, Valor AS Valor_ecologico, idVariable FROM factmonitoreo WHERE idEstacion IN (31) AND IdTiempoRegistro BETWEEN %s AND %s"
    query2 = "SELECT idVariable, Variable FROM dimvariable"
    datos_tabla = pd.read_sql(query1, engine,  params=(hace_40_dias_str, hora_actual_str))
    dimvariable = pd.read_sql(query2, engine)

    datos_tabla["IdTiempoRegistro"] = pd.to_datetime(datos_tabla["IdTiempoRegistro"], utc=True)
    datos_tabla = pd.merge(datos_tabla, dimvariable, on="idVariable")
    datos_tabla["timestamp"] = datos_tabla["IdTiempoRegistro"].astype('int64') // 10**9
    datos_tabla.sort_values(by="IdTiempoRegistro", inplace=True)
    time_data_min=datos_tabla["timestamp"].iloc[0]
    time_data_max=datos_tabla["timestamp"].iloc[-1]

    return (datos_tabla, time_data_min, time_data_max)

datos,min_actualized,max_actualized= obtener_datos()

register_page(__name__, name="Después de Nuevo Libaré", path='/EEP/despues_nuevo_libare' )


layout= dbc.Container(children=[
    html.Div(
        children=[
    html.H1("Visor Después de Nuevo Libaré", style={'textAlign': 'left', 'color': '#0d6efd', 'margin-left':'20px', 'padding':'10px'}),
    html.Hr()],
    style={'background-color':'AliceBlue'},
    ),

    dbc.Row(children=[
        dbc.Col(children=[dbc.Card(children=[
                    dbc.CardBody(children=[
                    html.H4("Controles", className="card-title"),
                    html.H6("Seleccione el rango de fechas a visualizar:", className="card-text" ),
                    dbc.Card(children=[
                    dcc.RangeSlider(
                                    id='datetime_range_slider_despues_nuevo_libare_EEP',
                                    min=min_actualized,
                                    max=max_actualized, 
                                    value=[min_actualized,max_actualized],
                                    step=1,
                                    marks=None,
                                    allowCross=False,
                                    tooltip={"placement": "top", "always_visible": False, "transform": "Hora_legible"},
                                    className='mt-3')],className="shadow-none p-1 mb-2 rounded", color="#D3F1FF"),
                    dcc.Interval(
                    id='interval-component',
                    interval=5*60*1000, # in milliseconds
                    n_intervals=0),
                    
                    html.H6("Seleccione la variable que desea visualizar:", className="card-text", style={'margin-top':'1em'}),
                    dcc.Dropdown(id='variable-button-Despues-nuevo-libare-EEP',
                                    options=pd.unique(datos["Variable"]),
                                    value='Nivel del cauce mediante radar', multi=False, className='mb-3')

                    ])], 
                    className="shadow p-3 mb-5 bg-white rounded"
            )], width=3
        ),
        dbc.Col(dcc.Graph(id='monitor_despues_bocatoma_nuevo_libare_conjugado_EEP'),
            style={'overflowY': 'scroll', 'height': '100%'},
                width=9),
            
    ]),
    html.Hr(),
    ], fluid=True)

@callback(
   [Output('datetime_range_slider_despues_nuevo_libare_EEP', 'min'),
    Output('datetime_range_slider_despues_nuevo_libare_EEP', 'max'),
    Output('datetime_range_slider_despues_nuevo_libare_EEP', 'value'),],
   Input('interval-component', 'n_intervals') 
)

def update_slider(n):
    datos,min_actualized,max_actualized =obtener_datos()
    return (min_actualized, max_actualized,[min_actualized,max_actualized])



@callback(
    Output('monitor_despues_bocatoma_nuevo_libare_conjugado_EEP', 'figure'),
    [Input('datetime_range_slider_despues_nuevo_libare_EEP', 'value'),
     Input('variable-button-Despues-nuevo-libare-EEP', 'value'),
    Input('interval-component', 'n_intervals'),]
    )

def update_monitor_lluvia(date_time, variable, n):

    datos,min_actualized,max_actualized=obtener_datos()
    start_time = pd.to_datetime(date_time[0], unit='s', utc=True)
    end_time = pd.to_datetime(date_time[1], unit='s', utc=True)

    datos_tabla_filtrados = datos[
        (datos["IdTiempoRegistro"] >= start_time) &
        (datos["IdTiempoRegistro"] <= end_time)
    ]
    datos_tabla_filtrados= datos_tabla_filtrados[datos_tabla_filtrados["Variable"] == variable]

    fig_3=go.Figure()
    fig_3.add_trace(go.Scatter(x=datos_tabla_filtrados['IdTiempoRegistro'],y=datos_tabla_filtrados['Valor_ecologico'], fill='tozeroy'))
    fig_3.update_traces(marker_color='LightSteelBlue')
    fig_3.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='LightSteelBlue',
        yaxis_title=variable,
        xaxis_title=None,
        margin=dict(l=30, r=30, t=0, b=40),
        height=400,
        showlegend=False
    )

    return fig_3
