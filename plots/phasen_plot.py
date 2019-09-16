# -*- coding: utf-8 -*-
import numpy as np
import sys

from bokeh.layouts import row, widgetbox
from bokeh.io import curdoc
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import Slider, RadioButtonGroup, Toggle, Dropdown
from bokeh.plotting import figure


HEIGHT = 400
WIDTH_PLOT = 500
WIDTH_TOTAl = 800

"""
CAUTION: This script is still experimental and needs an overhaul (#TODO)

This plot offers the user the chance to manipulate the vector field of phase
plot and see the solution of the underlying systems of ordinary differential
equations being plotted. This plot can then even be animated to see the
trajectory propagate through the field and tangentially align with the vectors.

The values of the initial conditions are adjusted by the help of sliders.

The following ODEs are currently available:
    * Undamped oscillator (adjust stiffness and mass)
    * Damped oscillator (additionally adjust the damping)
    * Volterra-Lotka (adjust all four parameters)

The vector field of the phase plot is drawn by the help of the system of ODEs.
The solution is drawn based on a time series trajectory calculated either
analytically (oscillator) with the general solution or numerically
(volterra-lotka), currently by the help of fixed time-stepping Euler-foreward
integrator.

Example: The ODE of a regular, undamped oscillator with no external forces is
    y'' = - k/m * y
This ODE of second order can be transformed into a system of ODEs of first order
    |y |'   | 0     1 |   |y |
    |  |  = |         | * |  |
    |y'|    | -k/m  0 |   |y'|
The Matrix can be used to draw the phase plot (y' over y) which is a vector
field in the form of the function (x_1, x_2) = f((y, y')).  The vectors (denoted
by x_vect = (x_1, x_2)^T) are either normalized or reshaped to be of a fixed
maximal length.  Within this vector field a solution is seen as the trajctory
drawn by the general solution of the ODE (or the system of ODEs of first order)
    |y |      |a*sin(sqrt(k/m)*t) + b*cos(sqrt(k/m)*t)                   |
    |  |(t) = |                                                          |
    |y'|      |a*sqrt(k/m)*cos(sqrt(k/m)*t - b*sqrt(k/m)*sin(sqrt(k/m)*t)|
whereas a and b are coefficients determined by the initial conditions.
    y(t=0) = y_0
    y'(t=0) = y_1

For more detailed derivations on the oscillator see ../docs/phasen_plot.tex
"""

# Endpoints for the vectors (the vector field is drawn for each integer pair
# within this interval, e.g. (2,3) )
N_spread_oscillator = [-5, 5]
N_spread_volterra = [0, 12]

# How to treat the vectors' lengths
# "scale": vectors a representative length between (0...1)
# "normalize": vectors have the same length of 1
# "none": vectors keep their length
VECTOR_TREATMENT = "scale"


# The first ODE is an osciallator (can be damped or undamped)
def oscillator(u, v, parameters):
    """
    The ODE of second order has been transformed to a system of two ODEs of
    first order which are used to calculate vectors in the (y,y')-pahse plot.
    """
    k = parameters["stiffness"]
    m = parameters["mass"]
    d = parameters["damping"]
    u_prime = v
    v_prime = -k/m* u - d/m * v
    return (u_prime, v_prime)

