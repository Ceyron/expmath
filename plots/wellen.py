import numpy as np

from bokeh.io import curdoc
from bokeh.layouts import Row, WidgetBox
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import Slider, RadioButtonGroup, Toggle
from bokeh.plotting import Figure

"""
This plot visualizes how waves propagate by simulating the right-going and
left-going wave. The user can choose the initial condition, which will determine
the shape of both waves.
An advanced option is used to enable the intial condition on the first
derivative with respect to time.
"""

# Define sizing constants for the plot to neatly fit in the website
HEIGHT = 400
WIDTH_PLOT = 600
WIDTH_TOAL = 800

# Left-most and righ-most point for value pairs to still be calculated
LEFT_X = -10
RIGHT_X = 10

LINE_WIDTH = 2

# The zeroth initial condition (elongation at time zero)
INIT_0_1_indicator = "Glocke"
def INIT_0_1(x):
    return np.exp(-x**2)
INIT_0_2_indicator = "Hütchen"
def INIT_0_2(x):
    return np.piecewise(x,
            [x<-1, (-1 <= x) & (x < 0), (0 <= x) & (x < 1), 1<=x],
            [0, lambda ele: ele+1, lambda ele: -ele+1, 0])

indicators_0 = [INIT_0_1_indicator, INIT_0_2_indicator, ]
initials_0 = [INIT_0_1, INIT_0_2, ]

# The first initial condition (velocity/momentum at time zero)
INIT_1_1_indicator = "1/(1+e^(-x)) - 0,5"
def INIT_1_1_integrated(x):
    return 0.5*x + np.log(1 + np.exp(-x))
INIT_1_2_indicator = "1"
def INIT_1_2_integrated(x):
    return x
INIT_1_3_indicator = "x, x in (-1, 1)"
def INIT_1_3_integrated(x):
    return np.piecewise(x,
            [x < -1, (-1 <= x ) & (x < 1), 1 <=x],
            [0, lambda ele: 0.5 * ele**2, 0])
    
indicators_1 = [INIT_1_1_indicator, INIT_1_2_indicator, INIT_1_3_indicator]
initials_1_integrated = [INIT_1_1_integrated, INIT_1_2_integrated,
        INIT_1_3_integrated]


def update_data(init_0_active, speed, scale_0, time, init_1_active, scale_1):
    """
    This function calculates the value pairs for the plotted line to be drawn
    upon. It therefore uses the general solution to the wave propagation
    equation in one dimension:
    u(t,x) = 1/2 * (
        u_0(x + c*t) * u_0(x - c*t) + 1/c * (
            integral from (x - c*t) to (x + c*t) over u_1(l) dl
            )

    The integration of the first (u_1) initial condition is preworked in the
    function pointer list 'initials_1_integrated'. Therefore, we only have to
    evaluate the antiderivate at the upper and lower boundary of the integral.

    We also encorporate a scale to visualize the influence of the initial
    condition:
        u_0 = scale_0 * u_0_original
        u_1 = scale_1 * u_1_original
    """
    x = np.linspace(LEFT_X, RIGHT_X, 200)
    u_left_going = scale_0 * initials_0[init_0_active](x + speed * time)
    u_right_going = scale_0 * initials_0[init_0_active](x - speed * time)
    U_momentum_left_going = scale_1 *\
            initials_1_integrated[init_1_active](x + speed * time)
    U_momentum_right_going = scale_1 *\
            initials_1_integrated[init_1_active](x - speed * time)

    u = 0.5 * (
            u_left_going + u_right_going +
            1/speed * (
                U_momentum_left_going - U_momentum_right_going
            ))

    return x, u


# The ColumnDataSource abstracts the transmission of data to the client over the
# Websocket Protocol. Whenever its data member variable is updated the new
# information is send to be displayed.
data_source = ColumnDataSource(data={'x': [], 'y': []})

plot = Figure(plot_height=HEIGHT, plot_width=WIDTH_PLOT, x_range=[-5, 5],
        y_range=[-0.5, 2.5])

plot.line("x", "y", source=data_source, color="blue", line_width=LINE_WIDTH)

# Select the zeroth initial condition
init_0_selector = RadioButtonGroup(labels=indicators_0, active=0)
# Select the speed at which the wave propagates
speed = Slider(title="Ausbreitungsgeschwindigkeit", start=0.1, end=2, step=0.1,
        value=1)
# Manipulate the influence of the zeroth initial condition
scale_0 = Slider(title="Skalierung der 1. Anfangsbedingung", start=0.1, end=2,
        step=0.1, value=1)
# Toggle that adds a periodic callback function, so that the plot seems to be
# moving
animation_toggle = Toggle(label="Animieren")
# Lets the user adjust the time in the transient simulation on its own
time = Slider(title="Zeit", value=0, start=0, end=10, step=0.1)

# Allow the initial speed to be considered (This is deactivated up front since
# the bevahiour might seem slightly unphysical)
advanced_toggle = Toggle(label="Zweite Anfangsbedingung aktivieren")
# Select the type of the first initial condition
init_1_selector = RadioButtonGroup(labels=indicators_1, active=0, visible=False)
# Manipulate the influence of the first initial condition
scale_1 = Slider(title="Skalierung der 2. Anfangsbedingung", start=0, end=2,
        step=0.1, value=0, visible=False)


def animate():
    if time.value >= time.end:
        time.value = time.start
    else:
        time.value += time.step

callback_id = 0
def animation_callback(source):
    """
    Function adds a callback to the function which animates it. The callback_id
    is the id of the process the bokeh server spawns. It is necessary to
    remove it later on.
    """
    global callback_id
    if animation_toggle.active == 1:
        callback_id = curdoc().add_periodic_callback(animate, 100)
    else:
        curdoc().remove_periodic_callback(callback_id)

def toggle_callback(source):
    """
    Enables the 'more advanced' options so that the user is not distracted by
    the functionality in the first place
    """
    advanced_toggle.visible = False
    init_1_selector.visible = True
    scale_1.visible = True
    # Set the time back to 0 so that solution stays in the viewport
    time.value = 0
    scale_1.value = 0.2

def slider_callback(attr, old, new):
    """
    Whenever a slider value changes, the value pairs for the plot are
    recalculated and sent to the client by updating the data member variable of
    the data_source object.
    """
    x, u = update_data(init_0_selector.active, speed.value, scale_0.value,
            time.value, init_1_selector.active, scale_1.value)

    data_source.data = {'x': x, 'y': u}

def init_0_selector_callback(source):
    scale_0.value = 1 
    slider_callback(0, 0, 0)

def init_1_selector_callback(source):
    scale_1.value = 0.2 
    slider_callback(0, 0, 0)

# Call callback once upfront to populate the plot
slider_callback(0,0,0)

# Connect the widgets with their respective callbacks
animation_toggle.on_click(animation_callback)
advanced_toggle.on_click(toggle_callback)

for slider in (speed, scale_0, time, scale_1):
    slider.on_change("value", slider_callback)

init_0_selector.on_click(init_0_selector_callback)
init_1_selector.on_click(init_1_selector_callback)

# Assemble the plot
inputs = WidgetBox(init_0_selector, speed, scale_0, animation_toggle, time,
        advanced_toggle, init_1_selector, scale_1)

curdoc().add_root(Row(plot, inputs, width=WIDTH_TOAL))
