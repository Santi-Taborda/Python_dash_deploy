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


def obtener_datos():

    datos_tabla= pd.read_csv('./assets/EEP_CALIDAD.csv', sep=';', encoding='utf-8')
    datos_tabla["IdTiempoRegistro"] = pd.to_datetime(datos_tabla["IdTiempoRegistro"], format="%d/%m/%Y %H:%M")
    datos_tabla['Valor_1'] = pd.to_numeric(datos_tabla['Valor_1'], errors='coerce')
    datos_tabla['Valor_2'] = pd.to_numeric(datos_tabla['Valor_2'], errors='coerce')
    return (datos_tabla)

datos_tabla=obtener_datos()


register_page(__name__, name="EEP_Calidad", path='/EEP/Calidad' )

layout= dbc.Container(children=[
    html.Div(
        children=[
    html.H1("Monitor de Energía de Pereira Calidad", style={'textAlign': 'left', 'color': '#0d6efd', 'margin-left':'20px', 'padding':'10px'}),
    html.Hr()],
    style={'background-color':'AliceBlue'},
    ),

    dbc.Row(children=[
        dbc.Col(children=[dbc.Card(children=[
                    dbc.CardBody(children=[
                    html.H4("Controles", className="card-title"),
                        
                    html.H6("Seleccione la bocatoma a monitorear:", className="card-text", style={'margin-top':'1em'}),

                    dcc.Dropdown(id='bocatoma_button_calidad',
                                    options=["Bocatoma Nuevo Libaré", "Bocatoma Belmonte"],
                                    value="Bocatoma Nuevo Libaré", multi=False, className='mb-3'),
                    
                    html.H6("Seleccione el punto a monitorear:", className="card-text", style={'margin-top':'1em'}),

                    dcc.Dropdown(id='punto_button_calidad',
                                    options=["Antes bocatoma Nuevo Libaré", "Puente Gaitán", "Bocatoma Belmonte", "Puente Marsella", "Casa de máquinas"],
                                    value="Antes bocatoma Nuevo Libaré", multi=False, className='mb-3'),
                    
                    html.H6("Seleccione la jornada del año:", className="card-text", style={'margin-top':'1em'}),

                    dcc.Dropdown(id='jornada_button_calidad',
                                    options=["Jornada 1", "Jornada 2"],
                                    value="Jornada 1", multi=False, className='mb-3'),
    

                    ])], 
                    className="shadow p-3 mb-5 bg-white rounded"
            )], width=3
        ),
        dbc.Col(
            dcc.Graph(id='monitor_calidad'),style={'overflowY': 'scroll', 'height': '100%'},
                width=9)
    ]),
    html.Hr(),
    ], fluid=True)

@callback(
    Output('monitor_calidad', 'figure'),
    Input ('bocatoma_button_calidad', 'value'),
    Input ('punto_button_calidad', 'value'),
    Input ('jornada_button_calidad', 'value')
    )

def update_monitor_ecotec(bocatoma, punto, jornada):
    datos_tabla = obtener_datos()

    if bocatoma == "Bocatoma Nuevo Libaré":
        datos_tabla=datos_tabla[datos_tabla['idBocatoma']==2]
    elif bocatoma == "Bocatoma Belmonte":
        datos_tabla=datos_tabla[datos_tabla['idBocatoma']==1]
    
    if punto == "Antes bocatoma Nuevo Libaré":
        datos_tabla=datos_tabla[datos_tabla['idPunto']==1]
    elif punto == "Puente Gaitán":
        datos_tabla=datos_tabla[datos_tabla['idPunto']==2]
    elif punto == "Bocatoma Belmonte":
        datos_tabla=datos_tabla[datos_tabla['idPunto']==3]
    elif punto == "Puente Marsella":
        datos_tabla=datos_tabla[datos_tabla['idPunto']==4]
    elif punto == "Casa de máquinas":
        datos_tabla=datos_tabla[datos_tabla['idPunto']==5]

    if jornada == "Jornada 1":
        datos_tabla=datos_tabla[datos_tabla['idJornada']==1]
    elif jornada == "Jornada 2":
        datos_tabla=datos_tabla[datos_tabla['idJornada']==2]

    cant_figures=pd.unique(datos_tabla["idVariable"])
    cant_figures_list=cant_figures.tolist()

    dic_variables={1:'Temperatura', 2:'Humedad relativa', 3:'pH', 4:'Conductividad', 5:'Temperatura agua', 6:'Oxígeno disuelto'}

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
            datos['Valor_promedio'] = (datos['Valor_1']+datos['Valor_2'])/2
            fig.add_trace( {
                'type': 'scatter',
                'x': datos['IdTiempoRegistro'],
                'y': datos['Valor_promedio'],
                'mode': 'none',
                'fill': 'tozeroy',
                'name': dic_variables[figure]
            },
            row=index+1, col=1)
            fig.update_yaxes(title_text=dic_variables[figure], range=[min(datos['Valor_promedio']), max(datos['Valor_promedio'])], row=index+1, col=1)

        fig.update_layout(autosize=True, height=len(cant_figures)*300, paper_bgcolor="LightSteelBlue", margin=dict(l=30, r=30, t=30, b=30))
    return fig