import numpy as np

from bokeh.io import curdoc
from bokeh.layouts import Row, WidgetBox
from bokeh.models import ColumnDataSource, Band
from bokeh.models.widgets import Slider, RadioButtonGroup
from bokeh.plotting import Figure

"""
This plot lets the user visually explore the Epsilon-Delta-criterium on the
continuity property of functions.

Therefore, a function is selected and the parameters of the criterium are
adjusted by sliders. The user can capture the idea that for the con-continuous
parts of the functions the rectangle spanned by epsilon and delta can not be
made infinitely small which contradicts the requirements of a continous point.
"""

# Geomtry constants
HEIGHT = 400
WIDTH_PLOT = 600
WIDTH_TOTAL = 800

# Thickness of the function line
LINE_WIDTH = 2

# Setup parameters for the tunnel sliders
MIN_TUNNEL_WIDTH = 0.05
MAX_TUNNEL_WIDTH = 2
STEP_TUNNEL_WIDTH = 0.05
INITIAL_TUNNEL_WIDTH = 0.3

# The position slider shares many setup parameters with the tunnel sliders but
# has a finer stepping
STEP_POSITION = 0.01

# The initial viewport in which the user starts, i.e., the plain that is visible
# upfront
VIEWPORT_X = [-5.5, 5.5]
VIEWPORT_Y = [-4.5, 4.5]

# Left-most and right-most points to still have value pairs - define the
# interval on which the function and the horizontal tunnel are drawn
X_LEFT = VIEWPORT_X[0] - 0.5
X_RIGHT = VIEWPORT_X[1] + 0.5

# Bottom-most and top-most point for drawing the vertical tunnel
Y_BOTTOM = VIEWPORT_Y[0] - 0.5
Y_TOP = VIEWPORT_Y[1] + 0.5


# Quadratic polynomial
def FUNC_1(x):
    y = 0.5 * x**2
    xs = [x, ]
    ys = [y, ]
    return xs, ys


# Absolute function
def FUNC_2(x):
    y = np.abs(x)
    xs = [x, ]
    ys = [y, ]
    return xs, ys


# Piecewise linear with jump
def FUNC_3(x):
    # Catch all 0-dimensional scalars
    if isinstance(x, (int, float)):
        if x < 1:
            y = x + 0.5
        else:
            y = 2.5*x

        xs = [x, ]
        ys = [y, ]
        return xs, ys
    else:
        xs = np.split(x, [np.where(x<1)[0][-1], ])
        # Make sure that the line properly jumps without creating
        # a undefined interval
        xs[0][-1] = 1
        xs[1][0] = 1

        y_left = xs[0] + 0.5
        y_right = 2.5 * xs[1]
        
        ys = [y_left, y_right]
        return xs, ys


functions = [FUNC_1, FUNC_2, FUNC_3, ]
function_names = ["Funktion 1", "Funktion 2", "Funktion 3", ]


def calculate_new_value_pairs(function_active):
    x = np.linspace(X_LEFT, X_RIGHT, 100)
    xs, ys = functions[function_active](x)

    return xs, ys


def update_horizontal_tunnel(function_active, position, epsilon):
    xs, ys = functions[function_active](position)
    y_position = ys[0]
    x = [X_LEFT, X_RIGHT]
    y_lower = [y_position - epsilon, y_position - epsilon]
    y_upper = [y_position + epsilon, y_position + epsilon]
    xs = [x, x]
    ys = [y_lower, y_upper]

    return xs, ys, x, y_lower, y_upper


def update_vertical_tunnel(function_active, position, delta):
    x = [position - delta, position + delta]
    y = [Y_BOTTOM, Y_TOP]
    y_lower = [Y_BOTTOM, Y_BOTTOM]
    y_upper = [Y_TOP, Y_TOP]
    x_left_bound = [x[0], x[0]]
    x_right_bound = [x[1], x[1]]
    xs = [x_left_bound, x_right_bound]
    ys = [y, y]

    return xs, ys, x, y_lower, y_upper


