#!/usr/local/conda2/bin/python
# roychan@: 3/2018
import time
import os
import copy
import pandas as pd
import numpy as np
import dash
import dash.dependencies as dep
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from plotly import tools

UPDATE_INTERVAL_MSEC=1000

def get_mhz():
    try:
        mhz=[]
        with open('/proc/cpuinfo', 'r') as fd:
            for line in fd:
                if line[0:len('cpu MHz')]=='cpu MHz':
                    mhz.append(line.split(':')[1].strip())
        return mhz
    except:
        return 0

def read(filename):
    try:
        with open(filename, 'r') as fd:
            s = fd.readline().rstrip()
            return int(s) if s.isdigit() else s
    except:
        return 0

def gen_graph():    
    data =[
        go.Scatter(x=[], y=[], name='VIN', yaxis='y1'),
        go.Scatter(x=[], y=[], name='VBAT', yaxis='y1'),
        
        go.Scatter(x=[], y=[], name='IBAT', yaxis='y2'),

        go.Scatter(x=[], y=[], name='CPU0', yaxis='y3'),
        go.Scatter(x=[], y=[], name='CPU1', yaxis='y3'),
        go.Scatter(x=[], y=[], name='CPU2', yaxis='y3'),
        go.Scatter(x=[], y=[], name='CPU3', yaxis='y3'),

        go.Scatter(x=[], y=[], name='x86_pkg', yaxis='y4'),
        #go.Scatter(x=[], y=[], name='INT3400', yaxis='y4'),
        go.Scatter(x=[], y=[], name='TSR0', yaxis='y4'),
        go.Scatter(x=[], y=[], name='TSR1', yaxis='y4'),
        go.Scatter(x=[], y=[], name='TSR2', yaxis='y4'),
        go.Scatter(x=[], y=[], name='TSR3', yaxis='y4'),
        #go.Scatter(x=[], y=[], name='B0D4', yaxis='y4'),
        #go.Scatter(x=[], y=[], name='iwlwifi', yaxis='y4')               
    ]
    layout = go.Layout(
        autosize=True, 
        height=768,
        plot_bgcolor="#C0C0C0",
        paper_bgcolor="#F0F0F0",
        margin=dict(l=50, b=40, r=0, t=30),
        xaxis1=dict(title='TIME (SEC)', anchor='y4'),
        yaxis1=dict(title='VOLTAGE (V)',  domain=[0.75375, 1.0]),
        yaxis2=dict(title='CURRENT (A)', domain=[0.5025, 0.7488]),
        yaxis3=dict(title='FREQUENCY (MHz)', domain=[0.25125, 0.4975]),
        yaxis4=dict(title='TEMPERATURE (degC)', domain=[0.0, 0.24625])
    )

    fig = dict(data=data, layout=layout)
    print "==========figure============="
    print fig
    print "============================="
    
    return fig

def gen_histo():    
    data =[
        go.Scatter(
            x=[], y=[], name='IBAT', xaxis='x1', yaxis='y1',
            marker={'color':'orange'}, showlegend=False
        ),
        go.Scatter(
            x=[], y=[], name='x86_pkg', xaxis='x2', yaxis='y1',
            marker={'color':'steelblue'}, showlegend=False
        ),
        go.Scatter(
            x=[], y=[], name='TSR3', xaxis='x3', yaxis='y1',
            marker={'color':'red'}, showlegend=False
        )    
    ]
    layout = go.Layout(
        autosize=True, 
        height=240, 
        plot_bgcolor="#C0C0C0",
        paper_bgcolor="#F0F0F0",
        margin=dict(l=50, b=40, r=0, t=10),
        yaxis1=dict(title='PROBABILITY'),
        xaxis1=dict(title='BAT0 POWER (W)', domain=[0,0.325]),
        xaxis2=dict(title='x86_pkg (deg C)', domain=[0.335, 0.655]),
        xaxis3=dict(title='TSR (deg C)', domain=[0.665, 1])
        
    )

    fig = dict(data=data, layout=layout)
    print "==========figure============="
    print fig
    print "============================="
    
    return fig

