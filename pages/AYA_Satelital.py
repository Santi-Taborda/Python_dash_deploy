from dash import Dash, html, dcc, callback, Output, Input, register_page
import plotly.express as px
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
import pandas as pd
from sqlalchemy import create_engine
import pymysql
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import numpy
from os import environ as env
import ftplib
import io
import base64

def obtener_datos(variable):
    items_baner_satelital = []

    if variable=='Temperatura':
        id_variable=1
    elif variable=='Humedad relativa':
        id_variable=3
    elif variable=='Precipitación':
        id_variable=2

    items_baner_satelital =  [ 
        {"key": "1", "src": "/assets/temp.png"},
        {"key": "2", "src": "/assets/hum.png"},
        {"key": "3", "src": "/assets/rain.png"}
        ]
    return (items_baner_satelital)

items_baner_satelital = obtener_datos(variable='Temperatura')


register_page(__name__, name="Satelital", path='/aya/satelital' )

layout= dbc.Container(children=[
    html.Div(
        children=[
    html.H1("Satelital AyA", style={'textAlign': 'left', 'color': '#0d6efd', 'margin-left':'20px', 'padding':'10px'}),
    html.Hr()],
    style={'background-color':'AliceBlue'},
    ),

    dbc.Row(children=[
        dbc.Col(children=[dbc.Card(children=[
                    dbc.CardBody(children=[
                    html.H4("Controles", className="card-title"),
                        
                    html.H6("Seleccione la variable que desea visualizar:", className="card-text", style={'margin-top':'1em'}),

                    dcc.Dropdown(id='variable_button_satelital',
                                    options=['Temperatura','Humedad relativa','Precipitación'],
                                    value='Temperatura', multi=False, className='mb-3'),
    
                    dcc.Interval(
                    id='interval-component',
                    interval=30*60*1000, # in milliseconds
                    n_intervals=0),

                    ])], 
                    className="shadow p-3 mb-5 bg-white rounded"
            )], width=3
        ),
        dbc.Col(
            dbc.Carousel(id='baner_satelital',
                         items=items_baner_satelital,
                         controls=True,
                         indicators=True,
                         interval=2000,
                         className="carousel-fade",

                         ),style={'overflowY': 'scroll', 'height': '100%'},
                width=9)
    ]),
    html.Hr(),
    ], fluid=True)


@callback(
    Output('baner_satelital', 'items'),
    Input ('variable_button_satelital', 'value'),
    Input('interval-component', 'n_intervals')
    )

def update_monitor_otun(variable,n):
    items_baner_satelital = obtener_datos(variable=variable)
    return items_baner_satelital
