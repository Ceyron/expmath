import numpy as np

from bokeh.io import curdoc
from bokeh.layouts import row, widgetbox
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import Slider, RadioButtonGroup
from bokeh.plotting import figure

# Geometry Constants of the plot
HEIGHT = 400
WIDTH_PLOT = 600
WIDTH_TOTAL = 800

# The initial viewport the user starts in
X_LEFT = -4
X_RIGHT = 4
Y_BOTTOM = -3
Y_TOP = 3

# Limits of the imaginary and real slider
CARTESIAN_SLIDER_LIMITS = (-3, 3)
RADIUS_SLIDER_LIMIT = (0.3, 4)


def switch_cartesian_polar(cartesian_or_polar, real_or_radius,
        imaginary_or_angle):
    '''
    This function is used as the callback for the RadioButtonGroup that allows
    for the switch between a cartesian or a polar representation of the complex
    number (i.e., the radicant). It sets the corresponding attributes of the
    two sliders and converts the values of the cartesian representation
    (real and imaginary part) into the polar representation (radius and
    angle/phase) and vice versa.  The inner mechanics of bokeh register the
    change in the slider values on the client- side as if the user was to
    change them. Therefore, the appropriate callback handlers will then be
    called calcuting the data the plot is redrawm upon.
    '''
    if cartesian_or_polar.active == 0:  # previously polar
        radius = real_or_radius.value
        angle = imaginary_or_angle.value

        # Calculate the real part out of radius and angle
        real_or_radius.title = "Realteil"
        real_or_radius.start = -CARTESIAN_SLIDER_LIMITS[0]
        real_or_radius.end = CARTESIAN_SLIDER_LIMITS[1]
        real_or_radius.value = radius * np.cos(np.deg2rad(angle))
        real_or_radius.step = 0.1

        # Calculate the imaginary part out of radius and angle
        imaginary_or_angle.title = "Imaginärteil"
        imaginary_or_angle.start = -CARTESIAN_SLIDER_LIMITS[0]
        imaginary_or_angle.end = CARTESIAN_SLIDER_LIMITS[1]
        imaginary_or_angle.value = radius * np.sin(np.deg2rad(angle))
        imaginary_or_angle.step = 0.1

    elif cartesian_or_polar.active == 1:  # previously cartesian
        real = real_or_radius.value
        imaginary = imaginary_or_angle.value

        # Calculate the radius out of real and imaginary part
        real_or_radius.title = "Abstand r vom Ursprung"
        real_or_radius.start = RADIUS_SLIDER_LIMIT[0]
        real_or_radius.end = RADIUS_SLIDER_LIMIT[1] 
        real_or_radius.value = np.sqrt(real**2 + imaginary**2)
        real_or_radius.step=0.1

        # Calculate the angle out of real and imaginary part
        imaginary_or_angle.title = "Winkel"
        imaginary_or_angle.start = 0.
        imaginary_or_angle.end = 360.
        imaginary_or_angle.value = np.rad2deg(np.arctan2(imaginary, real))
        imaginary_or_angle.step =  5.


def update_data(cartesian_or_polar, real_or_radius, imaginary_or_angle, order,
        circle_source, polyeder_source, radicant_number_source):
    '''
    This function is used as a callback for a change in the sliders. It first
    extracts the coordinates depending on the current representation and then
    converts them into their conterpart. The three ColumnDataSources are then
    filled appropriately.
    '''
    if cartesian_or_polar.active == 0:
        raticand_real = real_or_radius.value
        raticand_imaginary = imaginary_or_angle.value
        raticand_radius = np.sqrt(raticand_real**2 + raticand_imaginary**2)
        raticand_angle = np.rad2deg(np.arctan2(raticand_imaginary,
                raticand_real))
    else:
        raticand_radius = real_or_radius.value
        raticand_angle = imaginary_or_angle.value
        raticand_real = raticand_radius * np.cos(np.deg2rad(raticand_angle))
        raticand_imaginary = raticand_radius *\
                np.sin(np.deg2rad(raticand_angle))

    # The data for the arrow represting the radicand
    radicant_number_source.data = {
        "x": [0., raticand_real],
        "y": [0., raticand_imaginary],
        "sizes": [0, 15],
    }

    # The data for the outer circle which shares common points with
    # the vertices of the polyeder
    radius_circle = raticand_radius**(1/order.value)
    x_circle_top = np.linspace(radius_circle, -radius_circle, 50)
    x_circle_bottom = np.linspace(-radius_circle, radius_circle, 50)
    y_circle_top = np.sqrt(radius_circle**2 - x_circle_top**2)
    y_circle_bottom = -np.sqrt(radius_circle**2 - x_circle_bottom**2)
    x_circle = np.concatenate((x_circle_top, x_circle_bottom))
    y_circle = np.concatenate((y_circle_top, y_circle_bottom))
    circle_source.data = {
            "x": x_circle,
            "y": y_circle,
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


# The ColumnDataSource represents an AJAX-style element that abstracts the
# Websocket Connection between client BokehJS and the bokeh server
circle_source = ColumnDataSource()
polyeder_source = ColumnDataSource()
radicant_number_source = ColumnDataSource()

plot = figure(plot_height=HEIGHT, plot_width=WIDTH_PLOT,
        x_range=[X_LEFT, X_RIGHT], y_range=[Y_BOTTOM, Y_TOP])
plot.toolbar.active_drag = None
plot.line(x="x", y="y", color="black", source=circle_source)
plot.line(x="x", y="y", color="blue", source=polyeder_source)
plot.line(x="x", y="y", color="orange", source=radicant_number_source)
plot.cross(x="x", y="y", color="orange", size="sizes",
        source=radicant_number_source)

# The user can choose between a cartesian and polar representation. Within this
# script every angle is saved in degress. A conversion is easily done by the
# help of numpy's functions deg2rad and rad2deg
cartesian_or_polar_selector = RadioButtonGroup(labels=["Kartesisch", "Polar"],
        active=0)
real_or_radius_slider = Slider(title="Realteil", start=-5, end=5, value=1,
        step=0.1)
imaginary_or_angle_slider = Slider(title="Imaginärteil", start=-5, end=5,
        value=1, step=0.1)
order_slider = Slider(title="Ordnung der Wurzel", start=2, end=10, value=3,
        step=1)


update_data(cartesian_or_polar_selector, real_or_radius_slider,
        imaginary_or_angle_slider, order_slider, circle_source, polyeder_source,
        radicant_number_source)


def update_slider(attr, old, new):
    update_data(cartesian_or_polar_selector, real_or_radius_slider,
            imaginary_or_angle_slider, order_slider, circle_source,
            polyeder_source, radicant_number_source)

def update_button(source):
    switch_cartesian_polar(cartesian_or_polar_selector, real_or_radius_slider,
            imaginary_or_angle_slider)

# Connect the widgets with their respective callbacks
for button in (cartesian_or_polar_selector, ):
    button.on_click(update_button)

for slider in (real_or_radius_slider, imaginary_or_angle_slider, order_slider):
    slider.on_change("value", update_slider)

# Assemble the plot and create the html
inputs = widgetbox(cartesian_or_polar_selector, real_or_radius_slider,
        imaginary_or_angle_slider, order_slider)
curdoc().add_root(row(plot, inputs, width=WIDTH_TOTAL))
