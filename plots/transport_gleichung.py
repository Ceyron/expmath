# -*- coding: utf-8 -*-
import numpy as np

from bokeh.layouts import Row, Column, WidgetBox
from bokeh.io import curdoc
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import Slider, RadioButtonGroup, Toggle, Dropdown
from bokeh.plotting import Figure

"""
This plot presents the characteristics of transport equations drawn below the
simulation that can evolve over time. The user can select between different
fluxes (constant, ideal driving school recommendation, driving school
recommendation, burgers, location-dependent) as well as different shapes of
initial conditions (gaussian bell, piecewise linear, jump with gap). Together
with adjusting the parameters by the help of sliders, the user is able to
explore the aspects of transport equations:
    - Propagation of information
    - Shocks/Singularities
    - Rarefaction waves
    - Characteristics that are not straight lines

Aside for special case of burgers flux together with IC jump with gap, each
combination of flux and initial condition is generalized as the solution
definition u=u(t,x) or the characteristics defintion t=t(x,xi_0) calling the
definition of the initial condition. For a detailed derivation consult
../docs/transport_gleichung.tex
"""

# Geometry constants for the plot
HEIGHT_PLOT = 260
WIDTH_PLOT = 600
WIDTH_TOTAL = 800

# Define the user's initial vieport
X_LEFT = -5
X_RIGHT = 5
Y_BOTTOM = -0.5
Y_TOP = 2.5

# When drawing characteristics starting at starting point (x=xi_0, t=0),
# determines the endpoint (x=xi_0+offset, t)
X_CHARACTERISTICS_OFFSET = 5

# Proportionality factor "Halber Tacho" in 1/h
k = 2000

# Small value to avoid division by zero and logarithm of a zero argument
EPS = 0.0001

"""
Define the functions to draw the characteristics t = t(x, xi_0) and to draw
the solution u = u(t, x). They require the function pointer to the currently
active initial function.
a: Parameter to the respective flux
c, d: Parameters for the initial condition
xs_0: a numpy array of points on the x_axis on which the characteristics will
start (make sure the distance between the points is wide enough so that the
lines are not cluttered but also not far enough so that there are still a
representative number of characteristics)
"""

# Flux F(u, x) = a*u  (in the interface to the user a is the speed of the cars)
def CONSTANT_CHARACTERISTICS(a, c, d, xs_0, initial_function):
    xs = []
    ts = []
    for x_0 in xs_0:
        xs.append([x_0, x_0 + X_CHARACTERISTICS_OFFSET])
        ts.append([0, X_CHARACTERISTICS_OFFSET/a])
    return xs, ts

# Constant speed simply propagates the initial condition to the right
def CONSTANT_SOLUTION(x, t, a, c, d, initial_function):
    return initial_function(x - a * t, x, c, d, final_output=True)


# Flux F(u, x) = k  (velocity is inverse proportional to the density v(u) = k/u,
# flux is velocity times density F =  v(u) * u = k/u * u = k)
def IDEAL_SCHOOL_CHARACTERISTICS(a, c, d, xs_0, initial_function):
    xs = []
    ts = []
    for x_0 in xs_0:
        xs.append([x_0, x_0])
        ts.append([0, 10000]) # Just a vertical line
    return xs, ts

# If all cars follow the ideal recommendation, then the local higher density
# keeps at the same location over time
def IDEAL_SCHOOL_SOLUTION(x, t, a, c, d, initial_function):
    return initial_function(x, x, c, d, final_output=True)


# Flux F(u, x) = k - klu (velocity is inverse proportional to the density when
# considering the cars' lengths l: v(u) = k(1/u - l) . The length is aliased as
# the parameter a)
def SCHOOL_CHARACTERISTICS(a, c, d, xs_0, initial_function):
    length = a * 0.001  # Convert to kilometers

    xs = []
    ts = []
    for x_0 in xs_0:
        t_pos = -X_CHARACTERISTICS_OFFSET/(length*k + EPS)
        if t_pos > 0:
            xs.append([x_0, x_0 + X_CHARACTERISTICS_OFFSET])
            ts.append([0, -X_CHARACTERISTICS_OFFSET/(length*k + EPS)])
        else:
            xs.append([x_0 - X_CHARACTERISTICS_OFFSET, x_0])
            ts.append([-t_pos, 0])
    return xs, ts

# The local higher density propagates against the movement direction of the cars
# (i.e., it moves backwards) by a speed depending on the cars' length
def SCHOOL_SOLUTION(x, t, a, c, d, initial_function):
    length = a * 0.001  # Convert to kilometers
    return initial_function(x + length*k*t, x, c, d, final_output=True)


