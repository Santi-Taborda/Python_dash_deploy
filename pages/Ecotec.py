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

def obtener_datos():
    fecha_actual= datetime.now().replace(tzinfo=pd.Timestamp.now().tz)
    fecha_40_dias_atras=fecha_actual - timedelta(days=40)
    hora_actual_str = fecha_actual.strftime('%Y-%m-%d %H:%M:%S')
    hace_40_dias_str = fecha_40_dias_atras.strftime('%Y-%m-%d %H:%M:%S')
    # Conexión a la base de datos MySQL
    engine = create_engine(env.get('DB_URL'), echo=True)
    # Consultas SQL
    query1 = "SELECT IdRegistro, IdTiempoRegistro, idVariable, Valor, idGrupo FROM registros WHERE IdTiempoRegistro BETWEEN %s AND %s AND Valor is not NULL"

    datos_tabla = pd.read_sql(query1, engine,  params=(hace_40_dias_str, hora_actual_str))

    datos_tabla["IdTiempoRegistro"] = pd.to_datetime(datos_tabla["IdTiempoRegistro"])
    datos_tabla.sort_values(by="IdTiempoRegistro", inplace=True)

    return (datos_tabla)

datos_tabla=obtener_datos()


register_page(__name__, name="Ecotecnología", path='/ecotec' )


layout= dbc.Container(children=[
    html.Div(
        children=[
    html.H1("Monitor de intro a la ecotecnología", style={'textAlign': 'left', 'color': '#0d6efd', 'margin-left':'20px', 'padding':'10px'}),
    html.Hr()],
    style={'background-color':'AliceBlue'},
    ),

    dbc.Row(children=[
        dbc.Col(children=[dbc.Card(children=[
                    dbc.CardBody(children=[
                    html.H4("Controles", className="card-title"),
                        
                    html.H6("Seleccione el grupo que desea visualizar:", className="card-text", style={'margin-top':'1em'}),

                    dcc.Dropdown(id='grupo_button_ecotec',
                                    options=[1,2,3,4],
                                    value='1', multi=False, className='mb-3'),
    
                    dcc.Interval(
                    id='interval-component',
                    interval=5*60*1000, # in milliseconds
                    n_intervals=0),

                    html.Div([
                    html.Button("Descarga como CSV", id="download_csv_button_ecotec", className="btn btn-primary", style={'margin-bottom': '10px'}),
                    dcc.Download(id="download_csv_ecotec")]),

                html.Div([
                    html.Button("Descarga como xlsx", id="download_xlsx_button_ecotec", className="btn btn-primary"),
                    dcc.Download(id="download_xlsx_ecotec")]),

                    ])], 
                    className="shadow p-3 mb-5 bg-white rounded"
            )], width=3
        ),
        dbc.Col(
            dcc.Graph(id='monitor_ecotec'),style={'overflowY': 'scroll', 'height': '100%'},
                width=9)
    ]),
    html.Hr(),
    ], fluid=True)

@callback(
    Output("download_csv_ecotec", "data"),
    Input("download_csv_button_ecotec", "n_clicks"),
    Input("grupo_button_ecotec", "value"),
    prevent_initial_call=True,
)

def download_csv(n_clicks, grupo):
    if n_clicks:
        datos_tabla = obtener_datos()
        datos_tabla=datos_tabla[datos_tabla['idGrupo']==grupo]
        nombre="Datos_grupo"+str(grupo)+".csv"
        return dcc.send_data_frame(datos_tabla.to_csv, nombre, sep=',', index=False)
    else:
         return None
@callback(
    Output("download_xlsx_ecotec", "data"),
    Input("download_xlsx_button_ecotec", "n_clicks"),
    Input("grupo_button_ecotec", "value"),
    prevent_initial_call=True,
)

def download_xlsx(n_clicks, grupo):
    if n_clicks:
        datos_tabla = obtener_datos()
        datos_tabla=datos_tabla[datos_tabla['idGrupo']==grupo]
        nombre="Datos_grupo"+str(grupo)+".xlsx"
        return dcc.send_data_frame(datos_tabla.to_excel, nombre, sheet_name="Hoja 1", index=False)
    else:
         return None

@callback(
    Output('monitor_ecotec', 'figure'),
    Input ('grupo_button_ecotec', 'value'),
    Input('interval-component', 'n_intervals')
    )

def update_monitor_ecotec(grupo,n):
    datos_tabla = obtener_datos()

    datos_tabla=datos_tabla[datos_tabla['idGrupo']==grupo]
    datos_tabla["IdTiempoRegistro"] = pd.to_datetime(datos_tabla["IdTiempoRegistro"])
    cant_figures=pd.unique(datos_tabla["idVariable"])
    cant_figures_list=cant_figures.tolist()

    dic_variables={1:'Temperatura', 2:'Humedad relativa', 3:'Precipitación', 4:'Óxido reducción', 5:'pH', 6:'Conductividad'}

    dict_variable = [value for (figure) in cant_figures_list for (key, value) in dic_variables.items() if figure == key]

    if len(cant_figures)==0:
            fig= make_subplots(rows=1, cols=1, subplot_titles="")
            fig.add_trace(go.Scatter(x=None, y=None),
                row=1, col=1)
                
            fig.update_layout(autosize=True, title_text="NO HAY DATOS", paper_bgcolor="LightSteelBlue", margin=dict(l=30, r=30, t=30, b=30))
    
    else: 
        fig= make_subplots(rows=len(cant_figures), cols=1, subplot_titles=dict_variable, vertical_spacing=0.1)
        for index, figure in enumerate(cant_figures):
            datos= datos_tabla[datos_tabla['idVariable']==figure]
            #fig.add_trace(go.Scatter(x=datos['IdTiempoRegistro'], y=datos['Valor'], name=dic_variables[figure], mode="markers"),
            #   row=index+1, col=1)
            fig.add_trace( {
                'type': 'scatter',
                'x': datos['IdTiempoRegistro'],
                'y': datos['Valor'],
                'mode': 'none',
                'fill': 'tozeroy',
                'name': dic_variables[figure]
            },
            row=index+1, col=1)
            fig.update_yaxes(title_text=dic_variables[figure], range=[min(datos['Valor']), max(datos['Valor'])], row=index+1, col=1)

        fig.update_layout(autosize=True, height=len(cant_figures)*300, paper_bgcolor="LightSteelBlue", margin=dict(l=30, r=30, t=30, b=30))
    return fig