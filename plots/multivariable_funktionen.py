import numpy as np

from bokeh.driving import count
from bokeh.io import curdoc
from bokeh.layouts import row, widgetbox
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import Slider, RadioButtonGroup, Div

from extensions.surface3d import Surface3d

def FUNC_1(X, Y):
    return X
def FUNC_2(X, Y):
    return X + Y
def FUNC_3(X, Y):
    return x**2 + Y**2

# Collecting all functions in a list of function pointers
functions = [FUNC_1, FUNC_2, FUNC_3]

x = np.linspace(-5, 5, 20)
y = np.linspace(-5, 5, 20)
X, Y = np.meshgrid(x, y)
def update_data(function_selector, surface_source):
    Z = functions[function_selector.active](X, Y)
    surface_source.data = {"X": X, "Y": Y, "Z": Z}


surface_source = ColumnDataSource()

surface = Surface3d(x="X", y="Y", z="Z", data_source=surface_source)

# The employed 3d wrapper function seems to overlay the dropdown menus, there
# incorporate a simple div as spacing over which the plotting engine can be
# rendered
spacing = Div(text="", width=5, height=600)

function_selector = RadioButtonGroup(labels=["Funktion 1", "Funktion 2",
        "Funktion 3"], active=0)

inputs = widgetbox(function_selector)

#update_data(function_selector, source)

def update_button(source):
    update_data(function_selector, surface_source)

update_button(0)

for button in (function_selector, ):
    button.on_click(update_button)

curdoc().add_root(row(spacing, surface, inputs))
