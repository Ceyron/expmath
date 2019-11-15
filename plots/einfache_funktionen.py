import queue
import numpy as np

from bokeh.layouts import Row, WidgetBox
from bokeh.io import curdoc
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import Slider, Dropdown, Toggle
from bokeh.plotting import Figure

from extensions.Latex import LatexLabel

# Some functions are not defined for negative values or zero. Numpy will give
# out an warning. However, we simply don't want to draw this value. Therefore,
# we are going to ignore all values related to errors.
np.seterr(all="ignore") 

"""
This plot will introduce the user to basic functions and let them interactively
change parameter to them. The user can select between all major function groups:
    Polynomials
    Trigonometrics
    Exponentials
    Roots
    Logarithmns
    Hyperbolics
    Inverse Trigonometrics
    Inverse Hyperbolics
    Specials (Absolute, Heaviside ...)
"""

# Constants for the geometry of the plot, similar to other plots
HEIGHT = 400
WIDTH_PLOT = 600
WIDTH_TOTAL = 800

# Left-most and right-most points to still contain value pairs. They form the
# interval over which the function is drawn.
X_LEFT = -10
X_RIGHT = 10

# Initial vieport of the plot. The plain X by Y that the user sees intially.
X_RANGE_INITIAL = [-5, 5]
Y_RANGE_INTIAL = [-4, 4]

# Thickness of the function line
LINE_WIDTH = 2

# The way the function will appear in the dropdown menu. The key in the
# second element of every tuple is also used to address the dictionaries
# containing the implementation functions and the latex layout
dropdown_menu = [
        ("Konstantes Polynom", "constant"),
        ("Lineares Polynom", "linear"),
        ("Quadratisches Polynom", "quadratic"),
        ("Kubisches Polynom", "cubic"),
        None,
        ("Sinus", "sine"),
        ("Kosinus", "cosine"),
        ("Tangens", "tangent"),
        None,
        ("Allgemeine Exponentialfunktion", "exponential_general"),
        ("e-Funktion", "exponential"),
        None,
        ("Wurzel", "root"),
        ("Logarithmus", "logarithmn"),
        None,
        ("Sinus Hyperbolicus", "hyperbolic_sine"),
        ("Kosinus Hyperbolicus", "hyperbolic_cosine"),
        ("Tangens Hyperbolicus", "hyperbolic_tangent"),
        None,
        ("Arcus-Sinus", "arc_sine"),
        ("Arcus-Kosinus", "arc_cosine"),
        ("Arcus-Tangens", "arc_tangent"),
        None,
        ("Area Sinus Hyperbolicus", "area_hyperbolic_sine"),
        ("Area Kosinus Hyperbolicus", "area_hyperbolic_cosine"),
        ("Area Tangens Hyperbolicus", "area_hyperbolic_tangent"),
        None,
        ("Betragsfunktion", "absolute"),
        ("Heaviside Funktion", "heaviside"),
        ]