def osciallator_solution(parameters, u_0, v_0, t):
    """
    This is the general analytic solution to a damped oscillator with no
    external excitation. Consult ../docs/phasen_plot.tex for more info.
    """
    k = parameters["stiffness"]
    m = parameters["mass"]
    d = parameters["damping"]
    w = np.sqrt(k/m)  # eigen angular frequency
    delta = d/(2*m) # damping measure
    # Here we decide between the cases depending on the sign of the radicand when solving analytically
    if d == 0.0:  # non-damping
        u = v_0 * 1/w * np.sin(w * t) + u_0 * np.cos(w * t)
        v = v_0 * np.cos(w * t) - u_0 * w * np.sin(w * t)
    elif np.abs(delta**2 - w**2) < 0.1:  # aperiodic border-case
        C_1 = u_0
        C_2 = v_0 + delta * u_0
        u = C_1 * np.exp(-delta * t) + C_2 * t * np.exp(-delta * t)
        v = -C_1 * delta * np.exp(-delta * t) + C_2 * np.exp(-delta * t) - C_2 * t * delta * np.exp(-delta * t)
    elif delta**2 > w**2:  # non-oscillating, just damping
        aux = np.sqrt(delta**2 - w**2)
        C_1 = u_0/2 + (v_0 + delta * u_0) / (2 * aux)
        C_2 = u_0/2 - (v_0 + delta * u_0) / (2 * aux)
        u = np.exp(-delta * t) * (C_1 * np.exp(aux * t) + C_2 * np.exp(- aux * t))
        v = -delta * np.exp(-delta * t) * (C_1 * np.exp(aux * t) + C_2 * np.exp(-aux * t)) +\
            np.exp(-delta * t) * (C_1 * aux * np.exp(aux * t) - C_2 * aux * np.exp(-aux * t))
    elif w**2 > delta**2:  # oscillating and damping
        aux = np.sqrt(w**2 - delta**2)
        C_1 = (v_0 + delta * u_0) / aux
        C_2 = u_0
        u = np.exp(-delta * t) * (C_1 * np.sin(aux * t) + C_2 * np.cos(aux * t))
        v = -delta * np.exp(-delta * t) * (
                C_1 * np.sin(aux * t) + C_2 * np.cos(aux * t)
            ) +\
            np.exp(-delta * t) * (C_1 * aux * np.cos(aux * t) - C_2 * aux * np.sin(aux * t))
    return (u, v)

# The next ODE is the simple correlation between prey (e.g., a rabbit) and a
# predator (e.g., a fox)
def volterra_lotka(u, v, parameters):
    alpha = parameters["reproduction_rate_prey"]
    beta = parameters["hunting_rate"]
    gamma = parameters["death_rate_predator"]
    delta = parameters["reproduction_rate_predator"]
    u_prime = u * (alpha - beta * v)
    v_prime = v * (gamma * u - delta)
    return (u_prime, v_prime)

def volterra_lotka_solution(parameters, u_0, v_0, t):
    """
    Since there is no closed solution to the volterra-lotka equation (,i.e., no
    analytic solution), a numeric integrator has to be used. Here, we apply a
    simple first-order Euler-forward integrator with fixed time stepping.
    TODO: a proper integrator could reduce the computational load on the server.
    """
    delta_t = t[1] - t[0]  # we assume equal time stepping
    u = np.zeros(len(t))
    v = np.zeros(len(t))
    u[0] = u_0
    v[0] = v_0
    for i in range(1, len(t)):
        u_prime, v_prime = volterra_lotka(u[i-1], v[i-1], parameters)
        u[i] = u[i-1] + u_prime * delta_t
        v[i] = v[i-1] + v_prime * delta_t
        # TODO test more cases, if the numerically calculated trajectory escapes the view.
        # Therefore, we currently limit the trajectory to be in a 50 by 50 bounding box.
        # So the user can still see the vectors
        if np.abs(v[i]) > 25 or np.abs(u[i]) > 25:
            u[i] = u[i-1]
            v[i] = v[i-1]
    return (u, v)


def extract_parameters(ode_selectorm, slider_1, slider_2, slider_3, slider_4):
    """
    This function reads the slider values and saves them into a dictionary.
    """
    parameters = {}
    if ode_selector.value != "volterra-lotka":
        parameters["ode"] = "oscillator"
        parameters["mass"] = slider_1.value
        parameters["stiffness"] = slider_2.value
        parameters["damping"] = slider_3.value
        if ode_selector.value == "oscillator_undamped":
            parameters["damping"] = 0.
    else:
        parameters["ode"] = "volterra-lotka"
        parameters["reproduction_rate_prey"] = slider_1.value
        parameters["hunting_rate"] = slider_2.value
        parameters["death_rate_predator"] = slider_3.value
        parameters["reproduction_rate_predator"] = slider_4.value

    return parameters


