import numpy as np

from bokeh.io import curdoc
from bokeh.layouts import row, widgetbox
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import Slider, RadioButtonGroup
from bokeh.plotting import figure

# Geometry constants of the plot
HEIGHT = 400
WIDTH_PLOT = 600
WIDTH_TOTAL = 800

# The initial viewport the user starts in
LEFT = -5
RIGHT = 5
BOTTOM = -3
TOP = 3

SIZE_GLYPHS = 15
SECANT_LINE_WIDTH = 3
FUNCTION_LINE_WIDTH = 2

X_DIM = RIGHT - LEFT
Y_DIM = TOP - BOTTOM

# The additional length of the secants behind the points that are actually set
# by the sliders
ADDITIONAL_LENGTH = 0.3

# Small value to avoid division by zero
EPSILON = 0.0001

def FUNC_1(x):
    return np.exp(-(x - 1)**2)
def FUNC_2(x):
    return np.abs(x)
def FUNC_3(x):
    return np.piecewise(x, [x < 1, x >= 1],
            [lambda ele: 1/3*ele**2, lambda ele: -ele + 4/3])

functions = [FUNC_1, FUNC_2, FUNC_3]


def calculate_new_function_value_pairs(function_active):
    x = np.linspace(LEFT, RIGHT, 200)
    y = functions[function_active](x)
    return x, y
    
def calculate_new_secant_value_pairs(function_active, point_location, spacing):
    x_positions = np.array([point_location - (spacing + EPSILON),
            point_location, point_location + (spacing + EPSILON)])

    y_positions = functions[function_active](x_positions)

    # The two parameters defining a straight line
    slope_left_secant = (y_positions[1] - y_positions[0]) / \
            (x_positions[1] - x_positions[0] + EPSILON)
    slope_right_secant = (y_positions[2] - y_positions[1]) / \
            (x_positions[2] - x_positions[1] + EPSILON)

    offset_left_secant = y_positions[0] - slope_left_secant * x_positions[0] 
    offset_right_secant = y_positions[1] - slope_right_secant * x_positions[1] 

    # Manipulate the x locations so that the secant lines are slightly longer
    # than the points indicating their ends
    left_length_offset = ADDITIONAL_LENGTH *\
            np.cos(np.arctan(slope_left_secant))
    x_left_secant = np.array([
            x_positions[0] - left_length_offset,
            x_positions[1] + left_length_offset])
    
    right_length_offset = ADDITIONAL_LENGTH *\
            np.cos(np.arctan(slope_right_secant))
    x_right_secant = np.array([
            x_positions[1] - right_length_offset,
            x_positions[2] +  right_length_offset])

    # Construct the calue pairs based on the two line parameters
    y_left_secant = slope_left_secant * x_left_secant + offset_left_secant
    y_right_secant = slope_right_secant * x_right_secant + offset_right_secant

    xs = [x_left_secant, x_right_secant]
    ys = [y_left_secant, y_right_secant]

    return xs, ys

def calculate_new_dot_positions(function_active, point_location, spacing):
    left_x = point_location - spacing
    middle_x = point_location
    right_x = point_location + spacing

    left_y = functions[function_selector.active](left_x)
    middle_y = functions[function_selector.active](middle_x)
    right_y = functions[function_selector.active](right_x)

    x = [left_x, middle_x, right_x, left_x, middle_x, right_x]
    y = [left_y, middle_y, right_y, BOTTOM, BOTTOM, BOTTOM]

    return x, y


# ColumnDataSource abstract the sending of new value pairs to the client
curve_values = ColumnDataSource()
secant_line_values = ColumnDataSource()
dot_values = ColumnDataSource()


plot = figure(plot_height=HEIGHT, plot_width=WIDTH_PLOT,
              x_range=[-5, 5], y_range=[-2, 2])
plot.toolbar.active_drag = None

plot.line(x="x", y="y", source=curve_values, color="blue",
        line_width=FUNCTION_LINE_WIDTH)
plot.multi_line(xs="xs", ys="ys", source=secant_line_values, color="color",
        line_width="line_width")
plot.cross(x="x", y="y", source=dot_values, color="black", size=SIZE_GLYPHS)


function_selector = RadioButtonGroup(
        labels=["Funktion 1", "Funktion 2", "Funktion 3"], active=0)
point_slider = Slider(title="Betrachtete Stelle x_0", value=0,
        start=-4, end=4, step=0.1)
spacing_slider = Slider(title="Abstand h von der Stelle x_0", value=0.5, start=0.001,
        end=2, step=0.05)


# Define the callbacks
def update_slider(attr, old, new):
    xs, ys = calculate_new_secant_value_pairs(function_selector.active,
            point_slider.value, spacing_slider.value)
    secant_line_values.data = {
            "xs": xs,
            "ys": ys,
            "color" : ["orange", "purple"],
            "line_width": [SECANT_LINE_WIDTH, SECANT_LINE_WIDTH],
            }

    x, y = calculate_new_dot_positions(function_selector.active,
            point_slider.value, spacing_slider.value)
    dot_values.data = {"x": x, "y": y}


def update_button(source):
    x, y = calculate_new_function_value_pairs(function_selector.active)
    curve_values.data = {"x": x, "y": y}
    # Whenever the function is changed, the secants also have to be calculated
    # again
    update_slider(0, 0, 0)

# Use the callback in advance to populate the plot
update_button(0)

# Connect the widgets with their respective callbacks
for slider in (point_slider, spacing_slider):
    slider.on_change("value", update_slider)

function_selector.on_click(update_button)

# Assemble the plot and create the html
inputs = widgetbox(function_selector, point_slider, spacing_slider)
curdoc().add_root(row(plot, inputs, width=WIDTH_TOTAL))
