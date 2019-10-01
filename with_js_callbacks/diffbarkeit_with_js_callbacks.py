import numpy as np

from bokeh.io import curdoc
from bokeh.layouts import Row, WidgetBox
from bokeh.models import ColumnDataSource, CustomJS
from bokeh.models.widgets import Slider, RadioButtonGroup
from bokeh.plotting import Figure

"""
EXPERIMENTAL PROTOTYPE
This plot presents an example on how to use javascript callbacks on bokeh
widgets (sliders, buttons etc.).

WHY:
    Using javascript callbacks moves the computational load of recalculating the
    function value pairs to the client. This can prove handy if too many users
    are connected to the bokeh server so that it can no longer handle all
    requests to recalculate the value pairs. Aside from it, using js callbacks
    could also improve the responsiveness of the plots since the update request
    is handled on the same machine.

HOW:
    A javascript code snippet needs to be written for every callback associated.
    Every bokeh object one wants to access within this callback has to be
    explicitly in the arguments of CustomJS. The ColumnDataSource has to be
    filled up front on the Python backend site. This is also the reason the
    calculate functions are still present in this script. Numerical operations
    within Javascript are available by Math.xxx (e.g. Math.sin). Most of them
    are similar to the numpy variants.

DOWNSIDES SO FAR:
    * Calling other functions (Javascript on Client and Python on Backend) is
    more difficult (workaround so far: manipulate the value of widget so that
    its callback gets fired)
    * Efficiency (vector processing) might not be as powerful on the client as
    it can be on the server with multiple cores
"""

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


"""
The following three functions are necessary to fill plot with data for the first
time. Afterwards, they are not used anymore. They are similar to the ones
without JS callbacks.
"""
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


plot = Figure(plot_height=HEIGHT, plot_width=WIDTH_PLOT,
              x_range=[-5, 5], y_range=[-2, 2])
plot.toolbar.active_drag = None

plot.line(x="x", y="y", source=curve_values, color="blue",
        line_width=FUNCTION_LINE_WIDTH)
plot.multi_line(xs="xs", ys="ys", source=secant_line_values, color="color",
        line_width="line_width")
plot.cross(x="x", y="y", source=dot_values, color="black", size=SIZE_GLYPHS)


function_selector = RadioButtonGroup(
        labels=["Funktion 1", "Funktion 2", "Funktion 3"], active=0)
point_slider = Slider(title="Betrachteter Punkt $x_0$", value=0,
        start=-4, end=4, step=0.1)
spacing_slider = Slider(title="Abstand um den Punkt $h$", value=0.5, start=0.01,
        end=2, step=0.1)

# Populate the CDS - necessaary only once
x = np.linspace(LEFT, RIGHT, 100)
y = functions[function_selector.active](x)
curve_values.data = {"x": x, "y": y}

xs, ys = calculate_new_secant_value_pairs(function_selector.active,
        point_slider.value, spacing_slider.value)
secant_line_values.data = {
        "xs": xs,
        "ys": ys,
        "color" : ["orange", "purple"],
        "line_width": [SECANT_LINE_WIDTH, SECANT_LINE_WIDTH],
        }

x, y = calculate_new_dot_positions(function_selector.active, point_slider.value,
        spacing_slider.value)
dot_values.data = {"x": x, "y": y}


# Defining the javascript code of the callbacks
selector_callback = CustomJS(args={
        "function_selector": function_selector,
        "spacing_slider": spacing_slider,
        "curve_values": curve_values,
        },
        code="""
            var active_function = function_selector.active;

            // Define the function pointer list similar to Python one
            var functions = [
                (ele) => {return Math.exp(- Math.pow(ele - 1, 2))},
                (ele) => {return Math.abs(ele)},
                function(ele) {
                    if (ele < 1) {
                        return 1/3 * Math.pow(ele, 2);
                    } else {
                        return -ele + 4/3;
                    }
                }
            ];

            // Fetch the data of the ColumnDataSource, use its linearly spaced x
            // values and compute the new values
            var data = curve_values.data;
            var x = data['x'];
            var y = data['y'];
            //y = x.map(functions[active_function]);
            for (var i=0; i<x.length; i++) {
                y[i] = functions[active_function](x[i])
            }
            // Flush the new values to be drawn
            curve_values.change.emit();

            // Manipulate the value of the spacing_slider so that its js
            // callback is fired and the data of the secants and the dots gets
            // updated to the function
            if (spacing_slider.value === spacing_slider.end) {
                spacing_slider.value = spacing_slider.end - spacing_slider.step;
            } else {
                spacing_slider.value += spacing_slider.step;
            }
            """
        )