# Flux F(u, x) = a * u^2 (creates shocks and rarefaction waves)
# Requires special case for JUMP_WITH_GAP so that no characteristic lines are
# drawn in positions where the initial condition is not defined
def BURGERS_CHARACTERISTICS(a, c, d, xs_0, initial_function):
    xs = []
    ts = []
    for x_0 in xs_0:
        if initial_function == JUMP_WITH_GAP:
            if 0 < x_0 <= d:
                continue

        xs.append([x_0, x_0 + X_CHARACTERISTICS_OFFSET])
        # Value of the initial condition at the current starting point x_0
        initial = initial_function(x_0, x_0, c, d,
                final_output=False)[1]

        ts.append([0, X_CHARACTERISTICS_OFFSET/(a * initial + EPS)])

    return xs, ts

def BURGERS_SOLUTION(x, t, a, c, d, initial_function):
    # Special treatment for the JUMP_WITH_GAP IC so that the 
    if initial_function == JUMP_WITH_GAP:
        x_left = []
        x_middle = []
        x_right = []
        y_left = []
        y_middle = []
        y_right = []
        for ele in x:
            if ele < 0:
                x_left.append(ele)
                y_left.append(0)
            #elif d <= ele < a*t*c:
            #    x_middle.append(ele)
            #    y_middle.append(0)
            elif ele >= d + a*t*c:
                x_right.append(ele)
                y_right.append(c)
        return [x_left, x_middle, x_right], [y_left, y_middle, y_right]
    else:
        # Aside from the case of the jump with gap x_inital is equal to x.
        x_initial, u_initial = initial_function(x, x, c, d, final_output=False)
        return initial_function(x_initial - a * u_initial * t, x_initial, c, d,
                final_output=True)

# Flux F(u, x) = a * x * u
# TODO Check if the solution line that this function creates is physically
# accurate
def LOCATION_DEPENDENT_FLUX_CHARACTERISTICS(a, c, d, xs_0, initial_function):
    # Location dependent flux induces that the characteristics are not straight
    # lines anymore
    xs = []
    ts = []
    for x_0 in xs_0:
        # On the negative x-side the function is monotonically decreasing,
        # therefore it has to be drawn from top to bottom, for the positive
        # x-side it is the opposite
        if x_0 < 0:
            x = np.linspace(x_0 - X_CHARACTERISTICS_OFFSET, x_0)
            xs.append(x)
            t = 1/(a + EPS) * np.log(np.abs(x/(x_0 + EPS)) + EPS)
            ts.append(t)
        elif x_0 > 0:  # Ignore x_0 == 0 since log is not defined there
            x = np.linspace(x_0, x_0 + X_CHARACTERISTICS_OFFSET)
            xs.append(x)
            t = 1/(a + EPS) * np.log(np.abs(x/(x_0 + EPS)) + EPS)
            ts.append(t)
    return xs, ts

def LOCATION_DEPENDENT_FLUX_SOLUTION(x, t, a, c, d, initial_function):
    xi_0 = x * np.exp(-a * t)
    xs, ys = initial_function(xi_0, x, c, d, final_output=True)
    ys[0] = ys[0] * np.exp(-t)
    try:  # Only necessary for JUMP_WITH_GAP where two lines are drawn
        ys[1] = ys[1] * np.exp(-t)
    except:
        pass
    return xs, ys
    

"""
Define the initial conditions. They require the propagated x-position(x_of_t) as
well as the non-transformed x-position(x_original).
c, d: Parameters to the respective intial conditions
final_output: flag whether the output should be in a list of lists (necessary
for the multi_line renderer) or in one continous numpy array
"""

# Gaussian bell (normal distribution)
# c: Mean
# d: Standard deviation
def BELL(x_of_t, x_original, c, d, final_output=False):
    y = 1/(np.sqrt(2*np.pi*d**2)) * np.exp(-(x_of_t - c)**2/(2*d**2))
    if not final_output:
        return np.array(x_original), np.array(y)
    else:
        return [x_original, []], [y, []]

