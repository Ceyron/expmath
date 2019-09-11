import numpy as np

from bokeh.io import curdoc
from bokeh.layouts import Row, WidgetBox
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import Slider, RadioButtonGroup, Toggle
from bokeh.plotting import Figure

"""
This plot compares sequences and their partial sums. It will help the user
understand the difference and relation between both. The user can also examine
the convergence properties of the series.
"""

# Geometry constants of the plot
HEIGHT = 400
WIDTH_PLOT = 300
WIDTH_TOTAL = 800

# Defining the viewport height the user will start in
Y_BOTTOM = -1.5
Y_TOP = 5.5

SIZE_CIRCLE = 6
WIDTH_BAR = 0.3

# This also corresponds to the number of dots and bars that are drawn
MAX_NATURAL_NUMBERS = 20

# Set this to true if you want that, e.g., 10 pixels on the x-axis correspond to
# the same value-difference like 10 pixels on the y-axis
MATCH_ASPECT = False

# Harmonic sequence converges against 0 but its series diverges
def SEQUENCE_1(x, a):
    return a*1/x

# Special case of the Riemann sequence converges against 0, its series converges
# against pi**2/6 (Dirichlet series)
def SEQUENCE_2(x, a):
    return a*1/x**2

# Geometric sequence and series, if the absolute of the fraction is smaller than
# 1 the sequence converges against 0 and the series of it also converges against
# a value that is dependent on a
def SEQUENCE_3(x, a):
    return (1/a)**x

# Sinus sequence to show of a series of an oscillating sequence
def SEQUENCE_4(x, a):
    return np.sin(a * x)


SEQUENCES = [SEQUENCE_1, SEQUENCE_2, SEQUENCE_3, SEQUENCE_4, ]
NAMES = ["1/k", "1/k^2", "(1/a)^k", "sin(a*k)"]
# Use Dirichlet series as convergent majorant and Harmonic series and divergent
# minorant
CRITERIA = [SEQUENCE_2, SEQUENCE_1]

def update_sequence(sequence_selector, number_slider, parameter_slider,
        sequence_source):
    """
    Calculates the value pairs for the circles/dots of currently active sequence
    until the the limit defined by the number_slider.
    """
    x = np.linspace(1, number_slider.value, number_slider.value)
    a = parameter_slider.value
    if(sequence_selector.active in (0, 1)):
        a = 1.

    y = SEQUENCES[sequence_selector.active](x, a)
    sequence_source.data = {"x": x, "y": y}

def update_series(sequence_selector, number_slider, parameter_slider,
        series_source, shift_left):
    """
    Calculates the bar heights that shall indicate the partial sum of the series
    until the given point.
    """
    x = np.linspace(1, number_slider.value, number_slider.value)
    a = parameter_slider.value
    # The parameter within this given sequence should only be used for the
    # convergence aid sequence (convergen majorant and divergent minorant)
    if(sequence_selector.active in (0, 1)):
        a = 1.

    sums = 0.
    heights = []
    for pos in x:
        sums += SEQUENCES[sequence_selector.active](pos, a)
        heights.append(sums)

    # Shift to left if convergence aid is active so that they fit next to each
    # other
    if shift_left:
        x -= WIDTH_BAR / 2.

    series_source.data = {
            "x_center": x,
            "height" : heights}

def update_convergence_aid_sequence(number_slider,
        convergence_aid_selector, convergence_aid_parameter_slider,
        convergence_aid_sequence_source):
    """
    Similar to the regular sequence, this function calculates the value pairs
    for the dots/circles to be drawn upon.
    """
    x = np.linspace(1, number_slider.value, number_slider.value)
    a = convergence_aid_parameter_slider.value

    y = CRITERIA[convergence_aid_selector.active](x, a)
    convergence_aid_sequence_source.data = {"x": x, "y": y}

def update_convergence_aid_series(number_slider, convergence_aid_selector,
        convergence_aid_parameter_slider, convergence_aid_series_source):
    """
    Similar to the regular sequence, this function calcutes the bar heights
    representing the partial sum of the convergence aid sequence.
    """
    x = np.linspace(1, number_slider.value, number_slider.value)

    a_aid = convergence_aid_parameter_slider.value
    sums = 0.
    heights = []
    for pos in x:
        sums += CRITERIA[convergence_aid_selector.active](pos, a_aid)
        heights.append(sums)

    # Shift to the right so that both bars fit next to each other
    x += WIDTH_BAR / 2.

    convergence_aid_series_source.data = {
            "x_center": x,
            "height": heights}


# ColumnDataSource represents an abstraction for the data transmission to the
# Client over the Websocket protocol
sequence_source = ColumnDataSource()
series_source = ColumnDataSource()

# This ColumnDataSource are used for convergence aid sequence (convergent
# majorant and divergent minorant). By default, the user has to activate
# additional options and then activate this aid. Therefore, the data source
# stays empty when the plot is first drawn so that nothing will appear.
convergence_aid_sequence_source = ColumnDataSource(data={
        "x": [], "y": []})
convergence_aid_series_source = ColumnDataSource(data={
        "x_center": [], "height": []})

