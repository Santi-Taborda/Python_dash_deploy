from dash import Dash, html, dcc, callback, Output, Input, register_page
import plotly.express as px
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import pymysql
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from os import environ as env

env['DB_URL']="mysql+pymysql://{user}:{password}@{host}:{port}/{name}".format(
    user=env['DB_USER'],
    password=env['DB_PASSWORD'],
    host=env['DB_HOST'],
    port=env['DB_PORT'],
    name=env['DB_NAME']
    )

def redondeo_cincominutal(datetime_datos_tabla):
    # Encuentra la cantidad de minutos desde el inicio de la hora
    minutos = (datetime_datos_tabla - datetime_datos_tabla.replace(minute=0, second=0, microsecond=0)).total_seconds() / 60
    # Encuentra el múltiplo de 5 más cercano
    minutos_redondeados = int(np.round(minutos / 5.0) * 5)
    # Calcula la hora redondeada
    datetime_redondeado = datetime_datos_tabla.replace(minute=0, second=0, microsecond=0) + timedelta(minutes=minutos_redondeados)
    return datetime_redondeado


def obtener_datos():
    fecha_actual= datetime.now().replace(tzinfo=pd.Timestamp.now().tz)
    fecha_40_dias_atras=fecha_actual - timedelta(days=3)
    hora_actual_str = fecha_actual.strftime('%Y-%m-%d %H:%M:%S')
    hace_40_dias_str = fecha_40_dias_atras.strftime('%Y-%m-%d %H:%M:%S')
# Conexión a la base de datos MySQL
    engine = create_engine(env.get('DB_URL'), echo=True)
    # Consultas SQL
    
    query1 = "SELECT idVariable, FROM_UNIXTIME(FLOOR(UNIX_TIMESTAMP(IdTiempoRegistro) / 300) * 300) AS IdTiempoRegistro, round(SUM(Valor), 2) AS Valor FROM factmonitoreo WHERE idEstacion IN (14, 31, 26, 84, 24, 25, 79, 23, 10, 15, 8, 3) AND IdVariable in (2) AND IdTiempoRegistro BETWEEN %s AND %s AND Valor IS NOT NULL GROUP BY FROM_UNIXTIME(FLOOR(UNIX_TIMESTAMP(IdTiempoRegistro) / 300) * 300) "
    query2 = "SELECT idVariable, FROM_UNIXTIME(FLOOR(UNIX_TIMESTAMP(IdTiempoRegistro) / 300) * 300) AS IdTiempoRegistro, round(SUM(Valor), 2) AS Valor FROM factmonitoreo WHERE idEstacion IN (84,31) AND IdVariable in (12) AND IdTiempoRegistro BETWEEN %s AND %s AND Valor IS NOT NULL GROUP BY FROM_UNIXTIME(FLOOR(UNIX_TIMESTAMP(IdTiempoRegistro) / 300) * 300) "
    datos_tabla_1 = pd.read_sql(query1, engine,  params=(hace_40_dias_str, hora_actual_str))
    datos_tabla_2 = pd.read_sql(query2, engine,  params=(hace_40_dias_str, hora_actual_str))

    #Concateno tablas
    datos_tabla = pd.merge(datos_tabla_1, datos_tabla_2, on="IdTiempoRegistro")
    #Redondeo a 5 minutos
    datos_tabla["IdTiempoRegistro"] = pd.to_datetime(datos_tabla["IdTiempoRegistro"], utc=True)
    datos_tabla['IdTiempoRegistro'] = datos_tabla['IdTiempoRegistro'].apply(redondeo_cincominutal)
    datos_tabla["timestamp"] = datos_tabla["IdTiempoRegistro"].astype('int64') // 10**9
    datos_tabla.sort_values(by="IdTiempoRegistro", inplace=True)
    time_data_min=datos_tabla["timestamp"].iloc[0]
    time_data_max=datos_tabla["timestamp"].iloc[-1]

    return (datos_tabla, time_data_min, time_data_max)

