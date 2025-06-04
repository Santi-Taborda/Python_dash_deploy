from dash import Dash, html, dcc, callback, Output, Input, register_page
import plotly.express as px
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import statistics
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from os import environ as env
import openpyxl

def convertir_jornada_dia(jornada):
    # Definir el mapeo de jornadas a días
    jornada_a_dia = {
        "D1J1": 1,
        "D1J2": 2,
    }
    return jornada_a_dia.get(jornada, None)

def obtener_datos():
    # Cargar el archivo Excel
    df = pd.read_excel('./assets/Resumen historico ordenado.xlsx', engine='openpyxl')

    # Convertir la columna de fecha a tipo datetime
    df.rename(columns={'fecha': 'IdTiempoRegistro'}, inplace=True)
    df["IdTiempoRegistro"] = pd.to_datetime(df["IdTiempoRegistro"], format="%d/%m/%Y %H:%M")

    # Convertir las columnas de valores a numérico, manejando errores
    df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')
    df['Valor'] = df['Valor'].fillna(0)  # Rellenar NaN con 0
    df['Valor'] = df['Valor'].replace([np.inf, -np.inf], 0)  # Reemplazar inf y -inf con 0
    df['Valor'] = df['Valor'].round(2)  # Redondear a 2 decimales

    df['Jornada']=df['Periodo'].apply(convertir_jornada_dia)

    # Eliminar las columnas que no son necesarias
    df = df.drop(columns=['Hora', 'Periodo'])


    return df

datos_tabla = obtener_datos()

def obtener_parametros():
    return (datos_tabla["Parametro"].unique())

def obtener_puntos():
    return (datos_tabla["Punto"].unique())

parametros = obtener_parametros()
puntos = obtener_puntos()

register_page(__name__, name="EEP_Calidad_Historico", path='/EEP/Calidad_Historico')


layout= dbc.Container(children=[
    html.Div(
        children=[
    html.H1("Monitor de Energía de Pereira Calidad Histórico", style={'textAlign': 'left', 'color': '#0d6efd', 'margin-left':'20px', 'padding':'10px'}),
    html.Hr()],
    style={'background-color':'AliceBlue'},
    ),

    dbc.Row(children=[
        dbc.Col(children=[dbc.Card(children=[
                    dbc.CardBody(children=[
                    html.H4("Controles", className="card-title"),
                        
                    html.H6("Seleccione el punto a visualizar:", className="card-text", style={'margin-top':'1em'}),

                    dcc.Dropdown(id='punto_button_calidad_historico',
                                    options=puntos,
                                    value=puntos[0], multi=True, className='mb-3'),

                    html.H6("Seleccione la variable a visualizar:", className="card-text", style={'margin-top':'1em'}),

                    dcc.Dropdown(id='variable_button_calidad_historico',
                                    options=parametros,
                                    value=parametros[0], multi=False, className='mb-3'),

                    html.H6("Seleccione la jornada a visualizar:", className="card-text", style={'margin-top':'1em'}),

                    dcc.RadioItems(id='jornada_button_calidad_historico',
                                    options=[1, 2],
                                    value=1, inline=True, className='mb-3'),

                    ])], 
                    className="shadow p-3 mb-5 bg-white rounded"
            )], width=3
        ),
        dbc.Col(
            dcc.Graph(id='monitor_calidad_historico'),style={'overflowY': 'scroll', 'height': '100%'},
                width=9)
    ]),
    html.Hr(),
    ], fluid=True)

@callback(
    Output('monitor_calidad_historico', 'figure'),
    Input('punto_button_calidad_historico', 'value'),
    Input('variable_button_calidad_historico', 'value'),
    Input('jornada_button_calidad_historico', 'value')
)
def update_monitor_calidad_historico(punto, variable, jornada):
    datos_tabla = obtener_datos()

    if isinstance(punto, list):
        datos_tabla = datos_tabla[datos_tabla['Punto'].isin(punto)]
    else:
        datos_tabla = datos_tabla[datos_tabla['Punto'] == punto]

    datos_tabla = datos_tabla[(datos_tabla['Parametro'] == variable) & (datos_tabla['Jornada'] == jornada)]

    cant_figures=pd.unique(datos_tabla["Punto"])
    if len(cant_figures)==0:
        fig= make_subplots(rows=1, cols=1, subplot_titles="")
        fig.add_trace(go.Scatter(x=None, y=None),
            row=1, col=1)
        fig.update_layout(autosize=True, title_text="NO DATA AVAILABLE", paper_bgcolor="LightSteelBlue", margin=dict(l=30, r=30, t=30, b=30))
    else: 
        fig= make_subplots(rows=len(cant_figures), cols=1, subplot_titles=cant_figures, vertical_spacing=0.1)
        for index, figure in enumerate(cant_figures):
            datos= datos_tabla[datos_tabla['Punto']==figure]

            fig.add_trace( {
                'type': 'scatter',
                'x': datos['IdTiempoRegistro'],
                'y': datos['Valor'],
                'mode': 'none',
                'fill': 'tozeroy',
                'name': figure
            },
            row=index+1, col=1)
            fig.update_yaxes(title_text=variable, range=[min(datos['Valor'])-min(datos['Valor'])*0.1, max(datos['Valor'])+max(datos['Valor'])*0.1], row=index+1, col=1)

        fig.update_layout(autosize=True, height=len(cant_figures)*300, paper_bgcolor="LightSteelBlue", margin=dict(l=30, r=30, t=30, b=30))
    return fig