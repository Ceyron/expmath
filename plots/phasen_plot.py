# -*- coding: utf-8 -*-
import numpy as np
import sys

from bokeh.models.widgets import Panel, Tabs, Dropdown
from bokeh.layouts import row, widgetbox
from bokeh.io import curdoc
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import Slider, RadioButtonGroup, Toggle
from bokeh.plotting import figure


HEIGHT = 400
WIDTH_PLOT = 600
WIDTH_TOTAl = 800

"""
Example: The ODE of a regular, undamped oscillator with no external forces is
    y'' = - k/m * y
This ODE of second order can be transformed into a system of ODEs of first order
    |y |'   | 0     1 |   |y |
    |  |  = |         | * |  |
    |y'|    | -k/m  0 |   |y'|
The Matrix can be used to draw the phase plot (y' over y) which is a vector field
in the form of the function (x_1, x_2) = f((y, y')).
The vectors (denoted by x_vect = (x_1, x_2)^T) are either normalized or reshaped to be of a fixed maximal length.
Within this vector field a solution is seen as the trajctory drawn by the general
solution of the ODE (or the system of ODEs of first order)
    |y |      |a*sin(sqrt(k/m)*t) + b*cos(sqrt(k/m)*t)                   |
    |  |(t) = |                                                          |
    |y'|      |a*sqrt(k/m)*cos(sqrt(k/m)*t - b*sqrt(k/m)*sin(sqrt(k/m)*t)|
whereas a and b are coefficients determined by the initial conditions.
    y(t=0) = y_0
    y'(t=0) = y_1
"""

# Left-most position of vector to be drawn (must be integer)
N_x_left = -2
# Right-most position of vector to be drawn (must be integer)
N_x_right = 2
# Top-most position of vector to be drawn (must be integer)
N_y_top = 2
# Bottom-most position of vector to be drawn (must be integer)
N_y_bot = -2
# Number of vectors to be drawn
N_x = N_x_right - N_x_left + 1
N_y = N_y_top - N_y_bot + 1
N = N_x * N_y

# How to treat the vectors' lengths (if none selected, there is no manipulation)
# "scale": vectors a representative length between (0...1)
# "normalie": vectors have the same length of 1
# "none": vectors keep their length
VECTOR_TREATMENT = "scale"


# The first ODE is an undamped osciallator
def oscillator(u, v, parameters):
    k = parameters["stiffness"]
    m = parameters["mass"]
    w = np.sqrt(k/m)  # Auxilliary variable
    u_prime = v
    v_prime = -w**2 * u
    return (u_prime, v_prime)

def osciallator_solution(parameters, u_0, v_0, t):
    k = parameters["stiffness"]
    m = parameters["mass"]
    w = np.sqrt(k/m)  # Auxilliary variable
    u = v_0 * 1/w * np.sin(w * t) + u_0 * np.cos(w * t)
    v = v_0 * np.cos(w * t) - u_0 * w * np.sin(w * t)
    return (u, v)


def extract_parameters(ode_selectorm, slider_1, slider_2, slider_3, slider_4):
    parameters = {}
    if ode_selector.value != "volterra-lotka":
        parameters["ode"] = "oscillator"
        parameters["mass"] = slider_1.value
        parameters["stiffness"] = slider_2.value
        parameters["damping"] = slider_3.value
        parameters["excitation"] = slider_4.value
    else:
        parameters["ode"] = "volterra-lotka"

    return parameters


def update_vector(parameters, vector_source):
    x = np.linspace(N_x_left, N_x_right, N_x)
    y = np.linspace(N_y_bot, N_y_top, N_y)
    X, Y = np.meshgrid(x, y)
    X = X.flatten()
    Y = Y.flatten()
    if parameters["ode"] == "oscillator":
        U, V = oscillator(np.copy(X), np.copy(Y), parameters) # IMPORTANT: Use deep copies when necessary to avoid numpy optimizations
    elif parameters["ode"] == "volterra-lotka":
        pass
    else:
        sys.exit(1)
    angle = np.pi/4 + np.arctan2(np.copy(V), np.copy(U))  # The arrows seem to be slightly wrong as the arrow tip does not align with the arrow line. However, this is due to bokeh limitations on the ability to rotate triangles. The available set of angles is too small to represent all necessary calculated angles
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
    for i in range(N):
        vector_source.data["x_" + str(i)] = [start_x[i], end_x[i]]
        vector_source.data["y_" + str(i)] = [start_y[i], end_y[i]]
        vector_source.data["angle_" + str(i)] = [0., angle[i]]
    vector_source.data["size"] = [0., 10]


