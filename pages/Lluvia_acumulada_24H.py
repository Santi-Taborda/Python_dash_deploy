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

env['DB_URL']="mysql+pymysql://{user}:{password}@{host}:{port}/{name}".format(
    user=env['DB_USER'],
    password=env['DB_PASSWORD'],
    host=env['DB_HOST'],
    port=env['DB_PORT'],
    name=env['DB_NAME']
    )

# La colonia, Mundo Nuevo, Ukumarí, La curva, La católica, La Dulcera, El Lago


def obtener_datos():
    fecha_actual= datetime.now().replace(tzinfo=pd.Timestamp.now().tz)
    fecha_40_dias_atras=fecha_actual - timedelta(days=1)
    hora_actual_str = fecha_actual.strftime('%Y-%m-%d %H:%M:%S')
    hace_40_dias_str = fecha_40_dias_atras.strftime('%Y-%m-%d %H:%M:%S')
    # Conexión a la base de datos MySQL
    engine = create_engine(env.get('DB_URL'), echo=True)
    # Consultas SQL
    query1 = "SELECT idEstacion, idVariable, IdTiempoRegistro, Valor FROM factmonitoreo WHERE idEstacion IN (1, 12, 30, 29, 78, 11, 13) AND IdVariable in (2) AND IdTiempoRegistro BETWEEN %s AND %s"
    query2 = "SELECT IdEstacion, Estacion FROM dimestacion"


    datos_tabla = pd.read_sql(query1, engine,  params=(hace_40_dias_str, hora_actual_str))
    dimestacion = pd.read_sql(query2, engine)
    dimestacion.rename(columns={"IdEstacion": "idEstacion"}, inplace=True)


    datos_tabla["IdTiempoRegistro"] = pd.to_datetime(datos_tabla["IdTiempoRegistro"], utc=True)
    datos_tabla = pd.merge(datos_tabla, dimestacion, on="idEstacion")
    datos_tabla["timestamp"] = datos_tabla['IdTiempoRegistro'].apply(lambda x: x.timestamp())
    datos_tabla.sort_values(by="IdTiempoRegistro", inplace=True)
    time_data_min=datos_tabla["timestamp"].iloc[0]
    time_data_max=datos_tabla["timestamp"].iloc[-1]
    return (datos_tabla, time_data_min, time_data_max)

datos_tabla,min_actualized,max_actualized = obtener_datos()

register_page(__name__, name="Lluvia_acumulada_24H", path='/pereira/lluvia_24H' )

layout= dbc.Container(children=[
    html.Div(
        children=[
    html.H1("Monitor de lluvia acumulada a 24 horas - Alcaldía de Pereira", style={'textAlign': 'left', 'color': '#0d6efd', 'margin-left':'20px', 'padding':'10px'}),
    html.Hr()],
    style={'background-color':'AliceBlue'}, 
    ),

    dbc.Row(children=[
        dbc.Col(children=[dbc.Card(children=[
                    dbc.CardBody(children=[
                    html.H4("Controles", className="card-title"),
                    html.H6("Seleccione las estaciones que desea visualizar:", className="card-text" ),
                    dcc.Dropdown(
                        id='station-dropdown-alc-Per-lluvia-24H',
                        options=pd.unique(datos_tabla["Estacion"]),
                        value='El Lago',
                        multi=True,
                        className='mb-3'),
                    dcc.Interval(
                    id='interval-component',
                    interval=10*60*1000, # in milliseconds  
                    n_intervals=0),

                    ])], 
                    className="shadow p-3 mb-5 bg-white rounded"
            )], width=3
        ),
        dbc.Col(
            dcc.Graph(id='monitor-alc-Per-lluvia-24H'),style={'overflowY': 'scroll', 'height': '100%'},
                width=9)
    ]),
    html.Hr(),
    ], fluid=True)

@callback(
    Output('monitor-alc-Per-lluvia-24H', 'figure'),
    Input('station-dropdown-alc-Per-lluvia-24H', 'value'),
    Input('interval-component', 'n_intervals')
    )

def update_monitor(stations,n):
    htmls=[]
    datos_tabla,min_actualized,max_actualized= obtener_datos()
    if isinstance(stations, str):
        stations = [stations]

    datos_tabla_filtrados= datos_tabla[datos_tabla["Estacion"].isin(stations)]
    cant_figures=pd.unique(datos_tabla_filtrados["Estacion"])

    if len(cant_figures)==0:
        fig= make_subplots(rows=1, cols=1, subplot_titles="")
        fig.add_trace(go.Scatter(x=None, y=None),
            row=1, col=1)
            
        fig.update_layout(autosize=True, title_text="SELECCIONE AL MENOS UNA ESTACIÓN")

    else: 
        fig= make_subplots(rows=len(cant_figures), cols=1, subplot_titles=cant_figures, vertical_spacing=0.1)
        for index, figure in enumerate(cant_figures):
            datos= datos_tabla_filtrados[datos_tabla_filtrados['Estacion']==figure]
            suma=0
            for indexer, row in datos.iterrows():
                if pd.isnull(datos.loc[indexer,'Valor']):
                    suma=suma
                else:
                    suma=suma+row["Valor"]

                datos.at[indexer, 'Valor']=suma
            suma=round(suma,2)
        
            #fig.add_trace(go.Scatter(x=datos['IdTiempoRegistro'], y=datos['Valor'], name=figure, mode="markers"),
             #   row=index+1, col=1)
            text=""+figure+":\n Lluvia acumulada: "+str(suma)+" mm"
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

        fig.update_layout(autosize=True, height=len(cant_figures)*300, plot_bgcolor="white", paper_bgcolor="LightSteelBlue", margin=dict(l=30, r=30, t=50, b=50))
    return fig
