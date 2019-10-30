import numpy as np

from bokeh.io import curdoc
from bokeh.models import Arrow, NormalHead, ColumnDataSource
from bokeh.plotting import figure
from bokeh.models.widgets import Slider, RadioButtonGroup, Div
from bokeh.layouts import row, widgetbox

"""
This plot introduces the user to the Gaussian number plain, a way to
visualize complex numbers. Sliders can be used to change the real
and imaginary part (in cartesin mode) or the radius and angle (in
polar mode). The coordinates for the system other than the one chosen
are calculated and presented below the sliders. The user can switch
between degrees and radians for the angle measure.
"""

# Geometry constants of the plot
HEIGHT = 400
WIDTH_PLOT = 600
WIDTH_TOTAL = 800
DIV_BOX_WIDTH = WIDTH_TOTAL - WIDTH_PLOT
DIV_BOX_HEIGHT = 50

# The viewport the user initially starts in
X_LEFT = -5
X_RIGHT = 5
DISTORTION = HEIGHT/WIDTH_PLOT
Y_BOTTOM = DISTORTION * X_LEFT
Y_TOP = DISTORTION *  X_RIGHT

# Constants defining the size of the arrow-like thing
ARROW_LINE_WIDTH = 3
ARROWHEAD_CROSS_SIZE = 15

def redraw_plot(cartesian_or_polar, degree_or_radian, real_or_radius_slider,
        imaginary_or_angle_slider, number_source):
    """
    This callback handler calcuates the position of the complex number
    based on the slider values and the chosen input method (cartesian/
    polar and degrees/radian). It then fills the corresponding data_streamer
    """
    if cartesian_or_polar.active == 0: # Cartesian
        real = real_or_radius_slider.value
        imaginary = imaginary_or_angle_slider.value
    else: # Polar
        radius = real_or_radius_slider.value
        if degree_or_radian.active == 0: # Degrees
            angle = np.deg2rad(imaginary_or_angle_slider.value)
        else: # Radians
            angle = imaginary_or_angle_slider.value
        real = radius * np.cos(angle)
        imaginary = radius * np.sin(angle)
    # We need to send the (static) sizes of the crosses, since once
    # a plotted object in bokeh is drawn based upon a ColumnDataSource,
    # every multidimensional argument (like the two different cross sizes
    # we want to represent an arrow) has to be within this data streamer
    number_source.data = {
        "x": [0, real],
        "y": [0, imaginary],
        "size": [0, ARROWHEAD_CROSS_SIZE],
    }


def fill_boxes_for_other_coordinates(cartesian_or_polar, degree_or_radian, real_or_radius_slider, imaginary_or_angle_slider, radius_or_real_box, angle_or_imaginary_box):
    """
    This callback handler calculates the counterpart coordinates in the
    other coordinate system (e.g., polar coordinates out of cartesian)
    and then fills Div-Boxes below the sliders. This will give the user
    a hint how both addressing methods are related with each other
    TODO: Update the formatting in the boxes
    """
    if cartesian_or_polar.active == 0: # Cartesian
        real = real_or_radius_slider.value
        imaginary = imaginary_or_angle_slider.value

        radius = np.sqrt(real**2 + imaginary**2)
        radius_or_real_box.text = "zugehöriger Abstand vom Ursprung: " + str(round(radius, 2))
        if degree_or_radian.active == 0: # Degrees
            angle = np.rad2deg(np.arctan2(imaginary, real))
            angle_or_imaginary_box.text = "zugehöriger Winkel: " + str(round(angle, 1)) + "°"
        else: # Radians
            angle = np.arctan2(imaginary, real)
            angle_or_imaginary_box.text = "zugehöriger Winkel: " + str(round(angle, 3))
    else: # Polar
        radius = real_or_radius_slider.value
        if degree_or_radian.active == 0: # Degrees
            angle = np.deg2rad(imaginary_or_angle_slider.value)
        else: # Radians
            angle = imaginary_or_angle_slider.value

        real = radius * np.cos(angle)
        imaginary = radius * np.sin(angle)

        #print "Zugehörige kartesische Darstellung: "
        radius_or_real_box.text = "zugehöriger Realteil x = " + str(round(real, 2))
        angle_or_imaginary_box.text = "zugehöriger Imaginärteil y = " + str(round(imaginary, 2))


