# Antigravity Aesthetic (Premium Google Style)

Orchestrator uses the visual identity of **Antigravity**, designed to convey innovation, power, and clarity.

## Color Palette

- **Main Background (Deep Space)**: `#05060a` - A deep blue-black that reduces eye fatigue.
- **Primary Accent (Electric Cyan)**: `#00f2ff` - Used for focus states, activity indicators, and calls to action.
- **Secondary Accent (Galactic Purple)**: `#8a2be2` - Used to identify "Neural Thoughts" and user states.
- **Gradients**: Send button with a linear gradient from Cyan to Purple, representing the fusion of logic and creativity.

## Key UI Components

### 1. Glowing Capsule Input
The text input area is not a simple text box; it is a capsule designed with a reactive border that increases its glow (cyan glow) when the user interacts with it.

### 2. Neural Activity Log
Located in the bottom right, this panel provides a direct window into the agent's cognitive process. Logs are categorized by colors:
- **Purple**: Model thoughts.
- **Cyan**: System actions (Tools).
- **Green**: Observations and sensor data.
- **Red**: Critical errors.

### 3. Responsive Chat Layout
The chat dynamically adapts to the available width in the right panel. Message bubbles leverage horizontal space to maximize readability of code and long explanations.

### 4. Settings Dashboard (Dynamic Control)
The settings window extends the visual language with a clean tabbed design and integrated forms that allow managing the IA's "personality" without leaving the premium aesthetic.

## Technical Implementation

Styles are centralized in `styles.py` and dynamically applied through Qt Style Sheets (QSS). Transparencies (alpha), rounded borders (14px - 28px), and modern sans-serif typefaces are used to maintain a smooth and avant-garde aesthetic.