slider_callback = CustomJS(args={
        "function_selector": function_selector,
        "point_slider": point_slider,
        "spacing_slider": spacing_slider,
        "secant_line_values": secant_line_values,
        "dot_values": dot_values,
        "SECANT_LINE_WIDTH": SECANT_LINE_WIDTH,
        "ADDITIONAL_LENGTH": ADDITIONAL_LENGTH,
        "EPSILON": EPSILON,
        },
        code="""
            var active_function = function_selector.active;
            var point_location = point_slider.value;
            var spacing = spacing_slider.value;

            // Define the function pointer list similar to Python one
            var functions = [
                (ele) => {return Math.exp(- Math.pow(ele - 1, 2))},
                (ele) => {return Math.abs(ele)},
                function(ele) {
                    if (ele < 1) {
                        return 1/3 * Math.pow(ele, 2);
                    } else {
                        return -ele + 4/3;
                    }
                }
            ];

            // The tree dots relevant for the two secant lines
            var x_positions = [point_location - (spacing + EPSILON),
                    point_location, point_location + (spacing + EPSILON)];
            var y_positions = x_positions.map(functions[active_function])

            //
            // Fill the first ColumnDataSource with the info 
            //
            dot_values.data["x"] = x_positions;
            dot_values.data["y"] = y_positions;
            dot_values.change.emit();


            // Calculating the secant components
            var slope_left_secant = (y_positions[1] - y_positions[0]) /
                    (x_positions[1] - x_positions[0] + EPSILON);
            var slope_right_secant = (y_positions[2] - y_positions[1]) /
                    (x_positions[2] - x_positions[1] + EPSILON);

            var offset_left_secant = y_positions[0] - slope_left_secant *
                    x_positions[0];
            var offset_right_secant = y_positions[1] - slope_right_secant *
                    x_positions[1];

            // Manipulate the x locations so that the secant lines are slightly 
            // longer than the points indicating their ends
            var left_length_offset = ADDITIONAL_LENGTH *
                    Math.cos(Math.atan(slope_left_secant));
            var x_left_secant = [
                    x_positions[0] - left_length_offset,
                    x_positions[1] + left_length_offset];
            
            var right_length_offset = ADDITIONAL_LENGTH *
                    Math.cos(Math.atan(slope_right_secant));
            var x_right_secant = [
                    x_positions[1] - right_length_offset,
                    x_positions[2] +  right_length_offset];

            // Construct the value pairs based on the two line parameters
            var y_left_secant = x_left_secant.map(ele => slope_left_secant *
                    ele + offset_left_secant);
            var y_right_secant = x_right_secant.map(ele => slope_right_secant *
                    ele + offset_right_secant);

            var xs = [x_left_secant, x_right_secant];
            var ys = [y_left_secant, y_right_secant];
            
            secant_line_values.data['xs'] = xs;
            secant_line_values.data['ys'] = ys;
            secant_line_values.data['color'] = ['orange', 'purple'];
            secant_line_values.data['line_width'] =
                    [SECANT_LINE_WIDTH, SECANT_LINE_WIDTH];
            secant_line_values.change.emit();
            """
        )


# Connect the widgets with their respective callbacks
for slider in (point_slider, spacing_slider, ):
    slider.js_on_change("value", slider_callback)

function_selector.js_on_change("active", selector_callback)

# Assemble the plot and create the html
inputs = WidgetBox(function_selector, point_slider, spacing_slider)
curdoc().add_root(Row(plot, inputs, width=WIDTH_TOTAL))
