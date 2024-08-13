from dash import Dash, html, dcc, callback, Output, Input, register_page
import dash_bootstrap_components as dbc

register_page(__name__, name="Menu", path='/aya/menu' )

cards = [
    dbc.Card(
        dbc.CardBody(
            [
                html.Img(src="https://cdn.pixabay.com/photo/2015/05/15/01/48/computer-767776_1280.jpg", className="img-fluid"),
                html.Div(style={'margin-bottom': '10px'}),
                dcc.Link("Monitor de variables", href="https://satma-dashboards.onrender.com/aya/monitor", className="stretched-link"),
            ]
        ),
        className="shadow p-3 mb-5 bg-white rounded",
        style={'width': '30rem', "textAlign": "center"}
    ),
    dbc.Card(
        dbc.CardBody(
            [
                html.Img(src="https://cdn.pixabay.com/photo/2015/06/19/20/14/water-815271_1280.jpg", className="img-fluid"),
                html.Div(style={'margin-bottom': '10px'}),
                dcc.Link("Lluvia VS Caudal", href="https://satma-dashboards.onrender.com/aya/lluvia_vs_caudal", className="stretched-link"),
            ]
        ),
        className="shadow p-3 mb-5 bg-white rounded",
        style={'width': '30rem', "textAlign": "center"}
    ),
    dbc.Card(
        dbc.CardBody(
            [
                html.Img(src="https://cdn.pixabay.com/photo/2020/03/28/15/10/high-water-4977406_1280.jpg", className="img-fluid"),
                html.Div(style={'margin-bottom': '10px'}),
                dcc.Link("Bocatoma Nuevo Libaré", href="https://satma-dashboards.onrender.com/aya/bocatoma_nuevo_libare", className="stretched-link"),
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