def make_annotation_item(xref, x, y, text):
    return dict(xref=xref, yref='y1',
                x=x, y=y,
                font=dict(color='black'),
                text='{} ({:.2f}W)'.format(text,x,y),
                showarrow=True)

app = dash.Dash()

@app.server.route('/static/my.css')
def serve_stylesheet(stylesheet):
    return flask.send_from_directory(os.getcwd(), stylesheet)

app.css.append_css({"external_url": "/css/my.css"})
app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})
#app.css.append_css({'external_url': 'https://cdn.rawgit.com/plotly/dash-app-stylesheets/2d266c578d2a6e8850ebce48fdb52759b2aef506/stylesheet-oil-and-gas.css'})  # noqa: E501

def serve_layout():
    return html.Div(
        children=[
            html.Div(
                children=[
                    html.Button(
                        id='button', 
                        n_clicks=0, 
                        children='STARTING...',
                        style={
                            'margin':'10px', 
                            'float':'left',
                            'font-family': 'verdana', 
                            'font-size':'120%',
                        }
                    ),
                    html.P(
                        id='text_bat0',
                        children='',
                        style={
                            'font-size':'100%', 
                            'float':'left',
                            'border-style':'solid',
                            'border-width':'1px',
                            'margin':'10px',
                            'padding':'5px'
                        }
                    ),
                    html.P(
                        id='text_bat1',
                        children='',
                        style={
                            'font-size':'100%', 
                            'float':'left',
                            'border-style':'solid',
                            'border-width':'1px',
                            'margin':'10px',
                            'padding':'5px'
                        }
                    )
                ],
                style={
                    'position':'sticky',
                    'z-index':'100'
                }

            ),

            html.Div(
                children=[
                    dcc.Graph(
                        id='graph', 
                        figure=gen_graph()
                    ),
                    dcc.Graph(
                        id='histo', 
                        figure=gen_histo()
                    ),                
                    dcc.Interval(id='live-update', interval=1000),
                    html.Div(
                        id='time0', 
                        children=time.time(), 
                        style={'display':'none'}
                    )
                ],  
                style={
                    'position': 'relative',
                    'top': '50px',
                    'display': 'block',
                    'z-index': '10'
                },
            ),

 
        ], style={
            'background-color':'#F0F0F0',
        }
    )

app.layout = serve_layout

@app.callback(
    dep.Output('text_bat0', 'children'),
    [],
    [],
    [dep.Event('live-update', 'interval')]
)
def update_text():
    return 'BAT0: {}, {:.2f}V, {:.2f}A, {}%'.format(
        read('/sys/class/power_supply/BAT0/status'),
        read('/sys/class/power_supply/BAT0/voltage_now')/1e6,
        read('/sys/class/power_supply/BAT0/current_now')/1e6,
        read('/sys/class/power_supply/BAT0/capacity'),
    )

@app.callback(
    dep.Output('text_bat1', 'children'),
    [],
    [],
    [dep.Event('live-update', 'interval')]
)
def update_text():
    return 'BAT1: {}, {:.2f}V, {:.2f}A, {}%'.format(
        read('/sys/class/power_supply/BAT1/status'),
        read('/sys/class/power_supply/BAT1/voltage_now')/1e6,
        read('/sys/class/power_supply/BAT1/current_now')/1e6,
        read('/sys/class/power_supply/BAT1/capacity'),
    )

@app.callback(
    dep.Output('graph', 'figure'),
    [],
    [dep.State('graph', 'figure'),
     dep.State('time0', 'children')],
    [dep.Event('live-update', 'interval')])

