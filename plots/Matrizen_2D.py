import numpy as np

from bokeh.io import curdoc
from bokeh.layouts import row, widgetbox
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import Slider, RadioButtonGroup
from bokeh.plotting import figure

from extensions.Latex import LatexLabel

HEIGHT = 400
WIDTH_PLOTS = 300
WIDTH_TOTAL = 800

plot_left = figure(plot_height=HEIGHT, plot_width=WIDTH_PLOTS, tools="")
plot_right = figure(plot_height=HEIGHT, plot_width=WIDTH_PLOTS, tools="")
plot_right.line(x=[2,3], y=[2,3])
matrix_label = LatexLabel(text="""
   \\begin{pmatrix}
   2 & 3 \cr
    3 & 4
   \end{pmatrix}
""", x=0, y=-40, x_units="screen", y_units="screen", render_mode="css", text_font_size="10pt", background_fill_alpha=0)
plot_left.add_layout(matrix_label)

matrix_selector = RadioButtonGroup(labels=["Matrix 1", "Matrix 2", "Matrix 3"], active=0)
parameter_a = Slider(title="Parameter a", value=1., start=-3, end=3, step=0.1)
parameter_b = Slider(title="Parameter b", value=1., start=-3, end=3, step=0.1)
progress = Slider(title="Lineare Vorfaktor der Transformation", value=1., start=0., end=1., step=0.1)

inputs = widgetbox(matrix_selector, parameter_a, parameter_b, progress)

curdoc().add_root(row(plot_left, plot_right, inputs))