# Two different plots. The one on the left shows the sequence by the help of
# dots/circles. The one on the right plots bars that represent the partial sum
# of the sequence until the given point.
plot_left = Figure(plot_height=HEIGHT, plot_width=WIDTH_PLOT,
        y_range=[Y_BOTTOM, Y_TOP], title="Folge")
plot_left.toolbar.active_drag = None
plot_right = Figure(plot_height=HEIGHT, plot_width=WIDTH_PLOT,
        y_range=[Y_BOTTOM, Y_TOP], title="Partialsummen zu dieser Folge")
plot_right.toolbar.active_drag = None

plot_left.circle("x", "y", source=sequence_source, size=SIZE_CIRCLE,
        color="blue")
plot_left.circle("x", "y", source=convergence_aid_sequence_source,
        size=SIZE_CIRCLE, color="red")
plot_right.vbar(x="x_center", width=WIDTH_BAR, top="height",
        source=series_source, color="blue")
plot_right.vbar(x="x_center", width=WIDTH_BAR, top="height",
        source=convergence_aid_series_source, color="red")

sequence_selector = RadioButtonGroup(labels=NAMES, active=0)
number_slider = Slider(title="Anzahl an natürlichen Zahlen", start=1,
        end=MAX_NATURAL_NUMBERS, value=4, step=1)

# This button will toggle the visibility of 'advanced' options (all the
# widgets that have visibility=False in their arguments
advanded_toggle = Toggle(label="Erweiterte Widgets aktivieren")

parameter_slider = Slider(title="Parameter a", start=-5., end=5., value=2.,
        step=0.1, visible=False)

convergence_aid_toggle = Toggle(label="Konvergenzkriterien aktivieren",
        visible=False)
convergence_aid_selector = RadioButtonGroup(labels=["Konvergente Majorante",
    "Divergente Minorante"], active=0, visible=False)
convergence_aid_parameter_slider = Slider(title="Skalieren der Hilfe",
        start=0.5, end=3., value=1., step=0.1, visible=False)


inputs = WidgetBox(sequence_selector, number_slider, advanded_toggle,
        parameter_slider, convergence_aid_toggle, convergence_aid_selector,
        convergence_aid_parameter_slider)

# Call calculation in advance in order to populate the plot
update_sequence(sequence_selector, number_slider, parameter_slider,
        sequence_source)
update_series(sequence_selector, number_slider, parameter_slider, series_source,
        False)

# Define the callback handler for the slider
def update_slider(attr, old, new):
    update_sequence(sequence_selector, number_slider, parameter_slider,
            sequence_source)
    # Delete all previous data for the convergence aid so that nothing will be
    # displayed if the toggle is switched back off
    convergence_aid_sequence_source.data = {"x": [], "y": []}
    convergence_aid_series_source.data = {"x_center": [], "height": []}
    # Only call these update routines if the convergence aid is selected
    if(convergence_aid_toggle.active):
        update_convergence_aid_sequence(number_slider, convergence_aid_selector,
                convergence_aid_parameter_slider,
                convergence_aid_sequence_source)
        update_convergence_aid_series(number_slider, convergence_aid_selector,
                convergence_aid_parameter_slider, convergence_aid_series_source)
        update_series(sequence_selector, number_slider, parameter_slider,
                series_source, True)
    else:
        # This calls the update routine with the False flag so that the bars are
        # not shiftes to the left
        update_series(sequence_selector, number_slider, parameter_slider,
                series_source, False)


# Similar to the one above
def update_button(source):
    update_sequence(sequence_selector, number_slider, parameter_slider,
            sequence_source)
    # Delete all previous data for the convergence aid so that nothing will be
    # displayed if the toggle is switched back off
    convergence_aid_sequence_source.data = {"x": [], "y": []}
    convergence_aid_series_source.data = {"x_center": [], "height": []}
    if(convergence_aid_toggle.active):
        update_convergence_aid_sequence(number_slider, convergence_aid_selector,
                convergence_aid_parameter_slider,
                convergence_aid_sequence_source)
        update_convergence_aid_series(number_slider, convergence_aid_selector,
                convergence_aid_parameter_slider, convergence_aid_series_source)
        update_series(sequence_selector, number_slider, parameter_slider,
                series_source, True)
    else:
        update_series(sequence_selector, number_slider, parameter_slider,
                series_source, False)


def toggle_advaned_controls(source):
    """
    This callback handler sets the visibility for the 'advanced' widgets in
    order to not overwhelm the user in the first place
    """
    for advanced_widgets in (parameter_slider, convergence_aid_toggle,
            convergence_aid_selector, convergence_aid_parameter_slider):
        advanced_widgets.visible = True
    advanded_toggle.visible = False

# Connect all widgets' events with their corresponding callback handlers
for slider in (number_slider, parameter_slider,
        convergence_aid_parameter_slider):
    slider.on_change("value", update_slider)

for button in (sequence_selector, convergence_aid_toggle,
        convergence_aid_selector):
    button.on_click(update_button)

advanded_toggle.on_click(toggle_advaned_controls)

# Assemble the plot
curdoc().add_root(Row(plot_left, plot_right, inputs, width=WIDTH_TOTAL))
