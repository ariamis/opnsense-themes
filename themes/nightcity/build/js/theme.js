/* Night City theme OPNsense */
(function () {
  var OUT = ["#ffee08", "#b8a800", "#1ded83", "#00ffff", "#00a8a8", "#ff003c", "#b3002a", "#8c7a7f", "#3a2a2e", "#0e0e0e", "#161214", "#1f1a1c", "#fafafa"];
  var KEYS = ["backgroundColor", "borderColor", "pointBackgroundColor", "pointBorderColor", "hoverBackgroundColor", "hoverBorderColor"];
  var cx = document.createElement("canvas").getContext("2d");

  function hex(r, g, b) {
    return "#" + [r, g, b].map(function (v) { return ("0" + v.toString(16)).slice(-2); }).join("");
  }

  function parse(c) {
    cx.fillStyle = "#010203";
    cx.fillStyle = c;
    var s = cx.fillStyle;
    if (s === "#010203" && String(c).replace(/\s/g, "").toLowerCase() !== "#010203") return null;
    if (s.charAt(0) === "#") return [parseInt(s.substr(1, 2), 16), parseInt(s.substr(3, 2), 16), parseInt(s.substr(5, 2), 16), 1];
    var m = s.match(/[\d.]+/g);
    return [+m[0], +m[1], +m[2], m.length > 3 ? +m[3] : 1];
  }

  function pick(r, g, b) {
    var R = r / 255, G = g / 255, B = b / 255;
    var mx = Math.max(R, G, B), mn = Math.min(R, G, B), l = (mx + mn) / 2, d = mx - mn;
    var s = d === 0 ? 0 : d / (1 - Math.abs(2 * l - 1));
    if (s < 0.12) return l > 0.5 ? "#3a2a2e" : "#8c7a7f";
    if (s < 0.4 && l < 0.5) return "#8c7a7f";
    var h = mx === R ? ((G - B) / d + 6) % 6 : mx === G ? (B - R) / d + 2 : (R - G) / d + 4;
    h *= 60;
    if (h >= 345 || h < 15) return "#ff003c";
    if (h < 45) return "#ffee08";
    if (h < 70) return "#b8a800";
    if (h < 170) return "#1ded83";
    if (h < 270) return "#00ffff";
    if (h < 300) return "#b3002a";
    return "#00a8a8";
  }

  function map(c) {
    if (typeof c !== "string") return c;
    var p = parse(c);
    if (!p || OUT.indexOf(hex(p[0], p[1], p[2])) >= 0) return c;
    var o = pick(p[0], p[1], p[2]);
    if (p[3] >= 1) return o;
    return "rgba(" + parseInt(o.substr(1, 2), 16) + "," + parseInt(o.substr(3, 2), 16) + "," + parseInt(o.substr(5, 2), 16) + "," + p[3] + ")";
  }

  function guard(arr) {
    return new Proxy(arr, {
      set: function (t, k, v) {
        t[k] = (typeof k === "string" && /^\d+$/.test(k)) ? map(v) : v;
        return true;
      }
    });
  }

  function fix(v) {
    if (Array.isArray(v)) return guard(v.map(map));
    if (typeof v === "function") return function () { var r = v.apply(this, arguments); return Array.isArray(r) ? r.map(map) : map(r); };
    return map(v);
  }

  function wrap(ds) {
    KEYS.forEach(function (k) {
      var d = Object.getOwnPropertyDescriptor(ds, k);
      if (d && d.get) return;
      var val = fix(ds[k]);
      try {
        Object.defineProperty(ds, k, { configurable: true, enumerable: true, get: function () { return val; }, set: function (v) { val = fix(v); } });
      } catch (e) {
        ds[k] = val;
      }
    });
  }

  var plugin = {
    id: "nightcity-recolor",
    beforeUpdate: function (chart) {
      var round = chart.config.type === "doughnut" || chart.config.type === "pie";
      (chart.data.datasets || []).forEach(function (ds) {
        wrap(ds);
        if (round && ds.borderColor == null) ds.borderColor = "#161214";
      });
    }
  };

  function setupChart(C) {
    if (!C || C.__nightcity) return;
    C.__nightcity = true;
    try {
      C.register(plugin);
      C.defaults.color = "#fafafa";
      C.defaults.borderColor = "rgba(250,250,250,0.12)";
      C.defaults.font.family = "Rajdhani, system-ui, sans-serif";
    } catch (e) {}
  }

  function setupSmoothie(S) {
    if (!S || !S.prototype || S.__nightcity) return;
    S.__nightcity = true;
    var add = S.prototype.addTimeSeries;
    S.prototype.addTimeSeries = function (ts, opts) {
      if (opts) ["strokeStyle", "fillStyle"].forEach(function (k) { if (typeof opts[k] === "string") opts[k] = map(opts[k]); });
      return add.call(this, ts, opts);
    };
  }

  function trap(name, fn) {
    if (window[name]) { fn(window[name]); return; }
    var holder;
    try {
      Object.defineProperty(window, name, {
        configurable: true,
        get: function () { return holder; },
        set: function (v) { holder = v; fn(v); }
      });
    } catch (e) {
      var t = setInterval(function () { if (window[name]) { clearInterval(t); fn(window[name]); } }, 50);
    }
  }

  // Only the Memory and Disk gauge canvases ("memory-chart", "disk-chart") are
  // changed: their detail line (e.g. "1362 / 32486 MB") is squeezed to fit the
  // gauge. Every other canvas goes straight to the original fillText. The wrapper
  // is installed once, and skipped if the canvas API is missing.
  var ctxProto = window.CanvasRenderingContext2D && window.CanvasRenderingContext2D.prototype;
  if (ctxProto && !ctxProto.__themeFillText) {
  var fillText = ctxProto.fillText;
  ctxProto.__themeFillText = true;
  ctxProto.fillText = function (t, x, y, w) {
    var c = this.canvas, id = c && c.id;
    if (w === undefined && (id === "memory-chart" || id === "disk-chart") && String(t).indexOf("/") >= 0 && window.Chart && window.Chart.getChart) {
      try {
        var a = window.Chart.getChart(c).getDatasetMeta(0).data[0];
        var m = /([0-9.]+)px/.exec(this.font);
        var dy = Math.abs(y - a.y) + (m ? +m[1] : 0);
        var room = Math.sqrt(Math.max(a.innerRadius * a.innerRadius - dy * dy, 0)) * 1.84;
        if (room > 0) { var ow = this.measureText(t).width, al = this.textAlign; if (ow > room) { w = room; if (al !== "center") x += (al === "right" || al === "end" ? -1 : 1) * (ow - room) / 2; } }
      } catch (e) {}
    }
    return w === undefined ? fillText.call(this, t, x, y) : fillText.call(this, t, x, y, w);
  };
  }

  trap("Chart", setupChart);
  trap("SmoothieChart", setupSmoothie);
})();

