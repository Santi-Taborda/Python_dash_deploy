from dash import Dash, html, dcc, callback, Output, Input, register_page
import plotly.express as px
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
import pandas as pd
from sqlalchemy import create_engine, text
import pymysql
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import numpy
from os import environ as env

env['DB_URL']="mysql+pymysql://{user}:{password}@{host}:{port}/{name}".format(
    user=env['DB_USER_4'],
    password=env['DB_PASSWORD_4'],
    host=env['DB_HOST_2'],
    port=env['DB_PORT'],
    name=env['DB_NAME_SATMA']
    )
 
def Enviar_datos(api_key, id, temp, hum, PM10, PM25, PM100):
    fecha_actual= datetime.now().replace(tzinfo=pd.Timestamp.now().tz)
    hora_actual_str = fecha_actual.strftime('%Y-%m-%d %H:%M:%S')
# Conexión a la base de datos MySQL

    if api_key == '4LHTVAJZ2U7FKN3V':
        engine = create_engine(env.get('DB_URL'), echo=True)
        with engine.connect() as connection:
            insert_query = text("""
                INSERT INTO satma.calidad_aire_1 (IdTiempoRegistro, temperatura, humedad, pm10, pm25, pm100)
                VALUES (:IdTiempoRegistro, :temperatura, :humedad, :pm10, :pm25, :pm100)
            """)
            connection.execute(insert_query, {
                'IdTiempoRegistro': hora_actual_str,
                'temperatura': temp,
                'humedad': hum,
                'pm10': PM10,
                'pm25': PM25,
                'pm100': PM100
            })
            connection.commit()

register_page(__name__, path="/calidad_aire")


def layout(api_key=None, id=None, temp=None, hum=None, PM10=None, PM25=None, PM100=None, **other_unknown_query_strings):

    return (
        html.Div([
            html.H1('Dato guardado en la base de datos'),
            html.Div(f'''
            ID: {id}.\n
            api_key: {api_key}.\n
            Temperatura: {temp}.\n
            Humedad: {hum}.\n
            PM1: {PM10}.\n
            PM2.5: {PM25}.\n
            PM10: {PM100}.
            
            '''),
        ]),
        Enviar_datos(api_key, id, temp, hum, PM10, PM25, PM100)
    )
