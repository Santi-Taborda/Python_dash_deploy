"""from dash import Dash, html, dcc, callback, Output, Input, register_page
import plotly.express as px
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
import pandas as pd
from datetime import datetime, timedelta
from os import environ as env
from sqlalchemy import create_engine
import pymysql

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

# Conexión a la base de datos MySQL
engine = create_engine(env.get('DB_URL'), echo=True)

query1 = "SELECT IdTiempoRegistro, ppt_24h, yellow, orange, red FROM EL_LAGO_PPT"

register_page(__name__, name="Analisis_El_Lago", path='/SAT/Analisis_El_Lago' )

datos_tabla = pd.read_sql(query1, engine)
datos_tabla["IdTiempoRegistro"] = pd.to_datetime(datos_tabla["IdTiempoRegistro"], utc=True)
#datos_tabla= pd.read_csv('./assets/EVALUACION_ALERTA_24H.csv', sep=',')
datos_rojo=datos_tabla[datos_tabla["red"]==1]
datos_naranja=datos_tabla[datos_tabla["orange"]==1]
datos_amarillo=datos_tabla[datos_tabla["yellow"]==1]
#datos_verde=datos_tabla[(datos_tabla["orange"]==0) & (datos_tabla["red"]==0) & (datos_tabla["yellow"]==0)]

cantidad_rojo=len(datos_rojo)
cantidad_naranja=len(datos_naranja)
cantidad_amarillo=len(datos_amarillo)
cantidad_total=len(datos_tabla)
cantidad_verde=cantidad_total-cantidad_rojo-cantidad_naranja-cantidad_amarillo

porcentaje_rojo=cantidad_rojo*100/cantidad_total
porcentaje_naranja=cantidad_naranja*100/cantidad_total
porcentaje_amarillo=cantidad_amarillo*100/cantidad_total
porcentaje_verde=100-porcentaje_rojo-porcentaje_naranja-porcentaje_amarillo

fig_1=go.Figure()
fig_1.add_trace(go.Scatter(x=datos_rojo['IdTiempoRegistro'],y=datos_rojo['ppt_24h'], mode='markers',  name='Alerta roja', marker_line_width=2, marker_size=7, marker=dict(color="red"))),
fig_1.add_trace(go.Scatter(x=datos_naranja['IdTiempoRegistro'],y=datos_naranja['ppt_24h'], mode='markers',  name='Alerta naranja', marker_line_width=2, marker_size=7, marker=dict(color="rgb(255,116,0)"))),
fig_1.add_trace(go.Scatter(x=datos_amarillo['IdTiempoRegistro'],y=datos_amarillo['ppt_24h'], mode='markers',  name='Alerta amarilla', marker_line_width=2, marker_size=7, marker=dict(color="rgb(255,240,0)"))),
#fig_1.add_trace(go.Scatter(x=datos_verde['IdTiempoRegistro'],y=datos_verde['ppt_24h'], mode='markers',  name='Sin alerta', marker_line_width=2, marker_size=10, marker=dict(color="green"))),
fig_1.update_xaxes(rangeslider_visible=True)
fig_1.update_layout(autosize=True, height=500, paper_bgcolor="LightSteelBlue", margin=dict(l=30, r=30, t=30, b=30))

fig_2= go.Figure(data=[go.Table(
header=dict(values=['Alerta', 'Cantidad', 'Porcentaje'],
            line_color='darkslategray',
            fill_color='lightskyblue',
            align='left'),
cells=dict(values=[["Rojo", "Naranja", "Amarillo", "Verde"],
                    [cantidad_rojo,cantidad_naranja,cantidad_amarillo, cantidad_verde],
                    [round(porcentaje_rojo,2), round(porcentaje_naranja,2), round(porcentaje_amarillo,2), round(porcentaje_verde,2)]],
            line_color='darkslategray',
            fill_color='lightcyan',
            align='left'))
])

fig_2.update_layout(autosize=True, width=500)



layout= dbc.Container(children=[
    html.Div(
        children=[
    html.H1("Análisis de lluvia El Lago", style={'textAlign': 'left', 'color': '#0d6efd', 'margin-left':'20px', 'padding':'10px'}),
    html.Hr()],
    style={'background-color':'AliceBlue'},
    ),

    dbc.Row(children=[
        dbc.Col(xs=12, sm=12, md=4, lg=3, children=[dbc.Card(children=[
                    dbc.CardBody(children=[
                    html.H4("Tabla de alertas", className="card-title"),
                    html.Div(
                    children=[
                        dcc.Graph(figure=fig_2),
                    ],
                    style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center'}
                    ),

                    ])], 
                    className="shadow p-0 mb-0 bg-white rounded"
            )]),
        dbc.Col(xs=12, sm=12, md=8, lg=9,
            children=[dcc.Graph(figure=fig_1),
                      ],style={'overflowY': 'scroll', 'height': '100%'})]),
    html.Hr(),
    ], fluid=True)
""" 
