# TODO to have the tangent lines always appear with the same length, one also
# has to consider the distortian between x-axis and y-axis, as well as
# distortion when they are rendered within the HEIGHT and WIDTH of the plot
import numpy as np

from bokeh.io import curdoc
from bokeh.layouts import row, widgetbox, column
from bokeh.models import ColumnDataSource, Band
from bokeh.models.widgets import Slider, RadioButtonGroup
from bokeh.plotting import figure

# Geometry Constants of the plot
HEIGHT=400
WIDTH_MIDDLE_PLOT=300
WIDTH_OUTER_PLOTS=250

# The initial viewport the user starts, also used for setting the intervals the
# functions are drawn in
X_LEFT = -3
X_RIGHT = 3
Y_BOTTOM = -4
Y_TOP = 4

# Number of points used to discretize the value pairs interval
NUM_OF_POINTS = 50

FUNCTION_LINE_WIDTH = 2
TANGENT_LINE_WIDTH = 3
CROSS_SIZE = 15
CROSS_LINE_WIDTH = 3

# The curve length of the tangent used to visualize the slope at a the selected
# point of the regular function
TANGENT_LENGTH = 0.5


def FUNC_1(x):
    return x
def FUNC_1_derivative(x):
    return np.ones(x.shape) 
def FUNC_1_integral(x):
    return 1/2*x**2

def FUNC_2(x):
    return np.sin(2*x)
def FUNC_2_derivative(x):
    return 2*np.cos(2*x)
def FUNC_2_integral(x):
    return -1/2*np.sin(2*x) 

def FUNC_3(x):
    return np.exp(x)
def FUNC_3_derivative(x):
    return np.exp(x)
def FUNC_3_integral(x):
    return np.exp(x)

# This list collects the function pointers to the mathematical functions that
# are displayed in the plots
functions = [
        [FUNC_1_derivative, FUNC_1, FUNC_1_integral],
        [FUNC_2_derivative, FUNC_2, FUNC_2_integral],
        [FUNC_3_derivative, FUNC_3, FUNC_3_integral]
        ]

names = ["Linear Funktion", "Trigonometrische Funktion", "Exponentialfunktion"]

# Given the coordinates of one point and the slope at this, model the tangent line to this point and use it to return the y-coordinate for a given x-coordinate
def line_points_from_slope_and_one_point(slope, point, x):
    m = slope
    n = point[1] - m * point[0]
    return m*x+n

def calculate_new_function_value_pairs(function_active):
    x = np.linspace(X_LEFT, X_RIGHT, NUM_OF_POINTS)
    y_derivative = functions[function_active][0](x)
    y_regular = functions[function_active][1](x)
    y_integral = functions[function_active][2](x)

    all_y = [y_derivative, y_regular, y_integral]
    return x, all_y

def calculate_new_dot_value_pairs(function_active, left_x, right_x):
    x = np.array([left_x, right_x])
    y_derivative = functions[function_active][0](x)
    y_regular = functions[function_active][1](x)
    y_integral = functions[function_active][2](x)

    all_y = [y_derivative, y_regular, y_integral]
    return x, all_y

def calculate_new_tangent_line_value_pairs(function_active, left_x, right_x):
    x = np.array([left_x, right_x])
    y = functions[function_active][1](x)
    tangent_slopes = functions[function_active][0](x)
    tangent_offsets = y - tangent_slopes * x

    # The interval around the two points in which the tangent line will be drawn
    # is based on the set fixed length of the tangent line
    interval_spacing = TANGENT_LENGTH * np.cos(np.arctan(tangent_slopes))

    x_left_tangent = np.array(
            [x[0] - interval_spacing[0], x[0] + interval_spacing[0]])
    x_right_tangent = np.array(
            [x[1] - interval_spacing[0], x[1] + interval_spacing[0]])

    y_left_tangent = tangent_slopes[0] * x_left_tangent + tangent_offsets[0]
    y_right_tangent = tangent_slopes[1] * x_right_tangent + tangent_offsets[1]

    xs = [x_left_tangent, x_right_tangent]
    ys = [y_left_tangent, y_right_tangent]

    return xs, ys

def calculate_new_band_values(function_active, left_x, right_x):
    x = np.linspace(left_x, right_x, NUM_OF_POINTS)
    y = functions[function_active][1](x)

    # Collecting all points of the regular function which spans a negative or a
    # positive area underneith them
    y_pos = []
    y_neg = []
    for ele in y:
        if ele > 0:
            y_pos.append(ele)
            y_neg.append(0)
        else:
            y_pos.append(0)
            y_neg.append(ele)
    
    y_pos = np.array(y_pos)
    y_neg = np.array(y_neg)

    return x, y_pos, y_neg

def calculate_new_vertical_line_value_pairs(function_active, left_x, right_x):
    x = np.array([left_x, right_x])
    y = functions[function_active][1](x)

    xs = [[left_x, left_x], [right_x, right_x]]
    ys = [[0, y[0]], [0, y[1]]]

    return xs, ys


# ColumnDataSource abstract the sending of new value pairs to the client
derivative_values = ColumnDataSource()
derivative_dots = ColumnDataSource()

