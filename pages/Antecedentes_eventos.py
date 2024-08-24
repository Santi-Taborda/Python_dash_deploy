from dash import Dash, html, dcc, callback, Output, Input, register_page
import plotly.express as px
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import pymysql
from plotly.subplots import make_subplots
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

# La colonia, Mundo Nuevo, Ukumarí, La curva, La católica, La Dulcera, El Lago

def datos_iniciales():
    fecha_actual=datetime.now().replace(tzinfo=pd.Timestamp.now().tz)
    fecha_40_dias_atras=fecha_actual - timedelta(days=40)
    engine = create_engine(env.get('DB_URL'), echo=True)
    query2 = "SELECT IdEstacion, Estacion, Latitud, Longitud FROM dimestacion WHERE IdTipoEstacion IN(1,2,7,8,9,10,11,12)"
    dimestacion = pd.read_sql(query2, engine)
    dimestacion.rename(columns={"IdEstacion": "idEstacion"}, inplace=True)

    return dimestacion, fecha_actual, fecha_40_dias_atras

puntos, max_actualized, min_actualized = datos_iniciales()

register_page(__name__, name="Consulta_antecedentes", path='/SATMA/consulta_antecedentes' )

layout= dbc.Container(children=[
    html.Div(
        children=[
    html.H1("Consulta antecedentes de lluvia", style={'textAlign': 'left', 'color': '#0d6efd', 'margin-left':'20px', 'padding':'10px'}),
    html.Hr()],
    style={'background-color':'AliceBlue'}, 
    ),

    dbc.Row(children=[
        dbc.Col(children=[dbc.Card(children=[
                    dbc.CardBody(children=[
                    html.H4("Controles", className="card-title"),
                    html.H6("Seleccione la latitud:", className="card-text" ),
                    dcc.Input(
                        id='Latitud_consulta_antecedentes',
                        value=4.8212,
                        type='number',
                        className='mb-3'),
                    html.H6("Seleccione la longitud:", className="card-text" ),
                    dcc.Input(
                        id='Longitud_consulta_antecedentes',
                        value=-75.6979,
                        type='number',
                        className='mb-3'),

                    html.H6("Seleccione la fecha del evento:", className="card-text" ),
                    dcc.DatePickerSingle(
                        id='Fecha_consulta_antecedentes',
                        month_format='MMM Do, YY',
                        placeholder='MMM Do, YY',
                        date=date.today(),
                        className='mb-3'),
                    
                    html.H6("Seleccione la cantidad de días que quiere consultar:", className="card-text" ),
                    dcc.Input(
                        id='Cantidad_dias_antecedentes',
                        value=40,
                        type='number',
                        className='mb-3'),
                    html.Div(
                    children=[
                        dcc.Graph(id='tabla_lluvia_antecedentes'),
                    ],
                    style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center'}
                    ),
                    

                    ])], 
                    className="shadow p-3 mb-5 bg-white rounded"
            ), ], width=3
        ),
        dbc.Col(
            dcc.Graph(id='Monitor_consulta_antecedentes'),style={'overflowY': 'scroll', 'height': '100%'},
                width=9)
    ]),
    html.Hr(),
    ], fluid=True)

@callback(
    Output('Monitor_consulta_antecedentes', 'figure'),
    Output('tabla_lluvia_antecedentes', 'figure'),
    Input('Cantidad_dias_antecedentes', 'value'),
    Input('Latitud_consulta_antecedentes', 'value'),
    Input('Longitud_consulta_antecedentes', 'value'),
    Input('Fecha_consulta_antecedentes', 'date')
    )

