# directpx.py

import ctypes
import os
from PIL import Image

_dll_path = os.path.join(os.path.dirname(__file__), "main.dll")
_overlay = ctypes.CDLL(_dll_path)

_overlay.get_screen_size.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
_overlay.init.argtypes = [ctypes.c_int, ctypes.c_int]
_overlay.clear.argtypes = []
_overlay.draw_box.argtypes = [ctypes.c_int] * 8
_overlay.draw_text.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_int, ctypes.c_int]
_overlay.draw_image.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_char_p]
_overlay.update.argtypes = []
_overlay.close.argtypes = []
_overlay.show.argtypes = []
_overlay.hide.argtypes = []
_overlay.get_mouse.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
_overlay.get_screen.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
_overlay.get_screen_unedited.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]


def get_screen_size(monitor=0):
    w, h = ctypes.c_int(), ctypes.c_int()
    res = _overlay.get_screen_size(monitor, ctypes.byref(w), ctypes.byref(h))
    if res == 0 and w.value > 0 and h.value > 0:
        return (w.value, h.value)
    else:
        return None

def init(width, height):
    return _overlay.init(width, height)


def clear():
    return _overlay.clear()


def draw_box(x, y, w, h, r, g, b, a):
    return _overlay.draw_box(x, y, w, h, r, g, b, a)


def draw_text(x, y, text, r, g, b):
    return _overlay.draw_text(x, y, text.encode("utf-8"), r, g, b)


def draw_image(x, y, w, h, path):
    return _overlay.draw_image(x, y, w, h, path.encode("utf-8"))


def update():
    return _overlay.update()


def close():
    return _overlay.close()


def show():
    return _overlay.show()


def hide():
    return _overlay.hide()


def get_mouse():
    x, y = ctypes.c_int(), ctypes.c_int()
    res = _overlay.get_mouse(ctypes.byref(x), ctypes.byref(y))
    return (x.value, y.value) if res == 0 else None


def get_screen(as_image=False, save_path=None):
    w, h = get_screen_size()
    size = w * h * 4
    buf = (ctypes.c_ubyte * size)()
    if _overlay.get_screen(buf, size) == 0:
        img = Image.frombytes("RGBA", (w, h), bytes(buf))
        if save_path:
            img.save(save_path)
        return img if as_image else bytes(buf), (w, h)
    return None if as_image else (None, (0, 0))


def get_screen_unedited(as_image=False, save_path=None):
    w, h = get_screen_size()
    size = w * h * 4
    buf = (ctypes.c_ubyte * size)()
    if _overlay.get_screen_unedited(buf, size) == 0:
        img = Image.frombytes("RGBA", (w, h), bytes(buf))
        if save_path:
            img.save(save_path)
        return img if as_image else bytes(buf), (w, h)
    return None if as_image else (None, (0, 0))