# ColumnDataSource abstracts the assynchronous sending of new value pairs to the
# client
function_value_pairs = ColumnDataSource()
horizontal_tunnel = ColumnDataSource()
horizontal_tunnel_bounds = ColumnDataSource()
vertical_tunnel = ColumnDataSource()
vertical_tunnel_bounds = ColumnDataSource()

plot = Figure(plot_height=HEIGHT, plot_width=WIDTH_PLOT, x_range=VIEWPORT_X,
        y_range=VIEWPORT_Y)
plot.toolbar.active_drag = None  # For touchscreen users helpful
# Indicate the x-axis and the y-axis
plot.line(x=[X_LEFT, X_RIGHT], y=[0, 0], color="black")
plot.line(x=[0, 0], y=[Y_BOTTOM, Y_TOP], color="black")

# Use multi-line instead of single line to get proper jumps
plot.multi_line(xs="xs", ys="ys", source=function_value_pairs, color="blue",
        line_width=LINE_WIDTH)

horizontal_band = Band(base="base", lower="y_lower", upper="y_upper",
        source=horizontal_tunnel, fill_color="orange", fill_alpha=0.4)
vertical_band = Band(base="base", lower="y_lower", upper="y_upper",
        source=vertical_tunnel, fill_color="green", fill_alpha=0.4)
plot.add_layout(horizontal_band)
plot.add_layout(vertical_band)

# The bounding lines for the tunnel bands
plot.multi_line(xs="xs", ys="ys", color="black",
        source=horizontal_tunnel_bounds)
plot.multi_line(xs="xs", ys="ys", color="black",
        source=vertical_tunnel_bounds)

function_selector = RadioButtonGroup(labels=function_names, active=0)

epsilon_slider = Slider(title="Epsilon", start=MIN_TUNNEL_WIDTH,
        end=MAX_TUNNEL_WIDTH, step=STEP_TUNNEL_WIDTH,
        value=INITIAL_TUNNEL_WIDTH)
delta_slider = Slider(title="Delta", start=MIN_TUNNEL_WIDTH,
        end=MAX_TUNNEL_WIDTH, step=STEP_TUNNEL_WIDTH,
        value=INITIAL_TUNNEL_WIDTH)
position_slider = Slider(title="Betrachteter Punkt z", start=VIEWPORT_X[0] + 1,
        end= VIEWPORT_X[1] - 1, step = STEP_POSITION, value = 1)


def update_epsilon_slider(attr, old, new):
    xs, ys, base, y_lower, y_upper = update_horizontal_tunnel(
            function_selector.active, position_slider.value,
            epsilon_slider.value)

    horizontal_tunnel.data = {"base": base, "y_lower": y_lower,
            "y_upper": y_upper}
    horizontal_tunnel_bounds.data = {"xs": xs, "ys": ys}


def update_delta_slider(attr, old, new):
    xs, ys, base, y_lower, y_upper = update_vertical_tunnel(
            function_selector.active, position_slider.value,
            delta_slider.value)

    vertical_tunnel.data = {"base": base, "y_lower": y_lower,
            "y_upper": y_upper}
    vertical_tunnel_bounds.data = {"xs": xs, "ys": ys}


def update_position_slider(attr, old, new):
    update_epsilon_slider(0, 0, 0)
    update_delta_slider(0, 0, 0)

def update_selection(source):
    xs, ys = calculate_new_value_pairs(function_selector.active)
    function_value_pairs.data = {"xs": xs, "ys": ys}

    update_position_slider(0, 0, 0)


# Call the callback in advance to populate the plot
update_selection(0)

# Link the callbacks with the corresponding widgets
epsilon_slider.on_change("value", update_epsilon_slider)
delta_slider.on_change("value", update_delta_slider)
position_slider.on_change("value", update_position_slider)
function_selector.on_click(update_selection)

# Assemble the html page for the plot
inputs = WidgetBox(function_selector, position_slider, epsilon_slider,
        delta_slider)
curdoc().add_root(Row(plot, inputs, width=WIDTH_TOTAL))
