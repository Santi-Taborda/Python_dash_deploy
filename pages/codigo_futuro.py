from dash import Dash, html, dcc, callback, Output, Input, register_page
import plotly.express as px
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
import pandas as pd
from sqlalchemy import create_engine
import pymysql
from plotly.subplots import make_subplots
from datetime import datetime
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
    # Conexión a la base de datos MySQL
    engine = create_engine(env.get('DB_URL'), echo=True)
    # Consultas SQL
    query1 = "SELECT * FROM cc_visor"
    query2 = "SELECT idMunicipio, Municipio FROM ccmunicipios"
    query3 = "SELECT idVariable, Variable FROM ccvariables"


    datos_tabla = pd.read_sql(query1, engine)
    dimestacion = pd.read_sql(query2, engine)
    dimvariable = pd.read_sql(query3, engine)

    datos_tabla["idTiempo"] = pd.to_datetime(datos_tabla["idTiempo"])
    datos_tabla = pd.merge(datos_tabla, dimestacion, on="idMunicipio")
    datos_tabla = pd.merge(datos_tabla, dimvariable, on="idVariable")

    datos_tabla.sort_values(by="idTiempo", inplace=True)

    return (datos_tabla)

datos_tabla= obtener_datos()

register_page(__name__, name="Escenarios_futuros", path='/SAT/escenarios')


layout= dbc.Container(children=[
    html.Div(
        children=[
    html.H1("Monitor de escenarios futuros", style={'textAlign': 'left', 'color': '#0d6efd', 'margin-left':'20px', 'padding':'10px'}),
    html.Hr()],
    style={'background-color':'AliceBlue'},
    ),

    dbc.Row(children=[
        dbc.Col(children=[dbc.Card(children=[
                    dbc.CardBody(children=[
                    html.H4("Controles", className="card-title"),
                    html.H6("Seleccione los municipios que desea visualizar:", className="card-text" ),
                    dcc.Dropdown(
                        id='municipio-dropdown-escenarios-futuro',
                        options=pd.unique(datos_tabla["Municipio"]),
                        value="Mistrató",
                        multi=True,
                        className='mb-3'),

                    html.H6("Seleccione la variable que desea visualizar:", className="card-text", style={'margin-top':'1em'}),

                    dcc.RadioItems(id='variable-button-escenarios-futuro',
                                    options=pd.unique(datos_tabla["Variable"]),
                                    value='Precipitacion Histórica', inline=False, className='mb-3'),

                    ])], 
                    className="shadow p-3 mb-5 bg-white rounded"
            )], width=3
        ),
        dbc.Col(
            dcc.Graph(id='monitor-escenarios-futuro'),style={'overflowY': 'scroll', 'height': '100%'},
                width=9)
    ]),
    html.Hr(),
    ], fluid=True)

@callback(
    Output('monitor-escenarios-futuro', 'figure'),
    Input('municipio-dropdown-escenarios-futuro', 'value'),
    Input ('variable-button-escenarios-futuro', 'value')
    )

def update_monitor(stations, variable):
    datos_tabla = obtener_datos()

    if isinstance(stations, str):
        stations = [stations]

    datos_tabla_filtrados= datos_tabla[datos_tabla["Municipio"].isin(stations)]
    datos_tabla_filtrados= datos_tabla_filtrados[datos_tabla_filtrados["Variable"] == variable]
    cant_figures=pd.unique(datos_tabla_filtrados["Municipio"])

    if len(cant_figures)==0:
        fig= make_subplots(rows=1, cols=1, subplot_titles="")
        fig.add_trace(go.Scatter(x=None, y=None),
            row=1, col=1)
            
        fig.update_layout(autosize=True, title_text="NINGUNA DE LOS MUNICIPIOS SELECCIONADAS SIMULA LA VARIABLE ESTABLECIDA")
    else: 
        fig= make_subplots(rows=len(cant_figures), cols=1, subplot_titles=cant_figures, vertical_spacing=0.1)
        for index, figure in enumerate(cant_figures):
            datos= datos_tabla_filtrados[datos_tabla_filtrados['Municipio']==figure]

            fig.add_trace( {
                'type': 'scatter',
                'x': datos['idTiempo'],
                'y': datos['ValorProm'],
                'mode': 'none',
                'name': figure
            },
            row=index+1, col=1)
            fig.add_trace(go.Scatter(x=datos['idTiempo'], y=datos['ValorMax'], name="Máximo", fill= 'tozeroy', line=dict(color="gray" )))
            fig.add_trace(go.Scatter(x=datos['idTiempo'], y=datos['ValorMin'], name="Mínimo", fill= 'tozeroy', fillcolor="rgb(255, 255, 255, 0.9)", line=dict(color="gray")))
            fig.add_trace(go.Scatter(x=datos['idTiempo'], y=datos['ValorProm'], name="Promedio", line=dict(color="lightblue")))
            
            fig.update_yaxes(title_text=variable, row=index+1, col=1, showgrid=False)
            fig.update_xaxes(rangeslider_visible=True)


        fig.update_layout(autosize=True, height=len(cant_figures)*300, paper_bgcolor="LightSteelBlue", margin=dict(l=30, r=30, t=30, b=30))
    return fig
    
