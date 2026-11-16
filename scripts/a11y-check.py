#!/usr/bin/env python3
"""Static contrast and focus check for the theme CSS.

Usage: python3 -I scripts/a11y-check.py [theme ...]     (default: all four)

For every rule in themes/<name>/build/css/main.css that sets both a text
colour and a background colour it computes the WCAG contrast ratio. Rules that
set only a text colour are checked against the page background (body).
Rules that only set a background are ignored. Colours with alpha or
non-hex/rgb values are skipped. This is a static estimate: it cannot know
which element really sits on which background, so treat results as leads to
check in a browser, not as final verdicts.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
THEMES = ["dracula-inter", "dracula-macos", "nightcity", "tokyonight"]
HEX = re.compile(r"#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})\b")
RGB = re.compile(r"rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)")


def parse_color(v):
    v = v.replace("!important", "").strip()
    m = HEX.search(v)
    if m and "gradient" not in v:
        h = m.group(1)
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    m = RGB.search(v)
    if m and "gradient" not in v:
        return tuple(int(x) for x in m.groups())
    return None


def lum(c):
    def f(x):
        x /= 255
        return x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4
    r, g, b = (f(x) for x in c)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def rules(css):
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    for m in re.finditer(r"([^{}@][^{}]*)\{([^{}]*)\}", css):
        sel = " ".join(m.group(1).split())
        decl = {}
        for d in m.group(2).split(";"):
            if ":" in d:
                k, v = d.split(":", 1)
                decl[k.strip().lower()] = v.strip()
        yield sel, decl


def bg_of(decl):
    for k in ("background-color", "background"):
        if k in decl:
            c = parse_color(decl[k])
            if c:
                return c
    return None


def hex_(c):
    return "#%02x%02x%02x" % c


def check(theme):
    css = (ROOT / "themes" / theme / "build/css/main.css").read_text()
    page_bg = None
    allr = list(rules(css))
    for sel, d in allr:
        if re.search(r"(^|,\s*)body\s*$", sel) and bg_of(d):
            page_bg = bg_of(d)
    out, seen = [], set()
    for sel, d in allr:
        fg = parse_color(d["color"]) if "color" in d else None
        if not fg:
            continue
        bg = bg_of(d)
        basis = "own background"
        if not bg:
            if not page_bg:
                continue
            bg, basis = page_bg, "page background"
        r = ratio(fg, bg)
        key = (hex_(fg), hex_(bg), sel)
        if r < 4.5 and key not in seen:
            seen.add(key)
            out.append((r, sel, hex_(fg), hex_(bg), basis))
    out.sort()
    # focus: rules that remove the outline without a replacement style
    nofocus = []
    for sel, d in allr:
        if ":focus" in sel and d.get("outline", "").startswith(("none", "0")) \
                and not any(k in d for k in ("box-shadow", "border-color", "background-color")):
            nofocus.append(sel)
    return page_bg, out, nofocus


def main():
    themes = sys.argv[1:] or THEMES
    for t in themes:
        page_bg, low, nofocus = check(t)
        print("=" * 70)
        print(f"{t}: page background {hex_(page_bg) if page_bg else 'not found'}")
        print(f"  rules below 4.5:1 (small text): {len(low)}")
        for r, sel, fg, bg, basis in low[:25]:
            print(f"   {r:4.2f}  {fg} on {bg} ({basis})  {sel[:90]}")
        print(f"  :focus rules that remove the outline with no replacement: {len(nofocus)}")
        for s in nofocus[:10]:
            print(f"   {s[:100]}")


if __name__ == "__main__":
    main()
