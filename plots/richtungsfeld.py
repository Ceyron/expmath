#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
import holoviews as hv

from bokeh.models.widgets import Panel, Tabs
from bokeh.layouts import row, widgetbox
from bokeh.io import curdoc
from bokeh.models import ColumnDataSource

from bokeh.models.widgets import Slider

hv.extension('bokeh')
HEIGHT = 400
WIDTH_PLOT = 600
WIDTH_TOTAL = 800

'''
FUNC... defines the explicit ordinary differential equation that is first
order in the form y'=FUNC(X, Y)
FUNC..._solution defines the solution to this equation in the form
y = FUNC(X, C) with the integral constant C

To add new fields, declare the ODE and its general solution. Then, add
the functions to the list below the definitions.
'''


def FUNC_1(X, Y):
    return 1/3 * Y


def FUNC_1_SOLUTION(X, x_initial, y_initial):
    return y_initial * np.exp(- 1/3 * x_initial) * np.exp(1/3 * X)


def FUNC_2(X, Y):
    return X


def FUNC_2_SOLUTION(X, x_initial, y_initial):
    return 1/2 * X**2 + y_initial - 1/2 * x_initial**2


def FUNC_3(X, Y):
    return X + Y


def FUNC_3_SOLUTION(X, x_initial, y_initial):
    return np.exp(-x_initial) * (y_initial + x_initial + 1) * np.exp(X) -\
        (X + 1)

# Collect all functions as a list of function pointers
functions = [FUNC_1, FUNC_2, FUNC_3]
solutions = [FUNC_1_SOLUTION, FUNC_2_SOLUTION, FUNC_3_SOLUTION]

x = np.linspace(-10, 10, 21)
y = np.linspace(-10, 10, 21)

# Create the underlying grid for the vector field
X, Y = np.meshgrid(x, y)

U = np.ones((21, 21))

plots = []

# Use the holoview library to generate a vector_field plot since this is not
# yet natively available for bokeh. The holoview render method then turns
# this into a bokeh figure
for func in functions:
    V = func(X, Y)
    mag = np.sqrt(U**2 + V**2)
    ang = np.pi/2 - np.arctan2(U/mag, V/mag)
    vector_field = hv.VectorField((X, Y, ang, 0.5*np.ones((21, 21))))
    vector_field.opts(magnitude='Magnitude')
    plots.append(hv.render(vector_field, backend="bokeh"))

value_cross = ColumnDataSource()
values = []
for plot in plots:
    plot.width = WIDTH_PLOT
    plot.height = HEIGHT
    plot.tools = []
    values.append(ColumnDataSource())

# The slider controlling the value of the solution function at a certain point
# This will fix all degress of freedom the general solution to this ODE will
# have
height = Slider(title="y Position des Anfangswertes", value=1, start=-5, end=5,
        step=0.05)
x_pos = Slider(title="x Position des Anfangswertes", value=0., start=-5, end=5,
        step=0.05)

# Defining callback handlers
def update_slider(attr, old, new):
    x_plot = np.linspace(-10, 10, 100)
    for i, solution in enumerate(solutions):
        y_plot = solution(x_plot, x_pos.value, height.value)
        values[i].data = {"x": x_plot, "y": y_plot}
    value_cross.data = {"x": np.array([x_pos.value, ]), "y":
            np.array([height.value, ])}


# Initialize the data dictionaries by calling the update handler
update_slider(0, 0, 0)

tabs = []
names = ["Erstes Feld", "Zweites Feld", "Drittes Feld", "Viertes Feld",
        "Fünftes Feld"]
for i, plot in enumerate(plots):
    plot.line("x", "y", source=values[i], line_width=3)
    plot.cross("x", "y", source=value_cross, color="orange", line_width=12)
    tabs.append(Panel(child=plot, title=names[i]))


# Here, we have to use tabs. The user won't be able to choose the ODE in the
# right column. This might be inconsistent but is necessary since bokeh does
# not support native vector field plots yet
tabs = Tabs(tabs=tabs, width=WIDTH_PLOT)

# Connect the widgets with their respective callbacks
for slider in (height, x_pos):
    slider.on_change("value", update_slider)

# Assemble the plot and create the html
inputs = widgetbox(height, x_pos)
curdoc().add_root(row(tabs, inputs))
