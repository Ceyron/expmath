import numpy as np

from bokeh.io import curdoc
from bokeh.layouts import row, widgetbox
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import Slider
from bokeh.plotting import figure

from extensions.Latex import LatexLabel

'''
A ball is dropped so that it accelerates by the graviatational force of the
Earth. Instead of using Newtonian mechanics in which one would set up a balance
of forces and integrate to get the trajectory curve over time, we use Lagrangian
(or, similarily Hamiltonian,) machanis. Here, a energy functional is created
which is build upon the trajectory curve and its derivatives. Most of the time,
there are infinite solution functions that minize this functional, i.e., are a
weak solution to the corresponding partial differential equation. Minimizing can
be tideously done by the Gateaux Derivative which is not always possible, at
least analytically.  In this interactive plot we present one of the easiest
functional, the one of falling object and give different solutions each
complying with the boundary conditions and the requisites on differentiability.
Only one minimizes the functional.
'''

# Geometry constants of the plot
HEIGHT = 400
WIDTH_PLOT = 600
WIDTH_TOTAL = 800

# Precalculated values of the integral (used sympy)
numeric_values = [
        -1.0000,
        -1.0869,
        -1.1532,
        -1.2046,
        -1.2444,
        -1.2750,
        -1.2979,
        -1.3144,
        -1.3253,
        -1.3314,
        -1.3333,
        -1.3316,
        -1.3265,
        -1.3184,
        -1.3077,
        -1.2946,
        -1.2794,
        -1.2621,
        -1.2430,
        -1.2223,
        -1.2000,
        -1.1763,
        -1.1513,
        -1.1251,
        -1.0978,
        -1.0694,
        -1.0401,
        -1.0099,
        -0.9788,
        -0.9469,
        -0.9143,
        -0.8810,
        -0.8470,
        -0.8124,
        -0.7772,
        -0.7415,
        -0.7052,
        -0.6685,
        -0.6313,
        -0.5936,
        -0.5556,
        -0.5171,
        -0.4782,
        -0.4390,
        -0.3995,
        -0.3596,
        -0.3194,
        -0.2789,
        -0.2382,
        -0.1971,
        -0.1558,
        ]

def update_data(function_selector, plot_values, numeric_value_label,
        function_label):
    t = np.linspace(0, 1, 100)
    y = 1 - t**function_selector.value
    plot_values.data = {"t": t, "y": y}

    numeric_value_label.text =\
            "J(y) = \int_{0}^{1} \dot{y}^2 - 4 y \; \mathrm{d} t \\approx " +\
            str(round(numeric_values[int((function_selector.value - 1)*10)], 4))
    function_label.text = "y(t) = 1 - t^{" + str(function_selector.value) + "}"


# ColumnDataSource abstract the sending of new information to the client
plot_values = ColumnDataSource()

plot = figure(plot_height=HEIGHT, plot_width=WIDTH_PLOT, tools="", x_range=[-0.2, 1.2], y_range=[-0.5, 1.5])
plot.xaxis.axis_label="Zeit t"
plot.yaxis.axis_label="Höhe über Grund y"
plot.line(x="t", y="y", source=plot_values)

numeric_value_label = LatexLabel(text="", x=0.1, y=-0.1, render_mode="css",
        text_font_size="10pt", background_fill_alpha=0)
plot.add_layout(numeric_value_label)
function_label = LatexLabel(text="", x=0.1, y=1.0+0.2, render_mode="css",
        text_font_size="10pt", background_fill_alpha=0, text_color="blue")
plot.add_layout(function_label)

function_selector = Slider(title="Potenz des Polynoms", start=1, end=6,
        step=0.1, value=1)

# Defining callbacks
def update_slider(attr, old, new):
    update_data(function_selector, plot_values, numeric_value_label,
            function_label)

# Use callback in advance to populate the plot
update_slider(0, 0, 0)

# Connect the widgets with their respective callbacks
function_selector.on_change("value", update_slider)

# Assemble the plot and create the html
inputs = widgetbox(function_selector, )
curdoc().add_root(row(plot, inputs, width=WIDTH_TOTAL))
