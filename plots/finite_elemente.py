import numpy as np

from bokeh.io import curdoc
from bokeh.layouts import row, widgetbox
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import Slider, RadioButtonGroup
from bokeh.plotting import figure

"""
Thiis plot presents a simple case in which a general solution to a differential
equation is lineary interpolated bewteen nodal values of linear-1D finitie
elements
"""

HEIGHT = 400
WIDTH_PLOT = 600
WIDTH_TOTAL = 800
SIZE_CIRCLE = 10

LEFT_X = 0
RIGHT_X = 4

# Quadratic function - e.g. the initial condition to 1D heat transfer problem
def FUNC_1(x):
    return -0.5*(x - 2)**2 + 2

# Linear function - e.g. trivial solution to a 1D heat transfer problem with
# non-homogeneous Dirichlet boundary conditions
def FUNC_2(x):
    return x

functions = [FUNC_1, FUNC_2, ]



def update_real_solution(function_selector, real_values):
    """
    Calculate the value pairs for the black 'analytical' solution
    """
    x = np.linspace(LEFT_X, RIGHT_X, 50)
    y = functions[function_selector.active](x)
    real_values.data = {
            "x": x,
            "y": y,
            }

def update_hats(function_selector, discretization_slider, hat_functions):
    """
    Calculate the values for the hat functions. We hereby use the multiline
    drawing tool. Therefore, transmitted data is a list of lists.
    """
    # Each base point (left or right foot and middle node) is shared by three
    # Finite Elements aside from the two the most right and the most left
    number_points = discretization_slider.value + 2

    x_set = np.linspace(LEFT_X, RIGHT_X, number_points)

    xs = []
    ys = []
    for i in range(discretization_slider.value):
        xs.append(x_set[i:i+3])
        ys.append([
                0.,
                functions[function_selector.active](xs[i][1]),
                0.,
                ])

    hat_functions.data = {
            "xs": xs,
            "ys": ys,
            }

def update_interpolated_and_dots(function_selector, discretization_Slider,
    interpolated_values):
    """
    Calcuate the values where the hat function's top hits the analytical
    solution (our elements are point-wise correct). This data is used for the
    orange dots and for the interpolated solution.
    """
    # Each base point (left or right foot and middle node) is shared by three
    # Finite Elements aside from the two the most right and the most left
    number_points = discretization_slider.value + 2

    x = np.linspace(LEFT_X, RIGHT_X, number_points)

    y = functions[function_selector.active](x)

    interpolated_values.data = {
        "x": x,
        "y": y
        }


# The ColumnDataSource objects abstract the interactive transmission of new data
# over the websocket protocol to the client
real_values = ColumnDataSource()
hat_functions = ColumnDataSource()
interpolated_values = ColumnDataSource()

plot = figure(plot_height=HEIGHT, plot_width=WIDTH_PLOT)
plot.line("x", "y", source=real_values, color="black", line_width=4)
plot.multi_line("xs", "ys", source=hat_functions, color="blue", line_width=3)
plot.line("x", "y", source=interpolated_values, color="orange")
plot.circle("x", "y", source=interpolated_values, size=SIZE_CIRCLE,
        color="orange")
# TODO: add band

function_selector = RadioButtonGroup(labels=["Funktion 1", "Funktion 2",],
        active=0)
discretization_slider = Slider(title="Anzahl an Finiten Elementen", start=1,
        end=25, value=3, step=1)

inputs = widgetbox(function_selector, discretization_slider)

# Call the handlers first to populate the plot
update_real_solution(function_selector, real_values)
update_hats(function_selector, discretization_slider, hat_functions)
update_interpolated_and_dots(function_selector, discretization_slider,
    interpolated_values)

def update_slider(attr, old, new):
    update_real_solution(function_selector, real_values)
    update_hats(function_selector, discretization_slider, hat_functions)
    update_interpolated_and_dots(function_selector, discretization_slider,
        interpolated_values) 

def switch_functions(source):
    update_real_solution(function_selector, real_values)
    update_hats(function_selector, discretization_slider, hat_functions)
    update_interpolated_and_dots(function_selector, discretization_slider,
        interpolated_values) 

# Assign callback handlers to events
discretization_slider.on_change("value", update_slider)
function_selector.on_click(switch_functions)

# Assemble the document and design the layout
curdoc().add_root(row(plot, inputs, width=WIDTH_TOTAL))
