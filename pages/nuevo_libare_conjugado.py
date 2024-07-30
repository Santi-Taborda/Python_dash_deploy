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

env['DB_URL']="mysql+pymysql://{user}:{password}@{host}:{port}/{name}".format(
    user=env['DB_USER'],
    password=env['DB_PASSWORD'],
    host=env['DB_HOST'],
    port=env['DB_PORT'],
    name=env['DB_NAME']
    )

def min_ecologico(valor_dato):
    if valor_dato>=3.89 and valor_dato<=5.99:
        Valor_minimo = 1.83
    elif valor_dato>= 6 and valor_dato<=8.99:
        Valor_minimo = 2.5
    elif valor_dato>= 9 and valor_dato<=10.99:
        Valor_minimo = 3
    elif valor_dato>= 11 and valor_dato<=11.99:
        Valor_minimo = 4
    elif valor_dato>= 12 and valor_dato<=12.99:
        Valor_minimo = 5
    elif valor_dato>= 13 and valor_dato<=13.99:
        Valor_minimo = 6
    elif valor_dato>= 14 and valor_dato<=14.99:
        Valor_minimo = 7
    elif valor_dato>= 15 and valor_dato<=15.99:
        Valor_minimo = 8
    elif valor_dato>= 16 and valor_dato<=16.99:
        Valor_minimo = 9
    elif valor_dato>= 17 and valor_dato<=17.99:
        Valor_minimo = 10
    elif valor_dato>= 18 and valor_dato<=18.99:
        Valor_minimo = 11
    elif valor_dato>= 19:
        Valor_minimo = 12
    else: Valor_minimo=valor_dato

    return Valor_minimo
    

def obtener_datos():
    fecha_actual= datetime.now().replace(tzinfo=pd.Timestamp.now().tz)
    fecha_40_dias_atras=fecha_actual - timedelta(days=1)
    hora_actual_str = fecha_actual.strftime('%Y-%m-%d %H:%M:%S')
    hace_40_dias_str = fecha_40_dias_atras.strftime('%Y-%m-%d %H:%M:%S')
# Conexión a la base de datos MySQL
    engine = create_engine(env.get('DB_URL'), echo=True)
    # Consultas SQL
    
    query1 = "SELECT FROM_UNIXTIME(FLOOR(UNIX_TIMESTAMP(IdTiempoRegistro) / 300) * 300) AS IdTiempoRegistro, round(Valor, 2) AS Valor_ecologico FROM factmonitoreo WHERE idEstacion IN (31) AND IdVariable in (12) AND IdTiempoRegistro BETWEEN %s AND %s AND Valor IS NOT NULL GROUP BY FROM_UNIXTIME(FLOOR(UNIX_TIMESTAMP(IdTiempoRegistro) / 300) * 300) "
    query2 = "SELECT FROM_UNIXTIME(FLOOR(UNIX_TIMESTAMP(IdTiempoRegistro) / 300) * 300) AS IdTiempoRegistro, round(SUM(Valor), 2) AS Valor_oferta FROM factmonitoreo WHERE idEstacion IN (31,84) AND IdVariable in (12) AND IdTiempoRegistro BETWEEN %s AND %s AND Valor IS NOT NULL AND Valor >=2 GROUP BY FROM_UNIXTIME(FLOOR(UNIX_TIMESTAMP(IdTiempoRegistro) / 300) * 300) "
    query3 = "SELECT FROM_UNIXTIME(FLOOR(UNIX_TIMESTAMP(IdTiempoRegistro) / 300) * 300) AS IdTiempoRegistro, round(Valor, 2) AS Valor_parshal FROM factmonitoreo WHERE idEstacion IN (84) AND IdVariable in (12) AND IdTiempoRegistro BETWEEN %s AND %s AND Valor IS NOT NULL GROUP BY FROM_UNIXTIME(FLOOR(UNIX_TIMESTAMP(IdTiempoRegistro) / 300) * 300) "
    datos_tabla_1 = pd.read_sql(query1, engine,  params=(hace_40_dias_str, hora_actual_str))
    datos_tabla_2 = pd.read_sql(query2, engine,  params=(hace_40_dias_str, hora_actual_str))
    datos_tabla_3 = pd.read_sql(query3, engine,  params=(hace_40_dias_str, hora_actual_str))

    #Concateno tablas
    datos_tabla = pd.merge(datos_tabla_1, datos_tabla_2, on="IdTiempoRegistro")
    datos_tabla = pd.merge(datos_tabla, datos_tabla_3, on="IdTiempoRegistro")
    #Redondeo a 5 minutos
    datos_tabla["IdTiempoRegistro"] = pd.to_datetime(datos_tabla["IdTiempoRegistro"], utc=True)
    #datos_tabla['IdTiempoRegistro'] = datos_tabla['IdTiempoRegistro'].apply(redondeo_cincominutal)
    datos_tabla["timestamp"] = datos_tabla["IdTiempoRegistro"].astype('int64') // 10**9
    datos_tabla.sort_values(by="IdTiempoRegistro", inplace=True)
    time_data_min=datos_tabla["timestamp"].iloc[0]
    time_data_max=datos_tabla["timestamp"].iloc[-1]

    return (datos_tabla, time_data_min, time_data_max)

