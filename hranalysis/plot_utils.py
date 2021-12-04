import pandas as pd
import numpy as np

from statsmodels.nonparametric.smoothers_lowess import lowess
from sklearn.linear_model import LinearRegression
import itertools

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .filter import threshold_filter


def plot(data, plot_title, intervals=True, filt=None, threshold=10):
    """
    Displays interactive heart rate and speed plots.
    
    Parameters
    ----------
    data: pd.DataFrame
        The data to plot.
        
    plot_title: str
        The title of the plot.
        
    filt: str (optional, default None)
        Applies an optional filter to the heart rate. Valid filters are:
            *None: plot unfiltered data
            *lowess: locally weighted scatterplot smoothing, frac=0.5
            *mean: moving average, window=7
            *threshold: threshold filter from hr_filter.py
            
    threshold: int (optional, default 10)
        If filt='threshold', the amount of variation allowed between
        heart rate samples.
    
    Return
    -----------
    return: plotly.graph_objs.Figure
        Returns an instance of plotly.graph_objs with two subplots:
            heart rate vs time and speed vs time.
    """
    
    palette = itertools.cycle(px.colors.qualitative.Dark24)
    workout_num = 1

    fig = make_subplots(
            rows=5,
            cols=1,
            specs=[
                [{"rowspan": 3}],
                [None],
                [None],
                [{"rowspan": 2}],
                [None],
                ],
            vertical_spacing=0.1
            )

    visibility=None
    
    for name, workout in data.groupby(['date', 'protocol_name']):
        
        heartrate = []
        start = workout.sampletime.tolist()[0]
        time_elapsed=(workout['sampletime'].apply(lambda x: (x-start).total_seconds())).tolist()
        
        if intervals == True:
            intervals_array = workout.stage.values
        else:
            intervals_array = None
                
        if filt == 'lowess':
            heartrate = lowess(workout.heartrate_bpm, time_elapsed, frac=0.05).T[1].tolist()

        elif filt=='mean':   
            heartrate = workout.heartrate_bpm.rolling(window=7, min_periods=1, center=True, closed='both').mean()
            heartrate = heartrate.to_list()
            
        elif filt=='threshold':
            heartrate = threshold_filter(workout.heartrate_bpm.values, intervals_array=intervals_array, threshold=threshold)
        
        elif not filt:
            heartrate = workout.heartrate_bpm

        line_color = next(palette)
        line_name = '{}: {}'.format(workout_num, name[1])
        workout_num += 1
        line_group = name[1]

        fig.add_trace(
            go.Scatter(
                x=time_elapsed,
                y=heartrate,
                name=line_name,
                showlegend=True,
                legendgroup=line_name,
                marker=dict(color=line_color),
                visible=visibility
            ),
            row=1,
            col=1
        )

        fig.add_trace(
            go.Scatter(
                x=time_elapsed,
                y=workout.speed,
                showlegend=False,
                legendgroup=line_name,
                marker=dict(color=line_color),
                visible=visibility
            ),
            row=4,
            col=1
        )
        
        visibility='legendonly'

    fig.update_layout(height=700, width=1000, title_text=plot_title, title_x=0.45)
    fig.update_yaxes(title_text='Heart Rate (bpm)', row=1, col=1)
    fig.update_yaxes(title_text='Speed (mph)', row=4, col=1)
    fig.update_xaxes(title_text='Time (s)', row=1, col=1)
    fig.update_xaxes(title_text='Time (s)', row=4, col=1)
    
    return fig

def plot_compare(data, threshold=10):
    """
    Displays interactive heart rate plots applying different filters
        *unfiltered heart rate vs time
        *variation threshold filter vs time
        *moving average filter vs time
        *variation threshold + moving average filter vs time
    
    Parameters
    ----------
    data: pd.DataFrame
        The data of one workout to plot.
    
    threshold: int (optional, default 10)
        The amount of variation allowed between heart rate samples
        for the variation threshold filter.

    Return
    -----------
    return: None
    """
    
    start = data.sampletime.values[0]
    time = data['sampletime'].apply(lambda x: (x-start).total_seconds())
    heartrate = data.heartrate_bpm.values
    filtered_hr = threshold_filter(data.heartrate_bpm.values, data.stage.values, threshold=threshold)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=time, y=filtered_hr,
                        mode='lines',
                        showlegend=False))
    fig.update_layout(title="Comparison of Heart Rate Filters",
                      xaxis_title="Time Elapsed (s)",
                      yaxis_title="Heart Rate (bpm)",
                      title_x=0.5,
                      height=700,
                      width=1000
                     )

    fig = make_subplots(shared_xaxes='all', shared_yaxes='all', rows=2, cols=2, horizontal_spacing=0.05, vertical_spacing=0.12,
                        y_title='Heart Rate (bpm)',
                        x_title='Time (s)',
                        subplot_titles=("Unfiltered", "Variation Threshold", "Moving Average", "LOWESS"))

    fig.add_trace(go.Scatter(x=time, y=data.heartrate_bpm,
                        mode='lines',
                        showlegend=False),
                 row=1, col=1)
    
    fig.add_trace(go.Scatter(x=time, y=filtered_hr,
                        mode='lines',
                        showlegend=False),
                 row=1, col=2)

    fig.add_trace(go.Scatter(x=time, y=data.heartrate_bpm.rolling(window=7, min_periods=1, center=True, closed='both').mean(),
                        mode='lines',
                        showlegend=False),
                 row=2, col=1)

    fig.add_trace(go.Scatter(x=time, y= lowess(data.heartrate_bpm, time, frac=0.05).T[1].tolist(),
                        mode='lines',
                        showlegend=False),
                 row=2, col=2)

    fig.update_layout(yaxis_showticklabels=True, yaxis2_showticklabels=True, yaxis3_showticklabels=True, yaxis4_showticklabels=True)
    fig.update_layout(xaxis_showticklabels=True, xaxis2_showticklabels=True, xaxis3_showticklabels=True, xaxis4_showticklabels=True)
    
    fig.show()
    
    return