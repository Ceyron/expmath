import numpy as np

from bokeh.io import curdoc
from bokeh.layouts import row, widgetbox, column
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import Slider, RadioButtonGroup
from bokeh.plotting import figure

'''
This function updates the dynamically ColumnDataSources that are send via the
WebSocket connection. Based on the value of the slider phase and the currently
selected trigonmetric function the values of the triangle within the unit
circle, the relevant straight line and the values for plotting the function
itself are populated.
'''

# Geometry constants of the plot
HEIGHT = 270
WIDTH_LEFT = 300
WIDTH_RIGHT = 600

# The size of the dot located on the unit circle representing the angle as the
# arc length
DOT_RADIUS = 0.08

# A list of function pointers corresponding to the selection available by the
# RadioButtonGroup
TRIG_FUNCTIONS = [np.sin, np.cos, np.tan]

# A list of dictionaries for the relevant line which length represents the value
# of the trigonometric function at the current phase angle
def HIGHLIGHT_LINE_SINE(phase):
    x = [np.cos(phase), np.cos(phase)]
    y = [0, np.sin(phase)]
    return x, y

def HIGHLIGHT_LINE_COSINE(phase):
    x = [0, np.cos(phase)]
    y = [0, 0]
    return x, y

def HIGHLIGHT_LINE_TANGENT(phase):
    x = [1, 1]
    y = [0, min(np.tan(phase), 100.)]
    return x, y

HIGHLIGHT_LINES = [HIGHLIGHT_LINE_SINE, HIGHLIGHT_LINE_COSINE,
        HIGHLIGHT_LINE_TANGENT]


def calculate_new_function_value_pairs(trig_active, phase):
    x = np.linspace(0, phase, 100)
    y = TRIG_FUNCTIONS[trig_active](x)

    return x, y

def calculate_triangle_values_on_unit_circle(trig_active, phase):
    x = [np.cos(phase), 0, np.cos(phase), np.cos(phase)]
    y = [np.sin(phase), 0, 0, np.sin(phase)]
    radius = [DOT_RADIUS, 0, 0, 0]

    if trig_active == 2:  # Tangent is selected
        x.append(1)
        y.append(np.tan(phase))
        radius.append(0)

    return x, y, radius

def calculate_active_value_highlight_line(trig_active, phase):
    return HIGHLIGHT_LINES[trig_active](phase)


# ColumnDataSource abstract the sending of new value pairs to the client
trig_values = ColumnDataSource()
triangle_values = ColumnDataSource()
active_values = ColumnDataSource()

plot_left = figure(plot_width=WIDTH_LEFT, plot_height=HEIGHT, x_range=[-1.5, 1.5],
        y_range=[-1.5, 1.5])
plot_left.toolbar.active_drag = None
plot_right = figure(plot_width=WIDTH_RIGHT, plot_height=HEIGHT, x_range=[0, 13],
        y_range=[-1.5, 1.5])
plot_right.toolbar.active_drag = None

function_selector = RadioButtonGroup(labels=["Sinus", "Kosinus", "Tangens"],
        active=0)
phase_slider = Slider(title="Argument der trigonometrischen Funktion (mal pi)", start=0,
        end=4, step=0.05, value=0.25)

# Draw circle once in advance 
plot_left.circle(x=0, y=0, radius=1, color="black", line_width=2,
        fill_color=None)

plot_left.line(x="x", y="y", color="black", source=triangle_values)
plot_left.line(x="x", y="y", color="blue", source=active_values, line_width=2)
plot_left.circle(x="x", y="y", color="black", source=triangle_values,
        radius="radius")

plot_right.line(x="x", y="y", color="blue", source=trig_values, line_width=2)

# Define the callbacks
def update_slider(attr, old, new):
    x, y = calculate_new_function_value_pairs(function_selector.active,
            phase_slider.value*np.pi)
    trig_values.data = {"x": x, "y": y}

    x_triangle, y_triangle, radius = calculate_triangle_values_on_unit_circle(
            function_selector.active, phase_slider.value*np.pi)
    triangle_values.data = {"x": x_triangle, "y": y_triangle,
            "radius": radius}

    x_highlight, y_highlight = calculate_active_value_highlight_line(
            function_selector.active, phase_slider.value*np.pi)
    active_values.data = {"x": x_highlight, "y": y_highlight}


def update_button(source):
    update_slider(0, 0, 0)


# Use callback in advance to populate the plot
update_slider(0, 0, 0)

# Connect widgets with their respective callbacks
phase_slider.on_change("value", update_slider)
function_selector.on_click(update_button)

# Assemble the plot and create the html
curdoc().add_root(column(row(plot_left, plot_right), function_selector,
        phase_slider))