datos,min_actualized,max_actualized= obtener_datos()

register_page(__name__, name="Bocatoma Nuevo Libaré Conjugado", path='/aya/bocatoma_nuevo_libare' )


layout= dbc.Container(children=[
    html.Div(
        children=[
    html.H1("Bocatoma Nuevo Libaré Conjugado AyA", style={'textAlign': 'left', 'color': '#0d6efd', 'margin-left':'20px', 'padding':'10px'}),
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
                                    id='datetime_range_slider_bocatoma_nuevo_libare_conjugado_AyA',
                                    min=min_actualized,
                                    max=max_actualized, 
                                    value=[min_actualized,max_actualized],
                                    step=1,
                                    marks=None,
                                    allowCross=False,
                                    tooltip={"placement": "top", "always_visible": False, "transform": "Hora_legible"},
                                    className='mt-3')
                                    ],className="shadow-none p-1 mb-2 rounded", color="#D3F1FF"),
                    html.Div(
                    children=[
                        dcc.Graph(id='tabla_caudal_bocatoma_nuevo_libare_conjugado_AyA'),
                        dcc.Graph(id='tabla_cumplimiento_bocatoma_nuevo_libare_conjugado_AyA'),
                    ],
                    style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center'}
                    ),

                    ])], 
                    className="shadow p-3 mb-5 bg-white rounded"
            )], width=3
        ),
        dbc.Col(
            children=[
                dcc.Graph(id='monitor_oferta_bocatoma_nuevo_libare_conjugado_AyA'),
                dcc.Graph(id='monitor_parshal_bocatoma_nuevo_libare_conjugado_AyA'),
                dcc.Graph(id='monitor_ecologico_bocatoma_nuevo_libare_conjugado_AyA'),

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
   [Output('datetime_range_slider_bocatoma_nuevo_libare_conjugado_AyA', 'min'),
    Output('datetime_range_slider_bocatoma_nuevo_libare_conjugado_AyA', 'max'),
    Output('datetime_range_slider_bocatoma_nuevo_libare_conjugado_AyA', 'value'),],
   Input('interval-component', 'n_intervals') 
)

def update_slider(n):
    datos,min_actualized,max_actualized =obtener_datos()
    return (min_actualized, max_actualized,[min_actualized,max_actualized])



@callback(
    [Output('monitor_oferta_bocatoma_nuevo_libare_conjugado_AyA', 'figure'),
    Output('monitor_parshal_bocatoma_nuevo_libare_conjugado_AyA', 'figure'),
    Output('monitor_ecologico_bocatoma_nuevo_libare_conjugado_AyA', 'figure'),
    Output('tabla_caudal_bocatoma_nuevo_libare_conjugado_AyA', 'figure'),
    Output('tabla_cumplimiento_bocatoma_nuevo_libare_conjugado_AyA', 'figure'),],
    [Input('datetime_range_slider_bocatoma_nuevo_libare_conjugado_AyA', 'value'),
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

    datos_ecologico=datos["Valor_oferta"]
    datos_ecologico = datos_ecologico.apply(min_ecologico)

    fig_1=go.Figure()
    fig_1.add_trace(go.Scatter(x=datos['IdTiempoRegistro'],y=datos['Valor_oferta'], fill='tozeroy',line=dict(color="gray")))
    fig_1.update_traces(marker_color='LightSteelBlue')
    fig_1.update_xaxes(showticklabels=False)
    fig_1.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='LightSteelBlue',
        yaxis_title='Oferta',
        xaxis_title=None,
        margin=dict(l=30, r=30, t=30, b=0),
        height=170
    )
    fig_2=go.Figure()
    fig_2.add_trace(go.Scatter(x=datos['IdTiempoRegistro'],y=datos['Valor_parshal'], fill='tozeroy',line=dict(color="gray")))
    fig_2.update_traces(marker_color='LightSteelBlue')
    fig_2.update_xaxes(showticklabels=False)
    fig_2.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='LightSteelBlue',
        yaxis_title='Captación',
        xaxis_title=None,
        margin=dict(l=30, r=30, t=0, b=0),
        height=170
    )
    fig_3=go.Figure()
    fig_3.add_trace(go.Scatter(x=datos['IdTiempoRegistro'],y=datos['Valor_ecologico'], fill='tozeroy',line=dict(color="gray")))
    fig_3.add_trace(go.Scatter(x=datos['IdTiempoRegistro'], y=datos_ecologico, line=dict(color="red")))
    fig_3.update_traces(marker_color='LightSteelBlue')
    fig_3.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='LightSteelBlue',
        yaxis_title='Ambiental',
        xaxis_title=None,
        margin=dict(l=30, r=30, t=0, b=40),
        height=170,
        showlegend=False
    )

    fig_4= go.Figure(data=[go.Table(
    header=dict(values=['Estación', 'Max', 'Prom', 'Min'],
                line_color='darkslategray',
                fill_color='lightskyblue',
                align='left'),
    cells=dict(values=[["Oferta", "Captación", "Ambiental"],
                       [max(datos['Valor_oferta']), max(datos['Valor_parshal']), max(datos['Valor_ecologico']) ],
                       [round(statistics.mean(datos['Valor_oferta']),2),  round(statistics.mean(datos['Valor_parshal']),2), round(statistics.mean(datos['Valor_ecologico']),2)],
                       [min(datos['Valor_oferta']), min(datos['Valor_parshal']), min(datos['Valor_ecologico'])]],
                       
               line_color='darkslategray',
               fill_color='lightcyan',
               align='left'))
    ])

    fig_4.update_layout(width=290, height=150, margin=dict(l=0, r=0, t=20, b=0))

    fig_5= go.Figure(data=[go.Table(
    header=dict(values=['Caudal amb', 'Caudal min', 'Cumplimiento'],
                line_color='darkslategray',
                fill_color='lightskyblue',
                align='left'),
    cells=dict(values=[[datos['Valor_ecologico'].iloc[-1]],
                       [datos_ecologico.iloc[-1]],
                       [round(datos['Valor_ecologico'].iloc[-1]*100/ datos_ecologico.iloc[-1], 2)]],
               line_color='darkslategray',
               fill_color='lightcyan',
               align='left'))
    ])
    fig_5.update_layout(width=290, height=100, margin=dict(l=0, r=0, t=0, b=10))

    return fig_1,fig_2,fig_3, fig_4, fig_5