def update_initial(y_0, y_1, initial_value_source):
    initial_value_source.data = {"x": [y_0, ], "y": [y_1, ]}
    

def update_solution(parameters, y_0, y_1, end_time, solution_source):
    t = np.linspace(0, end_time, 25)
    if parameters["ode"] == "oscillator":
        x, y = osciallator_solution(parameters, y_0, y_1, t)
    elif parameters["ode"] == "volterra-lotka":
        pass
    else:
        sys.exit(1)
    solution_source.data = {"x": x, "y": y}
    

vector_source = ColumnDataSource()
initial_value_source = ColumnDataSource()
solution_source = ColumnDataSource()



plot = figure(plot_width=WIDTH_PLOT, plot_height=HEIGHT, match_aspect=True, output_backend = "webgl")

for i in range(N):
    plot.line(x="x_"+str(i), y="y_"+str(i), source=vector_source, color="black")
    plot.triangle(x="x_"+str(i), y="y_"+str(i), size="size", angle="angle_"+str(i), source=vector_source, color="black")

plot.cross(x="x", y="y", source=initial_value_source, color="orange", size=15, line_width=3)
plot.line(x="x", y="y", source=solution_source, line_width=3)

ode_selector = Dropdown(label="Welche gewöhnliche DGL", button_type="warning", menu = [
    ("Ungedämpfter Feder-Masse-Schwinger", "oscillator_undamped"),
    ("Gedämpfter Feder-Masse-Schwinger", "oscillator_damped"),
    ("Gedämpfter Feder-Masse-Schwinger mit Anregung", "oscillator_external_influence"),
    None,
    ("Räuber-Beute-Beziehung", "volterra-lotka"),
    ])
slider_1 = Slider(title="Masse", start=0., end=5., value=1., step=0.1)
slider_2 = Slider(title="Federkonstante", start=0., end=5., value=1., step=0.1)
slider_3 = Slider(title="Ohne Funktion", start=0., end=1., value=0., step=0.)
slider_4 = Slider(title="Ohne Funktion", start=0., end=1., value=0., step=0.)
initial_y = Slider(title="y(t=0)=", start=0., end=5., value=1., step=0.1)
initial_y_prime = Slider(title="y'(t=0)=", start=0., end=5., value=0., step=0.1)
animate_toggle = Toggle(label="Animieren")
end_time = Slider(title="Zeit", start=0., end=10., value=1., step=0.1)


parameters = extract_parameters(ode_selector, slider_1, slider_2, slider_3, slider_4)
update_vector(parameters, vector_source)
update_initial(initial_y.value, initial_y_prime.value, initial_value_source)
update_solution(parameters, initial_y.value, initial_y_prime.value, end_time.value, solution_source)

inputs = widgetbox(ode_selector, slider_1, slider_2, slider_3, slider_4, initial_y, initial_y_prime, animate_toggle, end_time, width=WIDTH_TOTAl)

def parameter_sliders_update(attr, old, new):
    parameters = extract_parameters(ode_selector, slider_1, slider_2, slider_3, slider_4)
    update_vector(parameters, vector_source)
    update_solution(parameters, initial_y.value, initial_y_prime.value, end_time.value, solution_source)

def end_time_update(attr, old, new):
    parameters = extract_parameters(ode_selector, slider_1, slider_2, slider_3, slider_4)
    update_solution(parameters, initial_y.value, initial_y_prime.value, end_time.value, solution_source)

def initial_value_update(attr, old, new):
    update_initial(initial_y.value, initial_y_prime.value, initial_value_source)
    parameters = extract_parameters(ode_selector, slider_1, slider_2, slider_3, slider_4)
    update_solution(parameters, initial_y.value, initial_y_prime.value, end_time.value, solution_source)


for parameter_slider in (slider_1, slider_2, slider_3, slider_4):
    parameter_slider.on_change("value", parameter_sliders_update)

end_time.on_change("value", end_time_update)

for initial_slider in (initial_y, initial_y_prime):
    initial_slider.on_change("value", initial_value_update)


curdoc().add_root(row(plot, inputs))
