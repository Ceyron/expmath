import numpy as np

from bokeh.io import curdoc
from bokeh.layouts import row, widgetbox
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import Slider, RadioButtonGroup, Toggle
from bokeh.plotting import figure

from extensions.Latex import LatexLabel

"""
This interactive plot portraits the idea of matrices for linear transformations.
The user sees a left plot for the inverse image and a right plot for the image
of the transformation. Buttons also for a switch between multiple parameterized
matrices. The parameters are adjusted by sliders. An additional slider is used
for manipulating the 'intensity' of the transformation. Therefore, a linear
transition between the identity matrix and the selected matrix is used. This
helps in understanding that every acting matrix is only a combination of
rotation and scaling.

Possible questions could guide the user to identiy eigenvectors, the rotation
matrix, the scaling matrix etc.

Since there are now arrow objects in bokeh that can be interactivly changed
(they are only used for static annotations), an arrow (representing a vector) is
a line ending with a glyph.
"""

# Geometry constants of the plot
HEIGHT = 400
WIDTH_PLOTS = 300
WIDTH_TOTAL = 800

# The initial viewport the user starts in
X_LEFT = -4.5
X_RIGHT = 4.5
DISTORTION = HEIGHT / WIDTH_PLOTS
Y_BOTTOM = DISTORTION * X_LEFT
Y_TOP = DISTORTION *  X_RIGHT


ARROW_CROSS_SIZE = 15

# These are the fixed input vectors (inverse image). One could consider changing
# them or making them selectable by the user
VECTOR_1 = np.array([2, 3])
VECTOR_2 = np.array([2, 0])
VECTOR_3 = np.array([0, 2])

# These functions compute the matric product between each input vector and the
# current matrix. The progess slider value is used for the linear transition
# between the identity matrix and the currently active
def MATRIX_1(a, b, coefficient, vector):
    matrix = (1 - coefficient) * np.eye(2) +\
            coefficient * np.array([[1/2, a], [1, 1/2]])
    return matrix.dot(np.array(vector))
def MATRIX_2(a, b, coefficient, vector):
    matrix = (1 - coefficient) * np.eye(2) +\
            coefficient * np.array([[np.cos(a), -np.sin(a)],
                [np.sin(a), np.cos(a)]])
    return matrix.dot(np.array(vector))

def MATRIX_3(a, b, coefficient, vector):
    matrix = (1 - coefficient) * np.eye(2) +\
            coefficient * np.array([[0, a], [b, 0]])
    return matrix.dot(np.array(vector))
def MATRIX_4(a, b, coefficient, vector):
    matrix = (1 - coefficient) * np.eye(2) +\
            coefficient * np.array([[a, -b], [b, a]])
    return matrix.dot(np.array(vector))

matrices = [MATRIX_1, MATRIX_2, MATRIX_3, MATRIX_4]

# These strings are the blueprints for the latex labels. Keep in mind that we
# have to use % string formating instead of the more modern .format() method
# since the latter misinterprets the curly braces of the Latex syntax.
MATRIX_1_LATEX = """
    A =
    \\begin{pmatrix}
        0.5 & a \cr
        1 & 0.5
    \end{pmatrix}
    =
    \\begin{pmatrix}
        0.5 & %1.2f \cr
        1 & 0.5
    \end{pmatrix}
"""

MATRIX_2_LATEX = """
    A =
    \\begin{pmatrix}
        \cos(a) & -\sin(a) \cr
        \sin(a) & \cos(a)
    \end{pmatrix}
    =
    \\begin{pmatrix}
        \cos(%1.2f) & -\sin(%1.2f) \cr
        \sin(%1.2f) & \cos(%1.2f)
    \end{pmatrix}
"""

MATRIX_3_LATEX = """
    A =
    \\begin{pmatrix}
        a & 0 \cr
        0 & b
    \end{pmatrix}
    =
    \\begin{pmatrix}
        %1.2f & 0 \cr
        0 & %1.2f
    \end{pmatrix}
"""

MATRIX_4_LATEX = """
    A =
    \\begin{pmatrix}
        a & -b \cr
        b & a
    \end{pmatrix}
    =
    \\begin{pmatrix}
        %1.2f & %1.2f \cr
        %1.2f & %1.2f
    \end{pmatrix}
"""

matrices_latex = [MATRIX_1_LATEX, MATRIX_2_LATEX, MATRIX_3_LATEX,
        MATRIX_4_LATEX]

# General callback for slider changes and button clicks to redraw the plot
def calucate_vectors(matrix_selector, parameter_a, parameter_b, progress,
        vector_1_output, vector_2_output, vector_3_output):
    vector_1 = matrices[matrix_selector.active](parameter_a.value,
            parameter_b.value, progress.value, VECTOR_1)
    vector_2 = matrices[matrix_selector.active](parameter_a.value,
            parameter_b.value, progress.value, VECTOR_2)
    vector_3 = matrices[matrix_selector.active](parameter_a.value,
            parameter_b.value, progress.value, VECTOR_3)

    vector_1_output.data = {"x": [0, vector_1[0]], "y": [0, vector_1[1]],
            "size": [0, ARROW_CROSS_SIZE]}
    vector_2_output.data = {"x": [0, vector_2[0]], "y": [0, vector_2[1]],
            "size": [0, ARROW_CROSS_SIZE]}
    vector_3_output.data = {"x": [0, vector_3[0]], "y": [0, vector_3[1]],
            "size": [0, ARROW_CROSS_SIZE]}

