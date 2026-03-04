# Image Library

Browsable catalog of all images available for AdGen. Claude reads this file to select hero images that match a brief's persona, tone, and subject matter.

**To add images:** Drop them in the appropriate category folder and add a row to the table below. Or use Slack: `@adgen save this as [category], tags: [tags]`

---

## Product Screenshots

| File | Tags | Description |
|------|------|-------------|
| product/portal-dashboard.png | product, portal, dashboard, dark, cio, executive | Mission Control portal overview — dark theme, full dashboard view |
| product/api-docs-screen.png | product, api, developer, light, technical | API documentation page with code samples |
| product/mission-control.png | product, portal, mission-control, dark, overview | Mission Control main navigation and status view |

## Photography

| File | Tags | Description |
|------|------|-------------|
| photography/data-center-01.png | photography, infrastructure, dark, tech, enterprise | Server room wide shot — rows of racks with blue lighting |
| photography/server-rack.png | photography, infrastructure, dark, tech, detail | Close-up server rack with cable management |

## Abstract

| File | Tags | Description |
|------|------|-------------|
| abstract/network-pattern-dark.png | abstract, network, dark, tech, connectivity | Network node visualization — interconnected points on dark background |
| abstract/gradient-green.png | abstract, gradient, green, background, modern | Smooth black-to-green gradient texture |
| abstract/geometric-citron.png | abstract, geometric, citron, bold, modern | Geometric pattern using citron accent color |

---

## Tagging Convention

Use these categories when tagging new images:

| Category | Values |
|----------|--------|
| **Type** | product, photography, abstract, icon, data-viz |
| **Subject** | portal, api, network, server, team, office, data-center |
| **Tone** | professional, technical, warm, bold, minimal |
| **Color** | dark, light, green, citron, neutral |
| **Persona** | cio, developer, devops, marketing, executive |

## Image Requirements

- **Format:** PNG or high-quality JPG
- **Resolution:** Minimum 2400px on longest edge
- **No baked-in text** — render.py handles all text
- **No baked-in logos** — logo compositing is automatic
- **Clean edges** — needed for bleed/crop zones
- **Transparent background (PNG) preferred** for compositing flexibility