def switch_cartesian_polar(cartesian_or_polar, degree_or_radian, real_or_radius_slider, imaginary_or_angle_slider):
    """
    This callback handler is responsible for a change in the addressing
    method (e.g., when changing from a cartesian to a polar coordinate
    system). This induces a change in the sliders (Their title, step, limits
    and obiviously their value has to be changed).
    The necessary change in the boxes is done by the previous callback
    handler which is immediately called when the sliders' values change
    """
    if cartesian_or_polar.active == 0: # This means it must have been 1 before
                                       # (polar -> cartesian)
        radius = real_or_radius_slider.value
        if degree_or_radian.active == 0: # Degrees
            angle = np.deg2rad(imaginary_or_angle_slider.value)
        else: # Radians
            angle = imaginary_or_angle_slider.value

        real = radius * np.cos(angle)
        imaginary = radius * np.sin(angle)

        real_or_radius_slider.title = "Realteil x"
        real_or_radius_slider.start = -5
        real_or_radius_slider.end = 5
        real_or_radius_slider.value = real
        real_or_radius_slider.step = 0.1

        imaginary_or_angle_slider.title = "Imaginärteil y"
        imaginary_or_angle_slider.start = -5
        imaginary_or_angle_slider.end = 5
        imaginary_or_angle_slider.value = imaginary
        imaginary_or_angle_slider.step = 0.1
    else: # This means it must have been 0 before (cartesian -> polar)
        real = real_or_radius_slider.value
        imaginary = imaginary_or_angle_slider.value

        radius = np.sqrt(real**2 + imaginary**2)
        if degree_or_radian.active == 0: # Degrees
            angle = np.rad2deg(np.arctan2(imaginary, real))
        else: # Radians
            angle = np.arctan2(imaginary, real)

        real_or_radius_slider.title = "Abstand r vom Ursprung"
        real_or_radius_slider.start = 0
        real_or_radius_slider.end = 5
        real_or_radius_slider.value = radius
        real_or_radius_slider.step = 0.1

        imaginary_or_angle_slider.title = "Winkel"
        if degree_or_radian.active == 0: # Degrees
            imaginary_or_angle_slider.start = -180
            imaginary_or_angle_slider.end = 360
            imaginary_or_angle_slider.step = 2
        else: # Radians
            imaginary_or_angle_slider.start = -np.pi
            imaginary_or_angle_slider.end = np.pi
            imaginary_or_angle_slider.step = 0.1
        imaginary_or_angle_slider.value = angle
    # Note: no update to the boxes is needed, since the change in the slider
    # values will automatically activate the callback handlers


def switch_degree_radian(cartesian_or_polar, degree_or_radian,
        real_or_radius_slider, imaginary_or_angle_slider,
        angle_or_imaginary_box):
    if cartesian_or_polar.active == 0: # Cartesian: The angle occurs in the div
                                       # boxes below the sliders
        real = real_or_radius_slider.value
        imaginary = imaginary_or_angle_slider.value

        if degree_or_radian.active == 0: # Degrees
            angle = np.rad2deg(np.arctan2(imaginary, real))
            angle_or_imaginary_box.text = "zugehöriger Winkel : " + str(round(angle, 1)) + "°"
        else: # Radians
            angle = np.arctan2(imaginary, real)
            angle_or_imaginary_box.text = "zugehöriger Winkel : " + str(round(angle, 3))
    else: # Polar: The angle occurs in the sliders
        if degree_or_radian.active == 0: #  This means it was 1 (radian ->
                                         #  degrees)
            angle_radian = imaginary_or_angle_slider.value
            angle_degrees = np.rad2deg(angle_radian)

            imaginary_or_angle_slider.start = -180
            imaginary_or_angle_slider.end = 360
            imaginary_or_angle_slider.value = angle_degrees
            imaginary_or_angle_slider.step = 2
        else: # This means it was 0 (degrees -> radian)
            angle_degrees = imaginary_or_angle_slider.value
            angle_radian = np.deg2rad(angle_degrees)

            imaginary_or_angle_slider.start = -np.pi
            imaginary_or_angle_slider.end = np.pi
            imaginary_or_angle_slider.value = angle_radian
            imaginary_or_angle_slider.step = 0.1


