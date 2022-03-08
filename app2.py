import dash_bootstrap_components as dbc
import dash
import pandas as pd
import dash_cytoscape as cyto
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc
import json
from dash.exceptions import PreventUpdate


data=pd.read_excel('Extract2.xlsx')
data=data.iloc[:136]
data['SOURCE_NODE']=data['SOURCE_NODE'].replace('#','',regex=True)
lineage=data[~data['TARGET_VALUE'].str.contains('JOIN\$',regex=True)]
joins=data[data['TARGET_VALUE'].str.contains('JOIN\$',regex=True)]
joins_group=joins.groupby(['OBJECT_NAME','TARGET_NODE'])
group=data.groupby(['OBJECT_NAME','SOURCE_NODE','TARGET_NODE'])
group2=lineage.groupby(['OBJECT_NAME','TARGET_NODE'])
lineage['parent']=lineage.apply(lambda x:(x['OBJECT_NAME'],x['SOURCE_NODE'],x['SOURCE_VALUE']),axis=1)
lin_group=lineage.groupby(['OBJECT_NAME','TARGET_NODE','TARGET_VALUE'])

def find_lineage(key):
    lin=[key]
    while key in lin_group.groups.keys():
        key=lin_group.get_group(key)['parent'].iloc[0]
        lin.append(key)
    return lin

edges=[('+'.join(i[:-1]),'+'.join(i[::2])) for i in list(group.groups.keys())]
nodes=[]
for i in list(group.groups.keys()):
    source='+'.join(i[:-1])
    target='+'.join(i[::2])
    if not source in nodes:
        nodes.append(source)
    if not target in nodes:
        nodes.append(target)

edges_ = [{'data': {'id':"{}+{}+edge".format(source,target),'source': source, 'target': target}} for source, target in edges]
nodes_=[{'data': {'id': label, 'label': label.split('+')[-1],},} for label in nodes]


app = dash.Dash(__name__,external_stylesheets=[dbc.themes.COSMO])

server = app.server

CV_CARD = {
    "position": "fixed",
    "top": 0,
    "left": '16rem',
    "bottom": 0,
    "width": "50rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}
CYTO_STYLESHEET=[{'selector':'node','style':{'padding':'50%','content':'data(label)','text-valign': 'center','text-halign': 'center','height':100,'width':300,'shape':'cut-rectangle','font-size':'30px','text-wrap':'wrap'},},

                     {'selector':'edge','style':{'curve-style':'straight','width':'3px','arrow-shape':'vee'}}
        ]
cv_card = dbc.Card(
    [
        dbc.CardBody([
            html.Div( cyto.Cytoscape(
        id='cv',
        layout={'name': 'breadthfirst','roots':'[id="CV_CLAIM+logicalModel"]','avoidOverlap':True,'animate':True,'spacingFactor':1.3,'nodeDimensionsIncludeLabels':True},
        style={ 'height': '500px'},
        elements=nodes_+edges_,
        stylesheet=CYTO_STYLESHEET
        ))
]
        ),
    ],style=CV_CARD
)


LIST_GROUP = {
    "position": "fixed",
    "top": 0,
    "left": '66rem',
    "bottom": 0,
    "width": "19rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
    'max-height':'650px',
}

list_group = dbc.ListGroup([],id='list_bar',
    style={'max-height':'370px','overflow-y':'scroll','width':'16rem'}
)

list_card = dbc.Card(
    [
        dbc.CardBody([
            list_group,
            #dbc.CardFooter("This is the footer",style={'bottom':0,'height':'150px','max-height':'200px','overflow-y':'scroll'})
            ]),
        dbc.CardFooter("Select a node to display its attributes.",id='attrib',style={'bottom':0,'height':'150px','max-height':'200px','overflow-y':'scroll'})
        ],style=LIST_GROUP,
)

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

sidebar = html.Div(
    [
        html.H2("Sedgwick", className="display-4"),
        html.Hr(),
        html.P(
            "Select the CV from this sidebar.", className="lead",id='temp_storage'
        ),
        dbc.Nav(
            [
                dbc.NavLink("CV_CLAIM", href="/cv_claim",),
                dbc.NavLink("CV_GROUP_VIEW", href="/cv_group_view",),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)


app.layout = dbc.Row(
    [sidebar,
        dbc.Col(cv_card,),
        list_card,

    ],
)
app.config['suppress_callback_exceptions']=True

@app.callback(Output('attrib', 'children'),Output('list_bar','children'),Input('cv', 'tapNodeData'))
def update_layout(node):
    if not node is None:
        key=tuple(node['id'].split('+'))
        try:
            fields=list(group2.get_group(key)['TARGET_VALUE'])
        except KeyError:
            return ["Node selected:",html.Br(), "{}".format(node['id'])],"Nothing to display here."
        return ["Node selected:",html.Br(), "{}".format(node['id'])],[dbc.ListGroupItem(i,id={'type':'list-item','name':"{}+{}+edge".format(node['id'],i)}) for i in fields]
    else:
        return "Select a node to display its attributes here.",["Select a node to display its fields here."]

@app.callback(
    Output('cv', 'stylesheet'),
    Input({'type': 'list-item', 'name': ALL}, 'n_clicks'),
)
def show_lineage(child):
    ctx=dash.callback_context
    flag=False
    if len(ctx.triggered)==1:
        if not ctx.triggered[0]['value'] is None:
            flag=True
    if not flag:
        raise PreventUpdate

    key=json.loads(ctx.triggered[0]['prop_id'].split('.')[0])['name'].split('+')[:-1]
    nodes=find_lineage(tuple(key))
    node_ids=['+'.join(i[:-1]) for i in nodes]
    selector=', '.join(["[id='{}']".format(i) for i in node_ids])
    stylesheet=CYTO_STYLESHEET[:]
    stylesheet.append({'selector':selector,'style':{'background-color':'#199ee6'}})
    return stylesheet

if __name__ == '__main__':
    app.run_server(debug=True)