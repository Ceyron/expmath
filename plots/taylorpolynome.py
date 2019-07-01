import numpy as np
import sympy as sp

from bokeh.io import curdoc
from bokeh.layouts import row, widgetbox
from bokeh.models import ColumnDataSource, Band
from bokeh.models.widgets import Slider, RadioButtonGroup, Div
from bokeh.plotting import figure

'''
This plot introduces the Taylor-Polynoms for approximating arbitrary continously differentiable functions. The user selects a order of approximation and an x_spot for their development.
The currently one function available is hardcoded together with its first 5 derivatives. The values of the function made up of the Taylor Polynomes up to the degree chosen are calculated according to the common rule.
A left-point based rectangualr quadrature is in use to compute the numerical deviation from the true solution.
'''

HEIGHT = 400
WIDTH_PLOT = 600
WIDTH_TOTAL = 800

def FUNC_1_0(x):
    return np.sin(x)
def FUNC_1_1(x):
    return np.cos(x)
def FUNC_1_2(x):
    return -np.sin(x)
def FUNC_1_3(x):
    return -np.cos(x)
def FUNC_1_4(x):
    return np.sin(x)
def FUNC_1_5(x):
    return np.cos(x)

# The function pointers are collected in a list to easily implement the summation later on
FUNC_1 = [FUNC_1_0, FUNC_1_1, FUNC_1_2, FUNC_1_3, FUNC_1_4, FUNC_1_5]

# Left-point based numerical integration (mid-point rule)
def integrate(first, second, spacing):
    result = 0.0
    for i in range(len(first)):
        result += (first[i] - second[i]) * spacing
    return np.abs(result)

# This function is called to create the dynamically updated ColumnDataSource that powers the drawing on the client-side
def update_data(order, x_spot, curve_values, taylor_values, point_values, band_values, error_box):
    x = np.linspace(-5, 5, 100)
    y_true = FUNC_1_0(x)
    y_taylor = np.zeros(x.shape)
    for i in range(order.value + 1):
        y_taylor += (x - x_spot.value * np.ones(x.shape))**i / np.math.factorial(i) * FUNC_1[i](x_spot.value)
    curve_values.data = {"x": x, "y": y_true}
    taylor_values.data = {"x": x, "y": y_taylor}
    point_values.data = {"x": (x_spot.value, ), "y": (FUNC_1_0(x_spot.value), )}
    band_values.data = {"x": x[20:80], "y1": y_true[20:80], "y2": y_taylor[20:80]}
    error = integrate(y_true[20: 80], y_taylor[20:80], 0.1)
    error_box.text = "Ungefährer Fehler im Interval (-3, 3): " + str(round(error, 4))


curve_values = ColumnDataSource()
taylor_values = ColumnDataSource()
point_values = ColumnDataSource()
band_values = ColumnDataSource()

plot = figure(plot_height=HEIGHT, plot_width=WIDTH_PLOT, tools="", x_range=[-5, 5], y_range=[-2, 2])

plot.line(x="x", y="y", source=curve_values, color="black", line_width=2)
plot.line(x="x", y="y", source=taylor_values, color="orange")
plot.cross(x="x", y="y", source=point_values, color="orange", size=10)
band = Band(base="x", lower="y1", upper="y2", source=band_values)
plot.add_layout(band)

order = Slider(title="Ordnung des Taylorpolynoms", value=0, start=0, end=5, step=1)
x_spot = Slider(title="Entwicklungstelle x_0", value=1, start=-4, end=4, step = 0.1)

error_box = Div(width=200, height=100)

# Call the update routine first to populate the plot
update_data(order, x_spot, curve_values, taylor_values, point_values, band_values, error_box)

inputs = widgetbox(order, x_spot, error_box)

def update_slider(attr, old, new):
    update_data(order, x_spot, curve_values, taylor_values, point_values, band_values, error_box)

for slider in (order, x_spot):
    slider.on_change("value", update_slider)

curdoc().add_root(row(plot, inputs, width=WIDTH_TOTAL))
