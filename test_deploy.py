from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
import pandas as pd
from sqlalchemy import create_engine
import pymysql
from plotly.subplots import make_subplots
from datetime import datetime
from os import environ as env

env['DB_URL']="mysql+pymysql://{user}:{password}@{host}:{port}/{name}".format(
    user=env['DB_USER'],
    password=env['DB_PASSWORD'],
    host=env['DB_HOST'],
    port=env['DB_PORT'],
    name=env['DB_NAME']
    )
 

def obtener_datos():
# Conexión a la base de datos MySQL
    engine = create_engine(env.get('DB_URL'), echo=True)
    # Consultas SQL
    query1 = "SELECT idEstacion, idVariable, IdTiempoRegistro, Valor FROM factmonitoreo_1s WHERE idEstacion IN (14, 31, 26, 84, 24, 25, 79, 23, 10, 15, 8, 3)"
    #query1 = "SELECT idEstacion, idVariable, IdTiempoRegistro, Valor FROM factmonitoreo_1s WHERE idEstacion IN (14)"
    query2 = "SELECT IdEstacion, Estacion FROM dimestacion"
    query3 = "SELECT idVariable, Variable FROM dimvariable"


    datos_tabla = pd.read_sql(query1, engine)
    dimestacion = pd.read_sql(query2, engine)
    dimestacion.rename(columns={"IdEstacion": "idEstacion"}, inplace=True)
    dimvariable = pd.read_sql(query3, engine)

    datos_tabla["IdTiempoRegistro"] = pd.to_datetime(datos_tabla["IdTiempoRegistro"])
    datos_tabla = pd.merge(datos_tabla, dimestacion, on="idEstacion")
    datos_tabla = pd.merge(datos_tabla, dimvariable, on="idVariable")
    datos_tabla["timestamp"] = datos_tabla['IdTiempoRegistro'].apply(lambda x: x.timestamp())
    datos_tabla.sort_values(by="IdTiempoRegistro", inplace=True)
    # Corregir valores de la variable 9 a 8
    datos_tabla.loc[datos_tabla["idVariable"] == 9, "idVariable"] = 8
    datos_tabla.loc[datos_tabla["idVariable"] == 9, "Variable"] = "Nivel del Cauce"

    return (datos_tabla)


def obtener_fecha():
# Conexión a la base de datos MySQL
    engine = create_engine(env.get('DB_URL'), echo=True)
    # Consultas SQL
    query1 = "SELECT IdTiempoRegistro, Valor FROM factmonitoreo_1s WHERE idEstacion IN (14, 31, 26, 84, 24, 25, 79, 23, 10, 15, 8, 3)"
    #query1 = "SELECT idEstacion, idVariable, IdTiempoRegistro, Valor FROM factmonitoreo_1s WHERE idEstacion IN (14)"

    datos_tabla = pd.read_sql(query1, engine)

    datos_tabla["IdTiempoRegistro"] = pd.to_datetime(datos_tabla["IdTiempoRegistro"])
    datos_tabla["timestamp"] = datos_tabla['IdTiempoRegistro'].apply(lambda x: x.timestamp())
    time_data=[datos_tabla["timestamp"].min(),datos_tabla["timestamp"].max()]
    return (time_data)

min_actualized,max_actualized =obtener_fecha()
datos_tabla = obtener_datos()
tooltip_new={"placement": "top", "always_visible": False, "transform": "Hora_legible"}

app = Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN])

