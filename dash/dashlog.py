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
from mytools import *

UPDATE_INTERVAL_MSEC=1000

app = dash.Dash()

@app.server.route('/css/my.css')
def serve_stylesheet(stylesheet):
    return flask.send_from_directory(os.getcwd(), stylesheet)

app.css.append_css({"external_url": "/css/my.css"})
app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})
#app.css.append_css({'external_url': 'https://cdn.rawgit.com/plotly/dash-app-stylesheets/2d266c578d2a6e8850ebce48fdb52759b2aef506/stylesheet-oil-and-gas.css'})  # noqa: E501

app.layout = html.Div(children=[
    html.Div([html.Button(id='button', n_clicks=0, children='STARTING...')], style={'color':'white'}),
    html.Div([dcc.Graph(id='graph_one', figure={})],  style={'display': 'inline-block'}),
    dcc.Interval(id='live-update', interval=1000),
], style={'background-color':"#F0F0F0"}) 

@app.callback(
    dep.Output('graph_one', 'figure'),
    [],
    [dep.State('graph_one', 'figure')],
    [dep.Event('live-update', 'interval')])

def do_plot(figure):
    df = pd.read_csv('/tmp/mon.csv')

    plt_w = uj2w(df.time, df.cpu_uj)
    sys_w = uj2w(df.time, df.sys_uj)*2
    
    t = df.time - df.time[0]

    y_data = (df.v0/1e6, df.v1/1e6, df.i0/1e6, df.i1/1e6, df.i0*df.v0/1e12, df.i1*df.v1/1e12, sys_w, plt_w, sys_w-plt_w, df.t0/1000, df.t1/1000, df.t2/1000, df.t3/1000, df.t4/1000, df.t5/1000, df.t6/1000, df.t7/1000,)
    
    
    if 'data' in figure:
        data = figure['data']
        for n, dat in enumerate(data):
            dat['x']=t
            dat['y']=y_data[n]
        fig=figure
    else:
        trace_v0 = go.Scatter(x=t, y=y_data[0], name='BAT0', 
                        marker=dict(color='orange'),
                        legendgroup='bat0', xaxis='TIME')
        trace_v1 = go.Scatter(x=t, y=y_data[1], name='BAT1',
                        marker=dict(color='steelblue'), 
                        legendgroup='bat1')
        trace_i0 = go.Scatter(x=t, y=y_data[2], name='BAT0',
                        marker=dict(color='orange'),
                        legendgroup='bat0', showlegend=False)
        trace_i1 = go.Scatter(x=t, y=y_data[3], name='BAT1',
                        marker = dict(color='steelblue'), 
                        legendgroup='bat1', showlegend=False)
        trace_p0 = go.Scatter(x=t, y=y_data[4], name='BAT0',
                        marker = dict(color='orange'),
                        legendgroup='bat0', showlegend=False)
        trace_p1 = go.Scatter(x=t, y=y_data[5], name='BAT1',
                        marker = dict(color='steelblue'), 
                        legendgroup='bat1', showlegend=False)
        trace_sys = go.Scatter(x=t, y=y_data[6], name='PSYS', 
                        legendgroup='psys')
        trace_plt = go.Scatter(x=t, y=y_data[7], name='SOC',
                        legendgroup='plt')
        trace_rop = go.Scatter(x=t, y=y_data[8], name='ROP',
                        legendgroup='rop')
        trace_t0 = go.Scatter(x=t, y=y_data[9], name='x86_pkg')
        trace_t1 = go.Scatter(x=t, y=y_data[10], name='INT3400')
        trace_t2 = go.Scatter(x=t, y=y_data[11], name='TSR0')
        trace_t3 = go.Scatter(x=t, y=y_data[12], name='TSR1')
        trace_t4 = go.Scatter(x=t, y=y_data[13], name='TSR2')
        trace_t5 = go.Scatter(x=t, y=y_data[14], name='TSR3')
        trace_t6 = go.Scatter(x=t, y=y_data[15], name='B0D4')
        trace_t7 = go.Scatter(x=t, y=y_data[16], name='iwlwifi')

        fig = tools.make_subplots(rows=4, cols=1, vertical_spacing=0.005, shared_xaxes=True)

        fig.append_trace(trace_v0, 1, 1)
        fig.append_trace(trace_v1, 1, 1)
        fig.append_trace(trace_i0, 2, 1)
        fig.append_trace(trace_i1, 2, 1)
        fig.append_trace(trace_p0, 3, 1)
        fig.append_trace(trace_p1, 3, 1)
        fig.append_trace(trace_sys, 3, 1)
        fig.append_trace(trace_plt, 3, 1)
        fig.append_trace(trace_rop, 3, 1)
        fig.append_trace(trace_t0, 4, 1)
        fig.append_trace(trace_t1, 4, 1)
        fig.append_trace(trace_t2, 4, 1)
        fig.append_trace(trace_t3, 4, 1)
        fig.append_trace(trace_t4, 4, 1)
        fig.append_trace(trace_t5, 4, 1)
        fig.append_trace(trace_t6, 4, 1)
        fig.append_trace(trace_t7, 4, 1)

        fig.layout.update(go.Layout(
            autosize=True,
            width=1200, 
            height=768, 
            margin=dict(l=50, b=40, r=0, t=30),
            plot_bgcolor="#D0D0D0",
            paper_bgcolor="#F0F0F0",
            xaxis1=dict(title='TIME (SEC)'),
            yaxis1=dict(title='VOLTAGE (V)'),
            yaxis2=dict(title='CURRENT (A)'),
            yaxis3=dict(title='POWER (W)'),
            yaxis4=dict(title='TEMPERATURE (degC)')      
        ))
        
        for n, dat in enumerate(fig["data"]):
            dat["line"]=dict(width=1.5)
            if n>8:
                dat["line"]["dash"]="dashdot"

    return fig

@app.callback(
     dep.Output('button', 'children'),
    [dep.Input('live-update', 'interval')]
)
def update_button_text(interval):
    if interval==UPDATE_INTERVAL_MSEC:
        return 'STOP UPDATE'
    else:
        return 'AUTO UPDATE'
        
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