# ____
#     \____
# c, d: Parameters that respectively control the top and bottom vertex, they
# change their role depending on which value is greater
def PIECEWISE_LINEAR(x_of_t, x_original, c, d, final_output=False):
    left = min(c, d)
    if left == c:
        right = d
    else:
        right = c

    if right == left:
        right = right + EPS

    # Model linear decreasing part y = slope * x + offset
    slope = -1/(right - left)
    offset = - slope * right

    y = np.piecewise(x_of_t,
        [x_of_t < left, (left <= x_of_t) & (x_of_t <= right), right < x_of_t],
        [1, lambda element: slope * element + offset, 0])
    
    if not final_output:
        return np.array(x_original), np.array(y)
    else:
        return [x_original, []], [y, []]

#          ______
#_______
# Two horizontal lines with a gap in between. The lower line is the x-axis until
# x=0
# c: Height of the right lines
# d: x Starting point of the right lines
def JUMP_WITH_GAP(x_of_t, x_original, c, d, final_output=False):
    # If the inputs are a multi-dimensional thay contain the __len__ methods
    # otherwhise not
    try:
        len(x_of_t)
        is_array = True
    except TypeError:
        is_array = False

    # Treatment depending on whether the input is multi-dimensional or not
    if is_array:
        x_left = []
        x_right = []
        y_left = []
        y_right = []
        for i in range(len(x_of_t)):
            if x_of_t[i] < 0:
                x_left.append(x_original[i])
                y_left.append(0)
            elif d <= x_of_t[i]:
                x_right.append(x_original[i])
                y_right.append(c)
    else:
        x_left = 0
        x_right = 0
        y_left = 0
        y_right = 0
        if x_of_t < 0:
            x_left = x_original
            y_left = 0
        elif d <= x_of_t:
            x_right = x_original 
            y_right = c

    if not final_output:
        return np.array(x_left + x_right), np.array(y_left + y_right)
    else:
        return [np.array(x_left), np.array(x_right)],\
                [np.array(y_left), np.array(y_right)]


# None elements will be rendered as seperators in the dropdown menu
names = [
        ("Konstante Geschwindigkeit $ u_t + [cu]_x = 0 $", "constant"),
        ("Idealisierte Fahrschulempfehlung $ u_t + [k]_x = 0 $",
            "ideal_school"),
        ("Fahrschulempfehlung $ u_t +\
                \left[ k \left( \\frac{1}{u} - l \\right) u \\right]_x = 0 $",
                "school"),
        None,
        ("Burgers-Gleichung $ u_t + [a u^2]_x = 0$", "burgers"),
        None,
        ("Ortsabhängiger Fluss $ u_t + [a x u ]_x = 0 $", "location_dependent")
        ]
solutions  = {
        "constant": CONSTANT_SOLUTION,
        "ideal_school": IDEAL_SCHOOL_SOLUTION,
        "school": SCHOOL_SOLUTION,
        "burgers": BURGERS_SOLUTION,
        "location_dependent": LOCATION_DEPENDENT_FLUX_SOLUTION
        }
characteristics = {
        "constant": CONSTANT_CHARACTERISTICS,
        "ideal_school": IDEAL_SCHOOL_CHARACTERISTICS,
        "school": SCHOOL_CHARACTERISTICS,
        "burgers": BURGERS_CHARACTERISTICS,
        "location_dependent": LOCATION_DEPENDENT_FLUX_CHARACTERISTICS
        }
slider_names = {
        "constant": "Fahrzeuggeschwindigkeit in km/h",
        "ideal_school": "Ohne Funktion",
        "school": "Fahrzeuglänge in m",
        "burgers": "Parameter a",
        "location_dependent": "Parameter a",
        }

initials_names = ["Glocke", "Stückweise Linear", "Sprung mit Lücke"] 

initials = [BELL, PIECEWISE_LINEAR, JUMP_WITH_GAP]


def calculate_solution_value_pairs(type_selected, initial_selected, time, a,
        c, d,):
    """
    Calls the respective functions.
    """
    x = np.linspace(X_LEFT, X_RIGHT, 100)
    xs, ys = solutions[type_selected](x, time, a, c, d,
            initials[initial_selected])

    return xs, ys


def calculate_characteristics_endpoints(type_selected, initial_selected, a,
        c, d):
    # The spacing of the characteristics, i.e., the density of lines to be drawn
    # is arbitrary. Here, 4 in one in integer interval
    xs_0 = np.linspace(X_LEFT, X_RIGHT, 4*int(X_RIGHT-X_LEFT) + 1)

    return characteristics[type_selected](a, c, d, xs_0,
            initials[initial_selected])
     

# ColumnDataSource abstract the sending of new value pairs to the client to be
# drawn
solution_source = ColumnDataSource()
characteristics_source = ColumnDataSource()
horizontal_time_line_source = ColumnDataSource()


