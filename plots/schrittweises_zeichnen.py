import numpy as np

from bokeh.io import curdoc
from bokeh.layouts import row, widgetbox
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import Slider, RadioButtonGroup
from bokeh.plotting import figure

from extensions.Latex import LatexLabel
"""
This plot aids in understanding the step-by-step drawing necessary for more
complicated drawings, based on the understanding of simples concepts or
primitive functions
"""

# Geometry constants of the plot
HEIGHT = 400
WIDTH_PLOT = 600
WIDTH_TOTAL = 800

LINE_WIDTH_OLD = 2
LINE_WIDTH_CURRENT = 3

# The initial viewport the user starts in, the x interval is also used for the
# limits in which the function is drawn in
X_LEFT = -5
X_RIGHT = 5
Y_BOTTOM = -2
Y_TOP = 5

# How fine to discretize the interval in which the function are drawn in
NUMER_OF_POINTS = 300

# To insert a new function, create a new list with annonymous functions to
# represent the steps (up to 5) and a list with latex draw commands for them
# The indiciator is the short representation seen in the button list on the
# right top

# The first function is a general fractional function
indicator_1 = "$\\displaystyle\\frac{1}{\\sqrt{1+x^2}}$"
func_1 = [
        lambda x: x**2,
        lambda x: 1 + x**2,
        lambda x: np.sqrt(1 + x**2),
        lambda x: 1 / np.sqrt(1 + x**2)
        ]
label_1 = [
        "$x^2$",
        "$1 + x^2$",
        "$\\sqrt{1 + x^2}$",
        "$\\frac{1}{\\sqrt{1 + x^2}}$",
        ]

indicator_2 = "$\\displaystyle\\sin^2\\left(x+\\frac{\\pi}{2}\\right)$"
func_2 = [
        lambda x: np.sin(x),
        lambda x: np.sin(x + np.pi/2),
        lambda x: np.sin(x + np.pi/2)**2,
        ]
label_2 = [
        "$\\sin(x)$",
        "$\\sin\\left(x + \\frac{\\pi}{2}\\right)$",
        "$\\sin^2\\left(x + \\frac{\\pi}{2}\\right)$",
        ]

indicator_3 = "$\\displaystyle\\frac{1}{x^2 - 2}$"
func_3 = [
        lambda x: x**2,
        lambda x: x**2 - 2,
        lambda x: 1/(x**2 - 2),
        ]
label_3 = [
        "$x^2$",
        "$x^2 - 2$",
        "$\\frac{1}{x^2 - 2}$",
        ]

indicator_4 = "$\\displaystyle\\frac{{\\rm{e}}^x}{1 + {\\rm{e}}^x}$"
func_4 = [
        lambda x: np.exp(x),
        lambda x: 1 + np.exp(x),
        lambda x: 1/(1 + np.exp(x)),
        lambda x: np.exp(x) / (1 + np.exp(x))
        ]
label_4 = [
        "${\\rm{e}}^x$",
        "$1 + {\\rm{e}}^x$",
        "$\\frac{1}{1 + {\\rm{e}}^x}$",
        "$\\frac{{\\rm{e}}^x}{1 + {\\rm{e}}^x}$",
        ]


indicators = [indicator_1, indicator_2, indicator_3, indicator_4, ]
functions = [func_1, func_2, func_3, func_4, ]
labels = [label_1, label_2, label_3, label_4, ]

def update_data(function_active, step_selected, source):
    # Calculate the value pairs that are inserted into the ColumnDataSource
    # which then transfers them to the client
    x = np.linspace(X_LEFT, X_RIGHT, NUMER_OF_POINTS)
    y = functions[function_active][step_selected](x)
    source.data = {'x': x, 'y': y}


# Creating a ColumnDataSource to asynchronously send data to the client. Each
# ColumnDataSource represents the line data for a step in creating the final
# function. They have to be set back to an empty list, once a new function to
# draw is selected
step_1_source = ColumnDataSource(data={'x': [], 'y': []})
step_2_source = ColumnDataSource(data={'x': [], 'y': []})
step_3_source = ColumnDataSource(data={'x': [], 'y': []})
step_4_source = ColumnDataSource(data={'x': [], 'y': []})
step_5_source = ColumnDataSource(data={'x': [], 'y': []})
sources = [step_1_source, step_2_source, step_3_source, step_4_source,
        step_5_source]

plot = figure(plot_height=HEIGHT, plot_width=WIDTH_PLOT,
        x_range=[X_LEFT, X_RIGHT], y_range=[Y_BOTTOM, Y_TOP])
plot.toolbar.active_drag = None

# Indicate the x and y axis by seperate lines
plot.line([-10, 10], [0, 0], color="black")
plot.line([0, 0], [-10, 10], color="black")

# Generate five plots for up to five different steps 
plot.line('x', 'y', source=step_1_source, line_width=LINE_WIDTH_OLD,
        color="black")
plot.line('x', 'y', source=step_2_source, line_width=LINE_WIDTH_OLD,
        color="blue")
plot.line('x', 'y', source=step_3_source, line_width=LINE_WIDTH_OLD,
        color="green")
plot.line('x', 'y', source=step_4_source, line_width=LINE_WIDTH_OLD,
        color="orange")
plot.line('x', 'y', source=step_5_source, line_width=LINE_WIDTH_OLD,
        color="red")

function_selector = RadioButtonGroup(labels=indicators, height = 2em, active=0)
step_slider = Slider(title="Schritt", start=1, end=4, value=1, step=1)
# The latex label is an updated label that is connected with the katex latex
# engine. Since it is connected to the plot, it has to adjusted with respect to
# the bottom left corner of the plot measuring in screen units (=pixels)
step_function_latex = LatexLabel(text="f(x) = " +\
        labels[function_selector.active][0], x=WIDTH_PLOT+10, y=250,
        x_units="screen", y_units="screen", render_mode="css",
        text_font_size="14pt", background_fill_alpha=0)
plot.add_layout(step_function_latex)

# Call this routine first to populate the plot with the first step
update_data(0, 0, step_1_source)

def update_slider(attr, old, new):
    # The user decides to go back one step, then we have to clear the data for
    # previously highest step else we call the functions declaring the
    # intermediary steps and calculate the value pairs
    if old > new:
        sources[old].data = {'x': [], 'y': []}
    else:
        # use -1 since we have zero based indexing on the Python lists
        update_data(function_selector.active, new-1, sources[new])

    # Fill the latex label
    step_function_latex.text = "f(x) = " +\
            labels[function_selector.active][new-1]


def update_button(source):
    # Callback handler for switching the function (the top RadioButtonGroup)
    function_active = function_selector.active

    # The maximum steps are given by the function steps that are available
    # defined in the top of this script
    step_slider.end = len(functions[function_active])
    # Reset all data sources to empty lists so that nothing is drawn
    for source in sources:
        source.data = {'x': [], 'y': []}
    # Calculate the value pairs for the first step of the newly selected
    # function
    update_data(function_active, 0, step_1_source)
    # Fill the latex label with the formula for the first step
    step_function_latex.text = "f(x) = " + labels[function_active][0]
    # Whenever the function is changed the steps start back at the first
    step_slider.value = 1

# Link the widgets with their callback handlers
step_slider.on_change("value", update_slider)
function_selector.on_click(update_button)

# Create the html page for the plot by assembling widgets and plot canvas
inputs = widgetbox(function_selector, step_slider, )
curdoc().add_root(row(plot, inputs, width=WIDTH_TOTAL))