app.layout= dbc.Container(children=[
    html.Div(
        children=[
    html.H1("Monitor de variables AyA", style={'textAlign': 'left', 'color': '#0d6efd', 'margin-left':'20px', 'padding':'10px'}),
    html.Hr()],
    style={'background-color':'AliceBlue'},
    ),

    dbc.Row(children=[
        dbc.Col(children=[dbc.Card(children=[
                    dbc.CardBody(children=[
                    html.H4("Controles", className="card-title"),
                    html.H6("Seleccione las estaciones que desea visualizar:", className="card-text" ),
                    dcc.Dropdown(
                        id='station-dropdown',
                        options=pd.unique(datos_tabla["Estacion"]),
                        value='Planta de tratamiento',
                        multi=True,
                        className='mb-3'),
                        
                    html.H6("Seleccione el rango de fechas que desea visualizar:", className="card-text" ),

                    dbc.Card(children=[
                    dcc.RangeSlider(id='datetime-range-slider',
                                    min=min_actualized,
                                    max=max_actualized, 
                                    value=[min_actualized,max_actualized],
                                    marks=None,
                                    allowCross=False,
                                    tooltip=tooltip_new,
                                    className='mt-3')
                                    ],className="shadow-none p-1 mb-2 rounded", color="#D3F1FF"),

                    html.H6(id='actualizador-slider'),

                    html.H6("Seleccione la variable que desea visualizar:", className="card-text", style={'margin-top':'1em'}),

                    dcc.RadioItems(id='variable-button',
                                    options=pd.unique(datos_tabla["Variable"]),
                                    value='Temperatura', inline=False, className='mb-3'),
                    dcc.Interval(
                    id='interval-component',
                    interval=3*60*1000, # in milliseconds
                    n_intervals=0),

                    ])], 
                    className="shadow p-3 mb-5 bg-white rounded"
            )], width=3
        ),
        dbc.Col(
            dcc.Graph(id='monitor'),style={'overflowY': 'scroll', 'height': '100%'},
                width=9)
    ]),
    html.Hr(),
    ], fluid=True)

@app.callback(
   [Output('datetime-range-slider', 'min'),
    Output('datetime-range-slider', 'max'),
    Output('datetime-range-slider', 'value'),
    Output('datetime-range-slider', 'tooltip'),
    Output('actualizador-slider', 'children')],
   Input('interval-component', 'n_intervals') 
)

def update_slider(n):
    min_actualized,max_actualized =obtener_fecha()
    time_max=pd.to_datetime(max_actualized, unit='s')
    time= datetime.now()
    dif=time-time_max
    tooltip_new={"placement": "top", "always_visible": False, "transform": "Hora_legible"}

    return (min_actualized, max_actualized,[min_actualized,max_actualized],tooltip_new,html.H6(f"{int(dif.total_seconds() // 60)} minutos desde la última actualización", 
                                                                                   style={'font-size':'80%'}))


@app.callback(
    Output('monitor', 'figure'),
    Input('datetime-range-slider', 'value'),
    Input('station-dropdown', 'value'),
    Input ('variable-button', 'value'),
    Input('interval-component', 'n_intervals')
    )

def update_monitor(date_time, stations, variable,n):
    datos_tabla = obtener_datos()

    if isinstance(stations, str):
        stations = [stations]

    datos_tabla_filtrados= datos_tabla[datos_tabla["Estacion"].isin(stations)]
    datos_tabla_filtrados= datos_tabla_filtrados[datos_tabla_filtrados["Variable"] == variable]
    start_time = pd.to_datetime(date_time[0], unit='s')
    end_time = pd.to_datetime(date_time[1], unit='s')
    datos_tabla_filtrados = datos_tabla_filtrados[
        (datos_tabla_filtrados["IdTiempoRegistro"] >= start_time) &
        (datos_tabla_filtrados["IdTiempoRegistro"] <= end_time)
    ]
    cant_figures=pd.unique(datos_tabla_filtrados["Estacion"])

    if len(cant_figures)==0:
        fig= make_subplots(rows=1, cols=1, subplot_titles="")
        fig.add_trace(go.Scatter(x=None, y=None),
            row=1, col=1)
            
        fig.update_layout(autosize=True, title_text="NINGUNA DE LAS ESTACIONES SELECCIONADAS MONITOREA LA VARIABLE ESTABLECIDA")
    else: 
        fig= make_subplots(rows=len(cant_figures), cols=1, subplot_titles=cant_figures, vertical_spacing=0.1)
        for index, figure in enumerate(cant_figures):
            datos= datos_tabla_filtrados[datos_tabla_filtrados['Estacion']==figure]
            #fig.add_trace(go.Scatter(x=datos['IdTiempoRegistro'], y=datos['Valor'], name=figure, mode="markers"),
             #   row=index+1, col=1)
            fig.add_trace( {
                'type': 'scatter',
                'x': datos['IdTiempoRegistro'],
                'y': datos['Valor'],
                'mode': 'none',
                'fill': 'tozeroy',
                'name': figure
            },
            row=index+1, col=1)
            fig.update_yaxes(title_text=variable, row=index+1, col=1)

        fig.update_layout(autosize=True, height=len(cant_figures)*300, paper_bgcolor="LightSteelBlue", margin=dict(l=30, r=30, t=30, b=30))
    return fig
