# Themes in Orchestrator (Linux)

Orchestrator uses a CSS-based (QSS) styling system to control the application's appearance.

## Visual Customization

Unlike the macOS version, the Linux version uses highly customizable style sheets located in `orchestrator/styles.py`.

### Theme Colors
You can modify the base colors in the configuration or by editing the CSS values. The main components include:

- **Primary Background**: The dark application background.
- **Accent**: Color for trigger buttons and links (Purple by default).
- **Text**: Optimized for reading on modern screens.

## Transparency Effects
On Linux, transparency depends on your window manager (Compositor). Orchestrator attempts to apply opacity and gradient effects to mimic a modern and premium aesthetic.

## Fonts
The use of **Inter** or **Roboto** is recommended for the UI, and a monospaced font like **JetBrains Mono** or **Fira Code** for code blocks.