/* 1.0.1: pick dark or light text for chips whose background colour is set inline by the page */
(function () {
  var DARK = "#0e0e0e", LIGHT = "#fafafa";
  function lum(r, g, b) {
    var c = [r, g, b].map(function (x) { x /= 255; return x <= 0.03928 ? x / 12.92 : Math.pow((x + 0.055) / 1.055, 2.4); });
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2];
  }
  function hexLum(h) { return lum(parseInt(h.substr(1, 2), 16), parseInt(h.substr(3, 2), 16), parseInt(h.substr(5, 2), 16)); }
  var dl = hexLum(DARK), ll = hexLum(LIGHT), queued = false;
  function fix() {
    queued = false;
    var list = document.querySelectorAll('.badge[style*="background"], .label[style*="background"]');
    for (var i = 0; i < list.length; i++) {
      var m = getComputedStyle(list[i]).backgroundColor.match(/[\d.]+/g);
      if (!m || m.length < 3 || (m.length > 3 && parseFloat(m[3]) < 0.5)) continue;
      var l = lum(+m[0], +m[1], +m[2]);
      var useDark = (l + 0.05) / (dl + 0.05) >= (ll + 0.05) / (l + 0.05);
      list[i].style.setProperty("color", useDark ? DARK : LIGHT, "important");
    }
  }
  function queue() { if (!queued) { queued = true; (window.requestAnimationFrame || setTimeout)(fix); } }
  if (document.readyState !== "loading") queue(); else document.addEventListener("DOMContentLoaded", queue);
  if (window.MutationObserver) new MutationObserver(queue).observe(document.documentElement, { childList: true, subtree: true });
})();

/* 1.0.1: dark text for the temperature labels drawn inside the bright bars of the Thermal Sensors widget */
(function () {
  var proto = window.CanvasRenderingContext2D && window.CanvasRenderingContext2D.prototype;
  if (!proto || proto.__themeThermal) return;
  proto.__themeThermal = true;
  var prev = proto.fillText;
  proto.fillText = function (t) {
    if (this.canvas && this.canvas.id === "thermalsensors-chart" && /\u00b0\s*C/.test(String(t))) {
      var old = this.fillStyle;
      this.fillStyle = "#0e0e0e";
      var r = prev.apply(this, arguments);
      this.fillStyle = old;
      return r;
    }
    return prev.apply(this, arguments);
  };
})();

/* 1.0.1: theme palette for the pie and doughnut charts (Firewall > Log Files > Overview). Colours are set per slice and per legend dot, in order. */
(function () {
  var PAL = ['#ffee08', '#00ffff', '#ff003c', '#1ded83', '#978d01', '#b3002a', '#867e0b', '#078686', '#860725', '#167e48', '#524e08', '#60071c'].map(function (c) { return c; }), EDGE = "#0e0e0e", queued = false;
  function setp(el, prop, val) {
    if (el.style.getPropertyValue(prop) === val && el.style.getPropertyPriority(prop) === "important") return;
    el.style.setProperty(prop, val, "important");
  }
  function paint() {
    queued = false;
    var svgs = document.querySelectorAll("svg");
    for (var s = 0; s < svgs.length; s++) {
      var slices = svgs[s].querySelectorAll(".nv-pie .nv-slice");
      if (!slices.length) continue;
      for (var i = 0; i < slices.length; i++) {
        var col = PAL[i % PAL.length], path = slices[i].querySelector("path");
        if (path) { setp(path, "fill", col); setp(path, "stroke", EDGE); }
      }
      var dots = svgs[s].querySelectorAll(".nv-legend .nv-series .nv-legend-symbol");
      for (var k = 0; k < dots.length; k++) {
        var c2 = PAL[k % PAL.length];
        setp(dots[k], "fill", c2); setp(dots[k], "stroke", c2);
      }
    }
  }
  function queue() { if (!queued) { queued = true; (window.requestAnimationFrame || setTimeout)(paint); } }
  if (document.readyState !== "loading") queue(); else document.addEventListener("DOMContentLoaded", queue);
  if (window.MutationObserver) new MutationObserver(queue).observe(document.documentElement, { childList: true, subtree: true, attributes: true, attributeFilter: ["style", "d"] });
})();