# General callback for slider changes and button clicks to update the Latex
# label
def update_visual_formula(matrix_selector, parameter_a, parameter_b,
        matrix_label):
    if matrix_selector.active == 0:
        text = matrices_latex[0] % parameter_a.value
    elif matrix_selector.active == 1:
        text = matrices_latex[1] % (parameter_a.value, parameter_a.value,
                parameter_a.value, parameter_a.value)
    elif matrix_selector.active == 2:
        text = matrices_latex[2] % (parameter_a.value, parameter_b.value)
    elif matrix_selector.active == 3:
        text = matrices_latex[3] % (parameter_a.value, -parameter_b.value,
                parameter_b.value, parameter_a.value)
    matrix_label.text = text
    

# The ColumnDataSource of a vector is used for drawing the line as well as for
# drawing the cross at each end. Since we don't want a cross at the origin of
# the coordinate system, the size of the crosses at both ends of the line have
# to be incorporated.
vector_1_input = ColumnDataSource(data={
        "x": [0, VECTOR_1[0]],
        "y": [0, VECTOR_1[1]],
        "size": [0, ARROW_CROSS_SIZE]})
vector_2_input = ColumnDataSource(data={
        "x": [0, VECTOR_2[0]],
        "y": [0, VECTOR_2[1]],
        "size": [0, ARROW_CROSS_SIZE]})
vector_3_input = ColumnDataSource(data={
        "x": [0, VECTOR_3[0]],
        "y": [0, VECTOR_3[1]],
        "size": [0, ARROW_CROSS_SIZE]})


# ColumnDataSource abstract the sending of new value pairs to the client
vector_1_output = ColumnDataSource()
vector_2_output = ColumnDataSource()
vector_3_output = ColumnDataSource()


plot_left = figure(plot_height=HEIGHT, plot_width=WIDTH_PLOTS,
        x_range=[X_LEFT, X_RIGHT], y_range=[Y_BOTTOM, Y_TOP])
plot_left.toolbar.active_drag = None
plot_right = figure(plot_height=HEIGHT, plot_width=WIDTH_PLOTS,
        x_range=[X_LEFT, X_RIGHT], y_range=[Y_BOTTOM, Y_TOP])
plot_right.toolbar.active_drag = None

plot_left.line(x="x", y="y", source=vector_1_input, color="blue")
plot_left.line(x="x", y="y", source=vector_2_input, color="orange")
plot_left.line(x="x", y="y", source=vector_3_input, color="green")

plot_left.cross(x="x", y="y", size="size", source=vector_1_input, color="blue")
plot_left.cross(x="x", y="y", size="size", source=vector_2_input,
        color="orange")
plot_left.cross(x="x", y="y", size="size", source=vector_3_input, color="green")


plot_right.line(x="x", y="y", source=vector_1_output, color="blue")
plot_right.line(x="x", y="y", source=vector_2_output, color="orange")
plot_right.line(x="x", y="y", source=vector_3_output, color="green")

plot_right.cross(x="x", y="y", size="size", source=vector_1_output,
        color="blue")
plot_right.cross(x="x", y="y", size="size", source=vector_2_output,
        color="orange")
plot_right.cross(x="x", y="y", size="size", source=vector_3_output,
        color="green")

# The LatexLabel renders the matrix in mathematical notation. Right now it is
# attached to plot. Therefore, we have to manually move it out of the plot
# canvas into the most right column under the sliders and buttons. TODO:
# automate this process or write an extension for latex based div that can be
# combined with the bokeh widgets in the widgetbox representing the most right
# column
matrix_label = LatexLabel(text="", x=300, y=100, x_units="screen",
        y_units="screen", render_mode="css", text_font_size="10pt",
        background_fill_alpha=0)
plot_right.add_layout(matrix_label)

matrix_selector = RadioButtonGroup(labels=["Matrix 1", "Matrix 2", "Matrix 3",
        "Matrix 4"], active=0)
parameter_a = Slider(title="Parameter a", value=1., start=-3, end=3, step=0.1)
parameter_b = Slider(title="Parameter b", value=1., start=-3, end=3, step=0.1,
        visible=False)

progress_toggle = Toggle(label="Lineare Übergang von Einheitsmatrix aus\
        aktivieren")
progress = Slider(title="\"Intensität\" der Transformation", value=1., start=0.,
        end=1., step=0.01, visible=False)

calucate_vectors(matrix_selector, parameter_a, parameter_b, progress,
        vector_1_output, vector_2_output, vector_3_output)
update_visual_formula(matrix_selector, parameter_a, parameter_b, matrix_label)

# Defining callbacks
def update_button(source):
    calucate_vectors(matrix_selector, parameter_a, parameter_b, progress,
            vector_1_output, vector_2_output, vector_3_output)
    update_visual_formula(matrix_selector, parameter_a, parameter_b,
            matrix_label)
    if matrix_selector.active in (0, 1):
        parameter_b.visible = False
    else:
        parameter_b.visible = True

def update_slider(attr, old, new):
    calucate_vectors(matrix_selector, parameter_a, parameter_b, progress,
            vector_1_output, vector_2_output, vector_3_output)
    update_visual_formula(matrix_selector, parameter_a, parameter_b,
            matrix_label)

def update_toggle(source):
    progress_toggle.visible = False
    progress.visible = True

# Connect the widgets with their respective callbacks
for slider in (parameter_a, parameter_b, progress, ):
    slider.on_change("value", update_slider)

matrix_selector.on_click(update_button)
progress_toggle.on_click(update_toggle)

# Assemble the plot and create the html
inputs = widgetbox(matrix_selector, parameter_a, parameter_b, progress_toggle,
        progress)
curdoc().add_root(row(plot_left, plot_right, inputs))
