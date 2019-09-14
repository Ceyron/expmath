import {LayoutDOM, LayoutDOMView} from "models/layouts/layout_dom"
import {ColumnDataSource} from "models/sources/column_data_source"
import {LayoutItem} from "core/layout"
import * as p from "core/properties"

declare namespace vis {
  class Graph3d {
    constructor(el: HTMLElement, data: object, OPTIONS: object)
    setData(data: vis.DataSet): void
  }

  class DataSet {
    add(data: unknown): void
  }
}

// This defines some default options for the Graph3d feature of vis.js
// See: http://visjs.org/graph3d_examples.html for more details.
const OPTIONS = {
  width: '%dpx',
  height: '%dpx',
  style: 'line',
  showPerspective: true,
  showGrid: true,
  keepAspectRatio: true,
  verticalRatio: 1.0,
  legendLabel: 'stuff',
  cameraPosition: {
    horizontal: 1,
    vertical: 0.5,
    distance: 1.7,
  },
  dataColor: {
    strokeWidth: %d,
  },
  xMin: %d,
  xMax: %d,
  yMin: %d,
  yMax: %d,
  zMin: %d,
  zMax: %d,
}
// To create custom model extensions that will render on to the HTML canvas
// or into the DOM, we must create a View subclass for the model.
//
// In this case we will subclass from the existing BokehJS ``LayoutDOMView``
export class Vector3dView extends LayoutDOMView {
  model: Vector3d

  private _graph: vis.Graph3d

  initialize(): void {
    super.initialize()

    const url = "https://cdnjs.cloudflare.com/ajax/libs/vis/4.16.1/vis.min.js"
    const script = document.createElement("script")
    script.onload = () => this._init()
    script.async = false
    script.src = url
    document.head.appendChild(script)
  }

  private _init(): void {
    // BokehJS Views create <div> elements by default, accessible as this.el.
    // Many Bokeh views ignore this default <div>, and instead do things like
    // draw to the HTML canvas. In this case though, we use the <div> to attach
    // a Graph3d to the DOM.
    this._graph = new vis.Graph3d(this.el, this.get_data(), OPTIONS)

    // Set a listener so that when the Bokeh data source has a change
    // event, we can process the new data
    this.connect(this.model.data_source.change, () => {
      this._graph.setData(this.get_data())
    })
  }

  // This is the callback executed when the Bokeh data changed. Its basic
  // function is to adapt the Bokeh data source to the vis.js DataSet format.
  get_data(): vis.DataSet {
    const data = new vis.DataSet()
    const source = this.model.data_source
    for (let i = 0; i < source.get_length()!; i++) {
      // Adding zero is important to that the line always comes back to the
      // origin
      data.add({
        x: 0,
        y: 0,
        z: 0,
      })
      data.add({
        x: source.data[this.model.x][i],
        y: source.data[this.model.y][i],
        z: source.data[this.model.z][i],
        style: 5,
      })
     
      data.add({
        x: 0,
        y: 0,
        z: 0,
      })
      data.add({
        x: source.data[this.model.u][i],
        y: source.data[this.model.v][i],
        z: source.data[this.model.w][i],
      })
      
      }
    return data
  }

  get child_models(): LayoutDOM[] {
    return []
  }

  _update_layout(): void {
    this.layout = new LayoutItem()
    this.layout.set_sizing(this.box_sizing())
  }
}

// We must also create a corresponding JavaScript BokehJS model subclass to
// correspond to the python Bokeh model subclass. In this case, since we want
// an element that can position itself in the DOM according to a Bokeh layout,
// we subclass from ``LayoutDOM``
export namespace Vector3d {
  export type Attrs = p.AttrsOf<Props>

  export type Props = LayoutDOM.Props & {
    x: p.Property<string>
    y: p.Property<string>
    z: p.Property<string>
    
    u: p.Property<string>
    v: p.Property<string>
    w: p.Property<string>
   
    data_source: p.Property<ColumnDataSource>
  }
}

export interface Vector3d extends Vector3d.Attrs {}

export class Vector3d extends LayoutDOM {
  properties: Vector3d.Props

  constructor(attrs?: Partial<Vector3d.Attrs>) {
    super(attrs)
  }

  static initClass() {
    // The ``type`` class attribute should generally match exactly the name
    // of the corresponding Python class.
    this.prototype.type = "Vector3d"

    // This is usually boilerplate. In some cases there may not be a view.
    this.prototype.default_view = Vector3dView

    // The @define block adds corresponding "properties" to the JS model. These
    // should basically line up 1-1 with the Python model class. Most property
    // types have counterparts, e.g. ``bokeh.core.properties.String`` will be
    // ``p.String`` in the JS implementatin. Where the JS type system is not yet
    // as rich, you can use ``p.Any`` as a "wildcard" property type.
    this.define<Vector3d.Props>({
      x:            [ p.String   ],
      y:            [ p.String   ],
      z:            [ p.String   ],
      
      u:            [ p.String   ],
      v:            [ p.String   ],
      w:            [ p.String   ],
      
      data_source:  [ p.Instance ],
    })
  }
}
Vector3d.initClass()
