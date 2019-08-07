import numpy as np

from bokeh.io import curdoc
from bokeh.layouts import Row, WidgetBox
from bokeh.models import ColumnDataSource

from extensions.vector3d import Vector3d

source = ColumnDataSource(data={"x": [1, ], "y": [1, ], "z": [1, ]})

vector_field = Vector3d(x="x", y="y", z="z", data_source=source)

curdoc().add_root(vector_field)