# Defaults are the values for what the sliders are set once this function gets
# selected
functions = {
        "constant": {
                "definition": (lambda a, b, c, d, x: a * np.ones(x.shape)),
                "latex": "f(x) = a = %1.2f",
                "number_of_placeholders": 1,
                "defaults": {"a": 1, "b": 0, "c": 0, "d": 0},
                },

        "linear": {
                "definition": (lambda a, b, c, d, x: a * x + b),
                "latex": "f(x) = ax + b = %1.2f x + %1.2f",
                "number_of_placeholders": 2,
                "defaults": {"a": 1, "b": 1, "c": 0, "d": 0},
                },

        "quadratic": {
                "definition": (lambda a, b, c, d, x: a * x**2 + b * x + c),
                "latex": """
                    \\begin{aligned}
                        f(x)
                        =&
                        ax^2 + bx + c
                        \\\\=&
                        %1.2f x^2 + %1.2f x + %1.2f
                    \end{aligned}
                    """,

                "number_of_placeholders": 3,
                "defaults": {"a": 1, "b": 0, "c": -1, "d": 0},
                },

        "cubic": {
                "definition": (lambda a, b, c, d, x:
                        a * x**3 + b * x**2 + c * x + d),
                "latex": """
                    \\begin{aligned}
                        f(x)
                        =&
                        ax^3 + bx^2 + cx + d
                        \\\\=&
                        %1.2f x^3 + %1.2f x^2 + %1.2f x + %1.2f
                    \end{aligned}
                    """,
                "number_of_placeholders": 4,
                "defaults": {"a": 1, "b": 0, "c": 0, "d": 0},
                },

        "sine": {
                "definition": (lambda a, b, c, d, x: a * np.sin(b*x + c) + d),
                "latex": """
                    \\begin{aligned}
                        f(x)
                        =&
                        a \cdot \sin(bx + c) + d
                        \\\\=&
                        %1.2f \cdot \sin(%1.2f x + %1.2f) + %1.2f
                    \end{aligned}
                    """,
                "number_of_placeholders": 4,
                "defaults": {"a": 1, "b": 1, "c": 0, "d": 0},
                },

        "cosine": {
                "definition": (lambda a, b, c, d, x: a * np.cos(b*x + c) + d),
                "latex": """
                    \\begin{aligned}
                        f(x)
                        =&
                        a \cdot \cos(bx + c) + d
                        \\\\=&
                        %1.2f \cdot \cos(%1.2f x + %1.2f) + %1.2f
                    \end{aligned}
                    """,
                "number_of_placeholders": 4,
                "defaults": {"a": 1, "b": 1, "c": 0, "d": 0},
                },

        "tangent": {
                "definition": (lambda a, b, c, d, x: a * np.tan(b*x + c) + d),
                "latex": """
                    \\begin{aligned}
                        f(x)
                        =&
                        a \cdot \\tan(bx + c) + d
                        \\\\=&
                        %1.2f \cdot \\tan(%1.2f x + %1.2f) + %1.2f
                    \end{aligned}
                    """,
                "number_of_placeholders": 4,
                "defaults": {"a": 1, "b": 1, "c": 0, "d": 0},
                },

        "exponential_general": {
                "definition": (lambda a, b, c, d, x: a * b**(x+c) + d),
                "latex": """
                    \\begin{aligned}
                        f(x)
                        =&
                        a \cdot b^{x+c} + d
                        \\\\=&
                        %1.2f \cdot %1.2f ^ {x +  %1.2f} + %1.2f
                    \end{aligned}
                    """,
                "number_of_placeholders": 4,
                "defaults": {"a": 1, "b": 2, "c": 0, "d": 0},
                },

        "exponential": {
                "definition": (lambda a, b, c, d, x: a * np.exp(b*(x+c)) + d),
                "latex": """
                    \\begin{aligned}
                        f(x)
                        =&
                        a e^{b(x+c)} + d
                        \\\\=&
                        %1.2f \cdot e^{%1.2f (x + %1.2f)} + %1.2f
                    \end{aligned}
                    """,
                "number_of_placeholders": 4,
                "defaults": {"a": 1, "b": 1, "c": 0, "d": 0},
                },

        "root": {
                "definition": (lambda a, b, c, d, x: a * (x + c)**(1/b) + d),
                "latex": """
                    \\begin{aligned}
                        f(x)
                        =&
                        a \sqrt[b]{x + c} + d
                        \\\\=&
                        %1.2f \sqrt[ %1.2f ]{x + %1.2f} + %1.2f
                    \end{aligned}
                    """,
                "number_of_placeholders": 4,
                "defaults": {"a": 1, "b": 2, "c": 0, "d": 0},
                },

        "logarithmn": {
                "definition": (lambda a, b, c, d, x: a * np.log(b*(x+c)) + d),
                "latex": """
                    \\begin{aligned}
                        f(x)
                        =&
                        a \ln(b(x+c)) + d
                        \\\\=&
                        %1.2f \ln(%1.2f (x + %1.2f)) + %1.2f
                    \end{aligned}
                    """,
                "number_of_placeholders": 4,
                "defaults": {"a": 1, "b": 1, "c": 0, "d": 0},
                },

        "hyperbolic_sine": {
                "definition": (lambda a, b, c, d, x: a * np.sinh(b*x + c) + d),
                "latex": """
                    \\begin{aligned}
                        f(x)
                        =&
                        a \sinh(bx + c) + d
                        \\\\=&
                        %1.2f \sinh(%1.2f x + %1.2f) + %1.2f
                    \end{aligned}
                    """,
                "number_of_placeholders": 4,
                "defaults": {"a": 1, "b": 1, "c": 0, "d": 0},
                },
        
        "hyperbolic_cosine": {
                "definition": (lambda a, b, c, d, x: a * np.cosh(b*x + c) + d),
                "latex": """
                    \\begin{aligned}
                        f(x)
                        =&
                        a \cosh(bx + c) + d
                        \\\\=&
                        %1.2f \cosh(%1.2f x + %1.2f) + %1.2f
                    \end{aligned}
                    """,
                "number_of_placeholders": 4,
                "defaults": {"a": 1, "b": 1, "c": 0, "d": 0},
                },

        "hyperbolic_tangent": {
                "definition": (lambda a, b, c, d, x: a * np.tanh(b*x + c) + d),
                "latex": """
                    \\begin{aligned}
                        f(x)
                        =&
                        a \\tanh(bx + c) + d
                        \\\\=&
                        %1.2f \\tanh(%1.2f x + %1.2f) + %1.2f
                    \end{aligned}
                    """,
                "number_of_placeholders": 4,
                "defaults": {"a": 1, "b": 1, "c": 0, "d": 0},
                },

        "arc_sine": {
                "definition": (lambda a, b, c, d, x:
                    a * np.arcsin(b*x + c) + d),
                "latex": """
                    \\begin{aligned}
                        f(x)
                        =&
                        a \\arcsin(bx + c) + d
                        \\\\=&
                        %1.2f \\arcsin(%1.2f x + %1.2f) + %1.2f
                    \end{aligned}
                    """,
                "number_of_placeholders": 4,
                "defaults": {"a": 1, "b": 1, "c": 0, "d": 0},
                },

        "arc_cosine": {
                "definition": (lambda a, b, c, d, x:
                    a * np.arccos(b*x + c) + d),
                "latex": """
                    \\begin{aligned}
                        f(x)
                        =&
                        a \\arccos(bx + c) + d
                        \\\\=&
                        %1.2f \\arccos(%1.2f x + %1.2f) + %1.2f
                    \end{aligned}
                    """,
                "number_of_placeholders": 4,
                "defaults": {"a": 1, "b": 1, "c": 0, "d": 0},
                },

        "arc_tangent": {
                "definition": (lambda a, b, c, d, x:
                    a * np.arctan(b*x + c) + d),
                "latex": """
                    \\begin{aligned}
                        f(x)
                        =&
                        a \\arctan(bx + c) + d
                        \\\\=&
                        %1.2f \\arctan(%1.2f x + %1.2f) + %1.2f
                    \end{aligned}
                    """,
                "number_of_placeholders": 4,
                "defaults": {"a": 1, "b": 1, "c": 0, "d": 0},
                },

        "area_hyperbolic_sine": {
                "definition": (lambda a, b, c, d, x:
                    a * np.arcsinh(b*x + c) + d),
                "latex": """
                    \\begin{aligned}
                        f(x)
                        =&
                        a \\text{ arsinh}(bx + c) + d
                        \\\\=&
                        %1.2f \\text{ arsinh}(%1.2f x + %1.2f) + %1.2f
                    \end{aligned}
                    """,
                "number_of_placeholders": 4,
                "defaults": {"a": 1, "b": 1, "c": 0, "d": 0},
                },

        "area_hyperbolic_cosine": {
                "definition": (lambda a, b, c, d, x:
                    a * np.arccosh(b*x + c) + d),
                "latex": """
                    \\begin{aligned}
                        f(x)
                        =&
                        a \\text{ arcosh}(bx + c) + d
                        \\\\=&
                        %1.2f \\text{ arcosh}(%1.2f x + %1.2f) + %1.2f
                    \end{aligned}
                    """,
                "number_of_placeholders": 4,
                "defaults": {"a": 1, "b": 1, "c": 0, "d": 0},
                },

        "area_hyperbolic_tangent": {
                "definition": (lambda a, b, c, d, x:
                    a * np.arctanh(b*x + c) + d),
                "latex": """
                    \\begin{aligned}
                        f(x)
                        =&
                        a \\text{ artanh}(bx + c) + d
                        \\\\=&
                        %1.2f \\text{ artanh}(%1.2f x + %1.2f) + %1.2f
                    \end{aligned}
                    """,
                "number_of_placeholders": 4,
                "defaults": {"a": 1, "b": 1, "c": 0, "d": 0},
                },

        "absolute": {
                "definition": (lambda a, b, c, d, x: a * np.abs(b*x + c) + d),
                "latex": """
                    \\begin{aligned}
                        f(x)
                        =&
                        a |bx + c | + d
                        \\\\=&
                        %1.2f |%1.2f x + %1.2f | + %1.2f
                    \end{aligned}
                    """,
                "number_of_placeholders": 4,
                "defaults": {"a": 1, "b": 1, "c": 0, "d": 0},
                },

        "heaviside": {
                "definition": (lambda a, b, c, d, x: 
                        a * np.piecewise(x, [x < b, b <= x], [0, 1]) + c),
                "latex": """
                    \\begin{aligned}
                        f(x) =& a + b \cdot
                        \\begin{cases}
                            0 & x < c \\\\
                            1 & x \ge c
                        \end{cases}
                        \\\\=& %1.2f + %1.2f \cdot
                        \\begin{cases}
                            0 & x < %1.2f \\\\
                            1 & x \ge c
                        \end{cases}
                    \end{aligned}""",
                "number_of_placeholders": 3,
                "defaults": {"a": 1, "b": 0, "c": 0, "d": 0}
                },



    }


