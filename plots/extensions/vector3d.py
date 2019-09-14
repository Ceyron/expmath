from bokeh.core.properties import Instance, String
from bokeh.models import ColumnDataSource, LayoutDOM
from bokeh.util.compiler import TypeScript

# General constants for the 3d plot
plot_width = 400
plot_height = 400
line_width = 4
x_range = [-5, 5]
y_range = [-5, 5]
z_range = [-5, 5]


"""
The TypeScript code initializes visJS library to plot a 3d scence. It therefore
connects the bokeh ColumnDataSource that is sent to the client with the 3d
plot's input. A listener is set up that will update the plot every time new data
is sent
"""


# This custom extension model will have a DOM view that should layout-able in
# Bokeh layouts, so use ``LayoutDOM`` as the base class. If you wanted to create
# a custom tool, you could inherit from ``Tool``, or from ``Glyph`` if you
# wanted to create a custom glyph, etc.
class Vector3d(LayoutDOM):

    # The special class attribute ``__implementation__`` should contain a string
    # of JavaScript (or CoffeeScript) code that implements the JavaScript side
    # of the custom extension model.
    __implementation__ = TypeScript(open("extensions/vector3d.ts", "r").read() %
            (plot_width, plot_height, line_width, x_range[0], x_range[1],
            y_range[0], y_range[1], z_range[0], z_range[1]))

    # Below are all the "properties" for this model. Bokeh properties are
    # class attributes that define the fields (and their types) that can be
    # communicated automatically between Python and the browser. Properties
    # also support type validation. More information about properties in
    # can be found here:
    #
    #    https://bokeh.pydata.org/en/latest/docs/reference/core.html#bokeh-core-properties

    # This is a Bokeh ColumnDataSource that can be updated in the Bokeh
    # server by Python code
    data_source = Instance(ColumnDataSource)

    # The vis.js library that we are wrapping expects data for x, y, and z.
    # The data will actually be stored in the ColumnDataSource, but these
    # properties let us specify the *name* of the column that should be
    # used for each field.
    x = String

    y = String

    z = String

    u = String

    v = String

    w = String
