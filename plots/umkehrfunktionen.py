import numpy as np
from scipy.special import lambertw
from scipy.optimize import newton

from bokeh.layouts import Row, WidgetBox
from bokeh.io import curdoc
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import RangeSlider, RadioButtonGroup, Slider
from bokeh.plotting import Figure

"""
This plot visualizes the idea that the invert function is the image of the
original function appearing when mirroring on the first major axis (a function
with y = x). This can be seen either by two arrows that are flipped or by the
mirrored image.
The user can select various functions. He then chooses the point on the axis
when using the arrow approach or adjusts a range slider that will define an
interval ON the mirroring axis. From the endpoint of this interval rays are
propagating perpendicularly that will hit the original and the invert function.
This aids in understanding the idea of pointwise mirroring. When using the
mirroring approach, the invert function is only drawn within this interval,
otherwise it is fully drawn.
"""

# Plot geometry constants
HEIGHT = 400
WIDTH_PLOT = 600
WIDTH_TOTAL = 800

# Thickness of original and invert function as well as the mirroring line
LINE_WIDTH = 2
# Diameter of the dots marking the end of the interval
CIRCLE_SIZE = 8

# The initial viewport in which the user starts, i.e., the plain that is visible
# upfront
VIEWPORT_X = [-6, 6]
VIEWPORT_Y = [-4.5, 4.5]

# Left-most and right-most points to still have value pairs
X_LEFT = VIEWPORT_X[0] - 0.5
X_RIGHT = VIEWPORT_X[1] + 0.5

# Bottom-most and top-most point for drawing the vertical axis 
Y_BOTTOM = VIEWPORT_Y[0] - 0.5
Y_TOP = VIEWPORT_Y[1] + 0.5

# The step by which the value is discretely increased on the slider
STEPPING = 0.1

# Regularly needed constant
SQRT_2 = 1.414


# Each function consists of the original and the invert, as well as two
# intersectors. These define a coordinate x at which the perpendicular ray from
# the mirror hits the original or invert function, respectively.
#
# The ray always has the function y = -x + SQRT(2)*t whereas t is the coordinate
# alongside the mirroring line. The intersectors are defined when the ray's
# definition is set equatunnell to function definition it tries to, then solved
# for x.
#
# Every function also has a corresponding interval on the mirroring axis that it
# allows to have values from. This interval is also used for the slider that
# allows selecting a point in the arrow approach.
#
# Another interval defines the drawing limits so that no exceptions occur at run
# time (negative radicands, log of 0 etc.). This is only necessary for the arrow
# approach.

# Simple linear function
def FUNC_1(x):
    return 0.5*x + 1

def FUNC_1_intersector(t):
    return 2/3 * (SQRT_2 * t - 1)

def FUNC_1_invert(y):
    return 2*y - 2

def FUNC_1_invert_intersector(t):
    return 1/3 * (SQRT_2 * t + 2)

FUNC_1_SLIDER_LIMITS = (-4, 4)
# Drawing limits relevant only for inverted function
FUNC_1_DRAWING_LIMITS = (X_LEFT, X_RIGHT)


# Quadratic Polynomial
def FUNC_2(x):
    return x**2

def FUNC_2_intersector(t):
    return -1/2 + np.sqrt(1/4 + SQRT_2 * t)

def FUNC_2_invert(y):
    return np.sqrt(y)

def FUNC_2_invert_intersector(t):
    return 1/2 * (1 + 2 * SQRT_2 * t) -\
            np.sqrt(1/4 * (1 + 2 *  SQRT_2 * t)**2 - 2*t**2)

FUNC_2_SLIDER_LIMITS  = (0, 4)
# Drawing limits relevant only for inverted function
FUNC_2_DRAWING_LIMITS = (0, X_RIGHT)


# Exponential and Logarithm
def FUNC_3(x):
    return np.exp(x)

def FUNC_3_intersector(t):
    return (SQRT_2 * t - lambertw(np.exp(SQRT_2 * t))).real

def FUNC_3_invert(y):
    return np.log(y)

def FUNC_3_invert_intersector(t):
    result = lambertw(np.exp(SQRT_2 * t)).real
    return result

FUNC_3_SLIDER_LIMITS = (-4, 4)
# Drawing limits relevant only for inverted function
FUNC_3_DRAWING_LIMITS = (0.001, X_RIGHT)


# Sine Wave - only half of the full period is used so that it still bijective,
# hence invertible
PERIOD = (X_RIGHT - X_LEFT) * 2
FREQUENCY = 1/PERIOD
ANGULAR_FREQUENCY = FREQUENCY * 2 * np.pi
SINE_SCALING = 3 # Increase the amplitude

def FUNC_4(x):
    return SINE_SCALING * np.sin(ANGULAR_FREQUENCY * x)