def update_plot(function_active, a, b, c, d):
    x = np.linspace(X_LEFT, X_RIGHT, 400)
    y = functions[function_active]["definition"](a, b, c, d, x)

    return x, y


def update_latex(function_active, a, b, c, d):
    unformatted_string = functions[function_active]["latex"]
    number_of_placeholders =\
            functions[function_active]["number_of_placeholders"]

    formatted_string = ""
    if number_of_placeholders == 1:
        formatted_string = unformatted_string % a
    elif number_of_placeholders == 2:
        formatted_string = unformatted_string % (a, b)
    elif number_of_placeholders == 3:
        formatted_string = unformatted_string % (a, b, c)
    elif number_of_placeholders == 4:
        formatted_string = unformatted_string % (a, b, c, d)

    return formatted_string


# The ColumnDataSource abstracts the sending of value pairs to the client.
# Whenever the data attribute changes the new information is sent over the open
# WebSocket
data_source = ColumnDataSource()
data_source_second = ColumnDataSource(data={"x": [], "y": []})

plot = Figure(plot_height=HEIGHT, plot_width=WIDTH_PLOT,
        x_range=X_RANGE_INITIAL, y_range=Y_RANGE_INTIAL)
plot.toolbar.active_drag = None
# Get the same tick (grid lines) depth for both axes
plot.xaxis[0].ticker.desired_num_ticks =\
        2*plot.yaxis[0].ticker.desired_num_ticks

