import numpy as np

from bokeh.io import curdoc
from bokeh.layouts import row, widgetbox
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import Slider, RadioButtonGroup
from bokeh.plotting import figure


HEIGHT= 400
WIDTH_PLOT=600
WIDTH_TOTAL = 800

def switch_cartesian_polar(cartesian_or_polar, real_or_radius, imaginary_or_angle):
    '''
    This function is used as the callback for the RadioButtonGroup that allows for the
    switch between a cartesian or a polar representation of the complex number (i.e.,
    the radicant). It sets the corresponding attributes of the two sliders and converts
    the values of the cartesian representation (real and imaginary part) into the polar
    representation (radius and angle/phase) and vice versa.
    The inner mechanics of bokeh register the change in the slider values on the client-
    side as if the user was to change them. Therefore, the appropriate callback handlers
    will then be called calcuting the data the plot is redrawm upon.
    '''
    if cartesian_or_polar.active == 0:
        radius = real_or_radius.value
        angle = imaginary_or_angle.value

        # Calculate the real part out of radius and angle
        real_or_radius.title = "Realteil"
        real_or_radius.start = -5
        real_or_radius.end = 5
        real_or_radius.value = radius * np.cos(angle)
        real_or_radius.step = 0.1

        # Calculate the imaginary part out of radius and angle
        imaginary_or_angle.title = "Imaginärteil"
        imaginary_or_angle.start = -5
        imaginary_or_angle.end = 5
        imaginary_or_angle.value = radius * np.sin(angle)
        imaginary_or_angle.step = 0.1

    elif cartesian_or_polar.active == 1:
        real = real_or_radius.value
        imaginary = imaginary_or_angle.value

        # Calculate the radius out of real and imaginary part
        real_or_radius.title = "Radius"
        real_or_radius.start = 0.3
        real_or_radius.end = 7.
        real_or_radius.value = np.sqrt(real**2 + imaginary**2)
        real_or_radius.step=0.1

        # Calculate the angle out of real and imaginary part
        imaginary_or_angle.title = "Winkel"
        imaginary_or_angle.start = -180.
        imaginary_or_angle.end = 180.
        imaginary_or_angle.value = np.rad2deg(np.arctan2(imaginary, real))
        imaginary_or_angle.step =  5.


def update_data(cartesian_or_polar, real_or_radius, imaginary_or_angle, order, circle_source, polyeder_source, radicant_number_source):
    '''
    This function is used as a callback for a change in the sliders. It first extracts
    the coordinates depending on the current representation and then converts them
    into their conterpart. The three ColumnDataSources are then filled appropriately.
    '''
    if cartesian_or_polar.active == 0:
        raticand_real = real_or_radius.value
        raticand_imaginary = imaginary_or_angle.value
        raticand_radius = np.sqrt(raticand_real**2 + raticand_imaginary**2)
        raticand_angle = np.rad2deg(np.arctan2(raticand_imaginary, raticand_real))
    else:
        raticand_radius = real_or_radius.value
        raticand_angle = imaginary_or_angle.value
        raticand_real = raticand_radius * np.cos(np.deg2rad(raticand_angle))
        raticand_imaginary = raticand_radius * np.sin(np.deg2rad(raticand_angle))

    # The data for the arrow represting the radicand
    radicant_number_source.data = {
        "x": [0., raticand_real],
        "y": [0., raticand_imaginary],
        "sizes": [0, 15],
    }

    # The data for the outer circle which shares common points with
    # the vertices of the polyeder
    radius_circle = raticand_radius**(1/order.value)
    x_circle = np.linspace(-radius_circle, radius_circle, 60)
    y_circle = np.sqrt(radius_circle**2 - x_circle**2)
    circle_source.data = {
        "x": np.concatenate((x_circle, x_circle)),
        "y": np.concatenate((y_circle, -y_circle)),
    }

    # The data for the polyeder
    vertices_angle = np.linspace(0., 360., order.value + 1)
    vertices_angle += raticand_angle
    vertices_real = radius_circle * np.cos(np.deg2rad(vertices_angle))
    vertices_imaginary = radius_circle * np.sin(np.deg2rad(vertices_angle))
    polyeder_source.data = {
        "x": vertices_real,
        "y": vertices_imaginary,
    }


# The ColumnDataSource represents an AJAX-style element that abstracts the Websocket
# Connection between client BokehJS and the bokeh server
circle_source = ColumnDataSource()
polyeder_source = ColumnDataSource()
radicant_number_source = ColumnDataSource()

# match_aspect is used to not distort the circle
plot = figure(plot_height=HEIGHT, plot_width=WIDTH_PLOT, tools="", match_aspect=True)
plot.line(x="x", y="y", color="black", source=circle_source)
plot.line(x="x", y="y", color="blue", source=polyeder_source)
plot.line(x="x", y="y", color="orange", source=radicant_number_source)
plot.cross(x="x", y="y", color="orange", size="sizes", source=radicant_number_source)

# The user can choose between a cartesian and polar representation. Within this script
# every angle is saved in degress. A conversion is easily done by the help of numpy's
# functions deg2rad and rad2deg
cartesian_or_polar = RadioButtonGroup(labels=["Kartesisch", "Polar"], active=0)
real_or_radius = Slider(title="Realteil", start=-5, end=5, value=1, step=0.1)
imaginary_or_angle = Slider(title="Imaginärteil", start=-5, end=5, value=1, step=0.1)
order = Slider(title="Ordnung der Wurzel", start=2, end=10, value=2, step=1)

inputs = widgetbox(cartesian_or_polar, real_or_radius, imaginary_or_angle, order)

update_data(cartesian_or_polar, real_or_radius, imaginary_or_angle, order, circle_source, polyeder_source, radicant_number_source)

def update_button(source):
    switch_cartesian_polar(cartesian_or_polar, real_or_radius, imaginary_or_angle)

def update_slider(attr, old, new):
    update_data(cartesian_or_polar, real_or_radius, imaginary_or_angle, order, circle_source, polyeder_source, radicant_number_source)

for button in (cartesian_or_polar, ):
    button.on_click(update_button)

for slider in (real_or_radius, imaginary_or_angle, order):
    slider.on_change("value", update_slider)

curdoc().add_root(row(plot, inputs, width=WIDTH_TOTAL))
