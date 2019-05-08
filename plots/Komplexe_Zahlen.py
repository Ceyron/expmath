import numpy as np

from bokeh.io import curdoc
from bokeh.models import Arrow, NormalHead, ColumnDataSource
from bokeh.plotting import figure
from bokeh.models.widgets import Slider, RadioButtonGroup
from bokeh.layouts import row, widgetbox

HEIGHT = 400
WIDTH_PLOT = 600
WIDTH_TOTAL = 800

used_degree = True

def update_data_polar(real, imaginary, radius, degree_or_radian, angle, number_source):
    global used_degree
    radius_value = radius.value
    if degree_or_radian.active == 0:
        if used_degree == True:
            angle_value = angle.value * np.pi / 180
        else:
            angle_value = angle.value
            angle.start = 0
            angle.end = 360
            angle.step = 5
            used_degree = True
    else:
        if used_degree == True:
            angle_value = angle.value * np.pi / 180
            angle.start = 0
            angle.end = 2 * np.pi
            angle.step = 2 * np.pi / 75
            used_degree = False
        else:
            angle_value = angle.value
    new_real = radius_value * np.cos(angle_value)
    new_imaginary = radius_value * np.sin(angle_value)

    number_source.data = {"x": (new_real, ), "y": (new_imaginary, )}
    real.value = new_real
    imaginary.value = new_imaginary

def update_data_cartesian(real, imaginary, radius, degree_or_radian, angle, number_source):
    real_value = real.value
    imaginary_value = imaginary.value

    number_source.data = {"x": (0, real_value, ), "y": (0, imaginary_value, ), "rads": (0, 12, )}
    
    new_radius = np.sqrt(real_value**2 + imaginary_value**2)
    new_angle = np.arctan2(imaginary_value, real_value)

    radius.value = new_radius
    if degree_or_radian.active == 0:
        angle.value = new_angle * 180 / np.pi
    else:
        angle.value = new_angle


number_source = ColumnDataSource()

plot = figure(plot_height=HEIGHT, plot_width=WIDTH_PLOT, tools="", x_range=[-5, 5], y_range=[-5, 5])
plot.cross(x="x", y="y", size="rads", source=number_source)
plot.line(x="x", y="y", source=number_source)

real = Slider(title="Realteil", start=-5, end=5, value=4, step=0.1)
imaginary = Slider(title="Imaginärteil", start=-5, end=5, value=3, step=0.1)
radius = Slider(title="Radius", start=0, end=7, value=5, step=0.1)
degree_or_radian = RadioButtonGroup(labels=["Grad", "Bogenmaß"], active=0)
angle = Slider(title="Phasenwinkel", start=0, end=360, value=30, step=5)


update_data_cartesian(real, imaginary, radius, degree_or_radian, angle, number_source)

used_cartesian = True
used_polar = True

def update_slider_cartesian(attr, old, new):
    update_data_cartesian(real, imaginary, radius, degree_or_radian, angle, number_source)

def update_slider_polar(attr, old, new):
    update_data_polar(real, imaginary, radius, degree_or_radian, angle, number_source)

def update_button(source):
    update_data_polar(real, imaginary, radius, degree_or_radian, angle, number_source)

for cartesian_slider in (real, imaginary):
    cartesian_slider.on_change("value", update_slider_cartesian)

#for polar_slider in (radius, angle):
#    polar_slider.on_change("value", update_slider_polar)

#for button in (degree_or_radian, ):
#    button.on_click(update_button)

inputs = widgetbox(real, imaginary, radius, degree_or_radian, angle)

curdoc().add_root(row(plot, inputs, width=WIDTH_TOTAL))
