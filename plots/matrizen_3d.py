import numpy as np

from bokeh.io import curdoc
from bokeh.layouts import Row, WidgetBox, Column
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import Slider, Div, Toggle, RadioButtonGroup
from bokeh.plotting import Figure

from extensions.vector3d import Vector3d
from extensions.Latex import LatexLabel

"""
This plot uses an overridden DOMlayout element together with the visJS library
to render a 3d context with two vectors in it. On of it is the input of a linear
transformation. The other one is the output. Three sliders let the user control
the input's components. The type of linear transformation matrix can be chosen
by a RadioButtonGroup selector, and its parameters are adjusted by sliders.

The following downsides of this implementation so far:
    * The vectors can only have one color. This makes distinguishing between the
    input and the ouput vector difficult. The workaround is that the user can
    toggle the rendering of the output vector.
    * Now latex representation of the matrix is given. All latex labels must be
    attached to an instance of the Figure Object. However, the used DOMlayout
    does not inherit the 'add_layout' method.
    * The rendering of the vectors within visJS seems to be slightly off. For
    example, if the x_component is set to 1, the vector is drawn with x~1.3
    * The camera of the 3D scene within visJS can not be moved totally freely.
    This could be handy, since the user would then be able to see the projection
    of the 3D scene on the xy-, yz-, yz-plain
"""

# Slider contants for adjusting the components of the input vector
INPUT_VECTOR_SLIDER_START = -3
INPUT_VECTOR_SLIDER_END = 3
INPUT_VECTOR_SLIDER_STEP = 0.1


# Slider constants for adjusting the parameters of the matrices
PARAMETER_SLIDER_START = -3
PARAMETER_SLIDER_END = 3
PARAMETER_SLIDER_STEP = 0.1


def apply_transformation(matrix_active, x, y, z, a, b, c):
    vector_in = np.array([x, y, z])
    if matrix_active == 0:  # Mirroring matrix
        matrix = np.array([
                [a, 0, 0],
                [0, b, 0],
                [0, 0, c]
                ])
    elif matrix_active == 1:  # Simple rotation around z-axis
        matrix = np.array([
                [np.cos(a), -np.sin(a), 0],
                [np.sin(a), np.cos(a), 0],
                [0, 0, 1]
                ])
    elif matrix_active == 2:  # General rotation aroun every axis
        matrix_x = np.array([
                [1, 0, 0],
                [0, np.cos(a), -np.sin(a)],
                [0, np.sin(a), np.cos(a)]
                ])
        matrix_y = np.array([
                [np.cos(b), 0, -np.sin(b)],
                [0, 1, 0],
                [np.sin(b), 0, np.cos(b)]
                ])
        matrix_z = np.array([
                [np.cos(a), -np.sin(a), 0],
                [np.sin(a), np.cos(a), 0],
                [0, 0, 1]
                ])
        matrix = matrix_x.dot(matrix_y.dot(matrix_z))
    else:
        return 1, 1, 1
    vector_out = matrix.dot(vector_in)

    return vector_out[0], vector_out[1], vector_out[2]


# ColumnDataSource abstract the sending of new value pairs to the client
source = ColumnDataSource(data={"x": [1, ], "y": [1, ], "z": [1, ], "u": [0, ],
    "v": [0, ], "w": [0, ]})

# Instantiates the DOMlayout element that was extended with the visJS library
vector_field = Vector3d(x="x", y="y", z="z", u="u", v="v", w="w",
        data_source=source)

input_vector_x_slider = Slider(title="x Komponente des Ausgangsvektors",
        start=INPUT_VECTOR_SLIDER_START, end=INPUT_VECTOR_SLIDER_END,
        step=INPUT_VECTOR_SLIDER_STEP, value=1)
input_vector_y_slider = Slider(title="y Komponente des Ausgangsvektors",
        start=INPUT_VECTOR_SLIDER_START, end=INPUT_VECTOR_SLIDER_END,
        step=INPUT_VECTOR_SLIDER_STEP, value=1)
input_vector_z_slider = Slider(title="z Komponente des Ausgangsvektors",
        start=INPUT_VECTOR_SLIDER_START, end=INPUT_VECTOR_SLIDER_END,
        step=INPUT_VECTOR_SLIDER_STEP, value=1)

# Currently, only vectors of one color can be drawn. Therefore, the user can
# enable and disable the drawing of the output vector, so that he can still see
# the change happening when the transformation applies
matrix_toggle = Toggle(label="Transformierten Vektor anzeigen")
matrix_selector = RadioButtonGroup(labels=["Spiegelmatrix", "Simple\
        Drehmatrix", "Allg. Drehmatrix"], active=0, visible=False)
parameter_a_slider = Slider(title="Parameter a", start=PARAMETER_SLIDER_START,
        end=PARAMETER_SLIDER_END, step=PARAMETER_SLIDER_STEP,
        value=-2, visible=False)
parameter_b_slider = Slider(title="Parameter b", start=PARAMETER_SLIDER_START,
        end=PARAMETER_SLIDER_END, step=PARAMETER_SLIDER_STEP,
        value=1, visible=False)
parameter_c_slider = Slider(title="Parameter c", start=PARAMETER_SLIDER_START,
        end=PARAMETER_SLIDER_END, step=PARAMETER_SLIDER_STEP,
        value=1, visible=False)

# The spacing is necessary since the overridden DOMlayout element unfortunately
# does not use an own DIV element, which makes all elements below being rendered
# on top of the 3D plot. Inserting a DIV that is thin but still high enough will
# simply get rid of this problem.
spacing = Div(text="", width=50, height=400)


# TODO Attach a latex label to the plot, so that the mathematical notation of
# the currently active transformation can be seen. However, since the Vector3D
# instance is not a Figure element, one can not simple attach a label to it. 

# Define callbacks
def update_slider(attr, old, new):
    x_value = input_vector_x_slider.value
    y_value = input_vector_y_slider.value
    z_value = input_vector_z_slider.value

    if matrix_toggle.active:
        u_value, v_value, w_value = apply_transformation(matrix_selector.active,
                x_value, y_value, z_value, parameter_a_slider.value,
                parameter_b_slider.value, parameter_c_slider.value)
    else:
        u_value = 0
        v_value = 0
        w_value = 0

    source.data = {"x": [x_value, ], "y": [y_value, ], "z": [z_value, ], "u":
            [u_value, ], "v": [v_value, ], "w": [w_value, ]}

def update_toggle(source):
    if matrix_toggle.active:
        matrix_selector.visible = True
        parameter_a_slider.visible = True
        parameter_b_slider.visible = True
        parameter_c_slider.visible = True
    else:
        matrix_selector.visible = False 
        parameter_a_slider.visible = False
        parameter_b_slider.visible = False
        parameter_c_slider.visible = False
    update_slider(0, 0, 0)


# Connect widgets with their respective callbacks
for slider in (input_vector_x_slider, input_vector_y_slider,
        input_vector_z_slider, parameter_a_slider, parameter_b_slider,
        parameter_c_slider):
    slider.on_change("value", update_slider)

matrix_toggle.on_click(update_toggle)

# Assemble the plot and create the html
inputs = WidgetBox(input_vector_x_slider, input_vector_y_slider,
        input_vector_z_slider, matrix_toggle, matrix_selector,
        parameter_a_slider, parameter_b_slider, parameter_c_slider)
curdoc().add_root(Row(inputs, spacing, vector_field))
