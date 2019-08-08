'''
A ball is dropped so that it accelerates by the graviatational force of the Earth. Instead of using Newtonian mechanics in which one would set up a balance of forces and integrate to get the trajectory curve over time, we use Lagrangian (or, similarily Hamiltonian,) machanis. Here, a energy functional is created which is build upon the trajectory curve and its derivatives. Most of the time, there are infinite solution functions that minize this functional, i.e., are a weak solution to the corresponding partial differential equation. Minimizing can be tideously done by the Gateaux Derivative which is not always possible, at least analytically.
In this interactive plot we present one of the easiest functional, the one of falling object and give different solutions each complying with the boundary conditions and the requisites on differentiability. Only one minimizes the functional.
'''

import numpy as np

from bokeh.io import curdoc
from bokeh.layouts import row, widgetbox
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import Slider
from bokeh.plotting import figure

from extensions.Latex import LatexLabel

HEIGHT = 400
WIDTH_PLOT = 600
WIDTH_TOTAL = 800


numeric_values = [
        -1.0,
        -4/3,
        -6/5,
        -32/35,
        -5/9,
        -12/77,
        ]

def update_data(function_selector, plot_values, numeric_value_label, function_label):
    t = np.linspace(0, 1, 100)
    y = 1 - t**function_selector.value
    plot_values.data = {"t": t, "y": y}

    numeric_value_label.text = "J(y) = \int_{0}^{1} \dot{y}^2 - 4 y \; \mathrm{d} t \\approx " + str(round(numeric_values[function_selector.value - 1], 4))
    function_label.text = "y(t) = 1 - t^" + str(function_selector.value)


plot_values = ColumnDataSource()

plot = figure(plot_height=HEIGHT, plot_width=WIDTH_PLOT, tools="", x_range=[-0.2, 1.2], y_range=[-0.5, 1.5])
plot.xaxis.axis_label="Zeit t"
plot.yaxis.axis_label="Höhe über Grund y"
plot.line(x="t", y="y", source=plot_values)

numeric_value_label = LatexLabel(text="", x=0.1, y=-0.1, render_mode="css", text_font_size="10pt", background_fill_alpha=0)
plot.add_layout(numeric_value_label)
function_label = LatexLabel(text="", x=0.1, y=1.0+0.2, render_mode="css", text_font_size="10pt", background_fill_alpha=0, text_color="blue")
plot.add_layout(function_label)

function_selector = Slider(title="Potenz des Polynoms", start=1, end=6, step=1, value=1)

update_data(function_selector, plot_values, numeric_value_label, function_label)

def update_slider(attr, old, new):
    update_data(function_selector, plot_values, numeric_value_label, function_label)

for slider in (function_selector, ):
    slider.on_change("value", update_slider)

inputs = widgetbox(function_selector, )

curdoc().add_root(row(plot, inputs, width=WIDTH_TOTAL))