# Indicate the x-axis and y_axis by thin black lines
plot.line(x=[X_LEFT, X_RIGHT], y=[0, 0], color="black")
plot.line(x=[0, 0], y=[X_LEFT, X_RIGHT], color="black")

# The first function is plotted right away, the second will be visible, once the
# toggle is activated
plot.line(x="x", y="y", source=data_source, color="blue", line_width=LINE_WIDTH)
plot.line(x="x", y="y", source=data_source_second, color="red",
        line_width=LINE_WIDTH)

function_selector = Dropdown(label="Funktion auswählen", button_type="warning",
        menu = dropdown_menu, value="constant")

parameter_a = Slider(title="Parameter a", start=-2, end=2, step=0.1, value=1)
parameter_b = Slider(title="Parameter b", start=-2, end=2, step=0.1, value=1)
parameter_c = Slider(title="Parameter c", start=-2, end=2, step=0.1, value=1)
parameter_d = Slider(title="Parameter d", start=-2, end=2, step=0.1, value=1)
parameter_sliders = (parameter_a, parameter_b, parameter_c, parameter_d)

# This toggle is used to activate a second function and once it is activated to
# switch between controling the first and the second function
second_toggle = Toggle(label="Zweite Funktion g (de-)aktivieren")

# Lable extension rendered by the help of KaTex on the client-side
function_latex = LatexLabel(text = "", x = WIDTH_PLOT - 20, y = 80,
        x_units="screen", y_units="screen", render_mode="css",
        text_font_size="12pt", background_fill_alpha=0)
