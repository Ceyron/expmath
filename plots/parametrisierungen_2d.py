import numpy as np

from bokeh.io import curdoc
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import RangeSlider, Slider, RadioButtonGroup, Toggle
from bokeh.layouts import WidgetBox, Row, Column
from bokeh.plotting import Figure

from extensions.Latex import LatexLabel

"""
This plot visualizes the concept of parameterized lines in two dimensions, i.e.,
a vector field with a one-dimensional inputs, which vector tips form a curve
through space.
The user can choose between functions to model the x and y component of the
parameterization. Sliders are used to adjust the parameters of this function. A
RangeSlider sets the interval for the parameter input for the curve to be drawn
upon.
"""

# Geometry constants for the plot
HEIGHT = 400
WIDTH_PLOT = 400
WIDTH_TOTAL = 800

# Define the initial viewport of the canvas the user starts in
X_LEFT = -3
X_RIGHT = 3
Y_BOTTOM = -3
Y_TOP = 3

# Thickness and color for the parameterized curve and the straight lines
# indicating the axes
LINE_WIDTH_LINE = 2
COLOR_LINE = "blue"
LINE_WIDTH_AXIS = 1
COLOR_AXIS = "black"

# Discretization used on the t-axis
NUM_T_POINTS = 100


def CONSTANT(a, b, t):
    return a * np.ones(t.shape)

# Uses only one argument that has to formatted. However, for generalization
# second parameter is also rendered and later removed. Therefore all other latex
# have to have a space at last position
CONSTANT_LATEX = " %1.2f %0.0f"

def LINEAR(a, b, t):
    return a * t + b

LINEAR_LATEX = " %1.2f t + %1.2f "

def SINE(a, b, t):
    return a * np.sin(b*t)

SINE_LATEX = " %1.2f \sin(%1.2f t) "

def COSINE(a, b, t):
    return a * np.cos(b*t)

COSINE_LATEX = " %1.2f \cos(%1.2f t) "


functions = [CONSTANT, LINEAR, SINE, COSINE]
latex = [CONSTANT_LATEX, LINEAR_LATEX, SINE_LATEX, COSINE_LATEX]
names_x = ["a", "a*t+b", "a*sin(b*t)", "a*cos(b*t)", ]
names_y = ["c", "c*t+d", "c*sin(d*t)", "c*cos(d*t)", ]


def calculate_new_value_pairs(x_active, x_a, x_b, y_active, y_c, y_d, t_start,
        t_end):
    t = np.linspace(t_start, t_end, NUM_T_POINTS)
    x = functions[x_active](x_a, x_b, t)
    y = functions[y_active](y_c, y_d, t)
    return x, y

def create_latex(x_active, x_a, x_b, y_active, y_c, y_d, t_start, t_end):
    # Strip the last character, since in the case of the constant function only
    # one parameter is necessary but for two are rendered for generality
    x_function = (latex[x_active] % (x_a, x_b))[:-1]
    y_function = (latex[y_active] % (y_c, y_d))[:-1]
    combined = """
        \\vec{\gamma}(t) = 
        \\begin{pmatrix}
            %s \cr
            %s
        \end{pmatrix}
        ,
        \quad
        t \in (%1.2f, %1.2f)
        """ % (x_function, y_function, t_start, t_end)
    return combined



# ColumnDataSource abstracts the sending of new value pairs to the client over
# the WebSocket protocol
line_source = ColumnDataSource()

plot = Figure(plot_height=HEIGHT, plot_width=WIDTH_PLOT,
        x_range=[X_LEFT, X_RIGHT], y_range=[Y_BOTTOM, Y_TOP])
plot.toolbar.active_drag = None
# Indicate the x-axis and the y-axis
plot.line(x=[-100, 100], y=[0, 0], line_width=LINE_WIDTH_AXIS, color=COLOR_AXIS)
plot.line(x=[0, 0], y=[-100, 100], line_width=LINE_WIDTH_AXIS, color=COLOR_AXIS)

plot.line(x="x", y="y", source=line_source, line_width=LINE_WIDTH_LINE,
        color=COLOR_LINE)

x_function_selector = RadioButtonGroup(name="Typ für x", labels=names_x,
        active=3)
y_function_selector = RadioButtonGroup(name="Typ für y", labels=names_y,
        active=2)

# The parameter slider are hidden in the first place
parameter_toggle = Toggle(label="Parameter-Slider hinzuschalten")

x_parameter_a = Slider(title="Parameter a für x", start=-2, end=2, step=0.1,
        value=1, visible=False)
x_parameter_b = Slider(title="Parameter b für x", start=-2, end=2, step=0.1,
        value=1, visible=False)
y_parameter_c = Slider(title="Parameter c für y", start=-2, end=2, step=0.1,
        value=-1, visible=False)
y_parameter_d = Slider(title="Parameter d für y", start=-2, end=2, step=0.1,
        value=2, visible=False)

parameter_t = RangeSlider(title="Bereich der Parametrisierung", start=-5, end=5,
        step=0.1, value=(2, 5))

function_definition = LatexLabel(text="", x=WIDTH_PLOT, y = 80,
        x_units="screen", y_units="screen", render_mode="css",
        text_font_size="12pt", background_fill_alpha=0)
plot.add_layout(function_definition)


# Callback handlers
def update_data(attr, old, new):
    x, y = calculate_new_value_pairs(x_function_selector.active,
            x_parameter_a.value, x_parameter_b.value,
            y_function_selector.active, y_parameter_c.value,
            y_parameter_d.value, parameter_t.value[0], parameter_t.value[1])

    line_source.data = {"x": x, "y": y}

    text = create_latex(x_function_selector.active,
            x_parameter_a.value, x_parameter_b.value,
            y_function_selector.active, y_parameter_c.value,
            y_parameter_d.value, parameter_t.value[0], parameter_t.value[1])
    function_definition.text = text

def selector_callback(source):
    update_data(0, 0, 0)

def toggle_callback(source):
    parameter_toggle.visible = False
    x_parameter_a.visible = True
    x_parameter_b.visible = True
    y_parameter_c.visible = True
    y_parameter_d.visible = True


# Call callback in advance to populate the plot
update_data(0, 0, 0)


# Connect the widgets with their respective callbacks
for slider in (x_parameter_a, x_parameter_b, y_parameter_c, y_parameter_d,
        parameter_t):
    slider.on_change("value", update_data)

for selector in (x_function_selector, y_function_selector):
    selector.on_click(selector_callback)

parameter_toggle.on_click(toggle_callback)


# Assemble the plot and create the html
inputs = WidgetBox(x_function_selector, y_function_selector, parameter_toggle,
        Row(Column(x_parameter_a, x_parameter_b),
            Column(y_parameter_c, y_parameter_d)), parameter_t)
curdoc().add_root(Row(plot, inputs, width=WIDTH_TOTAL))
