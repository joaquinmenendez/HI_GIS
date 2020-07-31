import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_table
import pandas as pd
import geopandas as geopd
import io
import base64
from flask import Flask, render_template

server = Flask(__name__, static_url_path = "/home", static_folder = "static") # Use Flash as a server to render html pages
COMUNAS = geopd.read_file('./polygons/CABA_comunas.geojson')
BARRIOS = geopd.read_file('./polygons/CABA_barrios.geojson')

app = dash.Dash(__name__,
                server=server,
                url_base_pathname="/dashboard/",
                external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'],
                suppress_callback_exceptions=True)  # Quiero poder navegar a diferentes paginas

app.layout = html.Div([dcc.Upload(id='upload_data',
                                  children=html.Div(['Drag and Drop or ',
                                                     html.A('Select Files')]),
                                  multiple=True),
                       html.Div(id='output_data_upload')
                       ])

#@server.route("/dashboard")
#def dash_app():
#    return app.layout


def print_df(file, filename):
    content_type, content_string = file.split(',')
    decoded = base64.b64decode(content_string)
    try:
        df = pd.read_csv(io.StringIO(decoded.decode('latin-1')))
        print (f'Shape of the file: {df.shape}')
        print(COMUNAS.columns)
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])
    return html.Div([html.H2(filename),
                     dash_table.DataTable(data=df.to_dict('records'),
                                          columns=[{'name': i, 'id': i} for i in df.columns]
                                           )
                     ])

@app.callback(Output('output_data_upload', 'children'),
              [Input('upload_data', 'contents')],
              [State('upload_data', 'filename')])
def update_output(list_of_contents, list_of_names):
    if list_of_contents is not None:
        children = [
            print_df(file, name) for file, name in
            zip(list_of_contents, list_of_names)]
        return children


@server.route('/about')
def about_page():
    return render_template('about.html')


@server.route('/home')
def home():
    return render_template('home.html')

if __name__ == '__main__':
    app.run_server()