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

**Direct-PX** — *Fast, Simple, and fun Windows screen overlay toolkit in Python.*

---

## What is this?

**Direct-PX** is a minimal Python Module that uses a Windows DLL that lets you draw pixels **directly** to the screen.

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
## Dependencies

**This uses A few modules to run, install all of them with**
   ```bash
   pip install ctypes
   pip install os
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
| `init(width, height)` | Initializes Program. |
| `update()` | Push changes to screen. |
| `clear()` | Clear current frame. |
| `close()` | Destroy the edits. |
| `show()` / `hide()` | Show/hide the changes. |

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
| `get_screen(as_image=True)` | Captures screen *including* changes. Can be `PIL.Image`. |
| `get_screen_unedited(as_image=True)` | Captures screen *excluding* changes. Can be `PIL.Image`. |

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
- `compile.txt` → Commands to compile main.c
- `libmain.a` → Lib file
- `stb_image.h` → Image library

---
>[!Warning]
>## Potential Issues
>
>**This can crash randomly *sometimes*.**
>
>*This is still under development so many things may not work!*
>
>**This module was only tested on Windows 11 and may not work in older versions.**
>**And also this was only *Built* For Windows and most likely break on other systems.**
---
