# Panel brand guide

How MCP App panels built in `panels/` carry the Accelerated Innovation brand. Source: the
*Accelerated Innovation Brand Book*, V01 (©2023), applied to an interactive view rendered inside
someone else's chat. Every panel PR is reviewed against the checklist at the end.

**The rule:** a panel looks like it belongs to the host, light or dark, and is recognisably ours
through **accent colour and one small mark**. It never imposes a full brand canvas (gradient
backgrounds, brand-coloured surfaces, custom fonts) on the host's chat. Decided in
discovery-engine feature 27 (nfrs D9–D11); the brand book supports it ("use the most legible
version … for the available background", p. 12; system fonts when custom fonts are not
realistic, p. 24).

## Hard constraints from the engine (not brand choices)

These come from the release contract in discovery-engine's
`docs/backend/api-contract/ui_handoff.md`, "MCP App panels". A panel that breaks one is not
bound by the engine.

- **No external requests:** no web fonts, CDN scripts, remote images or `fetch` to anything but
  the host bridge. This is the engine's rule.
- **One self-contained HTML file, at most 1,048,576 bytes, valid UTF-8**, with every script and
  style inline. This is also the engine's rule: it serves one pinned file and nothing beside it
  (`MAX_BUNDLE_BYTES` in discovery-engine's `composition.py`).
- **The CSP the host applies.** The resource declares no CSP origins, so hosts apply the MCP Apps
  default policy (spec 2026-01-26). That allows scripts and styles from `self` and inline, images
  from `self` and `data:`, no connections (`connect-src 'none'`), and no fonts (`font-src` is
  absent, so `default-src 'none'` applies). The inline-only rule comes from the engine, not from
  this policy.
- Names no engine tool other than the ones the panel may call. For the opportunities panel those
  are `list_opportunities`, `get_problem`, `list_evidence` and `find_similar_problems`
  (`get_evidence_text` is allowed by the engine but not yet used by the panel).
- **No `<form>` submission.** Hosts sandbox the iframe with `allow-scripts` only, so a submit
  event never fires; wire buttons and Enter keys instead.

## Colour

Brand palette (brand book pp. 20–22). Use **hex values**; see "Source notes" for two entries
whose RGB and hex disagree.

| Role | Name | Hex |
|---|---|---|
| Primary | Dark purple | `#19004f` |
| Primary | Purple | `#5865e7` |
| Primary | Light blue | `#0abeef` |
| Primary | Magenta | `#821db0` |
| Secondary | Blue | `#1a4b84` |
| Secondary | Red | `#af1e44` |
| Secondary | Green | `#6fa113` |
| Secondary | Yellow | `#d1b70d` |
| Neutral | Accelerated Innovation White | `#f2f2f2` |
| Neutral | 90% Black | `#1a1a1a` |

### Surfaces belong to the host

- Use the host's theme. The MCP Apps host context carries `theme` (`light` or `dark`) and
  CSS variables in `styles.variables` (MCP Apps spec 2026-01-26, "Theming"):
  `--color-background-primary`, `--color-text-primary`, `--color-border-primary`,
  `--color-ring-primary`, `--font-sans` and their siblings. Read them at `ui/initialize`, and
  again on `ui/notifications/host-context-changed`.
- `ui/notifications/host-context-changed` carries a **partial** context, for example a theme
  change without `styles.variables`. **Merge each update into the panel's current host context**;
  never replace it, or a theme-only update discards the surface and font variables.
- Hosts may omit any variable. Fall back to the brand neutrals: `#f2f2f2` or white in light
  mode, `#1a1a1a` in dark. Never true black, and never true white for large dark-mode surfaces
  (p. 22).
- No brand-coloured backgrounds and no gradient backgrounds behind content.

### Accents change with the theme

WCAG 2.1 contrast, measured against the surfaces a panel actually sits on. AA needs **4.5:1 for
text**, and **3:1 for large text (≥ 24 px, or ≥ 18.7 px bold) and for UI parts** such as focus
rings, borders and icons.

| Colour | on `#ffffff` | on `#f2f2f2` | on `#1a1a1a` | Use |
|---|---|---|---|---|
| Dark purple `#19004f` | 18.19 | 16.25 | 1.05 | **Light:** headings, emphasis text. **Dark:** never |
| Purple `#5865e7` | 4.74 | 4.23 | 3.67 | **Light:** links and accent text on white only; UI parts on any light surface. **Dark:** UI parts and large text only |
| Light blue `#0abeef` | 2.18 | 1.95 | 7.98 | **Light:** decoration only, never text or a sole indicator. **Dark:** the accent for links and text |
| Magenta `#821db0` | 7.63 | 6.82 | 2.28 | **Light:** secondary accent text. **Dark:** decoration only |

So the panel's accent is **purple in light mode and light blue in dark mode**, with dark purple
for light-mode headings. Define them once as CSS custom properties per theme; never hard-code
a brand colour in a component.

**Check against the surface actually resolved, not the theme name.** The table assumes the
fallback surfaces, but a host's `--color-background-primary` may be another shade. Each time the
host context changes, the panel computes the contrast of each accent against the resolved
background, using a small luminance function in `model.mjs` with its own unit tests. If an accent
falls below its threshold (4.5:1 for text, 3:1 for UI parts), that use falls back to the host's
own `--color-text-primary` or `--color-ring-primary`. The brand colour then stays decorative
only.

### Status colours

**Status never relies on colour alone**: pair it with a word or an icon. A status **marker**
(dot, bar, icon) is a UI part and must still meet **3:1** against its surface.

1. **Prefer the host's semantic status colours:** `--color-text-danger`, `--color-text-success`,
   `--color-text-warning`, `--color-text-info`, and their `--color-background-*` and
   `--color-border-*` siblings. They are tuned to the host's surfaces.
2. **Fall back to the brand secondaries** (p. 21, "to highlight and add details") only where they
   pass on the resolved surface:

| Marker | on `#ffffff` | on `#f2f2f2` | on `#1a1a1a` |
|---|---|---|---|
| Red `#af1e44` | 6.79 ✓ | 6.07 ✓ | 2.56 ✗ |
| Blue `#1a4b84` | 8.81 ✓ | 7.87 ✓ | 1.98 ✗ |
| Green `#6fa113` | 3.10 ✓ | 2.77 ✗ | 5.62 ✓ |
| Yellow `#d1b70d` | 2.00 ✗ | 1.79 ✗ | 8.69 ✓ |

A colour marked ✗ on a surface is **decorative only** there: never a marker, never text. The
runtime check above applies to markers too. As text (4.5:1), only red and blue on light surfaces,
and yellow and green on dark, are usable.

### Gradient

The brand's linear gradient (`#0abeef` → `#5865e7` → `#19004f`, 35°, p. 32) may appear only as
a **thin decorative rule** (≤ 4 px), for example under the panel header. Never behind text:
contrast varies across it.

## Type

- **Font: the host's, by necessity.** The brand book asks for Poppins (p. 24), but a panel
  cannot load it:
  - a web font is an external request, which the engine contract forbids;
  - the spec's default sandbox policy has no `font-src`, so it falls back to
    `default-src 'none'` and blocks even an inlined `data:` font.

  The brand book's own exception covers this: system sans-serif when custom fonts are not
  realistic. Set `font-family: var(--font-sans, system-ui, sans-serif)`.
- **Hierarchy through weight and size** (pp. 25–26): up to four weights (300, 400, 500, 700).
  When pairing, skip a weight and roughly double the size. Avoid weights the host font lacks.
- **Left-aligned, ragged right.** No centred or justified multi-line text (p. 27, "no
  exceptions"). Single-line numbers in table cells may be right-aligned for comparison.
- **Line length 45–70 characters** for prose (p. 26). Tables and lists are exempt.
- No stroke, outline or drop shadow on text. Text runs at 0°, or 90° reading up (p. 27).
- Never stretch or squash type; use a weight instead.

## The mark

- **One mark per panel, and small.** Use the **wordmark lockup**, which the brand book designs
  for small spaces (p. 14). Minimum height **25 px** (see "Source notes"). Place it in the header
  or footer, not over content.
- Use the **icon-only lockup** only where the brand name is visible beside it (p. 13), at a
  minimum of **50 px** high.
- Colour variant by theme (p. 12): **full colour on light** surfaces; **white / AI White
  (`#f2f2f2`) one-colour on dark** surfaces.
- Clear space: at least 1½ × the height of the "i" tittle on every side (p. 16).
- **Inline the official SVG artwork, unaltered:** no redrawing, recolouring, stretching,
  effects or drop shadows (pp. 10, 18). The logo is "locked artwork". The SVG comes from the
  brand owner's source files, not traced from the PDF (see "Open items").
- Never place the mark on a busy or high-contrast background (p. 18).

## Icons

Thin outlines and geometric shapes (p. 30). Keep them simple, never partially cut off, and never
used as or inside the logo. Inline them as SVG; no icon fonts. An icon that conveys state needs a
text label or an accessible name.

## Layout

- Generous negative space; group related elements tightly and separate groups (p. 26).
- Brand "shapes" (crops of the logo icon used as decoration, p. 31) are not used in panels: they
  compete with the data.
- Imagery (p. 29): none. A panel shows data, not photography.

## Source notes (discrepancies in the brand book, V01)

1. **Secondary Blue:** hex `#1a4b84` vs RGB 30, 64, 175 (`#1e40af`). This guide uses the hex.
2. **Secondary Yellow:** hex `#d1b70d` vs RGB 209, 193, 13 (`#d1c10d`). This guide uses the hex.
3. **Wordmark minimum:** 18 px (p. 14) vs 25 px (pp. 14 caption and 15). This guide uses 25 px.
4. Page 5 ("Our Story") is placeholder text, and the closing page carries another company's mark
   (template residue). Neither affects panels.

The brand owner should confirm items 1–3, and correct this guide if the RGB values are the
intended ones.

## Open items

- **Official SVG artwork** for the wordmark lockup and the icon, in full colour and one colour.
  Until it is supplied, panels ship without a mark rather than with a traced one.
- **Poppins in panels is not possible** while panels declare no CSP origins (see Type). It
  would take an engine-side change to declare a font origin, which ADR-AIG-039 rules out.

## Panel PR checklist

Copy into every PR that changes a panel. The reviewer is Marty Bradley (discovery-engine
feature 27, N12).

- [ ] Light and dark screenshots attached, in a host or the panel's check page, at the default
      panel size and a narrow width
- [ ] Surfaces, text and font come from the host theme, with fallbacks as above; no brand
      background, gradient behind text, or web font
- [ ] Accent is purple in light mode and light blue in dark; dark purple only for light-mode
      headings; each use is checked against the resolved host surface and falls back to the host
      colour when it fails
- [ ] All text meets 4.5:1 (3:1 large); focus rings, markers and indicators meet 3:1 in both
      themes
- [ ] Status uses the host's semantic colours first, is never colour alone, and uses no brand
      secondary marked ✗ for the surface
- [ ] Host-context updates are merged into the current context, never replacing it
- [ ] One mark: the official, unaltered SVG at or above its minimum size, correct variant for the
      theme, with clear space (or no mark while the artwork is outstanding)
- [ ] Left-aligned, ragged right; no centred or justified multi-line text; no text effects
- [ ] Icons are thin-outline inline SVGs with accessible names where they convey meaning
- [ ] The built file passes the panel contract test: size, UTF-8, no external requests, and only
      the allowed tool names
