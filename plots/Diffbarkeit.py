import numpy as np

from bokeh.io import curdoc
from bokeh.layouts import row, widgetbox
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import Slider, RadioButtonGroup
from bokeh.plotting import figure

HEIGHT = 400
WIDTH_PLOT = 600
WIDTH_TOTAL = 800
LEFT = -5
RIGHT = 5
BOTTOM = -2
TOP = 2
SIZE_GLYPHS = 15
SECANT_LINE_WIDTH = 3
FUNCTION_LINE_WIDTH = 2
X_DIM = RIGHT - LEFT
Y_DIM = TOP - BOTTOM

def FUNC_1(x):
    return np.exp(-(x - 1)**2)
def FUNC_2(x):
    return np.abs(x)
def FUNC_3(x):
        if x<0.5:
            return (1/3*x**2)
        else:
            return (x**3)

functions = [FUNC_1, FUNC_2, FUNC_3]


# A linear function is used to connect two points, given a x position, what is the corresponding y position on that line. Insert the two points as tuples
def line_from_two_points(first, second, x):
    return (first[1] - second[1]) / (first[0] - second[0]) * (x - first[0]) + first[1]

def update_data(function_selector, point_location, spacing_around, curve_values, left_line_values, right_line_values):
    x = np.linspace(LEFT, RIGHT, 200)
    y = []
    for i in x:
        y.append(functions[function_selector.active](i))
    curve_values.data = {"x": x, "y": y}
    # Extract x locations for hot points by using slider values
    left_x = point_location.value - (spacing_around.value + 0.01)
    middle_x = point_location.value
    right_x = point_location.value + (spacing_around.value + 0.01)
    # Calculate y location for hot points using the currently active function
    left_y = functions[function_selector.active](left_x)
    middle_y = functions[function_selector.active](middle_x)
    right_y = functions[function_selector.active](right_x)
    # Assemble the points used for interpolating and extrapolating the linear lines
    left_point = (left_x, left_y)
    middle_point = (middle_x, middle_y)
    right_point = (right_x, right_y)

    # TODO: Currently, the line of the secants differs since the x distance of their endpoints is fixed, however we need to fix the total length of it
    x_for_left = np.linspace(left_x - 0.1 * X_DIM, middle_x + 0.1 * X_DIM, 2)
    x_for_right = np.linspace(middle_x - 0.1 * X_DIM, right_x + 0.1 * X_DIM, 2)

    y_for_left = line_from_two_points(left_point, middle_point, x_for_left)
    y_for_right = line_from_two_points(middle_point, right_point, x_for_right)
    left_line_values.data = {"x": x_for_left, "y": y_for_left}
    right_line_values.data = {"x": x_for_right, "y": y_for_right}

    dots_values.data = {"x": [left_x, middle_x, right_x, left_x, middle_x, right_x], "y": [left_y, middle_y, right_y, BOTTOM, BOTTOM, BOTTOM]}




curve_values = ColumnDataSource()
left_line_values = ColumnDataSource()
right_line_values = ColumnDataSource()
dots_values = ColumnDataSource()


plot = figure(plot_height=HEIGHT, plot_width=WIDTH_PLOT,
              tools="", x_range=[-5, 5], y_range=[-2, 2])
plot.line("x", "y", source=curve_values, color="blue", line_width=FUNCTION_LINE_WIDTH)
plot.line("x", "y", source=left_line_values, color="orange", line_width=SECANT_LINE_WIDTH)
plot.line("x", "y", source=right_line_values, color="purple", line_width=SECANT_LINE_WIDTH)
plot.cross("x", "y", source=dots_values, color="black", size=SIZE_GLYPHS)


function_selector = RadioButtonGroup(
        labels=["Funktion 1", "Funktion 2", "Funktion 3"], active=0)
point_location = Slider(title="Betrachteter Punkt $x_0$", value=0,
        start=-4, end=4, step=0.1)
spacing_around = Slider(title="Abstand darum $h$", value=0.5, start=0, end=2, step=0.1)

update_data(function_selector, point_location, spacing_around, curve_values, left_line_values, right_line_values)

inputs = widgetbox(function_selector, point_location, spacing_around)

# Callback for all sliders
def update_slider(attr, old, new):
    update_data(function_selector, point_location, spacing_around, curve_values, left_line_values, right_line_values)


def update_button(source):
    update_data(function_selector, point_location, spacing_around, curve_values, left_line_values, right_line_values)


for slider in (point_location, spacing_around, ):
    slider.on_change("value", update_slider)
for button in (function_selector, ):
    button.on_click(update_button)


curdoc().add_root(row(plot, inputs, width=WIDTH_TOTAL))

