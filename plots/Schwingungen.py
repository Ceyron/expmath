import numpy as np

from bokeh.driving import count
from bokeh.layouts import row, widgetbox, column
from bokeh.io import curdoc
from bokeh.models import ColumnDataSource, Label
from bokeh.plotting import figure
from bokeh.util.compiler import TypeScript

from bokeh.models.widgets import Slider, Div

TS_CODE = """
import * as p from "core/properties"
import {Label, LabelView} from "models/annotations/label"
declare const katex: any

export class LatexLabelView extends LabelView {
  model: LatexLabel

  render(): void {
    //--- Start of copied section from ``Label.render`` implementation

    // Here because AngleSpec does units tranform and label doesn't support specs
    let angle: number
    switch (this.model.angle_units) {
      case "rad": {
        angle = -this.model.angle
        break
      }
      case "deg": {
        angle = (-this.model.angle * Math.PI) / 180.0
        break
      }
      default:
        throw new Error("unreachable code")
    }

    const panel = this.panel != null ? this.panel : this.plot_view.frame

    const xscale = this.plot_view.frame.xscales[this.model.x_range_name]
    const yscale = this.plot_view.frame.yscales[this.model.y_range_name]

    let sx = this.model.x_units == "data" ? xscale.compute(this.model.x) : panel.xview.compute(this.model.x)
    let sy = this.model.y_units == "data" ? yscale.compute(this.model.y) : panel.yview.compute(this.model.y)

    sx += this.model.x_offset
    sy -= this.model.y_offset

    //--- End of copied section from ``Label.render`` implementation
    // Must render as superpositioned div (not on canvas) so that KaTex
    // css can properly style the text
    this._css_text(this.plot_view.canvas_view.ctx, "", sx, sy, angle)

    // ``katex`` is loaded into the global window at runtime
    // katex.renderToString returns a html ``span`` element
    katex.render(this.model.text, this.el, {displayMode: true})
  }
}

export namespace LatexLabel {
  export type Attrs = p.AttrsOf<Props>

  export type Props = Label.Props
}

export interface LatexLabel extends LatexLabel.Attrs {}

export class LatexLabel extends Label {
  properties: LatexLabel.Props

  constructor(attrs?: Partial<LatexLabel.Attrs>) {
    super(attrs)
  }

  static initClass() {
    this.prototype.type = 'LatexLabel'
    this.prototype.default_view = LatexLabelView
  }
}
LatexLabel.initClass()
"""

class LatexLabel(Label):
    """A subclass of the Bokeh built-in `Label` that supports rendering
    LaTex using the KaTex typesetting library.

    Only the render method of LabelView is overloaded to perform the
    text -> latex (via katex) conversion. Note: ``render_mode="canvas``
    isn't supported and certain DOM manipulation happens in the Label
    superclass implementation that requires explicitly setting
    `render_mode='css'`).
    """
    __javascript__ = ["https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.6.0/katex.min.js"]
    __css__ = ["https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.6.0/katex.min.css"]
    __implementation__ = TypeScript(TS_CODE)


"""
This file creates an interactive chart presenting the oscialltions of a one-
dimensional string

@author: felix
"""

HEIGHT = 400
WIDTH_PLOT = 600
WIDTH_TOTAL = 800


def calculate_solution(div_field, length, tension, density, first, second,
                       third):
    div_field.text = "u(t,x) ="
    if(first != 0.0):
        div_field.text += " " + str(round(first, 1)) + " \cdot \cos \left( \\frac{1}{" + str(round(length, 1)) + "} \sqrt{\\frac{" + str(round(tension, 1)) + "}{" + str(round(density, 1)) + "}} t \\right)" + " \cdot \sin \left( \\frac{1}{" + str(round(length)) + "} x \\right)"
    if(second != 0.0):
        if(first != 0.0):
            div_field.text += " +"
        div_field.text += " {0} \cos({1}t) \sin({2}x)".format(second,2.,2.)
    if(third != 0.0):
        if(first != 0.0 or second != 0.0):
            div_field.text += " +"
        div_field.text += " {0} cos({1}t) sin({2}x)".format(third,3.,3.)


def compute(t, length, tension, density, first, second, third):
    x = np.linspace(0, (length*np.pi), 100)
    # We use a tenth of the time to slow down the oscillatio, making it more pleasing
    # for the user and reducing the amount of packages needed to be sent
    value = first * np.cos(1/length * np.sqrt(tension/density) * t/10.) *\
            np.sin(1/(length) * x) +\
            second * np.cos(2/length * np.sqrt(tension/density) * t/10.) *\
            np.sin(2/length * x) +\
            third * np.cos(3/length * np.sqrt(tension/density) * t/10.) *\
            np.sin(3/length * x)
    return {"x": x, "y": value}


length = Slider(title="Länge der Saite (mal $\pi$)", value=1., start=0.5, step=0.5, end=2.)
tension = Slider(title="Vorspannung", value=1, start=0.1, step=0.1, end=2)
density = Slider(title="Liniendichte", value=1, start=0.1, step=0.1, end=2)
first = Slider(title="Erste Eigenschwingung", value=1, start=0, step=0.1, end=2)
second = Slider(title="Zweite Eigenschwingung", value=0., start=0., step=0.1, end=2.)
third = Slider(title="Dritte Eigenschwingung", value=0, start=0., step=0.1, end=2.)

source = ColumnDataSource()

plot = figure(x_range=[-1, 2*np.pi+1], y_range=[-2, 2], plot_height=HEIGHT,
              plot_width=WIDTH_PLOT, tools="")
plot.line(x="x", y="y", source=source, line_width=2)

placeholder = Div(width=WIDTH_TOTAL, height=100)

field_solution = LatexLabel(text="",
                   x=0, y=-40, x_units='screen', y_units='screen',
                   render_mode='css', text_font_size='12pt',
                   background_fill_alpha=0)

plot.add_layout(field_solution)

inputs = widgetbox(length, tension, density, first, second, third)


@count()
def update(t):
    source.data = compute(t, length.value, tension.value, density.value,
                          first.value, second.value, third.value)


def update_slider(attr, old, new):
    calculate_solution(field_solution, length.value, tension.value, density.value, first.value, second.value, third.value)


update_slider(0, 0, 0)

for slider in (length, tension, density, first, second, third):
    slider.on_change("value", update_slider)



curdoc().add_root(column(row(plot, inputs, width=WIDTH_TOTAL), placeholder, height=HEIGHT+100))  

curdoc().add_periodic_callback(update, 100)
