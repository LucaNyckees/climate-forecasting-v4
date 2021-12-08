import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime
import os
import plotly.graph_objects as go
import plotly.express as px
import matplotlib.pyplot as plt
from textwrap import wrap
import matplotlib.colors as mcolors


colors_list = px.colors.qualitative.Plotly

def all_obs_precise(dfs, names, y1, y2):
    
    fig = go.Figure()
    
    fig.update_layout(
    title="Time-window daily evolution of mean temperature over all observatories",
    width = 1000,
    height = 400,
    xaxis_title="day (e.g. 1rst January "+str(y1)+" = 0)",
    yaxis_title='daily mean temperature'
    )
    
    i = 0
    
    for df in dfs:
        
        fig.add_trace(
            go.Scatter(x=np.arange(len(df[(df['Year']<=y2) & (df['Year']>=y1)]['TG'])), 
                    y=df[(df['Year']<=y2) & (df['Year']>=y1)]['TG'], 
                    mode='lines',
                    name = names[i],
                    line=dict(width=2),
                    showlegend = True)
            )
        i += 1
    
    return fig


def all_obs(dfs_M, names, y1, y2):
    
    fig = go.Figure()
    
    fig.update_layout(
    title="Time-window monthly evolution of mean temperature over all observatories",
    width = 1000,
    height = 400,
    xaxis_title="month (e.g. January "+str(y1)+" = 0)",
    yaxis_title='monthly mean temperature'
    )
    
    i = 0
    
    for df_M in dfs_M:
        
        fig.add_trace(
            go.Scatter(x=np.arange(len(df_M[(df_M['Years']<=y2) & (df_M['Years']>=y1)]['Mean'])), 
                    y=df_M[(df_M['Years']<=y2) & (df_M['Years']>=y1)]['Mean'], 
                    mode='lines',
                    name = names[i],
                    line=dict(width=2),
                    showlegend = True)
            )
        i += 1
    
    return fig


def circular_vision(data_M, Years, cumul):
    
    def cosine(i):
        
        return np.cos((3+i%12)*np.pi/6)
    
    def sine(i):
        
        return np.sin((3+i%12)*np.pi/6)

    m1 = max(data_M['Mean'])
    m0 = min(data_M['Mean'])
    c = np.mean(data_M['Mean'])
    angles = [np.pi/6 * n for n in range(12)]

    x = np.linspace(-m1+m0,m1-m0,1000)
    y = np.sqrt((m1-m0)**2-x**2)

    x_ = np.linspace(m0,-m0,1000)
    y_ = np.sqrt((-m0)**2-x_**2)

    coordinates = []
    
    a_ = [cosine(i) for i in range(12)]
    b_ = [sine(i) for i in range(12)]

    a = [cosine(i) for i in range(1447)]
    b = [sine(i) for i in range(1447)]

    #colors = list(mcolors.CSS4_COLORS.values())

    colors = ['violet' for i in range(120)]

    for year in Years:

        if year != 2021:

            c = colors[year-1901]

            z = str(year)

            if cumul:

                coordinates.append((a[:12*(year-1900)]*(data_M[data_M['Years']<=year]['Mean']-m0),b[:12*(year-1900)]*(data_M[data_M['Years']<=year]['Mean']-m0),z,c))

            else:

                coordinates.append((a_*(data_M[data_M['Years']==year]['Mean']-m0),b_*(data_M[data_M['Years']==year]['Mean']-m0),z,c))


    data = [go.Scatter(
                x=x,
                y=y,
                name=z,
                showlegend=True,
                mode="lines+markers",
                marker=dict(color=c)) for (x,y,z,c) in coordinates]

    fig = go.Figure(
        data=[go.Scatter(
                x=coordinates[0][0],
                y=coordinates[0][1], 
                name = '2019', 
                showlegend=True)],
        layout=go.Layout(
            xaxis=dict(range=[-35, 35], autorange=False),
            yaxis=dict(range=[-35, 35], autorange=False),
            title="Temperature Circular Visualization",
            width = 500,
            height = 500,
            updatemenus=[dict(
                type="buttons",
                buttons=[dict(label="Play",
                              method="animate",
                              args = [None, {"frame": {"duration": 50, 
                                                        "redraw": True},
                                            "fromcurrent": True, 
                                            "transition": {"duration": 0},
                                            "fromcurrent":True}])])]
        ),
        frames=[go.Frame(data=[dat]) for dat in data]
    )

    fig.add_trace(
    go.Scatter(x=x, 
            y=y, 
            mode='lines',
            name = 'max°',
            line=dict(width=2, color='lightblue'),
            showlegend = False)
    )
    fig.add_trace(
    go.Scatter(x=x, 
            y=-y, 
            mode='lines',
            name = 'max°',
            line=dict(width=2, color='lightblue'),
            showlegend = True)
    )
    fig.add_trace(
    go.Scatter(x=x_, 
            y=y_, 
            mode='lines',
            name = '0°',
            line=dict(width=2, color='cornflowerblue'),
            showlegend = False)
    )
    fig.add_trace(
    go.Scatter(x=x_, 
            y=-y_, 
            mode='lines',
            name = '0°',
            line=dict(width=2, color='cornflowerblue'),
            showlegend = True)
    )

    fig.add_trace(go.Scatter(
            x=[(m1-m0) * np.cos(s) for s in angles],
            y=[(m1-m0) * np.sin(s) for s in angles],
            mode="text",
            name="",
            text=["Oct", "Nov", "Dec", "Jan", "Feb", "Mar",
                    "Apr", "May", "Jun", "Jul", "Aug", "Sep"],
            textposition=["middle right", "middle right", "top center", "top center",
                      "middle left", "middle left", "middle left", "bottom left", "middle left",
                      "bottom center", "middle right", "top right"]

    ))
    
    return fig