datos,min_actualized,max_actualized= obtener_datos()

register_page(__name__, name="lluvia vs caudal", path='/aya/lluvia_vs_caudal' )


layout= dbc.Container(children=[
    html.Div(
        children=[
    html.H1("Sumatoria de lluvia vs caudal AyA", style={'textAlign': 'left', 'color': '#0d6efd', 'margin-left':'20px', 'padding':'10px'}),
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
                                    id='datetime_range_slider_lluvia_vs_caudal_AyA',
                                    min=min_actualized,
                                    max=max_actualized, 
                                    value=[min_actualized,max_actualized],
                                    step=1,
                                    marks=None,
                                    allowCross=False,
                                    tooltip={"placement": "top", "always_visible": False, "transform": "Hora_legible"},
                                    className='mt-3')
                                    ],className="shadow-none p-1 mb-2 rounded", color="#D3F1FF"),

                    ])], 
                    className="shadow p-3 mb-5 bg-white rounded"
            )], width=3
        ),
        dbc.Col(
            children=[
                dcc.Graph(id='monitor_lluvia_lluvia_vs_caudal_AyA'),
                dcc.Graph(id='monitor_caudal_lluvia_vs_caudal_AyA'),
                dcc.Interval(
                    id='interval_component',
                    interval=5*60*1000, # in milliseconds
                    n_intervals=0),
                ],
            style={'overflowY': 'scroll', 'height': '100%'},
                width=9),
            
    ]),
    html.Hr(),
    ], fluid=True)

@callback(
   [Output('datetime_range_slider_lluvia_vs_caudal_AyA', 'min'),
    Output('datetime_range_slider_lluvia_vs_caudal_AyA', 'max'),
    Output('datetime_range_slider_lluvia_vs_caudal_AyA', 'value'),],
    Input('interval-component', 'n_intervals') 
    )

def update_slider(n):
    datos,min_actualized,max_actualized =obtener_datos()
    return (min_actualized, max_actualized,[min_actualized,max_actualized])



@callback(
    [Output('monitor_lluvia_lluvia_vs_caudal_AyA', 'figure'),
    Output('monitor_caudal_lluvia_vs_caudal_AyA', 'figure'),],
    [Input('datetime_range_slider_lluvia_vs_caudal_AyA', 'value'),
    Input('interval_component', 'n_intervals'),]
    )

def update_monitor_lluvia(date_time,n):

    datos,min_actualized,max_actualized=obtener_datos()
    start_time = pd.to_datetime(date_time[0], unit='s', utc=True)
    end_time = pd.to_datetime(date_time[1], unit='s', utc=True)

    datos = datos[
        (datos["IdTiempoRegistro"] >= start_time) &
        (datos["IdTiempoRegistro"] <= end_time)
    ]

    fig_1=px.bar(datos,x='IdTiempoRegistro',y='Valor_x')
    fig_1.update_traces(marker_color="rgb(0,178,255)")
    fig_1.update_xaxes(showticklabels=False)
    fig_1.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='LightSteelBlue',
        yaxis_title='Lluvia acumulada [mm]',
        yaxis=dict(autorange='reversed'),
        xaxis_title=None,
        margin=dict(l=30, r=30, t=30, b=0),
        height=250
    )
    fig_2=go.Figure()
    fig_2.add_trace(go.Scatter(x=datos['IdTiempoRegistro'],y=datos['Valor_y'], fill='tozeroy',line=dict(color="blue")))
    fig_2.update_traces(marker_color='LightSteelBlue')
    fig_2.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='LightSteelBlue',
        yaxis_title='Caudal del río [m^3/s]',
        xaxis_title='FECHA - HORA',
        margin=dict(l=30, r=30, t=0, b=30),
        height=250
    )
    fig_2.update_yaxes(range=[None, None])

    return fig_1,fig_2
