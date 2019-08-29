import numpy as np

from bokeh.io import curdoc
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import Slider, RadioButtonGroup, Toggle
from bokeh.layouts import Row, WidgetBox
from bokeh.plotting import Figure

"""
This plot introduces the user to the idea of Fourier series approximation of
function of arbitrary periodicity. This topic is useful when projecting
arbitrary boundary condition to, e.g., the heat transfer equation to the
Eigenfunction fundamental solutions.
The user selects between representative functions, adjusts the period and the
amplitude. The original function is drawn as well as the approximation based on
the order chosen.
"""


# Geometry constants for the plot
HEIGHT = 400
WIDTH_PLOT = 600
WIDTH_TOTAL = 800

# Define the initial viewport the user starts in
X_LEFT = -3
X_RIGHT = 3
Y_BOT = -2
Y_TOP = 2

# The thickness the function lines are drawn with
LINE_WIDTH_ORIGINAL = 2
LINE_WIDTH_APPROXIMATION = 1


"""
Define the original definition as well as the Fourier series approximation
assuming a general periodicity with period "period" and amplitude "amplitude"
measuring the distance between the x-axis with the top-most point or bottom-most
point, respectively. Order is the upper limit for the sumation over the
components of the Fourier series.
"""
def RECTANGLE(x, period, amplitude):
    y = np.piecewise(x, [x % period < period/2, x % period >= period/2],
            [amplitude, -amplitude])
    return y

def RECTANGLE_APPROXIMATION(x, period, amplitude, order):
    y = np.zeros(x.shape)
    for k in range(1, order+1):
        if k % 2 == 0:
            continue
        else:
            b_k = 4*amplitude/(np.pi * k)
            y += b_k * np.sin((2*np.pi*k*x)/(period))
    return y


def SAW_TOOTH(x, period, amplitude):
    slope = 2*amplitude/period
    offset = -amplitude
    # The vectorized version can use mulitple cores simultaneously
    f = np.vectorize(lambda ele: (ele % period) * slope + offset,
            otypes=[np.float])
    y = f(x)
    return y

def SAW_TOOTH_APPROXIMATION(x, period, amplitude, order):
    y = np.zeros(x.shape)
    for k in range(1, order+1):
        b_k = - 2*amplitude/(np.pi*k)
        y += b_k * np.sin((2*np.pi*k*x)/(period))
    return y


def ARC_WITH_GAP(x, period, amplitude):
    return np.piecewise(x, [x % period < period/2, x % period >= period/2],
            [lambda ele: amplitude * np.sin(2*np.pi*ele/period), 0])

def ARC_WITH_GAP_APPROXIMATION(x, period, amplitude, order):
    a_0 = 2*amplitude/np.pi
    y = a_0/2 * np.ones(x.shape)
    for k in range(1, order+1):
        if k == 1:  # Sine only contributes to the first summand
            b_1 = amplitude/2
            y += b_1 * np.sin(2*np.pi*k*x/period)

        if k % 2 == 0:  # even
            a_n =  2 * amplitude/np.pi * 1/(1 - k**2)
            y += a_n * np.cos(2*np.pi*k*x/period)
    return y


# Collect all functions in lists of function pointers
original_functions = [RECTANGLE, SAW_TOOTH, ARC_WITH_GAP]
function_approximations = [RECTANGLE_APPROXIMATION, SAW_TOOTH_APPROXIMATION,
        ARC_WITH_GAP_APPROXIMATION]


# Helper function that are called to calculate the value pairs. At the moment
# the number of elements in the x-array is arbitrary, but according to Shannon's
# theorem it has to be high enough to capture all the high frequency components
# at higher order
def calculate_original_value_pairs(function_active, period, amplitude):
    x = np.linspace(X_LEFT, X_RIGHT, 200)
    y = original_functions[function_active](x, period, amplitude)
    return x, y

def calculate_approximation_value_pairs(function_active, period, amplitude,
        order):
    x = np.linspace(X_LEFT, X_RIGHT, 3000)
    y = function_approximations[function_active](x, period, amplitude, order)
    return x, y


# ColumnDataSource abstract the sending of new value pairs to the client for
# drawing over the WebSocket protocol
original_function_source = ColumnDataSource()
fourier_approximation_source = ColumnDataSource()


plot = Figure(plot_height=HEIGHT, plot_width=WIDTH_PLOT,
        x_range=[X_LEFT, X_RIGHT], y_range=[Y_BOT, Y_TOP])
plot.toolbar.active_drag = None

plot.line(x="x", y="y", source=original_function_source, line_width=LINE_WIDTH,
        color="black")
plot.line(x="x", y="y", source=fourier_approximation_source,
        line_width=LINE_WIDTH_APPROXIMATION, color="red")

function_selector = RadioButtonGroup(labels=["Rechteck", "Sägezahn",
        "Bogen mit Lücke"], active=0)
order_slider = Slider(title="Ordnung der Approximation", start=1, end=50,
        step=1, value=2)
advanced_toggle = Toggle(label="Erweiterte Optionen aktivieren")
period_slider = Slider(title="Periodenlänge der Originalfunktion", start=0.1,
        end=2, step=0.1, value=1, visible=False)
amplitude_slider = Slider(title="Amplitude der Originalfunktion", start=-2,
        end=2, step=0.1, value=1, visible=False)


# Callback handlers
def update_approximation(attr, old, new):
    x, y = calculate_approximation_value_pairs(function_selector.active,
            period_slider.value, amplitude_slider.value, order_slider.value)
    fourier_approximation_source.data = {"x": x, "y": y}

def update_original(attr, old, new):
    x, y = calculate_original_value_pairs(function_selector.active,
            period_slider.value, amplitude_slider.value)
    original_function_source.data = {"x": x, "y": y}
    update_approximation(0, 0, 0)

def toggle_callback(source):
    """
    Enables the 'more advanced' options so that the user is not distracted by
    the functionality in the first place
    """
    advanced_toggle.visible = False
    period_slider.visible = True
    amplitude_slider.visible = True

def selector_callback(source):
    update_original(0, 0, 0)


# Call callback in advance to populate the plot
update_original(0, 0, 0)

# Connect the widgets with their respective callbacks
order_slider.on_change("value", update_approximation)

advanced_toggle.on_click(toggle_callback)

for original_slider in (period_slider, amplitude_slider):
    original_slider.on_change("value", update_original)

function_selector.on_click(selector_callback)

# Assemble the plot and create the html
inputs = WidgetBox(function_selector, order_slider, advanced_toggle,
        period_slider, amplitude_slider)
curdoc().add_root(Row(plot, inputs, width=WIDTH_TOTAL))
