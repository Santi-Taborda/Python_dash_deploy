from dash import Dash, html, dcc, page_registry, page_container
import dash_bootstrap_components as dbc

app= Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.CERULEAN])

# Define the navigation bar
""" navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("HOME", href="/")),
    ],
    brand="SATMA DASHBOARDS",
    brand_href="/",
    color="dark",
    dark=True,
) """

app.layout =html.Div([
    #navbar,
    page_container
])

if __name__ == '__main__':
    app.run_server(debug=True)
