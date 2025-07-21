```
╔─────────────────────────────────────────────────────────────────────────────────────────────────╗
│                                                                                                 │
│   ██████████    ███                               █████               ███████████  █████ █████  │
│  ░░███░░░░███  ░░░                               ░░███               ░░███░░░░░███░░███ ░░███   │
│   ░███   ░░███ ████  ████████   ██████   ██████  ███████              ░███    ░███ ░░███ ███    │
│   ░███    ░███░░███ ░░███░░███ ███░░███ ███░░███░░░███░    ██████████ ░██████████   ░░█████     │
│   ░███    ░███ ░███  ░███ ░░░ ░███████ ░███ ░░░   ░███    ░░░░░░░░░░  ░███░░░░░░     ███░███    │
│   ░███    ███  ░███  ░███     ░███░░░  ░███  ███  ░███ ███            ░███          ███ ░░███   │
│   ██████████   █████ █████    ░░██████ ░░██████   ░░█████             █████        █████ █████  │
│  ░░░░░░░░░░   ░░░░░ ░░░░░      ░░░░░░   ░░░░░░     ░░░░░             ░░░░░        ░░░░░ ░░░░░   │
│                                                                                                 │
╚─────────────────────────────────────────────────────────────────────────────────────────────────╝
```

**Direct-PX** — *Fast, flexible, and freakishly fun Windows screen overlay toolkit in Python.*

---

## What is this?

**Direct-PX** is a minimal Python wrapper for a Windows DLL that lets you draw pixels **directly** to the screen.

Great for:
- Custom HUDs and overlays
- Realtime pixel effects (scanlines, CRT, pixelation, etc)
- Debuggers/visualizers
- Weird experiments that make Task Manager angry

---

## Installation
**As for now:**
1. Clone this repo or download the files.
2. Make sure `main.dll` is placed next to `directpx.py`.

**later in time this may become a module and be installed with:**
   ```bash
   pip install directpx
   ```
## Dependancies

**ctypes :**
   ```bash
   pip install ctypes
   ```
**os :**
   ```bash
   pip install os
   ```
**PIL :**
   ```bash
   pip install PIL
   ```
---

## Example

```python
import time
import directpx

# Init overlay with full screen size
w, h = directpx.get_screen_size(1)  # 1 = primary monitor
directpx.init(w, h)

# Draw translucent white box
directpx.clear()
directpx.draw_box(100, 100, 200, 200, 255, 255, 255, 128)
directpx.update()

time.sleep(2)
directpx.close()
```

---

## Reference

### Overlay Management
| Function | Description |
|---------|-------------|
| `init(width, height)` | Initialize overlay window. |
| `update()` | Push changes to screen. |
| `clear()` | Clear current frame. |
| `close()` | Destroy the overlay. |
| `show()` / `hide()` | Show/hide the overlay. |

---

### Drawing
| Function | Description |
|---------|-------------|
| `draw_box(x, y, w, h, r, g, b, a)` | Draw a rectangle with RGBA color. |
| `draw_text(x, y, "text", r, g, b)` | Draw UTF-8 text. |
| `draw_image(x, y, w, h, path)` | Draw image from disk path. |

---

### Input / Capture
| Function | Description |
|---------|-------------|
| `get_mouse()` | Returns `(x, y)` of cursor. |
| `get_screen(as_image=True)` | Gets current overlay as `PIL.Image`. |
| `get_screen_unedited(as_image=True)` | Captures screen *excluding* overlay. |

---

### Monitor Info
```python
get_screen_size(monitor=0)
```

- `0` = All monitors (virtual screen)
- `1` = Primary
- `2+` = Secondary / external monitors

Returns `(width, height)` of selected screen. Returns `None` if the monitor index is invalid.

---

## Files

- `main.c` → DLL source (C)
- `main.dll` → Compiled DLL
- `directpx.py` → Python wrapper
- `test.py` → Example/test file

---

## Tips

- Capture underlaying screen with `get_screen_unedited()`
- Alpha values matter: use `draw_box(..., a)` to control transparency.

---
>[!Warning]
>## Potensial Issues
>This is still under development so many things may not work!

---
