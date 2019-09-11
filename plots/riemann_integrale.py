import numpy as np

from bokeh.io import curdoc
from bokeh.layouts import row, widgetbox
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import RangeSlider, Slider, RadioButtonGroup, Div
from bokeh.plotting import figure

"""
This plot introduces the idea of Riemann-integrals, a way of visualizing the
idea of the defined integral. Here, we use the idea to discretize a given
interval into sub-intervals of equal size. Each sub-interval is associated with
a lower sum (sub-interval width times the function value at the left side) and
an upper sum (sub-interval width times the function value at the right side).
The numeric output of the sum of all lower and upper sums is given. The user
will see that both value will converge against each other when the
discretizations is getting fine enough, given that the function is continous.
"""

# Geometry constants of the plot
HEIGHT = 400
WIDTH_PLOT = 600
WIDTH_TOTAL = 800
WIDTH_BOX = WIDTH_TOTAL - WIDTH_PLOT
HEIGHT_BOX = 50

LEFT_X = -5.
RIGHT_X = 5.

# Simple linear function
def FUNC_1(x):
    return x

# Trigonometric function - The user does not see which function it is
def FUNC_2(x):
    return np.arctan(x)

# Store all functions in a list of function pointers for conveniant access
functions = [FUNC_1, FUNC_2]

def update_function(function_selector, function_values):
    """
    Calculates the value pairs for the smooth black function.
    """
    x = np.linspace(LEFT_X, RIGHT_X, 50)
    y = functions[function_selector.active](x)

    function_values.data = {"x": x, "y": y}


def update_sums(function_selector, interval_slider, discretization_slider,
        lower_sum, upper_sum):
    """
    Calculates the center location, the width and height for the boxes
    representing the upper and the lower triangle.
    """
    interval = interval_slider.value
    delta_x = (interval[1] - interval[0]) / discretization_slider.value

    x_set = np.linspace(interval[0], interval[1] - delta_x, discretization_slider.value)
    # The center of every bar is the left-point plus the half bar-width
    x_set += delta_x/2.

    height_lower = functions[function_selector.active](x_set - delta_x/2.)
    height_upper = functions[function_selector.active](x_set + delta_x/2.)

    lower_sum.data = {
            "x_center": x_set,
            "width": delta_x * np.ones(x_set.shape),
            "height": height_lower}
    upper_sum.data = {
            "x_center": x_set,
            "width": delta_x * np.ones(x_set.shape),
            "height": height_upper}

def update_boxes(function_selector, interval_slider, discretization_slider,
        delta_box, lower_sum_box, upper_sum_box):
    """
    Updates the string result values in the Div Boxes. They give a numerical
    representation on the areas of the lower and upper sum. The user can
    identify that increasing the number of boxes, i.e. decreasing the box width,
    will let these both value converge against each other.
    """
    interval = interval_slider.value
    delta_x = (interval[1] - interval[0]) / discretization_slider.value

    x_set = np.linspace(interval[0], interval[1] - delta_x,
            discretization_slider.value)

    lower_sum = 0.
    upper_sum = 0.
    # Area for the boxes is the height given by the function at the point (left
    # foot for lower_sum and right foot for upper_sum) times the box width
    for left_box_point in x_set:
        lower_sum += functions[function_selector.active](left_box_point) *\
                delta_x
        upper_sum += functions[function_selector.active](left_box_point +
                delta_x) * delta_x

    #TODO Improve styling
    delta_box.text = "delta x = %1.2f" % delta_x
    lower_sum_box.text = "Untersummen = %.2f" % lower_sum
    upper_sum_box.text = "Obersummen = %.2f" % upper_sum


# ColumnDataSource represents the abstraction for the dataset transmission to
# the client over the WebSocket protocol
function_values = ColumnDataSource()
lower_sum = ColumnDataSource()
upper_sum = ColumnDataSource()

plot = figure(plot_height=HEIGHT, plot_width=WIDTH_PLOT)
plot.toolbar.active_drag = None
plot.line("x", "y", source=function_values, color="black", line_width=2)
plot.vbar(x="x_center", width="width", top="height", source=upper_sum,
color="blue", alpha=0.6)
plot.vbar(x="x_center", width="width", top="height", source=lower_sum,
color="orange", alpha=0.6)

function_selector = RadioButtonGroup(labels=["Funktion 1", "Funktion 2"],
        active=0)
interval_slider = RangeSlider(title="Interval", start=-5., end=5., value=(1.,
    3.), step=0.1)
discretization_slider = Slider(title="Anzahl an Rechtecken", start=1, end=50,
    value=2, step=1)
delta_box = Div(text="delta x = 1.", width=WIDTH_BOX, height=HEIGHT_BOX)
lower_sum_box = Div(text="Untersummen = 123", width=WIDTH_BOX,
        height=HEIGHT_BOX)
upper_sum_box = Div(text="Obersummen = 123", width=WIDTH_BOX, height=HEIGHT_BOX)


inputs = widgetbox(function_selector, interval_slider, discretization_slider,
        delta_box, lower_sum_box, upper_sum_box)

# Calling all the update functions to initially populate the plot
update_function(function_selector, function_values)
update_sums(function_selector, interval_slider, discretization_slider,
        lower_sum, upper_sum)
update_boxes(function_selector, interval_slider, discretization_slider,
        delta_box, lower_sum_box, upper_sum_box)

# Defining callback handlers
def update_slider(attr, old, new):
    update_function(function_selector, function_values)
    update_sums(function_selector, interval_slider, discretization_slider,
            lower_sum, upper_sum)
    update_boxes(function_selector, interval_slider, discretization_slider,
            delta_box, lower_sum_box, upper_sum_box)

def update_button(source):
    update_function(function_selector, function_values)
    update_sums(function_selector, interval_slider, discretization_slider,
            lower_sum, upper_sum)
    update_boxes(function_selector, interval_slider, discretization_slider,
            delta_box, lower_sum_box, upper_sum_box)


# Link callback handlers to the occuring events
for slider in (interval_slider, discretization_slider, ):
    slider.on_change("value", update_slider)

function_selector.on_click(update_button)

# Assembele the plot and the input methods
curdoc().add_root(row(plot, inputs, width=WIDTH_TOTAL))
