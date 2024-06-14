from dash import html, register_page
import dash_bootstrap_components as dbc

register_page(__name__, name="HOME", path='/')

layout= dbc.Container(
    fluid=True,
    className="d-flex flex-column justify-content-center align-items-center vh-100",
    children=[
        dbc.Row([
            dbc.Col(html.H1("SATMA DASHBOARDS", style={'textAlign': 'center', 'color': '#0d6efd'}), width=12)
        ], className="my-3"),
        dbc.Row([
            dbc.Col(html.Img(src="https://via.placeholder.com/150", style={'display': 'block', 'margin-left': 'auto', 'margin-right': 'auto'}), width=12)
        ], className="mb-3"),
        dbc.Row([
            dbc.Col(html.P(
                "En esta página puedes acceder a los dashboards diseñados por el SATMA (Sistema de Alertas Tempranas y Monitoreo Ambiental de Risaralda), "
                "creados para suplir las necesidades de visualización de datos específicas de nuestros colaboradores. "
                "Para acceder a tu dashboard sólo debes ingresar en el URL tu dash-code, ejemplo: satma-dashboards/123456",
                style={'textAlign': 'center'}
            ), width=12)
        ], className="mb-5")
    ]
)