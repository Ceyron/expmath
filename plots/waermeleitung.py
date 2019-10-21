# -*- coding: utf-8 -*-
import numpy as np

from bokeh.layouts import Row, WidgetBox
from bokeh.io import curdoc
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import Slider, RadioButtonGroup, Toggle
from bokeh.plotting import Figure

"""
This plot presents the transient behaviour of the analytical solution to a
simple heat transfer problem in 1D with isotropic and homogeneous temperature
conductivity properties of the underlying material.
The user can set the parameters as well as initial and boundary conditions. We
only consider the more easy Dirichlet boundary conditions, i.e., fixed
temperature (but possibly non-zero) at both ends.

A toggle allows to activate advanced options so that the first user is not
distracted by the functionality.
"""

# Define constants for the plot. These are in accordance with all the other
# plots
HEIGHT = 400
WIDTH_PLOT = 600
WIDTH_TOTAL = 800

# The thickness of the line of the solution curve u(t,x)
LINE_WIDTH = 2

# The size of the dots marking the temperatures at the end of the bar (obviously
# has to correspond with the boundary conditions)
DOT_SIZE = 10


def update_data(length_factor, conductivity, first, second, third, left, right,
        time):
    """
    Callback to update the analytical solution. It will therefore superpose the
    contribution of each eigenfunction (we consider the first three). A
    superposition with the trivial solution is necessary when the temperature at
    the bar ends is unequal to zero.
    """
    x = np.linspace(0, length_factor*np.pi, 50)
    # Contribution of the first Eigenfunction
    y_first = first * np.exp(-conductivity * time/ length_factor**2) *\
            np.sin(x / length_factor)
    # Contribution of the second Eigenfunction
    y_second = second * np.exp(-4 * conductivity * time / length_factor**2) *\
            np.sin(2 * x / length_factor)
    # Contribution of the thirs Eigenfunction
    y_third = third * np.exp(-9 * conductivity * time / length_factor**2) *\
            np.sin(3 * x / length_factor)
    y = y_first + y_second + y_third

    # Superposition with the trivial solution (necessary for non-homogeneous
    # boundary conditions)
    y_trivial_endpoints = [0, 0]
    if (left != 0 or right != 0):
        y_trivial = (right - left)/(length_factor * np.pi) * x + left
        y += y_trivial
        y_trivial_endpoints = [y_trivial[0], y_trivial[49]]

    return (x, y, y_trivial_endpoints)


# Data source for the analytical solution. Whenever its data is changed, it will
# send the new information to the client to display it
data_source = ColumnDataSource(data={'x': [], 'y': []})
# Line for the trivial solution, especially helpful if boundary conditions are
# not homogeneous
trivial_line_source = ColumnDataSource(data={'x': [], 'y': []})

plot = Figure(plot_height=HEIGHT, plot_width=WIDTH_PLOT, x_range=[-1, 2*np.pi+1],
        y_range=[-2, 2], tools="")
plot.xaxis.axis_label = "Position x"
plot.yaxis.axis_label = "Temperatur u(t, x)"

# Analytical solution
plot.line(x="x", y="y", source=data_source, line_width=LINE_WIDTH, color="blue")
# Trivial solution
plot.line(x="x", y="y", source=trivial_line_source, color="black",
        line_dash="dashed")
# Dots marking the boundary conditions
plot.circle(x="x", y="y", source=trivial_line_source, color="black",
        size=DOT_SIZE)
# Line, indicating zero temperature, i.e., the x-axis
plot.line(x=[-5, 15], y=[0, 0], color="black")

# Define all widgets 
# The length of the bar
length = Slider(title="Länge des Stabes (mal pi)", value=1, start=0.5, end=2,
        step=0.5)
# Temperature conductivity, how fast heat is transported through the material.
# Here, we assume a linear isotropic homogoneous material in 1 dimension
conductivity = Slider(title="Temperaturleifähigkeit", value=1, start=0.1, end=2,
        step=0.1)
# The coefficient for the first Eigenfunction, determined by the initial
# condition
first = Slider(title="Auslenkung der ersten Eigenform", value=1, start=-2, end=2, step=0.1)
# Enables the visibility for advanced widgets that are collapsed for a better
# readability of the plot
advanced_toggle = Toggle(label="Mehr Optionen")
# The coefficient for the second Eigenfunction, determined by the initial
# condition
second = Slider(title="Auslenkung der zweiten Eigenform", value=0, start=-2, end=2, step=0.1,
        visible=False)
# The coefficient for the third Eigenfunction, determined by the initial
# condition
third = Slider(title="Auslenkung der dritten Eigenform", value=0, start=-2, end=2, step=0.1,
        visible=False)
# The temperature on the left and right vertex, determined by the boundary
# condition to the problem. If one of them is unequal to zero then the general
# solution is superposed with a linear function connecting both points
left = Slider(title="Temperatur am linken Rand u(t, x=0)", value=0, start=-2,
        end=2, step=0.1, visible=False)
right = Slider(title="Temperatur am rechten Rand u(t, x=L)", value=0, start=-2,
        end=2, step=0.1, visible=False)
# Toggle that adds a periodic callback function, so that the plot seems to be
# moving
animation_toggle = Toggle(label="Animieren")
# Lets the user adjust the time in the transient simulation on its own
time = Slider(title="Zeit", value=0, start=0, end=10, step=0.1)


def toggle_callback(source):
    """
    Enables the 'more advanced' options so that the user is not distracted by
    the functionality in the first place
    """
    advanced_toggle.visible = False
    second.visible = True
    third.visible = True
    left.visible = True
    right.visible = True

def animate():
    if time.value >= time.end:
        time.value = time.start
    else:
        time.value += time.step

callback_id = 0
def animation_callback(source):
    """
    Function adds a callback to the function which animates it. The callback_id
    is the id of the process the bokeh server spawns. It is necessary to
    remove it later on.
    """
    global callback_id
    if animation_toggle.active == 1:
        callback_id = curdoc().add_periodic_callback(animate, 100)
    else:
        curdoc().remove_periodic_callback(callback_id)

def slider_callback(attr, old, new):
    """
    Callback associated with a change in every slider. It calls to calculate the
    new value pairs and then outfits the ColumnDataSources with this
    information.
    """
    x, y, y_trivial = update_data(length.value, conductivity.value, first.value,
            second.value, third.value, left.value, right.value, time.value)
    
    data_source.data = {'x': x, 'y': y}
    trivial_line_source.data = {'x': [0, length.value * np.pi], 'y': y_trivial}

# Populate the plot by calling the callback manually
slider_callback(0,0,0)

# Connect the widgets with their respective callbacks
advanced_toggle.on_click(toggle_callback)

animation_toggle.on_click(animation_callback)

for slider in (length, conductivity, first, second, third, left, right, time):
    slider.on_change("value", slider_callback)

# Assemble the plot
inputs = WidgetBox(length, conductivity, first, advanced_toggle, second, third,
        left, right, animation_toggle, time)

curdoc().add_root(Row(plot, inputs, width=WIDTH_TOTAL))
