import numpy as np

from bokeh.io import curdoc
from bokeh.layouts import row, widgetbox
from bokeh.models import ColumnDataSource, Band
from bokeh.models.ranges import Range
from bokeh.models.widgets import Slider, TextInput, RadioButtonGroup
from bokeh.plotting import figure

"""
This python file creates the interactive plot for a epsilon-tunnel
showing off the convergence properties and the epsilon criterion
for three different sequences

Run this file by bokeh serve
"""

# Defining all constant values TODO: Create a read-in routine from a file
HEIGHT = 400
WIDTH_PLOT = 600
WIDTH_TOTAL = 880 
SIZE_CIRCLE = 10
SPREADING_SLIDERS = 2.
MIN_WIDTH_TUNNEL = 0.05
def FUNC_1(x):
    return 1/x
def FUNC_2(x):
    return np.sqrt(x)
def FUNC_3(x):
    return np.sin(x)

def update_data(sequence_selector, numbers_slider, bounding_selector,
                top_slider, bottom_slider, nodes_in, nodes_out, line_top,
                line_bottom, band_source):
    # Extract the current data
    selected_sequence = sequence_selector.active
    numbers = int(numbers_slider.value)
    selected_type = bounding_selector.active
    value_top = top_slider.value
    value_bottom = bottom_slider.value
    
    # Create new plotting values for the nodes depending on chosen sequence
    x_nodes = np.linspace(1, numbers, numbers)
    if selected_sequence == 0: # Harmonic Sequence
        y = FUNC_1(x_nodes)
    elif selected_sequence == 1: # Square-Root Sequence
        y = FUNC_2(x_nodes)
    elif selected_sequence == 2: # Sine Sequence
        y = FUNC_3(x_nodes)
    plot.x_range.end = int(1.1 * numbers)
    y_range = [int(np.min(y)) - 2, int(np.max(y)) + 2]
    plot.y_range.start = y_range[0]
    plot.y_range.end = y_range[1]
    
    # Create new plotting values for the bounding lines
    x_line = np.array([0, numbers+10])
    if selected_type == 0: # Konvergenz
        top_slider.title = "Grenzwert $a$"
        top_slider.start = y_range[0] + MIN_WIDTH_TUNNEL
        top_slider.end = y_range[1] - MIN_WIDTH_TUNNEL
        bottom_slider.title = "$\\varepsilon$"
        bottom_slider.start = 0.05
        bottom_slider.end = (y_range[1] - y_range[0])/2.1
        
        upper_line = value_top + value_bottom
        y_top = np.array([upper_line, upper_line])
        lower_line = value_top - value_bottom
        y_bottom = np.array([lower_line, lower_line])
    elif selected_type == 1: # Beschränktheit
        top_slider.title = "Obere Grenze"
        top_slider.start = value_bottom + MIN_WIDTH_TUNNEL
        top_slider.end = y_range[1] - MIN_WIDTH_TUNNEL
        bottom_slider.title = "Untere Grenze"
        bottom_slider.start = y_range[0] + MIN_WIDTH_TUNNEL
        bottom_slider.end = value_top - MIN_WIDTH_TUNNEL
        
        upper_line = value_top if value_top > value_bottom else value_bottom
        y_top = np.array([upper_line, upper_line])
        lower_line = value_bottom if value_bottom < value_top else value_top
        y_bottom = np.array([lower_line, lower_line])
    
    # Assign which values lie in the tunnel and which out of it
    x_out = []
    y_out = []
    x_in = []
    y_in = []
    for i in range(len(x_nodes)):
        if upper_line >= y[i] >= lower_line:
            x_in.append(x_nodes[i])
            y_in.append(y[i])
        else:
            x_out.append(x_nodes[i])
            y_out.append(y[i])
    
    # Update the referenced ColumDataSource
    nodes_in.data = {"x":x_in, "y":y_in}
    nodes_out.data = {"x":x_out, "y":y_out}
    line_top.data = {"x":x_line, "y":y_top}
    line_bottom.data = {"x":x_line, "y":y_bottom}
    band_source.data = {"x":x_line, "lower":y_bottom, "upper":y_top}


# The ColumnDataSource is an ajax like element that sends the new values
# calculated by the python backend callback function to the BokehJS within
# the browser
nodes_in = ColumnDataSource()
nodes_out = ColumnDataSource()
line_top = ColumnDataSource()
line_bottom = ColumnDataSource()
band_source = ColumnDataSource()

plot = figure(plot_height=HEIGHT, plot_width=WIDTH_PLOT,
              x_range=[0, 10], y_range=[-2, 2])
plot.toolbar.active_drag = None
plot.circle("x", "y", source=nodes_in, size=SIZE_CIRCLE, color="orange")
plot.circle("x", "y", source=nodes_out, size=SIZE_CIRCLE, color="black")
plot.line("x", "y", source=line_top, color="blue")
plot.line("x", "y", source=line_bottom, color="blue")
band = Band(base="x", lower="lower", upper="upper", source=band_source)
plot.add_layout(band)

# Define all occuring widgets
sequence_selector = RadioButtonGroup(
        labels=["Folge 1", "Folge 2", "Folge 3"], active=0)
numbers_slider = Slider(title="Anzahl der Folgenelemente", value=10, start=5,
                        end=50, step=1)
bounding_selector = RadioButtonGroup(
        labels=["Konvergenz", "Beschränktheit"], active=0)
top_slider = Slider(title="Grenzwert", value=1., step=0.01)
bottom_slider = Slider(title="Breite", value=0.5, step=0.01)
# The widget box is a representative for columm containing all widgets
inputs = widgetbox(sequence_selector, numbers_slider, bounding_selector,
                   top_slider, bottom_slider)

# Run the general callback once to initialize the plot
update_data(sequence_selector, numbers_slider, bounding_selector,
            top_slider, bottom_slider, nodes_in, nodes_out, line_top,
            line_bottom, band_source)

# Callback for all sliders
def update_slider(attr, old, new):
    update_data(sequence_selector, numbers_slider, bounding_selector,
            top_slider, bottom_slider, nodes_in, nodes_out, line_top,
            line_bottom, band_source)

# Callback for all buttons
def update_button(source):
    update_data(sequence_selector, numbers_slider, bounding_selector,
            top_slider, bottom_slider, nodes_in, nodes_out, line_top,
            line_bottom, band_source)

for slider in (numbers_slider, top_slider, bottom_slider):
    slider.on_change("value", update_slider)
for button in (sequence_selector, bounding_selector):
    button.on_click(update_button)

curdoc().add_root(row(plot, inputs, width=WIDTH_TOTAL))
curdoc().title = "Harmonische Folge"
