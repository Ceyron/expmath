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
    return -4*np.sin(2*x)

def FUNC_3(x):
    return np.exp(x)
def FUNC_3_derivative(x):
    return np.exp(x)
def FUNC_3_integral(x):
    return np.exp(x)

# This list collects the function pointers to the mathematical functions that are displayed in the plots
functions = [
        [FUNC_1_derivative, FUNC_1, FUNC_1_integral],
        [FUNC_2_derivative, FUNC_2, FUNC_2_integral],
        [FUNC_3_derivative, FUNC_3, FUNC_3_integral]
        ]

# Given the coordinates of one point and the slope at this, model the tangent line to this point and use it to return the y-coordinate for a given x-coordinate
def line_points_from_slope_and_one_point(slope, point, x):
    m = slope
    n = point[1] - m * point[0]
    return m*x+n


def update_data(function_selector, point_slider_left, point_slider_right, derivative_values, derivative_dots, regular_values, regular_tangent_line_left, regular_tangent_line_right, regular_vertical_line_left, regular_vertical_line_right, positive_area_band_values, negative_area_band_values, integral_values, integral_dots):
    x = np.linspace(-3, 3, 50)
    x_lim = np.array([point_slider_left.value, point_slider_right.value])
    y_left = functions[function_selector.active][0](x)
    y_middle = functions[function_selector.active][1](x)
    y_right = functions[function_selector.active][2](x)

    #  --- Populate the ColumnDataSources for the left plot ---
    # The black line that draws the continous function representing the derivative
    derivative_values.data = {"x": x, "y": y_left}
    # Two crosses representing the two locations chosen by the sliders
    derivative_dots.data = {"x": x_lim, "y": functions[function_selector.active][0](x_lim)}

    # --- Populate the ColumnDataSource for the middle plot ---
    # The black line thet draws the continous function representing the regular function
    regular_values.data = {"x": x, "y": y_middle}
    # Two data ranges for the tangent line to be plotted around the two points chosen by the sliders
    # TODO: New unit-circle method with the slope of the curve ensures that tangent lines always have the same length. This has to be reworked for all three functions so that the chosen multiplicator fits the dimensions of the plot
    x_for_tangent_left = np.linspace(point_slider_left.value - (0.001 + 0.3 * np.cos(np.arctan(functions[function_selector.active][0](np.array([point_slider_left.value, ]))))), point_slider_left.value + (0.001 + 0.3 * np.cos(np.arctan(functions[function_selector.active][0](np.array([point_slider_left.value, ]))))), 2)
    x_for_tangent_right = np.linspace(point_slider_right.value - 0.3, point_slider_right.value + 0.3, 2)
    # The ColumnDataSources for the tangent lines by using a function to model the straight line
    regular_tangent_line_left.data = {"x": x_for_tangent_left, "y": line_points_from_slope_and_one_point(functions[function_selector.active][0](np.array([point_slider_left.value, ])), (point_slider_left.value, functions[function_selector.active][1](point_slider_left.value)), x_for_tangent_left)}
    regular_tangent_line_right.data = {"x": x_for_tangent_right, "y": line_points_from_slope_and_one_point(functions[function_selector.active][0](np.array([point_slider_right.value, ])), (point_slider_right.value, functions[function_selector.active][1](point_slider_right.value)), x_for_tangent_right)}
    # Two dashed vertical lines that mark the beginning and end of the area under the curve
    regular_vertical_line_left.data = {"x": [point_slider_left.value, point_slider_left.value], "y": [0, functions[function_selector.active][1](point_slider_left.value)]}
    regular_vertical_line_right.data = {"x": [point_slider_right.value, point_slider_right.value], "y": [0, functions[function_selector.active][1](point_slider_right.value)]}
    # The two colorfull bands that fill the area under the curve
    y_pos, y_neg = [], [] 
    x_in_lim = np.linspace(point_slider_left.value, point_slider_right.value, 50)
    for elem in x_in_lim:
        if functions[function_selector.active][1](elem) < 0.:
            y_neg.append(functions[function_selector.active][1](elem))
            y_pos.append(0.)
        else:
            y_neg.append(0.)
            y_pos.append(functions[function_selector.active][1](elem))
    positive_area_band_values.data = {"x": x_in_lim, "lower": np.zeros(x.shape), "upper": y_pos}
    negative_area_band_values.data = {"x": x_in_lim, "lower": y_neg, "upper": np.zeros(x.shape)}

    # --- Populate the ColumnDataSource for the right plot
    integral_values.data = {"x": x, "y": y_right}
    integral_dots.data = {"x": x_lim, "y": functions[function_selector.active][2](x_lim)}


