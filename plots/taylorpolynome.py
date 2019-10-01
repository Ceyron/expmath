import numpy as np

from bokeh.io import curdoc
from bokeh.layouts import row, widgetbox
from bokeh.models import ColumnDataSource, Band
from bokeh.models.widgets import Slider, RadioButtonGroup, Toggle
from bokeh.plotting import figure

'''
This plot introduces the Taylor-Polynoms for approximating arbitrary continously
differentiable functions. The user selects a order of approximation and an
x_spot for their development.
The currently one function available is hardcoded together with its first 5
derivatives. The values of the function made up of the Taylor Polynomes up to
the degree chosen are calculated according to the common rule.
A left-point based rectangualr quadrature is in use to compute the numerical
deviation from the true solution.
'''

# Geometry constants of the plot
HEIGHT = 400
WIDTH_PLOT = 600
WIDTH_TOTAL = 800
WIDTH_DIV_BOX = WIDTH_TOTAL - WIDTH_PLOT + 100

# The initial viewport the user starts in
X_LEFT = -5
X_RIGHT = 5
Y_BOTTOM = -2
Y_TOP = 2

# The interval in which the user can set the pivot point for the Taylor
# approximation, also the interval in which the numerical error is calculated
X_TAYLOR_LEFT = -3
X_TAYLOR_RIGHT = 3

# Thickness of the drawn functions
LINE_WIDTH_TRUE = 3
LINE_WIDTH_TAYLOR = 2
LINE_WIDTH_ERROR_BAR = 4

SIZE_CROSS = 15

# The amount the slider value is changen when the slider is moved by one
# position
SLIDER_STEPPING = 0.1

# Number of points used to discretize the interval for drawing
NUMBER_OF_POINTS = 100

def FUNC_1_0(x):
    return np.sin(x)
def FUNC_1_1(x):
    return np.cos(x)
def FUNC_1_2(x):
    return -np.sin(x)
def FUNC_1_3(x):
    return -np.cos(x)
def FUNC_1_4(x):
    return np.sin(x)
def FUNC_1_5(x):
    return np.cos(x)

# The function pointers are collected in a list to easily implement the
# summation later on
FUNC_1 = [FUNC_1_0, FUNC_1_1, FUNC_1_2, FUNC_1_3, FUNC_1_4, FUNC_1_5]

def calculate_new_true_function_value_pairs():
    x = np.linspace(X_LEFT, X_RIGHT, NUMBER_OF_POINTS)
    y = FUNC_1_0(x)
    return x, y

def assemble_taylor_polynomial(order, x_spot):
    """
    Returns a function pointer that contains the polynomials Taylor
    approximation.
    """
    def approximation(x):
        y_taylor = np.zeros(x.shape)
        for i in range(order + 1):
            y_taylor += (x - x_spot * np.ones(x.shape))**i / \
                    np.math.factorial(i) * FUNC_1[i](x_spot)
        return y_taylor

    return approximation

def calculate_new_taylor_approximation_value_pairs(approximation):
    x = np.linspace(X_LEFT, X_RIGHT, NUMBER_OF_POINTS)
    y = approximation(x)

    return x, y

def calculate_new_error_bar(approximation, error_location):
    pos = np.array([error_location, ])
    true_value = FUNC_1_0(pos)
    approx_value = approximation(pos)
    x = [error_location, error_location]
    y = [true_value, approx_value]

    return x, y

# ColumnDataSource abstracts the sending of new value pairs to the client over
# the WebSocket protocol
curve_values = ColumnDataSource()
taylor_values = ColumnDataSource()
point_values = ColumnDataSource()
error_bar_values = ColumnDataSource(data={"x": [], "y": []})

plot = figure(plot_height=HEIGHT, plot_width=WIDTH_PLOT,
        x_range=[X_LEFT, X_RIGHT], y_range=[Y_BOTTOM, Y_TOP])
plot.toolbar.active_drag = None  # Helpful for touchscreen users

plot.line(x="x", y="y", source=curve_values, color="black",
        line_width=LINE_WIDTH_TRUE)
plot.line(x="x", y="y", source=taylor_values, color="blue",
        line_width=LINE_WIDTH_TAYLOR)
plot.cross(x="x", y="y", source=point_values, color="blue", size=SIZE_CROSS,
        line_width=LINE_WIDTH_TAYLOR)
plot.line(x="x", y="y", source=error_bar_values, color="red",
        line_width=LINE_WIDTH_ERROR_BAR)

order = Slider(title="Ordnung des Taylorpolynoms", value=0, start=0, end=5,
        step=1)
x_spot = Slider(title="Entwicklungstelle x_0", value=1, start=X_TAYLOR_LEFT,
        end=X_TAYLOR_RIGHT, step=SLIDER_STEPPING)

# Advanced options made visible after a Toggle is pressed: A red thick vertical
# bar indicates the error between the Taylor approximation and the true function
# at the chosen point
advanced_toggle = Toggle(label="Fehlerindikator einblenden")
error_position_slider = Slider(title="""Position zum Vergleich zwischen Original
        und Annäherung wählen""", value=-1, start=X_TAYLOR_LEFT,
        end=X_TAYLOR_RIGHT, step=SLIDER_STEPPING, visible=False)

# Right now, only one function is availabe, so its values can be statically
# calculated upfront
x_true, y_true = calculate_new_true_function_value_pairs()
curve_values.data = {"x": x_true, "y": y_true}

# Defining callbacks
def update_slider(attr, old, new):
    approximation = assemble_taylor_polynomial(order.value, x_spot.value)
    x_taylor, y_taylor = calculate_new_taylor_approximation_value_pairs(
            approximation)
    taylor_values.data = {"x": x_taylor, "y": y_taylor}
    point_values.data = {"x": [x_spot.value, ], "y": [FUNC_1_0(x_spot.value), ]}
    if advanced_toggle.active:
        x_error, y_error = calculate_new_error_bar(approximation,
                error_position_slider.value)
        error_bar_values.data = {"x": x_error, "y": y_error}


def show_advanced(source):
    advanced_toggle.visible = False
    error_position_slider.visible = True
    update_slider(0, 0, 0)

# Use callback in advance to populate the plot
update_slider(0, 0, 0)

# Connect widgets with their respective callbacks
for slider in (order, x_spot, error_position_slider):
    slider.on_change("value", update_slider)

advanced_toggle.on_click(show_advanced)

# Assemble plot and create html
inputs = widgetbox(order, x_spot, advanced_toggle, error_position_slider)
curdoc().add_root(row(plot, inputs, width=WIDTH_TOTAL))