plot.add_layout(function_latex)
function_latex_second = LatexLabel(text = "", x = WIDTH_PLOT - 20, y = 30,
        x_units="screen", y_units="screen", render_mode="css",
        text_font_size="12pt", background_fill_alpha=0)
plot.add_layout(function_latex_second)


def update_all():
    """
    General Update Routine: Read widget values, calculate value pairs and update
    the the Latex Label.
    """
    x, y = update_plot(function_selector.value, parameter_a.value,
            parameter_b.value, parameter_c.value, parameter_d.value)
    if not second_toggle.active:
        data_source.data = {"x": x, "y": y}
    else:
        data_source_second.data = {"x": x, "y": y}

    text_for_label = update_latex(function_selector.value,
            parameter_a.value, parameter_b.value, parameter_c.value,
            parameter_d.value)

    if not second_toggle.active:
        function_latex.text = text_for_label
    else:
        text_for_label_second = text_for_label.replace("f(x)", "g(x)")
        function_latex_second.text = text_for_label_second


def update_slider(attr, old, new):
    update_all()


def update_dropdown(attr, old, new):
    """
    Similar to the one used above but also reset the sliders to the defaults for
    the selected function.
    """
    new_defaults = functions[function_selector.value]["defaults"]
    parameter_a.value = new_defaults["a"]
    parameter_b.value = new_defaults["b"]
    parameter_c.value = new_defaults["c"]
    parameter_d.value = new_defaults["d"]

    update_all()


# When the user switches between the two functions remember the values of the
# widgets
saved_parameters_from_other_function = queue.Queue(2)
# Standard parameters for the second function are similar to those for the first
saved_parameters_from_other_function.put({
    "function_active": "constant",
    "a": 2,
    "b": 0,
    "c": 0,
    "d": 0,
    })

def toggle_callback(source):
    global saved_parameters_from_other_function

    current_parameter = {
            "function_active": function_selector.value,
            "a": parameter_a.value,
            "b": parameter_b.value,
            "c": parameter_c.value,
            "d": parameter_d.value
            }
    saved_parameters_from_other_function.put(current_parameter)
    
    previous_parameter = saved_parameters_from_other_function.get()
    function_selector.value = previous_parameter["function_active"]
    parameter_a.value = previous_parameter["a"]
    parameter_b.value = previous_parameter["b"]
    parameter_c.value = previous_parameter["c"]
    parameter_d.value = previous_parameter["d"]

    update_all()


# Call the callback function in advance to populate the plot
update_all()

# Connect the callbacks with the corresponding wigets
for slider in parameter_sliders:
    slider.on_change("value", update_slider)

function_selector.on_change("value", update_dropdown)

second_toggle.on_click(toggle_callback)


# Assemble the plot
inputs = WidgetBox(function_selector, *parameter_sliders, second_toggle)

curdoc().add_root(Row(plot, inputs, width=WIDTH_TOTAL))

