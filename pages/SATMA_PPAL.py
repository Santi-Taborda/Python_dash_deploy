from dash import Dash, html, dcc, callback, Output, Input, register_page, callback_context
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
import ftplib

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

icon_ECT= dict(
    iconUrl='/assets/ECT.png',
    iconSize=[35, 35]
)

icon_EHT= dict(
    iconUrl='/assets/EHT.png',
    iconSize=[35, 35]
)

icon_ENT= dict(
    iconUrl='/assets/ENT.png',
    iconSize=[35, 35]
)

def obtener_datos():
    fecha_actual= datetime.now().replace(tzinfo=pd.Timestamp.now().tz)
    fecha_2_dias_atras=fecha_actual - timedelta(days=2)
    hora_actual_str = fecha_actual.strftime('%Y-%m-%d %H:%M:%S')
    hace_2_dias_str = fecha_2_dias_atras.strftime('%Y-%m-%d %H:%M:%S')
    # Conexión a la base de datos MySQL
    engine = create_engine(env.get('DB_URL'), echo=True)
    engine2=create_engine(env.get('DB_URL_2'), echo=True)
    # Consultas SQL
    query1 = "SELECT idEstacion, IdTiempoRegistro, IdVariable, Valor FROM factmonitoreo WHERE IdTiempoRegistro BETWEEN %s AND %s AND Valor IS NOT NULL"
    query2 = "SELECT IdEstacion, IdTipoEstacion, Estacion, Latitud, Longitud, Ubicacion FROM dimestacion WHERE IdTipoEstacion IN(1,2,3,7,9,10,11,12)"
    query3= "SELECT Estacion, Estado FROM estaciones"

    datos_tabla = pd.read_sql(query1, engine,  params=(hace_2_dias_str, hora_actual_str))
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
name=""

register_page(__name__, name="SATMA_PPAL", path='/SATMA_PPAL')

layout = dbc.Container([
    dcc.Store(id='selected_station', data=None),  # Estado del marcador seleccionado
    dl.Map(center=[5.0381, -75.5950], zoom=10, children=[
        dl.TileLayer(),
        dl.LayerGroup(id="layer_SATMA_p")
    ], style={'width': '100%', 'height': '80vh'}),
    dcc.Interval(id='interval-component', interval=5*60*1000, n_intervals=0)
], fluid=True)


@callback(
    Output("layer_SATMA_p", "children"),
    [Input("layer_SATMA_p", "id"),
    Input('interval-component', 'n_intervals')]
)
def update_markers(_,n):
    datos_tabla, estaciones = obtener_datos()
    markers = []
    for _, row in estaciones.iterrows():
        if row['IdTipoEstacion']==1 or row['IdTipoEstacion']==11 or row['IdTipoEstacion']==12:
            icon=icon_ECT            
        elif row['IdTipoEstacion']==2 or row['IdTipoEstacion']==9 or row['IdTipoEstacion']==10:
            icon=icon_EHT
        elif row['IdTipoEstacion']==3 or row['IdTipoEstacion']==7:
            icon=icon_ENT
        name=row['Estacion']

        marker= dl.Marker(
            position=[row["Latitud"], row["Longitud"]],
            icon=icon, 
            id=row['Estacion'],
            children=[dl.Tooltip(name),dl.Popup(id=f"popup-{row['Estacion']}", children="Cargando...", maxWidth=700, minWidth=700)])
        
        markers.append(marker)
    
    return markers


