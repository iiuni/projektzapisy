// BokehJS 3 ships a prebuilt bundle; its package entry point is the unbundled
// source, which resolves its own modules by bare specifiers that Webpack
// cannot follow.
import * as Bokeh from "@bokeh/bokehjs/build/js/bokeh.esm.min.js";

window.Bokeh = Bokeh;
