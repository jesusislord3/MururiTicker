from MururiTrueFx import truefx
from MururiTrueFx.utils import actual_figure

import math
# https://github.com/femtotrader/pandas_datareaders_unofficial/commit/b3008b1eb9e2fd1cd86efd6561296fcb5adf0bd8 some copy and paste.
import time
import threading
from bokeh.core.properties import ColumnData
from bokeh.models import ColumnDataSource, Slider, Select
from bokeh.plotting import curdoc, figure

auth_response = truefx.login('jesusislord3','Anglocat777',['EUR/USD'])

print('auth response is',auth_response)

# plot axis
opens = []
closes = [] # bigbid and bidpips
highs = []
lows = []
timestamps = []
response = ''


#graph settings
tickrate = 0.25 # official tick rate
duration_to_plot = 3600 # in seconds
bootstrap = math.ceil(duration_to_plot / tickrate) # round up to give a rough estimated number of samples.

# https://www.continuum.io/content/painless-streaming-plots-bokeh

# from this example - http://stackoverflow.com/a/18793416

###  BEGIN GRAPH PLOTTING
import numpy as np
from bokeh.plotting import figure, output_file, show

def to_np_dt64(x):
    return np.datetime_as_string(np.datetime64(x,'ms'))

## EXAMPLE

window_size = 30
window = np.ones(window_size)/float(window_size)

# output to static HTML file
output_file("stocks.html", title="stocks.py example")

# create a new plot with a a datetime axis type
p = figure(width=800, height=350, x_axis_type="datetime")

# add renderers

# p.circle(aapl_dates, aapl, size=4, color='darkgrey', alpha=0.2, legend='close')

# p.line(aapl_dates, np.array(highs), color='green', legend='Highs') - values lack enough precision to be usualble
# p.line(aapl_dates, np.array(lows), color='red', legend='Lows') - values make no sense for now.

# p.line(aapl_dates, aapl_avg, color='navy', legend='Average')

# NEW: customize by setting attributes
p.title.text = "20 Second Sample"
p.legend.location = "top_left"
p.grid.grid_line_alpha=0
p.xaxis.axis_label = 'Date'
p.yaxis.axis_label = 'Price'
p.ygrid.band_fill_color="olive"
p.ygrid.band_fill_alpha = 0.1

# prep the data interfaces

"""
opends = openline.data_source
closeds = closeline.data_source
"""

# implement the server end. - http://bokeh.pydata.org/en/latest/docs/user_guide/server.html#userguide-server-applications
# latest live ticker example - https://github.com/bokeh/bokeh/blob/master/examples/app/ohlc/main.py
# extra hel;p on new feature - https://stackoverflow.com/questions/24800071/timeseries-streaming-in-bokeh
# start polling data

def poll():
    response = truefx.poll_one_pair(auth_response)
    return poll.update({'actual_figure': actual_figure(response['bigbid'], response['bidpips'])})


source = ColumnDataSource(poll()) # try this during tickerr hours.

closeline = p.line(y='', x='millisecond-timestamp', color='black', legend='Close',source=source )
openline = p.line(y='open', x='millisecond-timestamp', color='blue', legend='Open', source=source )

def data_listener(stop_interupt_signal:threading.Event):
    loop_running = not stop_interupt_signal.isSet()
    print('Data Listener Started')
    timestamps = []
    print('Loop Running', loop_running)
    """
    while loop_running:
        time.sleep(tickrate)
        current_poll = truefx.poll_one_pair(auth_response)
        print(current_poll)
        print('Tick') if current_poll else print('Sorry Kids - Markets Closed.')
        if not timestamps or timestamps[-1] != current_poll['millisecond-timestamp']:
            print('Current Poll is',current_poll['response'])
            opens = opends.data['y'] + [float(current_poll['pollopen'])]
            closes = closeds.data['y'] + [actual_figure(current_poll['bigbid'],current_poll['bidpips'])]
            highs = float(current_poll['high'])
            lows = float(current_poll['low'])
            timestamps = opends.data['x'] + [current_poll['millisecond-timestamp']] # opends/closeds - could use either really.

        else:
            print("skipped loop",current_poll)

        # pump one tick to dataset
        opends.data['y'],opends.data['x'] = (opens,timestamps)
        closeds.data['y'],closeds.data['x'] = (closes,timestamps)
        p.update()
    """

thread_stopper = threading.Event()
"""
    thread = threading.Thread(target=data_listener,args=(thread_stopper,))
    thread.daemon = True # do not be afraid christians! they dont exist (see galatians-12.) fear  is of the devil anyways :D
    thread.start()
"""
print('Showing Graph')

show(p)
data_listener(thread_stopper)