derivative_values = ColumnDataSource()
derivative_dots = ColumnDataSource()

regular_values = ColumnDataSource()
regular_tangent_line_left = ColumnDataSource()
regular_tangent_line_right = ColumnDataSource()
regular_vertical_line_left = ColumnDataSource()
regular_vertical_line_right = ColumnDataSource()
positive_area_band_values = ColumnDataSource()
negative_area_band_values = ColumnDataSource()

integral_values = ColumnDataSource()
integral_dots = ColumnDataSource()


plot_left = figure(plot_height=HEIGHT, plot_width=WIDTH_OUTER_PLOTS, tools="",
        title="Ableitung", x_range=[X_LEFT, X_RIGHT], y_range=[Y_BOTTOM, Y_TOP])
plot_middle = figure(plot_height=HEIGHT, plot_width=WIDTH_MIDDLE_PLOT, tools="",
        title="Betrachtete Funktion", x_range=[X_LEFT, X_RIGHT],
        y_range=[Y_BOTTOM, Y_TOP])
plot_right = figure(plot_height=HEIGHT, plot_width=WIDTH_OUTER_PLOTS, tools="",
        title="Eine Stammfunktion", x_range=[X_LEFT, X_RIGHT],
        y_range=[Y_BOTTOM, Y_TOP])

plot_left.line(x="x", y="y", source=derivative_values, line_width=2,
        color="black")
plot_left.cross(x="x", y="y", source=derivative_dots, size=15, line_width=3)

plot_middle.line(x="x", y="y", source=regular_values, line_width=2,
        color="black")
plot_middle.line(x="x", y="y", source=regular_tangent_line_left, line_width=3,
        color="orange")
plot_middle.line(x="x", y="y", source=regular_tangent_line_right, line_width=3,
        color="orange")
plot_middle.line(x="x", y="y", source=regular_vertical_line_left,
        line_dash="dashed", line_width=2, color="black")
plot_middle.line(x="x", y="y", source=regular_vertical_line_right,
        line_dash="dashed", line_width=2, color="black")
positive_area_band = Band(base="x", lower="lower", upper="upper",
        source=positive_area_band_values, fill_color="blue")
plot_middle.add_layout(positive_area_band)
negative_area_band = Band(base="x", lower="lower", upper="upper",
        source=negative_area_band_values, fill_color="purple")
plot_middle.add_layout(negative_area_band)

plot_right.line(x="x", y="y", source=integral_values, line_width=2, color="black")
plot_right.cross(x="x", y="y", source=integral_dots, size=15, line_width=2)

function_selector = RadioButtonGroup(labels=["Lineare Funktion",
    "Trigonometrische Funktion", "Exponentialfunktion"], active=0)
point_slider_left = Slider(title="Linker Punkt", value=0, start=-3, end=3,
        step=0.01)
point_slider_right = Slider(title="Rechter Punkt", value=1, start=-3, end=3,
        step=0.01)

update_data(function_selector, point_slider_left, point_slider_right, derivative_values, derivative_dots, regular_values, regular_tangent_line_left, regular_tangent_line_right, regular_vertical_line_left, regular_vertical_line_right, positive_area_band_values, negative_area_band_values, integral_values, integral_dots)

def update_slider(attr, old, new):
    update_data(function_selector, point_slider_left, point_slider_right, derivative_values, derivative_dots, regular_values, regular_tangent_line_left, regular_tangent_line_right, regular_vertical_line_left, regular_vertical_line_right, positive_area_band_values, negative_area_band_values, integral_values, integral_dots)
    
def update_button(source):
    update_data(function_selector, point_slider_left, point_slider_right, derivative_values, derivative_dots, regular_values, regular_tangent_line_left, regular_tangent_line_right, regular_vertical_line_left, regular_vertical_line_right, positive_area_band_values, negative_area_band_values, integral_values, integral_dots)


inputs = widgetbox(function_selector, point_slider_left, point_slider_right)

for slider in (point_slider_left, point_slider_right):
    slider.on_change("value", update_slider)

for button in (function_selector, ):
    button.on_click(update_button)

curdoc().add_root(column(row(plot_left, plot_middle, plot_right), inputs))