plot_top = Figure(plot_height=HEIGHT_PLOT, plot_width=WIDTH_PLOT,
        x_range=[X_LEFT, X_RIGHT], y_range=[Y_BOTTOM, Y_TOP])
plot_top.xaxis[0].axis_label = "Ort x"
plot_top.yaxis[0].axis_label = "Lösung u(t, x)"
plot_top.toolbar.active_drag = None  # Helpful for touchscreen users

plot_bottom = Figure(plot_height=HEIGHT_PLOT, plot_width=WIDTH_PLOT,
        x_range=[X_LEFT, X_RIGHT], y_range=[Y_BOTTOM, Y_TOP])
plot_bottom.xaxis[0].axis_label = "Ort x"
plot_bottom.yaxis[0].axis_label = "Zeit t"
plot_bottom.toolbar.active_drag = None  # Helpful for touchscreen users

# A horizontal black line that moves upwards to indicate the bevaiour in time
plot_bottom.line(x="x", y="y", source=horizontal_time_line_source,
        color="black")

# The solution is drawn as multiple lines however this is only necessary for
# JUMP_WITH_GAP IC so properly render the gap
plot_top.multi_line(xs="xs", ys="ys", source=solution_source)

plot_bottom.multi_line(xs="xs", ys="ts", source=characteristics_source)

type_selector = Dropdown(label="Typ des Flusses auswählen", menu=names,
        button_type ="warning", value="constant")
slider_1 = Slider(title="Fahrzeuggeschwindigkeit in km/h", start=0.1, end=10,
        step=0.1, value=1)
# Toggle that adds a periodic callback function, so that the plot seems to be
# moving
animation_toggle = Toggle(label="Animieren")
# Lets the user adjust the time in the transient simulation on its own
time = Slider(title="Zeit", value=0, start=0, end=10, step=0.1)
# Enables the visibility for advanced widgets that are collapsed for a better
# readability of the plot
advanced_toggle = Toggle(label="Mehr Optionen")
# Select the intial condition
initial_selector = RadioButtonGroup(labels=initials_names,
        active=0, visible=False)
initial_slider_1 = Slider(title="Skalierung der AB", start=0, end=5, step=0.1,
        value=1, visible=False)
initial_slider_2 = Slider(title="Skalierung der AB", start=0.1, end=5, step=0.1,
        value=0.4, visible=False)


# Callback helpers
def update_top_plot():
    xs, ys = calculate_solution_value_pairs(type_selector.value,
            initial_selector.active, time.value, slider_1.value,
            initial_slider_1.value, initial_slider_2.value)

    solution_source.data = {"xs": xs, "ys": ys}

def update_bottom_plot():
    xs, ts = calculate_characteristics_endpoints(type_selector.value,
            initial_selector.active, slider_1.value,
            initial_slider_1.value, initial_slider_2.value)
    characteristics_source.data = {"xs": xs, "ts": ts}

    horizontal_time_line_source.data = {
            "x": [-20, 20],
            "y": [time.value, time.value],
            }

def animate():
    if time.value >= time.end:
        time.value = time.start
    else:
        time.value += time.step


# Callbacks
def update_parameter_slider(attr, old, new):
    update_top_plot()
    update_bottom_plot()

def update_type_selector(attr, old, new):
    update_top_plot()
    update_bottom_plot()
    slider_1.title = slider_names[type_selector.value]

def update_initial_selector(source):
    update_top_plot()
    update_bottom_plot()

def toggle_callback(source):
    """
    Enables the 'more advanced' options so that the user is not distracted by
    the functionality in the first place
    """
    advanced_toggle.visible = False
    initial_selector.visible = True
    initial_slider_1.visible = True
    initial_slider_2.visible = True

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


# Call the callback in advance to populate the plot
update_top_plot()
update_bottom_plot()

# Connect the widgets with their respective callbacks
advanced_toggle.on_click(toggle_callback)
animation_toggle.on_click(animation_callback)
for parameter_slider in (slider_1, initial_slider_1, initial_slider_2, time):
    parameter_slider.on_change("value", update_parameter_slider)

type_selector.on_change("value", update_type_selector)

initial_selector.on_click(update_initial_selector)

# Assemble the plot and create the html
inputs = WidgetBox(type_selector, slider_1, animation_toggle, time,
        advanced_toggle, initial_selector, initial_slider_1, initial_slider_2)
curdoc().add_root(Row(Column(plot_top, plot_bottom), inputs, width=WIDTH_TOTAL))
