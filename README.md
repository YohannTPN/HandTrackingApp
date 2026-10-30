# HandTracking Paint

Draw in the air. A small Paint-style application controlled entirely by your hand: a webcam
tracks your thumb and index finger with [MediaPipe Hand Landmarker](https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker),
and a **pinch** is your mouse button.

## Features

- **Pinch to draw**: pinch your thumb and index finger together to draw on a white canvas.
- **Pinch to click**: the same gesture presses toolbar buttons and drags sliders. No mouse needed.
- **Tools**: brush, eraser, flood fill.
- **Undo / Restore** (10 steps).
- **Colour panel**:
  - colour wheel (hue and saturation) with a brightness slider, so true black is reachable,
  - brush size slider,
  - live preview of the current colour,
  - history of the last 5 colours you actually painted with.
- **Save** your drawing as a PNG.

## Requirements

- Python 3.11 (the version the project was developed on)
- A webcam
- The MediaPipe `hand_landmarker.task` model file (already in the folder)

## Installation

1. Clone or download the project, then create an isolated environment.

   With conda:

   ```bash
   conda create -n handtracking python=3.11
   conda activate handtracking
   ```

   Or with venv:

   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS / Linux
   source .venv/bin/activate
   ```

2. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Download the hand landmarker model into the project folder (if the file has magically dissapeared):

   ```bash
   curl -L -o hand_landmarker.task https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task
   ```

   On Windows PowerShell, `curl` is an alias for `Invoke-WebRequest` and rejects these options:
   use `curl.exe` instead, or download the file from the URL above with your browser.

## Usage

Run the app **from the project folder** (the model is loaded with a relative path):

```bash
python main.py
```

Two windows open: **Camera** (your hand with its skeleton) and **Paint** (the canvas).

### Controls

| Action | Gesture / key |
|---|---|
| Move the cursor | Move your hand (the cursor sits between thumb tip and index tip) |
| Draw | Pinch thumb and index, then move |
| Click a button | Pinch while the cursor is over it |
| Drag a slider | Pinch on it and move sideways (you can leave the slider area while dragging) |
| Save the drawing | `s` (writes `paint_<timestamp>.png` in the working directory) |
| Quit | `q` |

### Toolbar

| Button | Effect |
|---|---|
| Panel | Opens the colour panel |
| Brush | Selects the brush |
| Fill | Selects the flood-fill tool |
| Gomme | Selects the eraser |
| Undo / Restore | Steps back and forth through your last actions |

### Colour panel

Opening the panel shows the colour wheel, the brightness and thickness sliders, a preview of the
current colour and your last five colours. Pinch a colour on the wheel or in the history to select it.
Pinching anywhere **outside** the panel closes it. The panel is modal: while it is open,
nothing is drawn.

## How it works

- **Pinch detection**: the distance between thumb tip (landmark 4) and index tip (landmark 8)
  is divided by the size of the hand (wrist to middle-finger base), which makes it independent of
  your distance to the camera. Two thresholds (hysteresis) stop the pinch from flickering.
- **Cursor**: the midpoint of thumb tip and index tip, smoothed with an exponential filter to
  reduce jitter.
- **Click versus draw**: this is decided once, at the moment a pinch **starts**. If the interface
  takes the click (button, slider, panel), the whole pinch belongs to the interface and nothing is
  drawn; otherwise the pinch draws.
- **Undo**: a snapshot of the canvas is taken at the start of each stroke or fill.

## Project structure

| File | Role |
|---|---|
| `main.py` | Entry point |
| `HandLandMarker.py` | Base class: webcam loop and MediaPipe detection. Subclasses override the hooks `on_frame`, `render` and `on_key` |
| `HandPaint.py` | Subclass: pinch gesture, click-versus-draw logic, undo bookkeeping |
| `Ui.py` | `UI` class: canvas, toolbar, tools, panel, colour history, rendering |
| `Button.py` | Rectangular button with an action |
| `Slider.py` | Slider driven by a getter and a setter, so it is not tied to a particular setting |
| `ColorWheel.py` | HSV colour wheel with adjustable brightness |
| `Panel.py` | Modal panel grouping the wheel, sliders, preview and colour history |
| `Brush.py` | Brush settings (colour, thickness) |

## Configuration

Gesture tuning, in `HandPaint.py`:

| Constant | Meaning |
|---|---|
| `PINCH_ON` | Pinch ratio below which a pinch starts |
| `PINCH_OFF` | Pinch ratio above which a pinch ends |
| `SMOOTHING` | Cursor smoothing: `1` is none, lower values are smoother but laggier |

Panel layout is computed from the constants at the top of `Ui.py` (`PANEL_MARGIN`, `WHEEL_SIZE`,
`PREVIEW_SIZE`, `SWATCH_SIZE`, ...). The panel is centred in the frame, so it adapts to the camera
resolution as long as the frame is large enough to contain it.

## Known limitations

- The eraser paints white, so it assumes a white canvas.
- Flood fill spreads through any gap in an outline, so a shape that is not fully closed fills the
  surrounding area too. Strokes are drawn without anti-aliasing to avoid a pale halo between a
  stroke and the filled area.
- Toolbar buttons use fixed pixel positions designed for a 640x480 frame.
- Text is drawn with OpenCV's built-in font, which only supports ASCII characters.
- Undo keeps the last 10 actions.

## Troubleshooting

- **`A module that was compiled using NumPy 1.x cannot be run in NumPy 2.x`**: your environment
  contains packages built for an older NumPy. Create a fresh environment as described above rather
  than installing into a shared one.
- **MediaPipe prints `inference_feedback_manager.cc` warnings**: harmless, they can be ignored.
- **Black window or no camera**: the app opens camera index `0`. Close other applications that
  use the webcam, or change `camera_index` in `HandLandMarker.py`.
- **Cannot find `hand_landmarker.task`**: check that the file is in the folder you launch the
  app from.

## Roadmap

- Brush opacity
- Layers
- Zoom
- Nicer interface text (accents, centred labels) using Pillow

## Credits

Hand tracking by [MediaPipe](https://ai.google.dev/edge/mediapipe), image handling by
[OpenCV](https://opencv.org/).

## License

Not specified yet.