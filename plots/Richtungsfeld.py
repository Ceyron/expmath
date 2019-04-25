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
WIDTH_PLOT = 800
WIDTH_TOTAL = 1200

'''
FUNC... defines the explicit ordinary differential equation that is first
order in the form y'=FUNC(X, Y)
FUNC..._solution defines the solution to this equation in the form
y = FUNC(X, C) with the integral constant C
'''


def FUNC_1(X, Y):
    return 1/3 * Y


def FUNC_1_SOLUTION(X, C):
    return C*np.exp(1/3*X)


def FUNC_2(X, Y):
    return X


def FUNC_2_SOLUTION(X, C):
    return 1/2 * X**2 + C


def FUNC_3(X, Y):
    return X + Y


def FUNC_3_SOLUTION(X, C):
    return (C+1)*np.exp(X) - (X+np.ones(X.shape))


functions = [FUNC_1, FUNC_2, FUNC_3]
solutions = [FUNC_1_SOLUTION, FUNC_2_SOLUTION, FUNC_3_SOLUTION]

x = np.linspace(-10, 10, 21)
y = np.linspace(-10, 10, 21)

# Create the underlying grid for the vector field
X, Y = np.meshgrid(x, y)

U = np.ones((21, 21))

plots = []

# Use the holoview library to generate a vector_field plot since this is not
# yet natively available fpr bokeh. The holoview render method then turns
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

# The slider controlling the value of the solution function at x=0
height = Slider(title="y(0)=", value=1, start=-5, end=5, step=0.05)


def update_slider(attr, old, new):
    x_plot = np.linspace(-10, 10, 100)
    for i in range(3):
        y_plot = solutions[i](x_plot, height.value)
        values[i].data = {"x": x_plot, "y": y_plot}
    value_cross.data = {"x": np.array([0., ]), "y": np.array([height.value, ])}


# Initialize the data dictionaries by calling the update handler
update_slider(0, 0, 0)

tabs = []
names = ["Erstes Feld", "Zweites Feld", "Drittes Feld"]
for i in range(3):
    plots[i].line("x", "y", source=values[i], line_width=3)
    plots[i].cross("x", "y", source=value_cross, color="orange", line_width=7)
    tabs.append(Panel(child=plots[i], title=names[i]))


tabs = Tabs(tabs=tabs, width=WIDTH_PLOT)
sliders = widgetbox(height)

for slider in (height, ):
    slider.on_change("value", update_slider)

curdoc().add_root(row(tabs, sliders))
