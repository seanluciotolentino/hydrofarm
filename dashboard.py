# https://github.com/bokeh/bokeh/tree/master/examples/app/weather
# run with bokeh serve --show main.py

from os.path import join, dirname
import datetime

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

def days_ago(days):
    return pd.to_datetime(time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(time.time() - (60*60*24*days))))

TIME = {'last day':days_ago(1), 'last 4 days':days_ago(4), 'last week':days_ago(7), 'last month':days_ago(30), 'all time':days_ago(1000)}

# colors copy/pasted from seaborn
colors = [(219, 94, 86), (86, 219, 94), (94, 86, 219)]

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
        plot.title.text = measure
        plot.line('ts', measure, source=sources[measure], line_color=colors.pop())

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


agg = 'raw'
time = 'all time'
df = pd.read_csv(join(dirname(__file__), 'data/sensor_data.csv'), names=['ts']+MEASURES)
sources = get_dataset(df, agg, time)

# create plots and widgets
agg_select = Select(value=agg, title='Aggregation', options=list(AGGS.keys()))
time_select = Select(value=time, title='Time Frame', options=list(TIME.keys()))
plots = make_plots(sources)
agg_select.on_change('value', update_plot)
time_select.on_change('value', update_plot)
update_div = Div(text="<h3>Last Update:\n</h3>"+str(df.ts.iloc[-1]), width=200, height=100)

# set arrangement
plots_row = row(plots['temperature'], plots['light'], plots['moisture'])
widgets_row = row(agg_select, time_select, update_div)
column = column(widgets_row, plots_row)
curdoc().add_root(column)
curdoc().title = "Hydrofarm"