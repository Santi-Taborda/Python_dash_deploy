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
    items_baner_SAT_satelital = []

    if variable=='Temperatura':
        id_variable=1
        items_baner_SAT_satelital =  [ 
        {"key": "1", "src": "/assets/SAT/temp_1.bmp"},
        {"key": "2", "src": "/assets/SAT/temp_2.bmp"},
        {"key": "3", "src": "/assets/SAT/temp_3.bmp"},
        {"key": "4", "src": "/assets/SAT/temp_4.bmp"},
        {"key": "5", "src": "/assets/SAT/temp_5.bmp"},
        {"key": "6", "src": "/assets/SAT/temp_6.bmp"},
        {"key": "7", "src": "/assets/SAT/temp_7.bmp"},
        ]
    elif variable=='Precipitación':
        id_variable=3
        items_baner_SAT_satelital =  [ 
        {"key": "1", "src": "/assets/SAT/prec_1.bmp"},
        {"key": "2", "src": "/assets/SAT/prec_2.bmp"},
        {"key": "3", "src": "/assets/SAT/prec_3.bmp"},
        {"key": "4", "src": "/assets/SAT/prec_4.bmp"},
        {"key": "5", "src": "/assets/SAT/prec_5.bmp"},
        {"key": "6", "src": "/assets/SAT/prec_6.bmp"},
        {"key": "7", "src": "/assets/SAT/prec_7.bmp"},
        ]
    return (items_baner_SAT_satelital)

items_baner_SAT_satelital = obtener_datos(variable='Precipitación')


register_page(__name__, name="SAT Satelital", path='/SAT/satelital' )

layout= dbc.Container(children=[
    html.Div(
        children=[
    html.H1("SAT Satelital", style={'textAlign': 'left', 'color': '#0d6efd', 'margin-left':'20px', 'padding':'10px'}),
    html.Hr()],
    style={'background-color':'AliceBlue'},
    ),

    dbc.Row(children=[
        dbc.Col(children=[dbc.Card(children=[
                    dbc.CardBody(children=[
                    html.H4("Controles", className="card-title"),
                        
                    html.H6("Seleccione la variable que desea visualizar:", className="card-text", style={'margin-top':'1em'}),

                    dcc.Dropdown(id='variable_button_SAT_satelital',
                                    options=['Temperatura','Precipitación'],
                                    value='Precipitación', multi=False, className='mb-3')

                    ])], 
                    className="shadow p-3 mb-5 bg-white rounded"
            )], width=3
        ),
        dbc.Col(
            dbc.Carousel(id='baner_SAT_satelital',
                         items=items_baner_SAT_satelital,
                         controls=True,
                         indicators=True,
                         variant="dark",
                         interval=2000,
                         className="carousel-fade",

                         ),style={'overflowY': 'scroll', 'height': '100%'},
                width=9)
    ]),
    html.Hr(),
    ], fluid=True)


@callback(
    Output('baner_SAT_satelital', 'items'),
    Input ('variable_button_SAT_satelital', 'value')
    )

def update_monitor_otun(variable):
    items_baner_SAT_satelital = obtener_datos(variable=variable)
    return items_baner_SAT_satelital
