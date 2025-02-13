from dash import Dash, html, dcc, callback, Output, Input, register_page
import dash_bootstrap_components as dbc
import pandas as pd
from sqlalchemy import create_engine
import pymysql
import dash_leaflet as dl
from os import environ as env

env['DB_URL_2']="mysql+pymysql://{user}:{password}@{host}:{port}/{name}".format(
    user=env['DB_USER_2'],
    password=env['DB_PASSWORD_2'],
    host=env['DB_HOST_2'],
    port=env['DB_PORT_2'],
    name=env['DB_NAME_momos_satma']
    )

env['DB_URL_3']="mysql+pymysql://{user}:{password}@{host}:{port}/{name}".format(
    user=env['DB_USER_2'],
    password=env['DB_PASSWORD_2'],
    host=env['DB_HOST_2'],
    port=env['DB_PORT_2'],
    name=env['DB_NAME_slidetrack']
    )

icon_orange = dict(
    iconUrl='https://img.icons8.com/?size=40&id=13800&format=png&color=000000',
)
icon_red = dict(
    iconUrl='https://img.icons8.com/?size=50&id=21613&format=png&color=FA5252',
)

icon_green = dict(
    iconUrl='https://img.icons8.com/?size=20&id=7880&format=png&color=40C057',
)

icon_black = dict(
    iconUrl='https://img.icons8.com/?size=25&id=7880&format=png&color=1A1A1A',
)

def tabla_nodo():
# Conexión a la base de datos MySQL
    engine = create_engine(env.get('DB_URL_2'), echo=True)
    # Consultas SQL
    query1 = "SELECT idNodo, nameNodo, latitud, longitud FROM nodos"
    query2 = "SELECT idNodo, nameMomo, tableMomo, latitud, longitud FROM momos"

    datos_tabla = pd.read_sql(query1, engine)
    dimnodo = pd.read_sql(query2, engine)

    datos_tabla = pd.merge(datos_tabla, dimnodo, on="idNodo")

    return datos_tabla

def obtener_datos(datos_tabla):
    datos_tabla['state'] = None
    #datos_tabla['color_nodo']=None
    datos_tabla['color_momo']=None
    momos= pd.unique(datos_tabla["tableMomo"])

    engine = create_engine(env.get('DB_URL_3'), echo=True)

    for i, momo in enumerate(momos):
        query = "SELECT ModuleState FROM "+momo+" ORDER BY stationTime DESC LIMIT 1;"
        state_momo = pd.read_sql(query, engine)
        state=state_momo.iloc[0, 0]
        datos_tabla.at[i, 'state'] = state
        if state==0:
            datos_tabla.at[i, 'color_momo'] = 'MOMO INACTIVO'
        elif state==1:
            datos_tabla.at[i, 'color_momo'] = 'MOMO ACTIVO'
        elif state==2:
            datos_tabla.at[i, 'color_momo'] = 'ALERTA NARANJA'
        elif state==3:
            datos_tabla.at[i, 'color_momo'] = 'ALERTA ROJA'


    return (datos_tabla)

datos_nodos= tabla_nodo()
datos_tabla = obtener_datos(datos_nodos)
sound=False

register_page(__name__, name="Taludes", path='/pereira/taludes')

layout= dbc.Container(children=[
    html.Div(
        children=[
    html.H1("Monitor de taludes", style={'textAlign': 'left', 'color': '#0d6efd', 'margin-left':'20px', 'padding':'10px'}),
    html.Hr()],
    style={'background-color':'AliceBlue'},
    ),
    dbc.Row(children=[

        dbc.Col([
            dl.Map(center=[4.8074, -75.7345], zoom=13, children=[
                dl.TileLayer(),
                dl.LayerGroup(id="layer")
            ], style={'width': '100%', 'height': '80vh'}), 
            dcc.Interval(
                    id='interval-component',
                    interval=60*1000, # in milliseconds
                    n_intervals=0)     
        ], width=12)
    ]),
    html.Hr(),
    ], fluid=True)

@callback(
    Output("layer", "children"),
    [Input("layer", "id"),
    Input('interval-component', 'n_intervals')] 
    )

def update_map(_, n):
    datos_nodos= tabla_nodo()
    datos_tabla = obtener_datos(datos_nodos)
    nodos = datos_tabla.groupby(['nameNodo'])
    markers = []
    sound=False
    for nameNodo, momos in nodos:
        for _, row in momos.iterrows():
            icon_momo=icon_green
            state=row["state"]
            lon=row["longitud_y"]
            lat=row["latitud_y"]
            name=row["nameNodo"]
            if state==3:
                icon_momo=icon_red
                sound=True
            if state==2:
                icon_momo=icon_orange
                sound=True
            if state==1:
                icon_momo=icon_green
            if state==0:
                icon_momo=icon_black

            marker=dl.Marker(position=[lat, lon],
                                icon=icon_momo,
                            children=[html.Audio(src='/assets/alert-102266.mp3', autoPlay=sound, # Ruta del archivo de audio en la carpeta assets
                            controls=False),
                            dl.Tooltip(name),
                            dl.Popup(
                                children=[
                                        dbc.Card(
                                        dbc.CardBody([
                                            html.H3(row["nameMomo"], className="card-title",style={"text-align":"center"}),
                                            dbc.Row([
                                                dbc.Col(
                                                    html.Div(
                                                        html.H5(row['color_momo']),
                                                        style={"text-align":"center", "margin":"3px"},
                                                        title=name  # Esto es para el tooltip
                                                    ),
                                                    width=12, 
                                                )
                                            ])
                                        ]),
                                        className="mb-3"
                                    )
                                        ])])
            markers.append(marker)

    return markers