@callback(
    [Output(f"popup-{estacion}", "children") for estacion in estaciones["Estacion"]],
    [Input(estacion, "n_clicks") for estacion in estaciones["Estacion"]]
)
def display_popup(*args):
    ctx = callback_context
    if not ctx.triggered:
        return None  # No se ha hecho clic en ningún marcador

    estacion_seleccionada = ctx.triggered[0]["prop_id"].split(".")[0].replace("marker-", "")

    datos_tabla, estaciones=obtener_datos()
    estacion = estaciones[estaciones["Estacion"] == estacion_seleccionada]

    lon=estacion["Longitud"].iloc[0]
    lat=estacion["Latitud"].iloc[0]
    name=estacion["Estacion"].iloc[0]
    station_info=estacion["Ubicacion"].iloc[0]
    
    datos= datos_tabla[datos_tabla['Estacion']==estacion_seleccionada]
    datos_temp= datos[datos['IdVariable']== 1]
    fig_temp= go.Figure()
    fig_temp.add_trace({
            'type': 'scatter',
            'x': datos_temp['IdTiempoRegistro'],
            'y': datos_temp['Valor'],
            "mode": "lines",
            "fill": "tozeroy"
        })
    fig_temp.update_yaxes(title_text="Temperatura °C", showgrid=True, gridcolor='LightGray',range=[datos_temp['Valor'].min() * 0.9, datos_temp['Valor'].max() * 1.1])
    fig_temp.update_layout( width=425, height=225, plot_bgcolor="white", paper_bgcolor='Gainsboro', margin=dict(l=20, r=20, t=20, b=20), xaxis=dict(showgrid=False))
    
    datos_ppt= datos[datos['IdVariable']== 2]
    fig_ppt= go.Figure()
    fig_ppt.add_trace({
            'type': 'scatter',
            'x': datos_ppt['IdTiempoRegistro'],
            'y': datos_ppt['Valor'],
            "mode": "lines",
            "fill": "tozeroy"
        })
    fig_ppt.update_yaxes(title_text="Precipitación (mm)", showgrid=True, gridcolor='LightGray',range=[datos_ppt['Valor'].min() * 0.9, datos_ppt['Valor'].max() * 1.1])
    fig_ppt.update_layout( width=425, height=225, plot_bgcolor="white", paper_bgcolor='Gainsboro', margin=dict(l=20, r=20, t=20, b=20), xaxis=dict(showgrid=False))
    
    datos_hr= datos[datos['IdVariable']== 3]
    fig_hr= go.Figure()
    fig_hr.add_trace({
            'type': 'scatter',
            'x': datos_hr['IdTiempoRegistro'],
            'y': datos_hr['Valor'],
            "mode": "lines",
            "fill": "tozeroy"
        })
    fig_hr.update_yaxes(title_text="Humedad Relativa (%)", showgrid=True, gridcolor='LightGray',range=[datos_hr['Valor'].min() * 0.9, datos_hr['Valor'].max() * 1.1])
    fig_hr.update_layout( width=425, height=225, plot_bgcolor="white", paper_bgcolor='Gainsboro', margin=dict(l=20, r=20, t=20, b=20), xaxis=dict(showgrid=False))
    
    datos_rad= datos[datos['IdVariable']== 4]
    fig_rad= go.Figure()
    fig_rad.add_trace({
            'type': 'scatter',
            'x': datos_rad['IdTiempoRegistro'],
            'y': datos_rad['Valor'],
            "mode": "lines",
            "fill": "tozeroy"
        })
    fig_rad.update_yaxes(title_text="Radiación (W/m^2)", showgrid=True, gridcolor='LightGray')
    fig_rad.update_layout( width=425, height=225, plot_bgcolor="white", paper_bgcolor='Gainsboro', margin=dict(l=20, r=20, t=20, b=20), xaxis=dict(showgrid=False))
    

    datos_presion= datos[datos['IdVariable']== 5]
    fig_presion= go.Figure()
    fig_presion.add_trace({
            'type': 'scatter',
            'x': datos_presion['IdTiempoRegistro'],
            'y': datos_presion['Valor'],
            "mode": "lines",
            "fill": "tozeroy"
        })
    fig_presion.update_yaxes(title_text="Presión barométrica mm/Hg", showgrid=True, gridcolor='LightGray')
    fig_presion.update_layout( width=425, height=225, plot_bgcolor="white", paper_bgcolor='Gainsboro', margin=dict(l=20, r=20, t=20, b=20), xaxis=dict(showgrid=False))
    

    datos_vel= datos[datos['IdVariable']== 6]
    fig_vel= go.Figure()
    fig_vel.add_trace({
            'type': 'scatter',
            'x': datos_vel['IdTiempoRegistro'],
            'y': datos_vel['Valor'],
            "mode": "lines",
            "fill": "tozeroy"
        })
    fig_vel.update_yaxes(title_text="Velocidad del viento (m/s)", showgrid=True, gridcolor='LightGray')
    fig_vel.update_layout( width=425, height=225, plot_bgcolor="white", paper_bgcolor='Gainsboro', margin=dict(l=20, r=20, t=20, b=20), xaxis=dict(showgrid=False))
    
    datos_dir= datos[datos['IdVariable']== 7]
    fig_dir= go.Figure()
    fig_dir.add_trace({
            'type': 'scatter',
            'x': datos_dir['IdTiempoRegistro'],
            'y': datos_dir['Valor'],
            "mode": "lines",
            "fill": "tozeroy"
        })
    fig_dir.update_yaxes(title_text="direccion del viento (°)", showgrid=True, gridcolor='LightGray')
    fig_dir.update_layout( width=425, height=225, plot_bgcolor="white", paper_bgcolor='Gainsboro', margin=dict(l=20, r=20, t=20, b=20), xaxis=dict(showgrid=False))
    
    datos_eva= datos[datos['IdVariable']== 11]
    fig_eva= go.Figure()
    fig_eva.add_trace({
            'type': 'scatter',
            'x': datos_eva['IdTiempoRegistro'],
            'y': datos_eva['Valor'],
            "mode": "lines",
            "fill": "tozeroy"
        })
    fig_eva.update_yaxes(title_text="Evaporación (mm)", showgrid=True, gridcolor='LightGray')
    fig_eva.update_layout( width=425, height=225, plot_bgcolor="white", paper_bgcolor='Gainsboro', margin=dict(l=20, r=20, t=20, b=20), xaxis=dict(showgrid=False))

    datos_nivel= datos[(datos['IdVariable']== 8) | (datos['IdVariable']== 9)]
    fig_nivel= go.Figure()
    fig_nivel.add_trace({
            'type': 'scatter',
            'x': datos_nivel['IdTiempoRegistro'],
            'y': datos_nivel['Valor'],
            "mode": "lines",
            "fill": "tozeroy"
        })
    fig_nivel.update_yaxes(title_text="Nivel (%)", showgrid=True, gridcolor='LightGray',range=[datos_nivel['Valor'].min() * 0.9, datos_nivel['Valor'].max() * 1.1])
    fig_nivel.update_layout( width=425, height=225, plot_bgcolor="white", paper_bgcolor='Gainsboro', margin=dict(l=20, r=20, t=20, b=20), xaxis=dict(showgrid=False))
    
    datos_caudal= datos[datos['IdVariable']== 12]
    fig_caudal= go.Figure()
    fig_caudal.add_trace({
            'type': 'scatter',
            'x': datos_caudal['IdTiempoRegistro'],
            'y': datos_caudal['Valor'],
            "mode": "lines",
            "fill": "tozeroy"
        })
    fig_caudal.update_yaxes(title_text="Caudal m^3/s", showgrid=True, gridcolor='LightGray',range=[datos_caudal['Valor'].min() * 0.9, datos_caudal['Valor'].max() * 1.1])
    fig_caudal.update_layout( width=425, height=225, plot_bgcolor="white", paper_bgcolor='Gainsboro', margin=dict(l=20, r=20, t=20, b=20), xaxis=dict(showgrid=False))
    

    if estacion['IdTipoEstacion'].iloc[0]==1:
        dbc_tabs=dbc.Tabs([
            dbc.Tab(dcc.Graph(figure=fig_temp), label="Temperatura"),
            dbc.Tab(dcc.Graph(figure=fig_ppt), label="Precipitación"),
            dbc.Tab(dcc.Graph(figure=fig_hr), label="Humedad Relativa"),
            dbc.Tab(dcc.Graph(figure=fig_rad), label="Radiación"),
            dbc.Tab(dcc.Graph(figure=fig_vel), label="Velocidad del viento"),
            dbc.Tab(dcc.Graph(figure=fig_dir), label="Dirección del viento"),
            dbc.Tab(dcc.Graph(figure=fig_eva), label="Evaporación")                     
        ])
            
        
    elif estacion['IdTipoEstacion'].iloc[0]==2:
        dbc_tabs=dbc_tabs=dbc.Tabs([
        dbc.Tab(dcc.Graph(figure=fig_temp), label="Temperatura"),
        dbc.Tab(dcc.Graph(figure=fig_ppt), label="Precipitación"),
        dbc.Tab(dcc.Graph(figure=fig_nivel), label="Nivel")
        ])
        
    elif estacion['IdTipoEstacion'].iloc[0]==3:
        dbc_tabs=dbc_tabs=dbc.Tabs([
        dbc.Tab(dcc.Graph(figure=fig_nivel), label="Nivel")
        ])

    elif estacion['IdTipoEstacion'].iloc[0]==7:
        dbc_tabs=dbc_tabs=dbc.Tabs([dbc.Tab(dcc.Graph(figure=fig_caudal), label="Caudal")])

    elif estacion['IdTipoEstacion'].iloc[0]==9:
        dbc_tabs=dbc_tabs=dbc.Tabs([
        dbc.Tab(dcc.Graph(figure=fig_nivel), label="Nivel"),
        dbc.Tab(dcc.Graph(figure=fig_caudal), label="Caudal")
        ])

    elif estacion['IdTipoEstacion'].iloc[0]==10:
        dbc_tabs=dbc.Tabs([
        dbc.Tab(dcc.Graph(figure=fig_temp), label="Temperatura"),
        dbc.Tab(dcc.Graph(figure=fig_ppt), label="Precipitación"),
        dbc.Tab(dcc.Graph(figure=fig_hr), label="Humedad Relativa"),
        dbc.Tab(dcc.Graph(figure=fig_nivel), label="Nivel")
        ])
        
    elif estacion['IdTipoEstacion'].iloc[0]==11:
        dbc_tabs=dbc.Tabs([
        dbc.Tab(dcc.Graph(figure=fig_temp), label="Temperatura"),
        dbc.Tab(dcc.Graph(figure=fig_ppt), label="Precipitación"),
        dbc.Tab(dcc.Graph(figure=fig_nivel), label="Nivel"),
        dbc.Tab(dcc.Graph(figure=fig_caudal), label="Caudal")
        ])
    elif estacion['IdTipoEstacion'].iloc[0]==12:
        dbc_tabs=dbc.Tabs([
            dbc.Tab(dcc.Graph(figure=fig_temp), label="Temperatura"),
            dbc.Tab(dcc.Graph(figure=fig_ppt), label="Precipitación"),
            dbc.Tab(dcc.Graph(figure=fig_hr), label="Humedad Relativa"),
            dbc.Tab(dcc.Graph(figure=fig_presion), label="Presión barométrica"),
            dbc.Tab(dcc.Graph(figure=fig_vel), label="Velocidad del viento"),
            dbc.Tab(dcc.Graph(figure=fig_dir), label="Dirección del viento")                  
        ])                             


    popup_content = []

    for estacion in estaciones["Estacion"]:

        if estacion==estacion_seleccionada:
            children=[
                                dbc.Card(
                                    dbc.CardBody([
                                        html.Div([
                                            html.Div([
                                                html.H3(name, className="card-title", style={"text-align": "center"}),
                                                html.P(station_info, className="card-text", style={"text-align": "center"}),
                                                html.Img(src="/assets/bocatoma_nuevo_libare.jpeg", style={"width": "100%", "border-radius": "10px", "margin-top": "10px", "border": "3px solid #ddd"}),
                                            ], style={"flex": "1", "padding": "10px"}),
                                            html.Div([
                                                dbc_tabs
                                            ], style={"flex": "2", "padding": "10px"})
                                        ], style={"display": "flex", "flex-direction": "row"})
                                    ]),
                                    style={"width": "700px", "margin": "auto", "box-shadow": "0 4px 8px 0 rgba(0, 0, 0, 0.2)", "border-radius": "10px"}
                                )
                            ]
            popup_content.append(children)
        else: 
            popup_content.append(["Cargando..."])
    return popup_content
