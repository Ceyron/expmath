import numpy as np

from bokeh.driving import count
from bokeh.layouts import row, widgetbox, column
from bokeh.io import curdoc
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure

from bokeh.models.widgets import Slider, Div

"""
This file creates an interactive chart presenting the oscialltions of a one-
dimensional string

@author: felix
"""

HEIGHT = 400
WIDTH_PLOT = 600
WIDTH_TOTAL = 800


def calculate_solution(div_field, length, tension, density, first, second,
                       third):
    div_field.text = "u(t,x) ="
    if(first != 0.0):
        div_field.text += " {0} cos(1/{1}{2}/{3}t) sin(1/{4}x)".format(first, length, tension, density, length)
    if(second != 0.0):
        if(first != 0.0):
            div_field.text += " +"
        div_field.text += " {0} cos({1}t) sin({2}x)".format(second,2.,2.)
    if(third != 0.0):
        if(first != 0.0 or second != 0.0):
            div_field.text += " +"
        div_field.text += " {0} cos({1}t) sin({2}x)".format(third,3.,3.)


def compute(t, length, tension, density, first, second, third):
    x = np.linspace(0, (length*np.pi), 100)
    value = first * np.cos(np.pi**2/(length*np.pi)**2 * tension/density * t/10.) *\
            np.sin(np.pi / (length*np.pi) * x) +\
            second * np.cos(4*np.pi**2/(length*np.pi)**2 * tension/density * t/10.) *\
            np.sin(2*np.pi / (length*np.pi) * x) +\
            third * np.cos(9*np.pi**2/(length*np.pi)**2 * tension/density * t/10.) *\
            np.sin(3*np.pi / (length*np.pi) * x)
    return {"x": x, "y": value}


length = Slider(title="Länge der Saite (mal $\pi$)", value=1., start=0.5, step=0.5, end=2.)
tension = Slider(title="Vorspannung", value=1, start=0.1, step=0.1, end=2)
density = Slider(title="Liniendichte", value=1, start=0.1, step=0.1, end=2)
first = Slider(title="Erste Eigenschwingung", value=1, start=0, step=0.1, end=2)
second = Slider(title="Zweite Eigenschwingung", value=0., start=0., step=0.1, end=2.)
third = Slider(title="Dritte Eigenschwingung", value=0, start=0., step=0.1, end=2.)

source = ColumnDataSource()

plot = figure(x_range=[-1, 2*np.pi+1], y_range=[-2, 2], plot_height=HEIGHT,
              plot_width=WIDTH_PLOT, tools="")
plot.line(x="x", y="y", source=source, line_width=2)

field_solution = Div(width=WIDTH_TOTAL, height=100)

inputs = widgetbox(length, tension, density, first, second, third)


@count()
def update(t):
    source.data = compute(t, length.value, tension.value, density.value,
                          first.value, second.value, third.value)


def update_slider(attr, old, new):
    calculate_solution(field_solution, length.value, tension.value, density.value, first.value, second.value, third.value)


update_slider(0, 0, 0)

for slider in (length, tension, density, first, second, third):
    slider.on_change("value", update_slider)


curdoc().add_root(column(row(plot, inputs, width=WIDTH_TOTAL), field_solution, height=HEIGHT+100))  

curdoc().add_periodic_callback(update, 100)