def update_vector(parameters, triangle_source, multi_line_source):
    """
    This routine is new for the expmath-project. Until now, bokeh
    did not have the abilities to draw a vector-field similar to
    matplotlib etc.
    This functions updates two ColumnDataSources which are used for
    lines that represent the arrow body and triangles that represent
    the arrow head. The triangles are rotated in a direction to mimic
    the appearance of a classical arrow.
    """
    if parameters["ode"] == "oscillator":
        # Determin how many arrows to draw in each direction
        N_axis = N_spread_oscillator[1] - N_spread_oscillator[0] + 1
        # The total number of arrows is the product of the arrows in each
        # direction
        N = N_axis**2
        x = np.linspace(N_spread_oscillator[0], N_spread_oscillator[1], N_axis)
        y = np.linspace(N_spread_oscillator[0], N_spread_oscillator[1], N_axis)
    elif parameters["ode"] == "volterra-lotka":
        N_axis = N_spread_volterra[1] - N_spread_volterra[0] + 1
        N = N_axis**2
        x = np.linspace(N_spread_volterra[0], N_spread_volterra[1], N_axis)
        y = np.linspace(N_spread_volterra[0], N_spread_volterra[1], N_axis)
    else:
        sys.exit(1)
    # The vector field is drawn by the help of X,Y and U,V. Therefore, we need
    # every combination of coordinates possible -> meshgrid
    X, Y = np.meshgrid(x, y)
    # Dealing with one-dimensional arrays instead of matrices makes consecutive
    # calculations easier -> flatten
    X = X.flatten()
    Y = Y.flatten()
    if parameters["ode"] == "oscillator":
        # IMPORTANT: Use deep copies when necessary to avoid numpy optimizations
        U, V = oscillator(np.copy(X), np.copy(Y), parameters) 
    elif parameters["ode"] == "volterra-lotka":
        U, V = volterra_lotka(np.copy(X), np.copy(Y), parameters)
    else:
        sys.exit(1)
    angle_pure = np.arctan2(np.copy(V), np.copy(U))
    # The arrows seem to be slightly wrong as the arrow tip does not align with
    # the arrow line. However, this is due to bokeh limitations on the ability
    # to rotate triangles. The available set of angles is too small to represent
    # all necessary calculated angles
    angle = np.pi/4 + angle_pure  

    # It feels less clumsy if vectors either have the same length or a
    # representative length
    if VECTOR_TREATMENT == "normalize":
        magnitude = np.sqrt(U**2 + V**2)
        for i in range(len(magnitude)):
            if magnitude[i] < 0.01:
                magnitude[i] = 0.01
        U /= magnitude
        V /= magnitude
    elif VECTOR_TREATMENT == "scale":
        magnitude = np.sqrt(U**2 + V**2)
        max_maxgnitude = max(magnitude)
        U /= max_maxgnitude
        V /= max_maxgnitude

    start_x = X
    start_y = Y
    end_x = X + U
    end_y = Y + V
    xs = []
    ys = []
    triangle_x = []
    triangle_y = []
    triangle_angle = []
    if parameters["ode"] == "oscillator":
        SIZE = 10
    elif parameters["ode"] == "volterra-lotka":
        SIZE = 7
    for i in range(N):
        # IMPORTANT: Create the arrays the ColumnDataSources are filled with
        # prior to assigning them to them. Since every time you change the
        # ColumnDataSource, this data is send to the client. This slows down the
        # overall user experience. 
        triangle_x.append(end_x[i] + np.cos(angle_pure[i]) * 0.1)
        triangle_y.append(end_y[i] + np.sin(angle_pure[i]) * 0.1)
        triangle_angle.append(angle[i])
        xs.append([start_x[i], end_x[i]])
        ys.append([start_y[i], end_y[i]])

    # Updating the ColumnDataSources with the data assembled previously
    multi_line_source.data = {"xs": xs, "ys": ys}
    triangle_source.data = {"x": triangle_x, "y": triangle_y,
            "angle": triangle_angle, "size": SIZE*np.ones(N)}


def update_initial(y_0, y_1, initial_value_source):
    """
    This function simply fills the ColumnDataSource of the Cross indicating the
    initial condition with the data of the corresponding sliders
    """
    initial_value_source.data = {"x": [y_0, ], "y": [y_1, ]}

def update_solution(parameters, y_0, y_1, end_time, solution_source):
    """
    This function is responsible for updating the dataset upon which the
    solution trajectory is drawn. It will call the corresponding solution
    function to calculate the trajectory coordinate tuple at each point in time.
    The time varies linearly between 0 and the end adjusted by the corresponding
    slider.
    """
    if parameters["ode"] == "oscillator":
        t = np.linspace(0, end_time, 100)
        x, y = osciallator_solution(parameters, y_0, y_1, t)
    elif parameters["ode"] == "volterra-lotka":
        # Here a high number of steps is necessary to achieve a comparable
        # accuracy with the Euler-integrator
        t = np.linspace(0, end_time, 4000)
        x, y = volterra_lotka_solution(parameters, y_0, y_1, t)
        # Only select every 100th solution point so that we reduce the data that
        # is send to the client
        x = x[0::100]
        y = y[0::100]
    else:
        sys.exit(1)
    solution_source.data = {"x": x, "y": y}

