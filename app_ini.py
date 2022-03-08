import pandas as pd
import dash
import dash_cytoscape as cyto
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc


data=pd.read_csv('EDGE.csv')
nodes=pd.concat([data['TARGET_NODE'],data['SOURCE_NODE']],axis=0).unique()
roots=[i for i in nodes if 'logicalModel' in i]


edges={}
for i in range(data.shape[0]):
    target=data['SOURCE_NODE'].loc[i]
    source=data['TARGET_NODE'].loc[i]
    if source in edges.keys():
        edges[source].append(target)
    else:
        edges[source]=[target]

def trav(node):
    stack=[]
    nodes_=[]
    edges_=[]
    def foo(node):
        if node in edges.keys():
            stack.append(node)
            if node not in nodes_:
                nodes_.append(node)
            if len(edges[node])>0:
                for i in edges[node]:
                    edges_.append(((i,stack[-1])))
                    if i not in nodes_:
                        nodes_.append(i)
                    foo(i)
                stack.pop()
    foo(node)
    nodes_ = [{'data': {'id': label, 'label': label,},} for label in nodes_]
    edges_ = [{'data': {'source': source, 'target': target}} for source, target in edges_]
    return nodes_+edges_

app = dash.Dash(__name__,external_stylesheets=[dbc.themes.FLATLY])

server = app.server

app.layout = html.Div([
    dcc.Dropdown(
    id='dropdown_root',
    value='Select root node',
    clearable=False,
    options=[
        {'label': name.upper(), 'value': name}
        for name in roots
    ]
),
    dbc.Row(dbc.Col(html.Div("A single column"))),
        dbc.Row(
            [
                dbc.Col(html.Div( cyto.Cytoscape(
        id='cyto',
        layout={'name': 'breadthfirst'},
        style={ 'height': '600px'},
        stylesheet=[{'selector':'node','style':{'content':'data(label)','text-valign': 'center','text-halign': 'center','height':200,'width':200}}]
        ))),
                dbc.Col(html.Div("One of three columns")),
                dbc.Col(html.Div("One of three columns")),
            ]
        ),
   ])

@app.callback(Output('cyto', 'elements'),Output('cyto', 'layout'),Input('dropdown_root', 'value'))
def update_layout(value):
    return trav(value),{'name': 'breadthfirst',}#'roots':'[id = {}]'.format(value)}

if __name__ == '__main__':
    app.run_server(debug=True)