def layout(fig):
    
    fig['layout'].update({
        'showlegend': True,
        'width': 600,
        'height': 500,
    })
    
def plotly_mean_temp(year, fig, df, elt):
    
    data=df[df.Year==year]

    fig.add_trace(go.Scatter(x=data['Day_of_year'], y=data['TG'],
            fill=None,
            mode='lines',
            name = year
            #line_color='rgb(184, 247, 212)',
            ))
    fig.update_layout(
    title=elt+" curve",
    xaxis_title="day of the year",
    yaxis_title=elt
    )
    layout(fig)
    
    
def plotly_hist_mean(year, fig, df, elt, bins, iterate=False):
    
    data=df[df.Year==year]['TG']
    
    if iterate:
        
        fig.add_trace(go.Histogram(x=data, 
                                   name=str(year),
                               xbins=dict( 
        start=-130.0,
        end=280,
        size=410/float(bins)
    )))
        
    else:
    
        fig.add_trace(go.Histogram(x=data, 
                                   name=str(year),
                                   marker_color=colors_list[5],
                                   xbins=dict( 
            start=-130.0,
            end=280,
            size=410/float(bins)
        )))
    
    fig.update_layout(
    title=elt+" histogram",
    xaxis_title="value",
    yaxis_title="count"
    )
    layout(fig)
    
    
def plotly_pie_chart_missing(year, fig, df):
    
    fig.update_layout(
    title="Proportion of missing values",
    )
    layout(fig)
    
def plotly_min(years, x, fig, df, elt):
    
    fig.update_layout(
    title="Minimum " + elt + " curve",
    xaxis_title="year",
    yaxis_title="Minimum " + elt
    )
    layout(fig)
    
    year = years[x]

    min_temps = [min(df[df.Year==year]['TG']) for year in years]
    
    fig.add_trace(go.Scatter(x=years, y=min_temps,
            fill=None,
            name="",
            mode='lines',
            line_color=colors_list[7]
            ))
    fig.add_trace(go.Scatter(x=[years[x]], y=[min_temps[x]],
            fill=None,
            mode='markers',
            name = str(year)
            ))
    layout(fig)
    
def plotly_max(years, x, fig, df, elt):
    
    fig.update_layout(
    title="Maximum " + elt + " curve",
    xaxis_title="year",
    yaxis_title="Maximum " + elt
    )
    
    year = years[x]

    max_temps = [max(df[df.Year==year]['TG']) for year in years]
    
    fig.add_trace(go.Scatter(x=years, y=max_temps,
            fill=None,
            name="",
            mode='lines',
            line_color='rgb(184, 247, 212)'
            ))
    fig.add_trace(go.Scatter(x=[years[x]], y=[max_temps[x]],
            fill=None,
            mode='markers',
            name = str(year)
            ))
    layout(fig)
    
    
def plotly_std(years, x, fig, df):
    
    fig.update_layout(
        title="Standard deviations curve",
        xaxis_title="year",
        yaxis_title="std"
        )
    
    year = years[x]
    stds = [df[df.Year==year]['TG'].std() for year in years]
    
    fig.add_trace(go.Scatter(x=years, y=stds,
            fill=None,
            mode='lines',
            name="",
            line_color='violet'
            ))
    fig.add_trace(go.Scatter(x=[years[x]], y=[stds[x]],
            fill=None,
            mode='markers',
            name = str(year)
            ))
    layout(fig)
    
    
def plotly_mean_temp_global(years, x, fig, df_av, element):
    
    fig.update_layout(
    title="Average " + element + " curve",
    xaxis_title="year",
    yaxis_title="Average " + element
    )
    layout(fig)
    
    year = years[x]
    temps = [df_av[df_av.Year==year]['ATG'] for year in years]

    fig.add_trace(go.Scatter(x=df_av['Year'], y=df_av['ATG'],
            fill=None,
            mode='lines',
            name="",
            line_color='cornflowerblue'
            ))
    fig.add_trace(go.Scatter(x=[years[x]], y=[temps[x]],
            fill=None,
            mode='markers',
            name = str(year)
            ))