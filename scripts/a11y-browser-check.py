#!/usr/bin/env python3
"""Browser-based contrast and focus check for the four themes.

Usage: python3 -I scripts/a11y-browser-check.py [theme ...]   (default: all four)
Needs: python3 playwright with Chromium (development only, not part of the release).

Renders scripts/a11y-sample.html (common Bootstrap 3 / OPNsense components) with
each theme's build/css/main.css and measures, using the real cascade:
  * text contrast: WCAG ratio against the effective background (4.5:1 for normal
    text, 3:1 for large text)
  * placeholder contrast
  * focus indicators: whether keyboard focus changes outline, shadow, border or
    background of focusable elements

Limits: this is a sample page, not a live OPNsense page. Elements with a
background image or gradient are reported as "needs manual check".
"""
import json
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
THEMES = ["dracula-inter", "dracula-macos", "nightcity", "tokyonight"]

JS = r"""
() => {
  const parse = s => { const m = s.match(/rgba?\(([^)]+)\)/); if (!m) return null;
    const p = m[1].split(/[ ,\/]+/).filter(Boolean).map(Number); return {r:p[0],g:p[1],b:p[2],a:p.length>3?p[3]:1}; };
  const over = (top, bot) => { const a = top.a + bot.a*(1-top.a); if (a === 0) return {r:0,g:0,b:0,a:0};
    return {r:(top.r*top.a+bot.r*bot.a*(1-top.a))/a, g:(top.g*top.a+bot.g*bot.a*(1-top.a))/a, b:(top.b*top.a+bot.b*bot.a*(1-top.a))/a, a}; };
  const lin = x => { x/=255; return x<=0.03928 ? x/12.92 : Math.pow((x+0.055)/1.055,2.4); };
  const L = c => 0.2126*lin(c.r)+0.7152*lin(c.g)+0.0722*lin(c.b);
  const ratio = (a,b) => { const x=L(a), y=L(b); return (Math.max(x,y)+0.05)/(Math.min(x,y)+0.05); };
  const hex = c => '#'+[c.r,c.g,c.b].map(v=>Math.round(v).toString(16).padStart(2,'0')).join('');
  const bgOf = el => { let layers=[], image=false;
    for (let e=el; e; e=e.parentElement) { const cs=getComputedStyle(e);
      if (cs.backgroundImage && cs.backgroundImage!=='none') image=true;
      const c=parse(cs.backgroundColor); if (c && c.a>0) { layers.push(c); if (c.a>=1) break; } }
    let acc = {r:255,g:255,b:255,a:1};   // browser default canvas
    const htmlBg = parse(getComputedStyle(document.documentElement).backgroundColor);
    if (htmlBg && htmlBg.a>0) acc = over(htmlBg, acc);
    for (let i=layers.length-1;i>=0;i--) acc = over(layers[i], acc);
    return {c:acc, image}; };
  const label = el => el.tagName.toLowerCase() + (el.className && typeof el.className==='string' ? '.'+el.className.trim().split(/\s+/).join('.') : '');
  const out = [];
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  const seen = new Set();
  while (walker.nextNode()) {
    const n = walker.currentNode; if (!n.textContent.trim()) continue;
    const el = n.parentElement; if (!el || seen.has(el)) continue; seen.add(el);
    const cs = getComputedStyle(el); if (cs.visibility==='hidden' || cs.display==='none') continue;
    if (el.closest(':disabled, .disabled, [disabled]')) continue;   // disabled controls are exempt
    const fg = parse(cs.color); if (!fg) continue;
    const {c:bg, image} = bgOf(el);
    const fgc = over({...fg, a: fg.a*parseFloat(cs.opacity||1)}, bg);
    const size = parseFloat(cs.fontSize), bold = parseInt(cs.fontWeight)>=700;
    const large = size>=24 || (size>=18.66 && bold);
    out.push({kind:'text', el:label(el), text:n.textContent.trim().slice(0,30), fg:hex(fgc), bg:hex(bg), ratio:ratio(fgc,bg), need: large?3:4.5, image});
  }
  document.querySelectorAll('input[placeholder]').forEach(el => {
    const ph = parse(getComputedStyle(el,'::placeholder').color); const {c:bg,image}=bgOf(el); if (!ph) return;
    const fgc = over({...ph, a: ph.a}, bg);
    out.push({kind:'placeholder', el:label(el), text:el.placeholder, fg:hex(fgc), bg:hex(bg), ratio:ratio(fgc,bg), need:4.5, image});
  });
  return out;
}
"""