number_source = ColumnDataSource()

plot = figure(plot_height=HEIGHT, plot_width=WIDTH_PLOT, 
        x_range=[X_LEFT, X_RIGHT], y_range=[Y_BOTTOM, Y_TOP], match_aspect=True)
plot.toolbar.active_drag = None

# Use thin black lines to indicate x-axis and y-axis
plot.line(x=[-10, 10], y=[0, 0], color="black")
plot.line(x=[0, 0], y=[-10, 10], color="black")

# Currently, there is no interactive arrow element in bokeh. Therefore,
# we cheat by using a line with a cross at the end
plot.cross(x="x", y="y", size="size", line_width=ARROW_LINE_WIDTH,
        source=number_source)
plot.line(x="x", y="y", line_width=ARROW_LINE_WIDTH, source=number_source)

cartesian_or_polar = RadioButtonGroup(labels=["Kartesisch", "Polar"], active=0)
degree_or_radian = RadioButtonGroup(labels=["Grad", "Bogenmaß"], active=0)
real_or_radius_slider = Slider(title="Realteil x", start=-5, end=5, value=4,
        step=0.1)
imaginary_or_angle_slider = Slider(title="Imaginärteil y", start=-5, end=5,
        value=3, step=0.1)
radius_or_real_box = Div(width=DIV_BOX_WIDTH, height=DIV_BOX_HEIGHT)
angle_or_imaginary_box = Div(width=DIV_BOX_WIDTH, height=DIV_BOX_HEIGHT)

# Use the update functions once in advane to populate the plot
redraw_plot(cartesian_or_polar, degree_or_radian, real_or_radius_slider,
        imaginary_or_angle_slider, number_source)
fill_boxes_for_other_coordinates(cartesian_or_polar, degree_or_radian,
        real_or_radius_slider, imaginary_or_angle_slider, radius_or_real_box,
        angle_or_imaginary_box)

# Defining callbacks
def update_slider(attr, old, new):
    redraw_plot(cartesian_or_polar, degree_or_radian, real_or_radius_slider,
            imaginary_or_angle_slider, number_source)
    fill_boxes_for_other_coordinates(cartesian_or_polar, degree_or_radian,
            real_or_radius_slider, imaginary_or_angle_slider,
            radius_or_real_box, angle_or_imaginary_box)

def update_coordinate_addressing(source):
    switch_cartesian_polar(cartesian_or_polar, degree_or_radian,
            real_or_radius_slider, imaginary_or_angle_slider)

def update_angle_measure(source):
    switch_degree_radian(cartesian_or_polar, degree_or_radian,
            real_or_radius_slider, imaginary_or_angle_slider,
            angle_or_imaginary_box)

# Connect widgets with their respective callbacks
for slider in (real_or_radius_slider, imaginary_or_angle_slider, ):
    slider.on_change("value", update_slider)

cartesian_or_polar.on_click(update_coordinate_addressing)
degree_or_radian.on_click(update_angle_measure)

# Assemble plot and create html
inputs = widgetbox(cartesian_or_polar, degree_or_radian, real_or_radius_slider,
        imaginary_or_angle_slider, radius_or_real_box, angle_or_imaginary_box)
curdoc().add_root(row(plot, inputs, width=WIDTH_TOTAL))