def update_plot(fig, time0):
    y_data = []
    
    y_data.append(read('/sys/class/power_supply/BAT0/voltage_now')/1e6)
    y_data.append(read('/sys/class/power_supply/CROS_USB_PD_CHARGER0/voltage_now')/1e6)
    
    y_data.append(read('/sys/class/power_supply/BAT0/current_now')/1e6)

    t = time.time() - time0
    
    mhz = get_mhz()
    for m in mhz:
        y_data.append(m)

    y_data.append(read('/sys/class/thermal/thermal_zone0/temp')/1e3)
    #y_data.append(read('/sys/class/thermal/thermal_zone1/temp')/1e3)
    y_data.append(read('/sys/class/thermal/thermal_zone2/temp')/1e3)
    y_data.append(read('/sys/class/thermal/thermal_zone3/temp')/1e3)
    y_data.append(read('/sys/class/thermal/thermal_zone4/temp')/1e3)
    y_data.append(read('/sys/class/thermal/thermal_zone5/temp')/1e3)
    #y_data.append(read('/sys/class/thermal/thermal_zone6/temp')/1e3)
    #y_data.append(read('/sys/class/thermal/thermal_zone7/temp')/1e3)

    
    data = fig['data']
        
    for dat, y in zip(data, y_data):
        dat['x'].append(t)
        dat['y'].append(y)
        
    return fig

@app.callback(
    dep.Output('histo', 'figure'),
    [],
    [dep.State('graph', 'figure'),
     dep.State('histo', 'figure')],
    [dep.Event('live-update', 'interval')])

def update_histo(fig, histo):    
    annotation = []    
    y = np.array(fig['data'][2]['y'])  
    if min(y)>5:
        y=y[y>0]

    y, x = np.histogram(y, bins=32)
    y=y.astype(float)
    y=y/sum(y)
    y = np.cumsum(y)
    
    histo['data'][0]['x'] = x
    histo['data'][0]['y'] = y

    annotation.append(
        make_annotation_item('x1', x[np.where(y>=0.5)[0][0]], 0.52, "50%")
    )
    annotation.append(
        make_annotation_item('x1', x[np.where(y>=0.9)[0][0]], 0.92, "90%")
    )
    
    y = fig['data'][3]['y']
    if min(y)>5:
        y=y[y>0]

    y, x = np.histogram(y, bins=32)
    y=y.astype(float)/sum(y)    
    y = np.cumsum(y)
    
    histo['data'][1]['x'] = x
    histo['data'][1]['y'] = y

    annotation.append(
        make_annotation_item('x2', x[np.where(y>=0.9)[0][0]], 0.92, "90%")
    )  
    annotation.append(
        make_annotation_item('x2', x[np.where(y>=0.5)[0][0]], 0.52, "50%")
    )  
     
    y = fig['data'][4]['y']
    if min(y)>5:
        y=y[y>0]

    y, x = np.histogram(y, bins=32)
    y=y.astype(float)/sum(y)    
    y = np.cumsum(y)
    
    histo['data'][2]['x'] = x
    histo['data'][2]['y'] = y

    annotation.append(
        make_annotation_item('x3', x[np.where(y>=0.9)[0][0]], 0.92, "90%")
    )  
    annotation.append(
        make_annotation_item('x3', x[np.where(y>=0.5)[0][0]], 0.52, "50%")
    )
    
    histo['layout'].update(
        {'annotations':annotation}
    )
    
    return histo

@app.callback(
     dep.Output('button', 'children'),
    [dep.Input('live-update', 'interval')]
)
def update_button_text(interval):
    if interval==UPDATE_INTERVAL_MSEC:
        return 'STOP'
    else:
        return 'RUN'
        
@app.callback(
     dep.Output('live-update', 'interval'),
    [dep.Input('button', 'n_clicks')]
)
def button(n_clicks):
    if n_clicks%2:
        return UPDATE_INTERVAL_MSEC*3600*24
    else:
        return UPDATE_INTERVAL_MSEC

if __name__ == '__main__':
    app.run_server(debug=True, port=9011)
    #app.run_server(port=9001)