def switch_ode(ode_selector, slider_1, slider_2, slider_3, slider_4, initial_y,
        initial_y_prime, end_time, plot):
    """
    This function is called when a new entry in the dropdown menu is chosen. It
    just changes the slider properties and the axis labels. TODO: Tweak the
    values so that the trajectories don't escape the vector-field.
    """
    if ode_selector.value in ("oscillator_undamped", "oscillator_damped"):
        slider_1.title = "Masse"
        slider_1.start = 0.1
        slider_1.end = 5.
        slider_1.value = 1.
        slider_1.step = 0.1
        slider_2.title = "Federsteifigkeit"
        slider_2.start = 0.1
        slider_2.end = 5.
        slider_2.value = 1.
        slider_2.step = 0.1
        slider_3.title = "Ohne Funktion"
        slider_3.start = 0.
        slider_3.end = 0.01
        slider_3.value = 0.
        slider_3.step = 0.1
        slider_3.visible = False
        slider_4.title = "Ohne Funktion"
        slider_4.start = 0.
        slider_4.end = 0.01
        slider_4.value = 0.
        slider_4.step = 0.1
        slider_4.visible = False

        initial_y.title = "Anfangsauslenkung y(0)"
        initial_y.start = -5
        initial_y.end = 5
        initial_y.value = 1
        initial_y.step = 0.1
        initial_y_prime.title = "Anfangsgeschwindigkeit y'(0)"
        initial_y_prime.start = -5.
        initial_y_prime.end = 5.
        initial_y_prime.value = 0.
        initial_y_prime.step = 0.1

        end_time.end = 30.
        end_time.value = 1.
        end_time.step = 0.1

        plot.xaxis.axis_label = "Auslenkung y(t)"
        plot.yaxis.axis_label = "Geschwindigkeit y'(t)"

    if ode_selector.value == "oscillator_damped":
        slider_3.title="Dämpfungsfaktor"
        slider_3.start= 0.05
        slider_3.end = 5.
        slider_3.value = 0.5
        slider_3.step = 0.05
        slider_3.visible = True

    elif ode_selector.value == "volterra-lotka":
        slider_1.title = "Reproduktionsrate der Beute"
        slider_1.start = 2
        slider_1.end = 20.
        slider_1.value = 10.
        slider_1.step = 0.1
        slider_2.title = "Fressrate der Räuber"
        slider_2.start = 2
        slider_2.end = 20.
        slider_2.value = 3.
        slider_2.step = 0.1
        slider_3.title = "Sterberate der Räuber"
        slider_3.start = 2
        slider_3.end = 20.
        slider_3.value = 3.
        slider_3.step = 0.1
        slider_3.visible = True
        slider_4.title = "Reproduktionsrate der Räuber"
        slider_4.start = 2
        slider_4.end = 20.
        slider_4.value = 15.
        slider_4.step = 0.1
        slider_4.visible = True

        initial_y.title = "Anfangsanzahl an Beute u(0)"
        initial_y.start = 1
        initial_y.end = 8
        initial_y.value = 5
        initial_y.step = 0.5
        initial_y_prime.title = "Anfangsanzahl an Räubern v(0)"
        initial_y_prime.start = 1
        initial_y_prime.end = 8
        initial_y_prime.value = 5
        initial_y_prime.step = 0.5

        end_time.end = 1.5
        end_time.value = 0.2
        end_time.step = 0.01

        plot.xaxis.axis_label = "Anzahl an Beute u(t)"
        plot.yaxis.axis_label = "Anzahl an Räubern v(t)"

# ColumnDataSource is the object abstracting the constant stream of new datasets
# to the client
vector_source = ColumnDataSource()
multi_line_source = ColumnDataSource()
initial_value_source = ColumnDataSource()
solution_source = ColumnDataSource()

# WebGL brought some minor performance boosts to the client-side drawing
plot = figure(plot_width=WIDTH_PLOT, plot_height=HEIGHT, match_aspect=True,
        output_backend = "webgl")

# The new multiline accepts a list of list as datsets. Here, we draw the body of
# the arrow
plot.multi_line(xs="xs", ys="ys", source=multi_line_source, color="black",
        line_width=2)