# Using newton's method to approximately find the intersecting point
def FUNC_4_intersector(t):
    intersections = []
    for ele in t:
        func = lambda x: (-x + SQRT_2 * ele) -\
                SINE_SCALING * np.sin(ANGULAR_FREQUENCY * x)
        intersections.append(newton(func, 0, maxiter=30))
    return intersections

def FUNC_4_invert(y):
    return 1/ANGULAR_FREQUENCY * np.arcsin(1/SINE_SCALING * y)

def FUNC_4_invert_intersector(t):
    intersections = []
    for ele in t:
        func = lambda x: (-x + SQRT_2 * ele) -\
                1/ANGULAR_FREQUENCY * np.arcsin(1/SINE_SCALING * x)
        intersections.append(newton(func, 0, maxiter=30))
    return intersections

FUNC_4_SLIDER_LIMITS = (-5, 5)
# Drawing limits relevant only for inverted function
FUNC_4_DRAWING_LIMITS = (-3, 3)


# The functions are collected in function pointer lists
functions = [FUNC_1, FUNC_2, FUNC_3, FUNC_4, ]
functions_intersector = [FUNC_1_intersector, FUNC_2_intersector,
        FUNC_3_intersector, FUNC_4_intersector, ]
functions_inverted = [FUNC_1_invert, FUNC_2_invert, FUNC_3_invert,
        FUNC_4_invert, ] 
functions_inverted_intersector = [FUNC_1_invert_intersector,
        FUNC_2_invert_intersector, FUNC_3_invert_intersector,
        FUNC_4_invert_intersector,]
SLIDER_LIMITS = [FUNC_1_SLIDER_LIMITS, FUNC_2_SLIDER_LIMITS,
        FUNC_3_SLIDER_LIMITS, FUNC_4_SLIDER_LIMITS, ]
DRAWING_LIMITS = [FUNC_1_DRAWING_LIMITS, FUNC_2_DRAWING_LIMITS,
        FUNC_3_DRAWING_LIMITS, FUNC_4_DRAWING_LIMITS, ]

# The names appearing in the RadioButtonGroup at the top
function_names = ["Funktion 1", "Funktion 2", "Funktion 3", "Funktion 4", ]


def calculate_function_value_pairs(function_active):
    x = np.linspace(X_LEFT, X_RIGHT, 100)
    y = functions[function_active](x)

    return x, y

def find_intersecting(function_active, t, use_invert=False):
    if use_invert:
        return functions_inverted_intersector[function_active](t)
    else:
        return functions_intersector[function_active](t)

def calculate_inverted_value_pairs(function_active, left, right):
    x = np.linspace(left, right, 100)
    y = functions_inverted[function_active](x)

    return x, y


# The ColumnDataSource abstracts the sending of information to the Client over
# the WebSocket protocol
original_function_value_pairs = ColumnDataSource()
dots_values = ColumnDataSource()
mirror_line = ColumnDataSource()
mirror_rays = ColumnDataSource()
mirror_arrows = ColumnDataSource()
inverted_function_value_pairs = ColumnDataSource()


plot = Figure(plot_height=HEIGHT, plot_width=WIDTH_PLOT, x_range=VIEWPORT_X,
        y_range=VIEWPORT_Y)
plot.toolbar.active_drag = None  # Helpful for touchscreen users
# Indicate the x-axis and the y-axis
plot.line(x=[X_LEFT, X_RIGHT], y=[0, 0], color="black")
plot.line(x=[0, 0], y=[Y_BOTTOM, Y_TOP], color="black")
# Indicate the mirroring line
plot.line(x="x", y="y", color="black", source=mirror_line,
        line_width=LINE_WIDTH)

plot.line(x="x", y="y", source=original_function_value_pairs, color="blue",
        line_width=LINE_WIDTH)

plot.line(x="x", y="y", source=inverted_function_value_pairs, color="red",
        line_width=LINE_WIDTH)

plot.multi_line(xs="xs", ys="ys", source=mirror_rays)
plot.multi_line(xs="xs", ys="ys", color="colors", source=mirror_arrows)

# The two dots on the mirroring line indiciating the RangeSlider's values
plot.circle(x="x", y="y", source=dots_values, color="black",
        size=CIRCLE_SIZE)

function_selector = RadioButtonGroup(labels=function_names, active=0)
type_selector = RadioButtonGroup(labels=["Pfeilumkehr", "Spiegeln"], active=0)

# In the case of the arrow approach, the user can choose to either manipulate
# the original or the invert function
point_slider = Slider(title="Betrachtete Position auf x und y", start=0, end=1,
        step=0.1, value=1)

# The values for start, end and value are arbitrary since they will be
# overridden in the initiliazation by the callback
interval_slider = RangeSlider(title="In welchem Bereich invertieren",
        start=0, end=1, step=STEPPING, value=(0, 1), visible=False)


