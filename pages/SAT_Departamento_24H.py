from dash import Dash, html, dcc, callback, Output, Input, register_page
import plotly.express as px
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import pymysql
from plotly.subplots import make_subplots
import dash_leaflet as dl
from datetime import datetime, timedelta, date, time
from os import environ as env
from scipy.spatial import cKDTree

env['DB_URL']="mysql+pymysql://{user}:{password}@{host}:{port}/{name}".format(
    user=env['DB_USER'],
    password=env['DB_PASSWORD'],
    host=env['DB_HOST'],
    port=env['DB_PORT'],
    name=env['DB_NAME']
    )

env['DB_URL_2']="mysql+pymysql://{user}:{password}@{host}:{port}/{name}".format(
    user=env['DB_USER_2'],
    password=env['DB_PASSWORD_2'],
    host=env['DB_HOST_2'],
    port=env['DB_PORT_2'],
    name=env['DB_NAME_SATMA']
    )

icon_yellow= dict(
    iconUrl='https://img.icons8.com/?size=40&id=VW9mAoyk46FP&format=png&color=000000',
)

icon_orange = dict(
    iconUrl='https://img.icons8.com/?size=60&id=zQ1yf8Peqsvz&format=png&color=000000',
)

icon_red = dict(
    iconUrl='https://img.icons8.com/?size=80&id=Zyo5wDjgJxRW&format=png&color=000000',
)

icon_green = dict(
    iconUrl='https://img.icons8.com/?size=20&id=FkQHNSmqWQWH&format=png&color=000000',
)

def obtener_datos():
    fecha_actual= datetime.now().replace(tzinfo=pd.Timestamp.now().tz)
    fecha_40_dias_atras=fecha_actual - timedelta(days=1)
    hora_actual_str = fecha_actual.strftime('%Y-%m-%d %H:%M:%S')
    hace_40_dias_str = fecha_40_dias_atras.strftime('%Y-%m-%d %H:%M:%S')
    # Conexión a la base de datos MySQL
    engine = create_engine(env.get('DB_URL'), echo=True)
    engine2=create_engine(env.get('DB_URL_2'), echo=True)
    # Consultas SQL
    query1 = "SELECT idEstacion, IdTiempoRegistro, Valor FROM factmonitoreo WHERE IdVariable in (2) AND IdTiempoRegistro BETWEEN %s AND %s AND Valor IS NOT NULL"
    query2 = "SELECT IdEstacion, Estacion, Latitud, Longitud FROM dimestacion WHERE IdTipoEstacion IN(1,2,7,8,9,10,11,12) "
    query3= "SELECT Estacion, Estado FROM estaciones"

    datos_tabla = pd.read_sql(query1, engine,  params=(hace_40_dias_str, hora_actual_str))
    dimestacion = pd.read_sql(query2, engine)
    dimestado = pd.read_sql(query3, engine2)
    dimestacion.rename(columns={"IdEstacion": "idEstacion"}, inplace=True)

    datos_tabla["IdTiempoRegistro"] = pd.to_datetime(datos_tabla["IdTiempoRegistro"], utc=True)
    datos_tabla = pd.merge(datos_tabla, dimestacion, on="idEstacion")
    datos_tabla = pd.merge(datos_tabla, dimestado, on="Estacion")
    datos_tabla_filtrados= datos_tabla[datos_tabla["Estado"] == 1]
    datos_tabla_filtrados.sort_values(by="IdTiempoRegistro", inplace=True)

    return datos_tabla_filtrados, dimestacion

datos_tabla, estaciones=obtener_datos()
sound=False

register_page(__name__, name="SAT_DEPARTAMENTAL_24H", path='/SAT/DEPARTAMENTO/24H')

layout= dbc.Container(children=[
    html.Div(
        children=[
    html.H1("Monitor SAT DEPARTAMENTAL 24 HORAS", style={'textAlign': 'left', 'color': '#0d6efd', 'margin-left':'20px', 'padding':'10px'}),
    html.Hr()],
    style={'background-color':'AliceBlue'},
    ),
    dbc.Row(children=[
        dbc.Col([
            dl.Map(center=[5.0381, -75.5950], zoom=10, children=[
                dl.TileLayer(),
                dl.LayerGroup(id="layer_SAT_Departamento_24H")
            ], style={'width': '100%', 'height': '80vh'}), 

            dcc.Interval(
                    id='interval-component',
                    interval=5*60*1000, # in milliseconds
                    n_intervals=0)     
        ], width=12)
    ]),
    html.Hr(),
    ], fluid=True)


@callback(
    Output("layer_SAT_Departamento_24H", "children"),
    [Input("layer_SAT_Departamento_24H", "id"),
    Input('interval-component', 'n_intervals')] 
    )

def update_map(_, n):
    datos_tabla, estaciones=obtener_datos()
    markers = []
    cant_figures=pd.unique(estaciones["Estacion"])

    for index, figure in enumerate(cant_figures):
        datos= datos_tabla[datos_tabla['Estacion']==figure]
        suma=0
        for indexer, row in datos.iterrows():
            if pd.isnull(datos.loc[indexer,'Valor']):
                suma=suma
            else:
                suma=suma+row["Valor"]

            datos.at[indexer, 'Valor']=suma
        suma=round(suma,2)
        fig= go.Figure()
        fig.add_trace({
                'type': 'scatter',
                'x': datos['IdTiempoRegistro'],
                'y': datos['Valor'],
                "mode": "lines",
                "fill": "tozeroy"
            })
        fig.update_yaxes(title_text="Lluvia acumulada (mm)")
        fig.update_layout(showlegend=False, width=350, height=225, plot_bgcolor="white", paper_bgcolor="LightSteelBlue", margin=dict(l=30, r=30, t=30, b=30))
        
        estacion=estaciones[estaciones['Estacion']==figure]
        #estacion=estaciones[estaciones['Estacion']=='El Lago']
        icon=icon_green
        lon=estacion["Longitud"].iloc[0]
        lat=estacion["Latitud"].iloc[0]
        name=estacion["Estacion"].iloc[0]
        sound=False
        if suma>=50:
            if icon != icon_red:
                icon=icon_red
                sound=True
        elif suma >=32.5:
            if icon != icon_orange:
                icon=icon_orange
                sound=True
        elif suma >=25:
            if icon != icon_yellow:
                icon=icon_yellow
                sound=True

        marker=dl.Marker(position=[lat, lon],
                            icon=icon,
                            children=[
                            html.Audio(src='/assets/alert-102266.mp3', autoPlay=sound, # Ruta del archivo de audio en la carpeta assets
                            controls=False),
                            dl.Tooltip(name),
                            dl.Popup(
                                children=[    
                                        dbc.Card(
                                        dbc.CardBody([
                                            html.H3(figure, className="card-title",style={"text-align":"center"}),
                                            dbc.Row([
                                                dbc.Col(
                                                    html.Div(
                                                        dcc.Graph(figure=fig),
                                                    ), 
                                                )
                                            ])
                                        ]),
                                        className="mb-3", 
                                    )
                                        ],maxWidth = 375, minWidth=375)])
        markers.append(marker)

    return markers