def update_monitor(dias, latitud, longitud, dia_inicio):
    datos_tabla,max_actualized,min_actualized= datos_iniciales()
    fecha=date.fromisoformat(dia_inicio)
    #fecha=date.today()
    hora_1159pm = time(23, 59, 0)
    max_actualized=datetime.combine(fecha, hora_1159pm)
    min_actualized=max_actualized - timedelta(days=dias)
    #min_actualized=max_actualized - timedelta(days=40)
    puntos = np.empty((len(datos_tabla), 2))

    for i, row in datos_tabla.iterrows():
        puntos[i] = [row['Latitud'],row['Longitud']]
    #nuevo_punto = np.array([4.8146, -75.6981])
    nuevo_punto = np.array([latitud, longitud])
    tree = cKDTree(puntos)
    distancias, indices = tree.query(nuevo_punto, k=5)

    puntos=puntos[indices,0]

    datos_tabla_filtrados=datos_tabla[datos_tabla["Latitud"].isin(puntos)]

    engine = create_engine(env.get('DB_URL'), echo=True)
    
    query="SELECT idEstacion, date(IdTiempoRegistro) AS IdTiempoRegistro, ROUND(SUM(Valor), 2) AS Valor FROM factmonitoreo WHERE idEstacion IN (%s, %s, %s, %s, %s) AND IdVariable IN (2) AND IdTiempoRegistro BETWEEN %s AND %s AND Valor IS NOT NULL GROUP BY idEstacion, date(IdTiempoRegistro)"

    datos_fin = pd.read_sql(query, engine, params=(datos_tabla_filtrados.iloc[0]['idEstacion'],datos_tabla_filtrados.iloc[1]['idEstacion'],datos_tabla_filtrados.iloc[2]['idEstacion'],datos_tabla_filtrados.iloc[3]['idEstacion'],datos_tabla_filtrados.iloc[4]['idEstacion'],min_actualized, max_actualized))

    datos_fin = pd.merge(datos_fin, datos_tabla_filtrados, on="idEstacion")

    cant_figures=pd.unique(datos_tabla_filtrados["Estacion"])

    if len(cant_figures)==0:
        fig= make_subplots(rows=1, cols=1, subplot_titles="")
        fig.add_trace(go.Scatter(x=None, y=None),
            row=1, col=1)
            
        fig.update_layout(autosize=True, title_text="EL PUNTO INTRODUCIDO NO TIENE ESTACIONES CERCANAS")

    else:
        sumas = np.empty((5, 1))
        fig= make_subplots(rows=len(cant_figures), cols=1, subplot_titles=cant_figures, vertical_spacing=0.1)
        for index, figure in enumerate(cant_figures):
            datos= datos_fin[datos_fin['Estacion']==figure]
            suma=0
            distancia=round(distancias[index],3)
            for indexer, row in datos.iterrows():
                if pd.isnull(datos.loc[indexer,'Valor']):
                    suma=suma
                else:
                    suma=suma+row["Valor"]

                datos.at[indexer, 'Valor']=suma
            suma=round(suma,2)
            sumas[index]=suma

            text=""+figure+""
            fig.add_trace({
                'type': 'scatter',
                'x': datos['IdTiempoRegistro'],
                'y': datos['Valor'],
                'name': text,
                "mode": "lines",
                "fill": "tozeroy"
            },
            row=index+1, col=1)
            fig.update_yaxes(title_text="Lluvia acumulada (mm)", row=index+1, col=1)

        fig.update_layout(autosize=True, height=len(cant_figures)*300, bargap=0.1, plot_bgcolor="white", paper_bgcolor="LightSteelBlue", margin=dict(l=30, r=30, t=30, b=0))
    
    fig_4= go.Figure(data=[go.Table(
    header=dict(values=['Estación', 'Precipitación acumulada', 'Distancia'],
                line_color='darkslategray',
                fill_color='lightskyblue',
                align='left'),
    cells=dict(values=[[datos_tabla_filtrados.iloc[0]['Estacion'], datos_tabla_filtrados.iloc[1]['Estacion'], datos_tabla_filtrados.iloc[2]['Estacion'], datos_tabla_filtrados.iloc[3]['Estacion'], datos_tabla_filtrados.iloc[4]['Estacion']],
                       [sumas[0], sumas[1], sumas[2],sumas[3],sumas[4]],
                       [round(distancias[0]*111,3),round(distancias[1]*111,3),round(distancias[2]*111,3),round(distancias[3]*111,3),round(distancias[4]*111,3)]],
                       
               line_color='darkslategray',
               fill_color='lightcyan',
               align='left'))
    ])

    fig_4.update_layout(width=300, height=300, margin=dict(l=0, r=0, t=20, b=10))


    return fig, fig_4
