# https://github.com/bokeh/bokeh/tree/master/examples/app/weather
# run with bokeh serve --show dashboard.py

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

MEASURES = ['temperature', 'light', 'moisture']
AGGS = {'raw': 'raw', '5 MIN': '5T', '15 MIN': '15T', 'HOUR': 'H', 'DAY': 'D'}
COLORS = [(219, 94, 86), (86, 219, 94), (94, 86, 219)]  # colors copy/pasted from seaborn
DAYS_AGO = lambda days: pd.to_datetime(time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(time.time() - (60*60*24*days))))
TIME = {'last day':DAYS_AGO(1), 'last 4 days':DAYS_AGO(4), 'last week':DAYS_AGO(7), 'last month':DAYS_AGO(30), 'all time':DAYS_AGO(1000)}

def get_dataset(full, agg, time):
    sources = {}
    full['ts'] = pd.to_datetime(full.ts)
    for measure in MEASURES:
        df = full[full.ts>=TIME[time]].set_index(['ts'])
        df.sort_index(inplace=True)
        if agg!='raw':
            df = df.resample(AGGS[agg]).mean()
        sources[measure] = ColumnDataSource(data=df.reset_index())
    return sources

def make_plots(sources):
    plots = {}
    for measure in MEASURES:
        plot = figure(x_axis_type="datetime", plot_width=400, plot_height=400, tools="pan,box_zoom,reset")
        plot.title.text = measure.capitalize()
        plot.line('ts', measure, source=sources[measure], line_color=COLORS.pop())

        # fixed attributes
        plot.xaxis.axis_label = None
        plot.yaxis.axis_label = None
        plot.axis.axis_label_text_font_style = "bold"
        plot.x_range = DataRange1d(range_padding=0.0)
        plot.grid.grid_line_alpha = 0.3

        plots[measure] = plot

    return plots

def update_plot(attrname, old, new):
    srcs = get_dataset(df, agg_select.value, time_select.value)
    for measure in MEASURES:
        sources[measure].data.update(srcs[measure].data)

def timelapse(q):
    """
    When new images are added to the server, have these gifs created
    """
    return Div(text='<IMG SRC="dashboard/static/timelapse/q%s.gif" height="225" width="300">'%q)

def recent(q):
    """
    When new images are added to the server, this folder is updated
    """
    return row([Div(text='<IMG SRC="dashboard/static/recent/q%s_%s.jpg" height="187.5" width="250">'%(q, r)) for r in range(1,6)])

# load data
df = pd.read_csv(join(dirname(__file__), '../data/sensor_data.csv'), names=['ts']+MEASURES)

# 1. create sensor widgets and plots
sensor_title = Div(text="<h1>Sensor Data</h1>")
agg = 'raw'
agg_select = Select(value=agg, title='Aggregation level', options=list(AGGS.keys()), width=400)
time = 'last 4 days'
time_select = Select(value=time, title='Time frame', options=list(TIME.keys()), width=400)
agg_select.on_change('value', update_plot)
time_select.on_change('value', update_plot)
update_div = Div(text="<h4>Last updated</h4> "+str(df.ts.iloc[-1]), width=390)

# create plots
sources = get_dataset(df, agg, time)
plots = make_plots(sources)

# arrange them
widgets_row = row(update_div, agg_select, time_select)
plots_row = row(plots['temperature'], plots['light'], plots['moisture'])
sensors_arrangement = column(sensor_title, widgets_row, plots_row)

# 2. add timelapse gifs
timelapse_title = Div(text="<h1>Last 24 hours</h1>")
timelapse_row = row([timelapse(q) for q in range(1,5)])
timelapse_arrangement = column(timelapse_title, timelapse_row)

# 3. add most recent pictures
recent_title = Div(text="<h1>Most recent</h1>")
time_labels = json.load(open('dashboard/static/recent/labels.json', 'r'))
recent_labels = row([Div(text='<h4>%s</h4>'%tl, width=300) for tl in time_labels])
recent_arrangement = column(recent_title, recent_labels, column([recent(q) for q in range(1,5)]))

column = column(sensors_arrangement, timelapse_arrangement, recent_arrangement)


curdoc().add_root(column)
curdoc().title = "Hydrofarm"