# The triangle represents an arrow head
plot.triangle(x="x", y="y", size="size", angle="angle", source=vector_source,
        color="black", fill_color=None)

# Marks the initial condition
plot.cross(x="x", y="y", source=initial_value_source, color="orange", size=15,
        line_width=5)
# Draws the solution trajectory
plot.line(x="x", y="y", source=solution_source, line_width=3)

# Dropdown widget to select the ODE system.
ode_selector = Dropdown(label="Welche gewöhnliche DGL", button_type="warning",
        menu = [
        ("Ungedämpfter Feder-Masse-Schwinger", "oscillator_undamped"),
        ("Gedämpfter Feder-Masse-Schwinger", "oscillator_damped"),
        None,
        ("Räuber-Beute-Beziehung", "volterra-lotka"),
        ],
        default_value="oscillator_undamped")

slider_1 = Slider(title="Masse", start=0.1, end=5., value=1., step=0.1)
slider_2 = Slider(title="Federkonstante", start=0.1, end=5., value=1., step=0.1)
slider_3 = Slider(title="Ohne Funktion", start=0., end=1., value=0., step=0.)
slider_4 = Slider(title="Ohne Funktion", start=0., end=1., value=0., step=0.)
initial_y = Slider(title="y(t=0)=", start=-5., end=5., value=1., step=0.1)
initial_y_prime = Slider(title="y'(t=0)=", start=-5., end=5., value=0., step=0.1)
animate_toggle = Toggle(label="Animieren")
end_time = Slider(title="Zeit", start=0., end=30., value=5., step=0.1)

# Calling all functions in advance to populate the plot
parameters = extract_parameters(ode_selector, slider_1, slider_2, slider_3,
        slider_4)
update_vector(parameters, vector_source, multi_line_source)
update_initial(initial_y.value, initial_y_prime.value, initial_value_source)
update_solution(parameters, initial_y.value, initial_y_prime.value,
        end_time.value, solution_source)

# The widgetbox is just a container for all input objects
inputs = widgetbox(ode_selector, slider_1, slider_2, slider_3, slider_4,
        initial_y, initial_y_prime, animate_toggle, end_time)

# Declaration of various callback handlers
def parameter_sliders_update(attr, old, new):
    parameters = extract_parameters(ode_selector, slider_1, slider_2, slider_3,
            slider_4)
    update_vector(parameters, vector_source, multi_line_source)
    update_solution(parameters, initial_y.value, initial_y_prime.value,
            end_time.value, solution_source)

def end_time_update(attr, old, new):
    parameters = extract_parameters(ode_selector, slider_1, slider_2, slider_3,
            slider_4)
    update_solution(parameters, initial_y.value, initial_y_prime.value,
            end_time.value, solution_source)

def initial_value_update(attr, old, new):
    update_initial(initial_y.value, initial_y_prime.value, initial_value_source)
    parameters = extract_parameters(ode_selector, slider_1, slider_2, slider_3,
            slider_4)
    update_solution(parameters, initial_y.value, initial_y_prime.value,
            end_time.value, solution_source)

def animate():
    if end_time.value >= end_time.end:
        end_time.value = end_time.start
    else:
        end_time.value += end_time.step

# This id is the process_id of the periodic_callback. It is necessary to
# deactivate it with the toggle button
callback_id = 0. 
def toggle_animation(source):
    global callback_id
    if animate_toggle.active == 1:
        callback_id = curdoc().add_periodic_callback(animate, 100)
    else:
        curdoc().remove_periodic_callback(callback_id)

def selector_callback(attr, old, new):
    if old != new:
        switch_ode(ode_selector, slider_1, slider_2, slider_3, slider_4,
                initial_y, initial_y_prime, end_time, plot)

# Connect the callback handlers with event loop
for parameter_slider in (slider_1, slider_2, slider_3, slider_4):
    parameter_slider.on_change("value", parameter_sliders_update)

end_time.on_change("value", end_time_update)

for initial_slider in (initial_y, initial_y_prime):
    initial_slider.on_change("value", initial_value_update)

animate_toggle.on_click(toggle_animation)

ode_selector.on_change("value", selector_callback)
# This value has to be called manually since otherwhise a first click on the
# dopdown container would just yield the standard entry
ode_selector.value = "oscillator_undamped"

# Assembling the html page
curdoc().add_root(row(plot, inputs, width=WIDTH_TOTAl))
