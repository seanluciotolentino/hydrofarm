# https://github.com/bokeh/bokeh/tree/master/examples/app/weather
# run with bokeh serve --show dashboard

from os.path import join, dirname
import datetime
import os
import json
import pandas as pd
from scipy.signal import savgol_filter
import time
from bokeh.io import curdoc
from bokeh.layouts import row, column
from bokeh.models import ColumnDataSource, DataRange1d, Select, Div
from bokeh.palettes import Blues4
from bokeh.plotting import figure

DAYS_AGO = lambda days: pd.to_datetime(time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(time.time() - (60*60*24*days))))

def daily(q):
    """
    When new images are added to the server, have these gifs created
    """
    d = DAYS_AGO(0)  # add a timestamp so images don't get cached
    return Div(text='<IMG SRC="dashboard/static/timelapse/q%s.gif?dummy=%s" height="225" width="300">'%(q,d))

def weekly(q):
    """
    When new images are added to the server, have these gifs created
    """
    return Div(text='<IMG SRC="dashboard/static/timelapse/weekly%s.gif" height="225" width="300">'%q)

def recent(q):
    """
    When new images are added to the server, this folder is updated
    """
    d = DAYS_AGO(0)  # add a timestamp so images don't get cached
    return row([Div(text='<IMG SRC="dashboard/static/recent/q%s_%s.jpg?dummy=%s" height="187.5" width="250">'%(q, r, d)) for r in range(1,5)])


# 1. create sensor widgets and plots
sensor_title = Div(text="<h1>CatWatch</h1>")

# 2. add timelapse gifs
daily_title = Div(text="<h2>Last 24 hours</h2>")
daily_row = row([daily(q) for q in range(1,5)])
daily_arrangement = column(daily_title, daily_row)

# weekly_title = Div(text="<h1>Last 7 days</h1>")
# weekly_row = row([weekly(q) for q in range(1,6)])
# weekly_arrangement = column(weekly_title, weekly_row)

# 3. add most recent pictures
recent_title = Div(text="<h2>Most recent</h2>")
recent_arrangement = column(recent_title, column([recent(q) for q in range(1,5)]))

#column = column(sensors_arrangement, daily_arrangement, weekly_arrangement, recent_arrangement)
column = column(daily_arrangement, recent_arrangement)

curdoc().add_root(column)
curdoc().title = "CatWatch"
