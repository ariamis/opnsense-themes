# Third-party notices

The four themes (`dracula-inter`, `dracula-macos`, `nightcity`, `tokyonight`) are derived from the OPNsense theme files and bundle third-party components. Each component keeps its own licence. The BSD 2-Clause licence in `LICENSE` (`LICENSE.ariamis` inside the archives) covers only the additions made by ariamis: the override CSS and `build/js/theme.js`.

Files in each theme archive:

- `LICENSE.OPNsense`: OPNsense copyright and licence (BSD 2-Clause)
- `LICENSE.ariamis`: licence of the additions
- `LICENSE.bootstrap-select`: bootstrap-select licence (MIT)
- `licenses/`: full licence texts referenced below
- `build/fonts/`: font licence texts

Many bundled CSS files are recoloured to match each theme. They are modified copies, not the unmodified upstream files.

## Bundled components

All entries were checked against the upstream licence file (links below) in November 2026. The third-party files were copied from the OPNsense 26.7.9 theme folder, so their versions are those shipped in that release. Many of these CSS files are recoloured for the themes, so they are modified copies of the originals.

| Component | Version | Files | Copyright | Licence | Licence text in archive |
|---|---|---|---|---|---|
| bootstrap-select | 1.13.3 | `build/css/bootstrap-select.css` | 2012-2018 SnapAppointments, LLC | MIT | `LICENSE.bootstrap-select`, `licenses/MIT-bootstrap-select.txt` |
| jQuery Bootgrid | 1.3.1 | `build/css/jquery.bootgrid.css` | 2014-2015 Rafael Staib | MIT | `licenses/MIT-jquery-bootgrid.txt` |
| normalize.css | 3.0.1 | compiled into `build/css/main.css` | Nicolas Gallagher and Jonathan Neal | MIT | `licenses/MIT-normalize-css.txt` |
| Bootstrap 3 and Glyphicons Halflings | 3.x, as in OPNsense 26.7.9 | compiled into `build/css/main.css`, `assets/fonts/bootstrap/*`, `build/fonts/bootstrap/*` | 2011-2019 Twitter, Inc. (from the 3.4.1 licence file) | MIT | `licenses/MIT-bootstrap.txt` |
| NVD3 | 1.8.6 | `build/css/nv.d3.css` | 2011-2014 Novus Partners, Inc. | Apache-2.0 | `licenses/NVD3-NOTICE.txt`, `licenses/Apache-2.0.txt` |
| Tabulator | as in OPNsense 26.7.9 | `build/css/tabulator.min.css` | Oli Folkerd | MIT | `licenses/MIT-tabulator.txt` |
| Pick-a-Color | 1.2.3 | `build/css/pick-a-color-1.2.3.min.css` | 2013 Lauren Sperber and Broadstreet Ads | MIT | `licenses/MIT-pick-a-color.txt` |
| Tokenize2 | as in OPNsense 26.7.9 | `build/css/tokenize2.css` | 2005-2016 DragonOfMercy | BSD 3-Clause | `licenses/BSD-3-Clause-tokenize2.txt` |
| bootstrap-dialog (bootstrap3-dialog) | as in OPNsense 26.7.9 | `build/css/bootstrap-dialog.css` | none published upstream | MIT | `licenses/MIT-bootstrap-dialog.txt` |
| OPNsense theme files | n/a | `build/css/main.css`, `dashboard.css`, `dns-overview.css`, `opnsense-bootgrid.css`, `build/images/*` | see `LICENSE.OPNsense` | BSD 2-Clause | `LICENSE.OPNsense` |
| Source Sans Pro | n/a | `assets/fonts/SourceSansPro-*`, `build/fonts/SourceSansPro-*` | 2010, 2012, 2014 Adobe Systems Incorporated | SIL OFL 1.1 | `build/fonts/LICENSE.SourceSansPro.txt` |

Upstream sources:

- bootstrap-select: https://github.com/snapappointments/bootstrap-select (licence of v1.13.3)
- jQuery Bootgrid: https://github.com/rstaib/jquery-bootgrid (copyright from the bundled file header)
- normalize.css: https://github.com/necolas/normalize.css
- Bootstrap: https://github.com/twbs/bootstrap
- NVD3: https://github.com/novus/nvd3
- Tabulator: https://github.com/olifolkerd/tabulator
- Pick-a-Color: https://github.com/lauren/pick-a-color
- Tokenize2: https://github.com/zellerda/Tokenize2
- bootstrap-dialog: https://github.com/nakupanda/bootstrap3-dialog (no LICENSE file; the MIT licence is stated in the source header and README)

`build/css/bootstrap-dialog.css` contains an icon animation marked as copied from Font Awesome (https://fontawesome.io/). Font Awesome code is MIT licensed and its fonts are SIL OFL 1.1. No Font Awesome font files are bundled.

## Fonts bundled per theme

| Theme | Fonts in `build/fonts` | Licence text |
|---|---|---|
| `dracula-inter` | Inter (300, 400, 600), Fira Code (400), Source Sans Pro, Glyphicons Halflings | `OFL-inter.txt`, `OFL-fira-code.txt`, `LICENSE.SourceSansPro.txt` |
| `dracula-macos` | Source Sans Pro, Glyphicons Halflings. No Inter, Fira Code or Apple SF Pro files. | `LICENSE.SourceSansPro.txt` |
| `nightcity` | Rajdhani (400, 500, 600, 700), Orbitron (500), Fira Code (400), Source Sans Pro, Glyphicons Halflings | `OFL-rajdhani.txt`, `OFL-orbitron.txt`, `OFL-fira-code.txt`, `LICENSE.SourceSansPro.txt` |
| `tokyonight` | Inter (400, 600), Fira Code (400), Source Sans Pro, Glyphicons Halflings | `OFL-inter.txt`, `OFL-fira-code.txt`, `LICENSE.SourceSansPro.txt` |

The system font stack of `dracula-macos` names SF Pro, but no Apple font file is distributed. SF Pro is only used where the user's operating system provides it.

## Colour palettes

Only colour values are used. No files from these projects are bundled. The licence texts are included for attribution.

- Dracula: https://draculatheme.com, https://github.com/dracula/dracula-theme (MIT, 2023 Dracula Theme): `licenses/MIT-dracula-palette.txt`
- Tokyo Night by enkia: https://github.com/tokyo-night/tokyo-night-vscode-theme (MIT, 2018-present Enkia): `licenses/MIT-tokyo-night-palette.txt`
- Night City: independently chosen colours inspired by the Cyberpunk 2077 interface. No game assets are included. The project is unofficial and not affiliated with or endorsed by CD PROJEKT RED.
