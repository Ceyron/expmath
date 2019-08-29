import numpy as np

from bokeh.layouts import Row, WidgetBox, Column
from bokeh.io import curdoc
from bokeh.models import ColumnDataSource 
from bokeh.plotting import Figure

from bokeh.models.widgets import Slider, Div, Toggle

from extensions.Latex import LatexLabel


"""
This file creates an interactive chart presenting the oscialltions of a one-
dimensional string

@author: felix
"""

# Geometry constants to the plot
HEIGHT = 400
WIDTH_PLOT = 600
WIDTH_TOTAL = 800

# Thickness of the line that is oscillating
LINE_WIDTH = 2

# How many points are used to discretize the curve(i.e., how many lines+1 are
# used)
NUM_POINTS = 100

# Concatenates the string of latex syntax that will be rendered on the client
def create_latex(length, tension, density, first, second, third):
    text = "u(t,x) ="
    if(first != 0.0):
        text += " " +\
        str(round(first, 1)) +\
        " \cdot \cos \left( \\frac{1}{" +\
        str(round(length, 1)) +\
        "} \sqrt{\\frac{" +\
        str(round(tension, 1)) +\
        "}{" +\
        str(round(density, 1)) +\
        "}} t \\right)" +\
        " \cdot \sin \left( \\frac{1}{" +\
        str(round(length, 1)) +\
        "} x \\right)"

    if(second != 0.0):
        if(first != 0.0):
            # Not necessary if the second Eigenfunction is the first to appear
            text += " +"

        text += " " +\
        str(round(second, 1)) +\
        " \cdot \cos \left( \\frac{2}{" +\
        str(round(length, 1)) +\
        "} \sqrt{\\frac{" +\
        str(round(tension, 1)) +\
        "}{" +\
        str(round(density, 1)) +\
        "}} t \\right)" +\
        " \cdot \sin \left( \\frac{2}{" +\
        str(round(length, 1)) +\
        "} x \\right)"


    if(third != 0.0):
        if(first != 0.0 or second != 0.0):
            # Not necessary if the third Eigenfunction is the first to appear
            text += " +"

        text += " " +\
        str(round(third, 1)) +\
        " \cdot \cos \left( \\frac{3}{" +\
        str(round(length, 1)) +\
        "} \sqrt{\\frac{" +\
        str(round(tension, 1)) +\
        "}{" + str(round(density, 1)) +\
        "}} t \\right)" +\
        " \cdot \sin \left( \\frac{3}{" +\
        str(round(length, 1)) +\
        "} x \\right)"

    return text


def calculate_new_value_pairs(t, length, tension, density, first, second, third):
    x = np.linspace(0, (length*np.pi), NUM_POINTS)
    # We use a tenth of the time to slow down the oscillatio, making it more pleasing
    # for the user and reducing the amount of packages needed to be sent
    y = first * np.cos(1/length * np.sqrt(tension/density) * t) *\
            np.sin(1/(length) * x) +\
            second * np.cos(2/length * np.sqrt(tension/density) * t) *\
            np.sin(2/length * x) +\
            third * np.cos(3/length * np.sqrt(tension/density) * t) *\
            np.sin(3/length * x)
    return x, y


# ColumnDataSource abstracts the sending of new value pairs to the client
source = ColumnDataSource()

plot = Figure(x_range=[-1, 2*np.pi+1], y_range=[-2, 2], plot_height=HEIGHT,
              plot_width=WIDTH_PLOT)
plot.toolbar.active_drag = None  # Helpful for touchscreen users
# Indicate the x-axis
plot.line(x=[-100, 100], y=[0, 0], color="black")

plot.line(x="x", y="y", source=source, line_width=LINE_WIDTH)

length = Slider(title="Länge der Saite (mal $\pi$)", value=1., start=0.5,
        step=0.5, end=2.)
tension = Slider(title="Vorspannung", value=1, start=0.1, step=0.1, end=2)
density = Slider(title="Liniendichte", value=1, start=0.1, step=0.1, end=2)
first = Slider(title="Erste Eigenschwingung", value=1, start=0, step=0.1, end=2)
second = Slider(title="Zweite Eigenschwingung", value=0., start=0., step=0.1,
        end=2.)
third = Slider(title="Dritte Eigenschwingung", value=0, start=0., step=0.1,
        end=2.)

# Related to the time-dependent behavior
animation_toggle = Toggle(label="Animieren")
time = Slider(title="Zeit t", start=0, end=10, step=0.1, value=0)

placeholder = Div(width=WIDTH_TOTAL, height=100)

field_solution = LatexLabel(text="",
                   x=0, y=-40, x_units='screen', y_units='screen',
                   render_mode='css', text_font_size='10pt',
                   background_fill_alpha=0)

plot.add_layout(field_solution)


# Callback handlers
def update(attr, old, new):
    x, y = calculate_new_value_pairs(time.value, length.value, tension.value,
            density.value, first.value, second.value, third.value)
    source.data = {"x": x, "y": y}


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

def update_parameter_slider(attr, old, new):
    text = create_latex(length.value, tension.value, density.value, first.value,
            second.value, third.value)
    field_solution.text = text
    time.value = time.start
    duration_of_full_cycle = 2*np.pi*length.value *\
            np.sqrt(density.value/tension.value)
    time.end = duration_of_full_cycle
    update(0, 0, 0)

# Call callback in advance to populate the plot
update_parameter_slider(0, 0, 0)


# Connect widgets with their respective callbacks
for slider in (length, tension, density, first, second, third):
    slider.on_change("value", update_parameter_slider)

time.on_change("value", update)

animation_toggle.on_click(animation_callback)

# Assemble plot and create html
inputs = WidgetBox(length, tension, density, first, second, third,
        animation_toggle, time)
curdoc().add_root(Column(Row(plot, inputs, width=WIDTH_TOTAL), placeholder,
        height=HEIGHT+100))  
