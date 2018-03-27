# roychan@: 3/2018
import time
import os
import pandas as pd
import numpy as np
import dash
import dash.dependencies as dep
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from plotly import tools
from flask import request, redirect, url_for

UPDATE_INTERVAL_MSEC=1500

def uj2w(t,e):
    w = [(e[1]-e[0])/(t[1]-t[0])/1e6]
    for t0,t1,e0,e1 in zip(t[:-1],t[1:],e[:-1],e[1:]):
        p = (e1-e0)/(t1-t0)/1e6
        if p>100 or p<-100:
            p=0
        w.append(p)
    return np.array(w)

def sysvar(filename):
    try:
        with open(filename, 'r') as fd:
            s = fd.readline().rstrip()
            return int(s) if s.isdigit() else s
    except:
        return 0

app = dash.Dash()
time0=time.time()

path1 = '/sys/class/power_supply/BAT0/current_now'
path2 = '/sys/class/power_supply/BAT1/current_now'

@app.server.route('/scope')
def scope():
    global path
    path = request.args.get('path')
    print '========={}========'.format(path)
    return redirect(url_for('/'))
    
@app.server.route('/css/my.css')
def serve_stylesheet(stylesheet):
    return flask.send_from_directory(os.getcwd(), stylesheet)

app.css.append_css({"external_url": "/css/my.css"})
app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})

app.layout = html.Div(
    children=[

        html.Div(
            children=[
                html.Div([
                    html.Button(
                        id='button-1', 
                        n_clicks=1, 
                        children='CLEAR'
                    ),
                    html.Span(" "),
                    dcc.Input(
                        id='path-1',
                        placeholder='PATH',
                        size=35,
                        type='text',
                        value=path1
                    ),
                ]),
                dcc.Graph(
                    id='graph-1', 
                    figure=dict(
                        data=[
                            go.Scatter(
                                x=[], 
                                y=[], 
                                name='BAT0',
                                xaxis='TIME'
                            )
                        ],
                        layout = go.Layout(
                            width=600, 
                            height=300, 
                            margin=dict(l=40, b=40, r=0, t=22),
                            plot_bgcolor="#D0D0D0"  
                        )
                    )
                ),
                html.Div([
                    html.Button(
                        id='button-2', 
                        n_clicks=1, 
                        children='CLEAR'
                    ),
                    html.Span(" "),
                    dcc.Input(
                        id='path-2',
                        placeholder='PATH',
                        size=35,
                        type='text',
                        value=path2
                    ),
                ]),
                dcc.Graph(
                    id='graph-2', 
                    figure=dict(
                        data=[
                            go.Scatter(
                                x=[], 
                                y=[], 
                                name='BAT0',
                                xaxis='TIME'
                            )
                        ],
                        layout = go.Layout(
                            width=600, 
                            height=300, 
                            margin=dict(l=50, b=40, r=0, t=22),
                            plot_bgcolor="#D0D0D0"    
                        )
                    )
                )
            ]
        ),
        
        dcc.Interval(
            id='live-update', 
            interval=1000, 
        )
    ]
)        

@app.callback(
    dep.Output('graph-1', 'figure'),
    [],
    [dep.State('path-1', 'value'),
     dep.State('graph-1', 'figure'),
     dep.State('button-1', 'n_clicks')],
    [dep.Event('live-update', 'interval')]
)
def update_fig(path, fig, n_clicks):
    data = fig["data"]
    if n_clicks%2:
        data[0]['x'].append(time.time()-time0)
        data[0]['y'].append(sysvar(path))
    else:
        data[0]['x']=[]
        data[0]['y']=[]
    return fig

@app.callback(
    dep.Output('graph-2', 'figure'),
    [],
    [dep.State('path-2', 'value'),
     dep.State('graph-2', 'figure'),
     dep.State('button-2', 'n_clicks')],
    [dep.Event('live-update', 'interval')]
)
def update_fig(path, fig, n_clicks):
    data = fig["data"]
    if n_clicks%2:
        data[0]['x'].append(time.time()-time0)
        data[0]['y'].append(sysvar(path))
    else:
        data[0]['x']=[]
        data[0]['y']=[]
    return fig

@app.callback(
     dep.Output('button-1', 'children'),
    [dep.Input('button-1', 'n_clicks')]
)
def update_button_text(n_clicks):
    if n_clicks%2:
        return 'CLEAR'
    else:
        return 'RUN'
        
@app.callback(
     dep.Output('button-2', 'children'),
    [dep.Input('button-2', 'n_clicks')]
)
def update_button_text(n_clicks):
    if n_clicks%2:
        return 'CLEAR'
    else:
        return 'RUN'

if __name__ == '__main__':
    app.run_server(debug=True, port=9002)