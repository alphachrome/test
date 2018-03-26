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
from mytools import sysvar

UPDATE_INTERVAL_MSEC=1500

app = dash.Dash()

varOptions =[
    dict(label='BAT0_V', value='/sys/class/power_supply/BAT0/voltage_now'),
    dict(label='BAT0_I', value='/sys/class/power_supply/BAT0/current_now'),
    dict(label='BAT0_SOC', value='/sys/class/power_supply/BAT0/capacity'),
    dict(label='BAT0_Q', value='/sys/class/power_supply/BAT0/charge_now'),
    dict(label='BAT1_V', value='/sys/class/power_supply/BAT1/voltage_now'),
    dict(label='BAT1_I', value='/sys/class/power_supply/BAT1/current_now'),
    dict(label='BAT1_SOC', value='/sys/class/power_supply/BAT1/capacity'),
    dict(label='BAT1_Q', value='/sys/class/power_supply/BAT1/charge_now')]

@app.server.route('/css/my.css')
def serve_stylesheet(stylesheet):
    return flask.send_from_directory(os.getcwd(), stylesheet)

app.css.append_css({"external_url": "/css/my.css"})
app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})

app.layout = html.Div(
    children=[
        html.Div(
            [
                html.Button(
                   id='button', 
                   n_clicks=0, 
                   children='RUN'),
                dcc.Dropdown(
                   id='option_value', 
                   options=varOptions, 
                   value=varOptions[0]['value']
                ),
            ],
            style={'display': 'inline-block'}
        ),
        
        html.Div(
            [
                dcc.Graph(
                    id='graph_one', 
                    figure=dict(
                        data=[
                            go.Scatter(
                                x=[], 
                                y=[], 
                                name='BAT0',
                                xaxis='TIME'
                            ),
                        ],
                        layout = go.Layout(
                            autosize=True,
                            width=800, 
                            height=600, 
                            margin=dict(l=50, b=40, r=0, t=30),
                            plot_bgcolor="#D0D0D0",
                            paper_bgcolor="#F0F0F0",    
                        )
                    )
                )
            ],  

        ),
        
        dcc.Interval(
            id='live-update', 
            interval=1000, 
        ),
        
        html.Div(
            id='clear_fig', 
            children=True, 
            style=dict(display='none')
        )
    ], 
    style={"background-color":"#F0F0F0"}
)        

@app.callback(
    dep.Output('graph_one', 'figure'),
    [],
    [dep.State('graph_one', 'figure'),
     dep.State('option_value', 'value')
    ],
    [dep.Event('live-update', 'interval')]
)
def update_fig(figure, option_value):
    data = figure["data"]
    data[0]['x'].append(time.time())
    data[0]['y'].append(sysvar(option_value))
    return figure

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
    app.run_server(debug=True)