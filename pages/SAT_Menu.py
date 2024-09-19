from dash import Dash, html, dcc, callback, Output, Input, register_page
import dash_bootstrap_components as dbc

register_page(__name__, name="SAT_Menu", path='/SAT/menu' )

cards = [
    dbc.Card(
        dbc.CardBody(
            [
                html.Img(src="https://img.icons8.com/?size=100&id=MIHEeBkgtsFY&format=png&color=000000", className="img-fluid"),
                html.Div(style={'margin-bottom': '10px'}),
                dcc.Link("Monitor departamental 24 horas", href="https://satma-dashboards.onrender.com/SAT/DEPARTAMENTO/24H", className="stretched-link"),
            ]
        ),
        className="shadow p-3 mb-5 bg-white rounded",
        style={'width': '30rem', "textAlign": "center"}
    ),
    dbc.Card(
        dbc.CardBody(
            [
                html.Img(src="https://img.icons8.com/?size=100&id=MIHEeBkgtsFY&format=png&color=000000", className="img-fluid"),
                html.Div(style={'margin-bottom': '10px'}),
                dcc.Link("Monitor departamental 40 días", href="https://satma-dashboards.onrender.com/SAT/DEPARTAMENTO/40D", className="stretched-link"),
            ]
        ),
        className="shadow p-3 mb-5 bg-white rounded",
        style={'width': '30rem', "textAlign": "center"}
    ),
    dbc.Card(
        dbc.CardBody(
            [
                html.Img(src="https://img.icons8.com/?size=100&id=MIHEeBkgtsFY&format=png&color=000000", className="img-fluid"),
                html.Div(style={'margin-bottom': '10px'}),
                dcc.Link("Consulta de antecedentes", href="https://satma-dashboards.onrender.com/SATMA/consulta_antecedentes", className="stretched-link"),
            ]
        ),
        className="shadow p-3 mb-5 bg-white rounded",
        style={'width': '30rem', "textAlign": "center"}
    ),
]

layout = dbc.Container(
    dbc.Row([dbc.Col(card, width="auto", align="center") for card in cards], 
        justify="center",
        align="center",),
    fluid=True,
    className="d-flex align-items-center vh-100",
    style={'background-color':'AliceBlue'}
)