# Only used within the arrow approach
def point_slider_callback(attr, old, new):
    x_pos = point_slider.value
    original_value = functions[function_selector.active](x_pos)

    # All components of the two arrows for the original function
    up_arrow_original_x = [x_pos, x_pos]
    up_arrow_original_y = [0, original_value]
    left_arrow_original_x = [x_pos, 0]
    left_arrow_original_y = [original_value, original_value]

    # All components of the two arrows for the inverted function
    right_arrow_inverted_x = [0, original_value]
    right_arrow_inverted_y = [x_pos, x_pos]
    down_arrow_inverted_x = [original_value, original_value]
    down_arrow_inverted_y = [x_pos, 0]

    mirror_arrows.data = {
            "xs": [up_arrow_original_x, left_arrow_original_x,
                right_arrow_inverted_x, down_arrow_inverted_x],
            "ys": [up_arrow_original_y, left_arrow_original_y,
                right_arrow_inverted_y, down_arrow_inverted_y],
            "colors": ["green", "purple", "green", "purple"]
            }

    dots_values.data = {"x": [x_pos, 0], "y": [0, x_pos]}


# Only used within in the mirroring approach
def interval_slider_callback(attr, old, new):
    # The value of the RangeSlider indicates the distance on the mirroring line
    # measured from the origin
    points = np.array(interval_slider.value)
    # Get the x and y position of a position on the mirroring line
    x = SQRT_2/2 * points
    y = SQRT_2/2 * points
    dots_values.data = {"x": x, "y": y}

    # Where will the rays hit the original and invert function
    xs_on_original = find_intersecting(function_selector.active, points,
            use_invert=False)
    xs_on_original = np.array(xs_on_original)
    xs_on_inverted = find_intersecting(function_selector.active, points,
            use_invert=True)
    xs_on_inverted = np.array(xs_on_inverted)
    ys_on_original = functions[function_selector.active](xs_on_original)
    ys_on_inverted =\
            functions_inverted[function_selector.active](xs_on_inverted)

    # The information to plot the rays' lines
    xs_for_rays = [
            [xs_on_original[0], xs_on_inverted[0]],
            [xs_on_original[1], xs_on_inverted[1]]]
    ys_for_rays = [
            [ys_on_original[0], ys_on_inverted[0]],
            [ys_on_original[1], ys_on_inverted[1]]]
    mirror_rays.data = {"xs": xs_for_rays, "ys": ys_for_rays}

    x_inverted, y_inverted = calculate_inverted_value_pairs(
            function_selector.active, *xs_on_inverted)

    inverted_function_value_pairs.data = {"x": x_inverted, "y": y_inverted}


def function_selector_callback(source):
    # The original function only has to be redrawn when the a new function is
    # selected, since there is no slider that changes it so far
    x, y = calculate_function_value_pairs(function_selector.active)
    original_function_value_pairs.data = {"x": x, "y": y}

    # Update the corresponding invert function and the mirroring rays
    if type_selector.active == 0:  # Using arrows 
        point_slider.start = SLIDER_LIMITS[function_selector.active][0]
        point_slider.end = SLIDER_LIMITS[function_selector.active][1]

        x_inverted, y_inverted = calculate_inverted_value_pairs(
                function_selector.active,
                DRAWING_LIMITS[function_selector.active][0],
                DRAWING_LIMITS[function_selector.active][1])
        inverted_function_value_pairs.data = {
                "x": x_inverted,
                "y": y_inverted,
                }

        point_slider_callback(0, 0, 0)

    elif type_selector.active == 1:  # Using mirroring lines
        # Set the default values for the sliders
        interval_slider.start = SLIDER_LIMITS[function_selector.active][0]
        interval_slider.end = SLIDER_LIMITS[function_selector.active][1]
        interval_slider.value = (
                SLIDER_LIMITS[function_selector.active][0] + 1,
                SLIDER_LIMITS[function_selector.active][1] - 1
                )
        interval_slider_callback(0, 0, 0)


def type_selector_callback(source):
    if type_selector.active == 0:  # Arrow approach
        point_slider.visible = True
        interval_slider.visible = False

        point_slider.value = 1.5

        mirror_line.data = {"x": [], "y": []}
        mirror_rays.data = {"xs": [], "ys": []}


    elif type_selector.active == 1:  # Mirroring approach
        point_slider.visible = False
        interval_slider.visible = True

        mirror_line.data = {"x": [-15, 15], "y": [-15, 15]}
        mirror_arrows.data = {"xs": [], "ys": [], "colors": []}


    function_selector_callback(0)


# Call this callback in advance to populate the plot with data
type_selector_callback(0)

# Connect widgets with their respectice callbacks
point_slider.on_change("value", point_slider_callback)
interval_slider.on_change("value", interval_slider_callback)
function_selector.on_click(function_selector_callback)
type_selector.on_click(type_selector_callback)

# Assemble the plot and create the html element
inputs = WidgetBox(function_selector, type_selector, interval_slider,
        point_slider)
curdoc().add_root(Row(plot, inputs, width=WIDTH_TOTAL))