regular_values = ColumnDataSource()
regular_dots = ColumnDataSource()
regular_tangent_line_values = ColumnDataSource()
regular_vertical_line_values = ColumnDataSource()
positive_area_band_values = ColumnDataSource()
negative_area_band_values = ColumnDataSource()

integral_values = ColumnDataSource()
integral_dots = ColumnDataSource()


plot_left = figure(plot_height=HEIGHT, plot_width=WIDTH_OUTER_PLOTS,
        title="Ableitung", x_range=[X_LEFT, X_RIGHT], y_range=[Y_BOTTOM, Y_TOP])
plot_left.toolbar.active_drag = None

plot_middle = figure(plot_height=HEIGHT, plot_width=WIDTH_MIDDLE_PLOT,
        title="Betrachtete Funktion", x_range=[X_LEFT, X_RIGHT],
        y_range=[Y_BOTTOM, Y_TOP])
plot_middle.toolbar.active_drag = None

plot_right = figure(plot_height=HEIGHT, plot_width=WIDTH_OUTER_PLOTS,
        title="Eine Stammfunktion", x_range=[X_LEFT, X_RIGHT],
        y_range=[Y_BOTTOM, Y_TOP])
plot_right.toolbar.active_drag = None


plot_left.line(x="x", y="y", source=derivative_values, line_width=2,
        color="black")
plot_left.cross(x="x", y="y", source=derivative_dots, size=CROSS_SIZE,
        line_width=CROSS_LINE_WIDTH)

plot_middle.line(x="x", y="y", source=regular_values,
        line_width=FUNCTION_LINE_WIDTH, color="black")
plot_middle.multi_line(xs="xs", ys="ys", source=regular_tangent_line_values,
        line_width=TANGENT_LINE_WIDTH, color="orange")
plot_middle.cross(x="x", y="y", source=regular_dots, size=CROSS_SIZE,
        line_width=CROSS_LINE_WIDTH)
plot_middle.multi_line(xs="xs", ys="ys", source=regular_vertical_line_values,
        line_dash="dashed", line_width=2, color="black")
positive_area_band = Band(base="x", lower="lower", upper="upper",
        source=positive_area_band_values, fill_color="blue")
plot_middle.add_layout(positive_area_band)
negative_area_band = Band(base="x", lower="lower", upper="upper",
        source=negative_area_band_values, fill_color="purple")
plot_middle.add_layout(negative_area_band)

plot_right.line(x="x", y="y", source=integral_values,
        line_width=FUNCTION_LINE_WIDTH, color="black")
plot_right.cross(x="x", y="y", source=integral_dots, size=CROSS_SIZE,
        line_width=CROSS_LINE_WIDTH)

# Define widgets
function_selector = RadioButtonGroup(labels=names, active=0)
point_slider_left = Slider(title="Linker Punkt", value=0, start=-3, end=3,
        step=0.01)
point_slider_right = Slider(title="Rechter Punkt", value=1, start=-3, end=3,
        step=0.01)


# Callback defition
def update_slider(attr, old, new):
    x_dots, y_dots_all = calculate_new_dot_value_pairs(function_selector.active,
            point_slider_left.value, point_slider_right.value)
    derivative_dots.data = {"x": x_dots, "y": y_dots_all[0]}
    regular_dots.data = {"x": x_dots, "y": y_dots_all[1]}
    integral_dots.data = {"x": x_dots, "y": y_dots_all[2]}

    xs_tangent, ys_tangent = calculate_new_tangent_line_value_pairs(
            function_selector.active, point_slider_left.value,
            point_slider_right.value)
    regular_tangent_line_values.data = {"xs": xs_tangent, "ys": ys_tangent}

    x_band, y_band_pos, y_band_neg = calculate_new_band_values(
            function_selector.active, point_slider_left.value,
            point_slider_right.value)
    positive_area_band_values.data = {"x": x_band, "lower":
            np.zeros(y_band_pos.shape), "upper": y_band_pos} 
    negative_area_band_values.data = {"x": x_band, "lower": y_band_neg,
            "upper": np.zeros(y_band_neg.shape)}

    xs_vertical_line, ys_vertical_line = calculate_new_vertical_line_value_pairs(
            function_selector.active, point_slider_left.value,
            point_slider_right.value)
    regular_vertical_line_values.data = {"xs": xs_vertical_line,
            "ys": ys_vertical_line}


def update_button(source):
    x_functions, y_functions_all = calculate_new_function_value_pairs(
            function_selector.active)
    derivative_values.data = {"x": x_functions, "y": y_functions_all[0]}
    regular_values.data = {"x": x_functions, "y": y_functions_all[1]}
    integral_values.data = {"x": x_functions, "y": y_functions_all[2]}

    # Changing the function also requires an update for tangents etc.
    update_slider(0, 0, 0)


# Use the callback in advance to populate the plot
update_button(0)

# Connect the widgets with their respective callbacks
for slider in (point_slider_left, point_slider_right):
    slider.on_change("value", update_slider)

function_selector.on_click(update_button)

# Assemble the plot and create the html
inputs = widgetbox(function_selector, point_slider_left, point_slider_right)
curdoc().add_root(column(row(plot_left, plot_middle, plot_right), inputs))
