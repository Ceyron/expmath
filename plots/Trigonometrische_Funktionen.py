import numpy as np

from bokeh.io import curdoc
from bokeh.layouts import row, widgetbox, column
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import Slider, RadioButtonGroup
from bokeh.plotting import figure

# These values are used to assemble the final look of the plot and slider
HEIGHT = 270
WIDTH_LEFT = 300
WIDTH_RIGHT = 600

'''
This function updates the dynamically ColumnDataSources that are send via the WebSocket connection. Based on the value of the slider phase and the currently selected trigonmetric function the values of the triangle within the unit circle, the relevant straight line and the values for plotting the function itself are populated.
'''
def update_data(phase, selector_trig, trig_values, triangle_values, active_values):
    x = np.linspace(0, phase.value, 100)
    trig_functions = [np.sin, np.cos, np.tan]  # A list of function pointers corresponding to the selection available by the RadioButtonGroup
    y = trig_functions[selector_trig.active](x)
    trig_values.data = {"x": x, "y": y}
    triangle_values.data = {"x": [0, np.cos(phase.value), np.cos(phase.value), 0], "y": [0, 0, np.sin(phase.value), 0], "radius": [0, 0, 0.05, 0]}
    active_values_functions = [
            {"x": [np.cos(phase.value), np.cos(phase.value)], "y": [0, np.sin(phase.value)]},
            {"x": [0, np.cos(phase.value)], "y": [0, 0]},
            {"x": [1, 1] if (0<=phase.value<=np.pi/2 or 3*np.pi/2<=phase.value<=2*np.pi) else [-1, -1], "y": [0, min(np.tan(phase.value), 2.)]},
            ]  # A list of dictionaries for the relevant line which length represents the value of the trigonometric function at the current phase angle
    active_values.data = active_values_functions[selector_trig.active]


circle_values = ColumnDataSource()
trig_values = ColumnDataSource()
triangle_values = ColumnDataSource()
active_values = ColumnDataSource()

plot_left = figure(plot_width=WIDTH_LEFT, plot_height=HEIGHT, x_range=[-2, 2], y_range=[-2, 2], tools="")
plot_right = figure(plot_width=WIDTH_RIGHT, plot_height=HEIGHT, x_range=[0, 8], y_range=[-2, 2], tools="")

selector_trig = RadioButtonGroup(labels=["Sinus", "Kosinus", "Tangenz"], active=0)
phase = Slider(title="Phase der trig. Funktion", start=0, end=2*np.pi, step=0.1, value=0.7)

x = np.linspace(-1, 1, 100)
y_top = np.sqrt(1 - x**2)

# TODO: Make circle drawing easier by using bokeh's built-in circle method
plot_left.line(x=x, y=y_top, color="black", line_width=2)
plot_left.line(x=x, y=-y_top, color="black", line_width=2)
plot_left.line(x="x", y="y", color="black", source=triangle_values)
plot_left.line(x="x", y="y", color="blue", source=active_values, line_width=2)
plot_left.circle(x="x", y="y", color="black", source=triangle_values, radius="radius")
plot_right.line(x="x", y="y", color="blue", source=trig_values, line_width=2)

update_data(phase, selector_trig, trig_values, triangle_values, active_values)

def update_slider(attr, old, new):
    update_data(phase, selector_trig, trig_values, triangle_values, active_values)

def update_button(source):
    update_data(phase, selector_trig, trig_values, triangle_values, active_values)

for slider in (phase, ):
    slider.on_change("value", update_slider)

for button in (selector_trig, ):
    button.on_click(update_button)

curdoc().add_root(column(row(plot_left, plot_right), selector_trig, phase))
