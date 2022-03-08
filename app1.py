# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objs as go
import pandas as pd
import igraph
import os
import numpy as np
import matplotlib.pyplot as plt

#df = pd.read_csv('https://gist.githubusercontent.com/chriddyp/c78bf172206ce24f77d6363a2d754b59/raw/c353e8ef842413cae56ae3920b8fd78468aa4cb2/usa-agricultural-exports-2011.csv')
data=pd.read_csv('EDGE.csv')
nodes=pd.concat([data['TARGET_NODE'],data['SOURCE_NODE']],axis=0).unique()
graph=igraph.Graph()
graph.vs["name"]=list(nodes)
graph=igraph.Graph().DataFrame(data)
fig, ax = plt.subplots()
layout = graph.layout("kk")
igraph.plot(graph, layout=layout, target=ax)
figure=go.Figure()


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
import plotly.graph_objects as go # or plotly.express as px
fig = go.Figure() # or any Plotly Express function e.g. px.bar(...)
# fig.add_trace( ... )
# fig.update_layout( ... )

app.layout = html.Div([
    dcc.Graph(figure=fig)
])
if __name__ == '__main__':
    app.run_server(debug=True)