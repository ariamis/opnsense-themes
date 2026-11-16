# Accessibility check, 1.0.1 candidate

## Status in 1.0.1

Fixed (override block at the end of each theme's `build/css/main.css`): findings 1, 2, 3 and 5 below, plus the top-bar user/host text (finding 9). Keyboard focus now shows a 2 px outline in the theme's cyan accent for keyboard users (`:focus-visible`). Re-running the check gives 0 element types without visible focus in all four themes.

| Theme | Items below AA before | After |
|---|---|---|
| `dracula-inter` | 20 | 11 |
| `dracula-macos` | 20 | 11 |
| `nightcity` | 14 | 5 |
| `tokyonight` | 24 | 15 |

Also fixed (user-approved): findings 4, 6, 7 and 8 (breadcrumb, muted text and placeholders, active tab and list item, near misses; same hues, minimally lightened or darkened to reach 4.5:1), the dialog close button "x", the active page button in tables, and the dialog title bars, which are now a dark bar with light title text and an accent underline instead of dark text on a bright fill. Re-running the check gives 0 items below AA in all four themes. Night City was also checked live in a browser on the Aliases page with the fixes injected: 194 text items, 0 failing. The other three themes were only checked with the sample page.

Method: `scripts/a11y-browser-check.py` renders a sample page of common Bootstrap 3 and OPNsense components (`scripts/a11y-sample.html`) in Chromium with each theme's `build/css/main.css`. It measures contrast with the real CSS cascade and presses Tab to test keyboard focus. WCAG AA needs 4.5:1 for normal text and 3:1 for large text. Disabled controls are exempt and are not counted.

Limits: this is a sample page, not a live OPNsense page. OPNsense pages may override some of these rules, so confirm each finding on the firewall before changing colours.

| Theme | Text items checked | Below AA | Element types with no visible keyboard focus |
|---|---|---|---|
| `dracula-inter` | 126 | 20 | 12 |
| `dracula-macos` | 126 | 20 | 12 |
| `nightcity` | 126 | 14 | 12 |
| `tokyonight` | 126 | 24 | 12 |

## Findings, most serious first

1. **Text colour equals background colour (1.0:1).** `.panel-success > .panel-heading` and `.panel-danger > .panel-heading` (and their badges), `.list-group-item-success` and `-danger`, and `.has-success` / `.has-error .input-group-addon` all set `color` and `background-color` to the same value. Text in these elements is invisible. Present in all four themes.
2. **No visible keyboard focus.** `.btn:focus` ends with `outline:0`, which cancels the focus ring. Buttons then rely on a background change, but most coloured buttons (primary, success, info, warning, danger) already have that background, so focus changes nothing. Links have `outline:0` as well. At least one text input shows no change. Present in all four themes.
3. **Light text on accent fills (1.1:1 to 1.6:1).** `.label-primary`, `.label-warning`, `.label-danger`, the badge in a primary panel, the modal close button and the modal title sit on the orange or yellow accent with light text. Worst in `nightcity` (1.15:1 on yellow) and `tokyonight` (1.26:1 on orange).
4. **Breadcrumb.** `.breadcrumb` has a light background with light link colours (1.06:1 to 1.3:1). Check on a live page whether OPNsense overrides it.
5. **`<mark>` highlight** is 1.4:1 to 1.9:1 in all four themes.
6. **Muted palette colours (about 2.2:1 to 3.4:1)** in `dracula-inter`, `dracula-macos` and `tokyonight`: `.text-muted`, `<small>`, `.help-block`, dropdown headers and input placeholders use the palette's "comment" colour. `tokyonight` also has inactive nav links at 3.6:1. This comes from the palettes themselves, so fixing it changes the look.
7. **Active tab and active list item** use accent text on grey at 3.5:1 to 3.8:1 in `dracula-*` and `tokyonight`.
8. **Near misses (4.2:1 to 4.4:1):** `.label-default`, `.badge`, the active breadcrumb item and some placeholders.

9. **Top-bar user and host text** (`.navbar-default .navbar-text`) is dark text on a dark bar: 1.4:1 in `nightcity`, about 1.8:1 to 1.9:1 in the other three. Found on the live dashboard, not on the sample page.

## Live check (Night City 1.0 on OPNsense 26.7.9_1, dashboard page)

96 text items measured with the real cascade. Only the top-bar text failed (1.43:1). With the 1.0.1 overrides injected into the open tab (temporary, not saved on the firewall), 0 of 96 failed and the sidebar toggle showed the new cyan focus ring on Tab. Only `nightcity` was tested live, and only the dashboard page.

## Not yet checked

- Chart and gauge colours (canvas, drawn by `theme.js`)
- Hover and active states
- Mobile layout and zoom
- Live pages other than the Night City dashboard, including the login page and the other three themes

## Calm pass (1.0.1)

Bright accent and red stay for text, thin lines and small controls (buttons, tags, page numbers, ticked boxes). An extra, darker palette colour is used for wide, text-heavy or very loud areas: selected dropdown rows, panel heading bars, danger bars, Live View block rows and text selection. Night City: yellow #978d01 and red #b3002a (its own 1.0 dark red). The other themes use proportionally darker versions of their own accent and red, kept at 4.5:1 or better against their text. The display font (Orbitron) is no longer used for help text, captions or chips. Checkboxes, radio buttons and the file picker follow the theme palette. Chips coloured inline by the page get dark or light text by luminance (theme.js). Pie chart labels have an outline so they read on every slice colour.