FOCUS_JS = r"""
(el) => { const cs = getComputedStyle(el);
  return {outline: cs.outlineStyle+' '+cs.outlineWidth+' '+cs.outlineColor, shadow: cs.boxShadow,
          border: cs.borderTopColor+' '+cs.borderLeftColor, bg: cs.backgroundColor, color: cs.color, deco: cs.textDecorationLine}; }
"""


def outline_visible(o):
    st, w, *rest = o.split(" ", 2)
    return st not in ("none", "hidden") and not w.startswith("0")


def check(page, theme):
    css = (ROOT / "themes" / theme / "build/css/main.css").read_text()
    html = (ROOT / "scripts/a11y-sample.html").read_text()
    page.set_viewport_size({"width": 1280, "height": 900})
    page.set_content(html)
    page.add_style_tag(content=css)
    items = page.evaluate(JS)
    fails = [i for i in items if i["ratio"] < i["need"]]
    # collapse duplicates
    uniq = {}
    for f in fails:
        k = (f["el"], f["fg"], f["bg"])
        uniq.setdefault(k, f)
    fails = sorted(uniq.values(), key=lambda f: f["ratio"])

    return items, fails


def focus_check(page):
    """Tab through the page with the keyboard and report elements whose style
    does not change when focused (no visible focus indicator)."""
    sels = "a[href], button:not(:disabled), input:not([type=hidden]):not(:disabled), select:not(:disabled), textarea:not(:disabled)"
    handles = [h for h in page.query_selector_all(sels) if h.is_visible()]
    for i, h in enumerate(handles):
        h.evaluate("(e, i) => e.setAttribute('data-a11y-i', i)", i)
    before = {i: h.evaluate(FOCUS_JS) for i, h in enumerate(handles)}
    page.evaluate("() => { document.activeElement && document.activeElement.blur(); window.scrollTo(0,0); }")
    page.mouse.move(0, 0)
    missing, seen = [], set()
    for _ in range(len(handles) + 5):
        page.keyboard.press("Tab")
        idx = page.evaluate("() => { const e = document.activeElement; return e && e.hasAttribute('data-a11y-i') ? +e.getAttribute('data-a11y-i') : -1; }")
        if idx < 0 or idx in seen:
            continue
        seen.add(idx)
        h = handles[idx]
        after = h.evaluate(FOCUS_JS)
        b4 = before[idx]
        changed = (outline_visible(after["outline"]) or after["shadow"] != b4["shadow"]
                   or after["border"] != b4["border"] or after["bg"] != b4["bg"]
                   or after["color"] != b4["color"] or after["deco"] != b4["deco"])
        if not changed:
            missing.append(h.evaluate("e => e.tagName.toLowerCase() + (e.className ? '.' + e.className.trim().split(/\\s+/).join('.') : '')"))
    return missing, len(seen), len(handles)


def main():
    themes = sys.argv[1:] or THEMES
    report = {}
    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page()
        for t in themes:
            items, fails = check(page, t)
            missing, tabbed, total = focus_check(page)
            report[t] = {
                "checked": len(items),
                "fail": [{k: (round(v, 2) if isinstance(v, float) else v) for k, v in f.items()} for f in fails],
                "no_focus_indicator": sorted(set(missing)),
            }
            print("=" * 72)
            print(f"{t}: {len(items)} text items checked, {len(fails)} below WCAG AA")
            for f in fails:
                flag = "  [background image: check manually]" if f["image"] else ""
                print(f"  {f['ratio']:4.2f} (need {f['need']})  {f['fg']} on {f['bg']}  {f['el'][:48]}  \"{f['text']}\"{flag}")
            print(f"  keyboard focus reached {tabbed} of {total} focusable elements; {len(set(missing))} element types show no visible focus change:")
            for m in sorted(set(missing)):
                print(f"    {m}")
        b.close()
    (ROOT / "dist").mkdir(exist_ok=True)
    (ROOT / "dist" / "a11y-report.json").write_text(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
