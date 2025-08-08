import dash
from dash import Dash, html, dcc, callback, Output, Input, register_page, callback_context
from dash import html, dcc, Output, Input, State, ctx
import dash_bootstrap_components as dbc
import ftplib
import os
from os import environ as env
import base64
import tempfile

FTP_USER = env.get('FTP_USER')
FTP_PASS = env.get('FTP_PASS')
FTP_HOST = env.get('FTP_HOST')

ROOT_PATH = "/estaciones"

def get_estaciones():
    try:
        ftp = ftplib.FTP(FTP_HOST)
        ftp.login(FTP_USER, FTP_PASS)
        ftp.cwd(ROOT_PATH)
        items = []
        ftp.retrlines('LIST', items.append)
        ftp.quit()
        estaciones = []
        for item in items:
            parts = item.split(maxsplit=8)
            if len(parts) < 9:
                continue
            name = parts[8]
            if item.startswith('d'):
                estaciones.append(name)
        return estaciones
    except Exception as e:
        return []

def list_ftp_dir(path):
    try:
        ftp = ftplib.FTP(FTP_HOST)
        ftp.login(FTP_USER, FTP_PASS)
        ftp.cwd(path)
        items = []
        ftp.retrlines('LIST', items.append)
        ftp.quit()
        dirs = []
        files = []
        for item in items:
            parts = item.split(maxsplit=8)
            if len(parts) < 9:
                continue
            name = parts[8]
            if item.startswith('d'):
                dirs.append(name)
            else:
                files.append(name)
        return dirs, files
    except Exception as e:
        texto= f"Error: {str(e)}"
        if "550" in texto:
            return [""], []
        else:
            return [f"Error: {str(e)}"], []

def get_file_content(path, filename):
    try:
        ftp = ftplib.FTP(FTP_HOST)
        ftp.login(FTP_USER, FTP_PASS)
        ftp.cwd(path)
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            ftp.retrbinary(f"RETR {filename}", tmp_file.write)
            tmp_file_path = tmp_file.name
        ftp.quit()
        with open(tmp_file_path, "rb") as f:
            data = f.read()
        b64 = base64.b64encode(data).decode()
        src = f'data:application/pdf;base64,{b64}'
        return html.Iframe(src=src, style={"width": "100%", "height": "800px", "border": "none", "background": "#222"})
    except Exception as e:
        return f"Error: {str(e)}"

# Obtener estaciones dinámicamente
ESTACIONES = get_estaciones()

register_page(__name__, name="BOLETINES_SATMA", path='/BOLETINES_SATMA', external_stylesheets=[dbc.themes.DARKLY])

layout = dbc.Container([
    html.H2("Navegador de Boletines SATMA", className="text-center mb-4", style={"color": "#00d4ff", "fontWeight": "bold"}),
    html.P("Selecciona una estación para navegar por sus carpetas y archivos:",
           className="text-center", style={"color": "#b0b0b0"}),
    dcc.Store(id="ftp-path", data=""),  # <-- Agrega esta línea
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id="estacion-dropdown",
                options=[{"label": est, "value": est} for est in ESTACIONES],
                value=None,
                searchable=True,
                placeholder="Buscar estación...",
                style={"color": "gray"}
            ),
        ], width=8),
        dbc.Col([
            dbc.Button("Ir a raíz", id="go-root", color="info", className="w-100")
        ], width=4)
    ], className="mb-3"),
    html.Div(id="ftp-dir-list", className="mb-3"),
    html.Div(id="ftp-file-content", style={"whiteSpace": "pre-wrap", "fontFamily": "monospace", "background": "#181818", "borderRadius": "8px", "padding": "10px"})
], fluid=True, style={"backgroundColor": "#181818", "minHeight": "100vh"})

@callback(
    Output("ftp-path", "data"),
    Input("estacion-dropdown", "value"),
    Input("go-root", "n_clicks"),
    Input({"type": "ftp-dir-btn", "name": dash.ALL}, "n_clicks"),
    State("ftp-path", "data"),
    prevent_initial_call=False
)
def update_path(estacion, go_root, dir_clicks, current_path):
    triggered = ctx.triggered_id
    if triggered is None or triggered == "estacion-dropdown" or triggered == "go-root":
        path = f"{ROOT_PATH}/{estacion}"
    elif isinstance(triggered, dict) and triggered.get("type") == "ftp-dir-btn":
        subdir = triggered.get("name")
        # Evita agregar dos veces el mismo subdirectorio
        if current_path and current_path.rstrip("/").endswith(f"/{subdir}"):
            path = current_path
        else:
            if current_path:
                path = f"{current_path}/{subdir}"
            else:
                path = f"{ROOT_PATH}/{estacion}/{subdir}"
    else:
        path = current_path or f"{ROOT_PATH}/{estacion}"
    return path

@callback(
    Output("ftp-dir-list", "children"),
    Output("ftp-file-content", "children"),
    Input("ftp-path", "data"),
    Input({"type": "ftp-file-btn", "name": dash.ALL}, "n_clicks"),
    State("ftp-path", "data"),
    prevent_initial_call=True
)
def show_dir(path, file_clicks, current_path):
    triggered = ctx.triggered_id
    if isinstance(triggered, dict) and triggered.get("type") == "ftp-file-btn":
        filename = triggered.get("name")
        content = get_file_content(current_path, filename)
        return dash.no_update, content
    dirs, files = list_ftp_dir(path)
    if dirs and isinstance(dirs[0], str) and dirs[0].startswith("Error"):
        return html.Div(dirs[0], style={"color": "#ff4c4c"}), ""
    dir_buttons = [
        dbc.Button(
            d,
            id={"type": "ftp-dir-btn", "name": d},
            color="secondary",
            className="m-1",
            style={"backgroundColor": "#23272b", "color": "#00d4ff", "border": "1px solid #00d4ff"}
        ) for d in dirs
    ]
    file_buttons = [
        dbc.Button(
            f,
            id={"type": "ftp-file-btn", "name": f},
            color="success",
            className="m-1",
            style={"backgroundColor": "#1e7e34", "color": "#fff", "border": "1px solid #00d4ff"}
        ) for f in files
    ]
    return html.Div(dir_buttons + file_buttons, className="d-flex flex-wrap"), ""