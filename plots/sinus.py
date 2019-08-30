import numpy as np

from bokeh.plotting import Figure
from bokeh.models import ColumnDataSource
from bokeh.io import curdoc
from bokeh.models.widgets import Slider
from bokeh.layouts import WidgetBox, Row

sinus_source = ColumnDataSource()

plot = Figure(plot_height=400, plot_width=600)
plot.line(x="x", y="y", source=sinus_source)

phase = Slider(title="Phase", start=0, end=2*np.pi, step=0.1, value=0)

x = np.linspace(0, 2*np.pi, 100)
y = np.sin(x)
sinus_source.data = {"x": x, "y": y}

def slider_callback(attr, old, new):
    phase_value = phase.value
    x = np.linspace(0, 2*np.pi, 100)
    y = np.sin(x + phase_value)
    sinus_source.data = {"x": x, "y": y}

phase.on_change("value", slider_callback)

inputs = WidgetBox(phase)
curdoc().add_root(Row(plot, inputs, width=800))
