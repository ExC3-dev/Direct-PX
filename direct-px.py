import ctypes
from ctypes import wintypes
from PIL import Image, ImageFont, ImageDraw

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
kernel32 = ctypes.windll.kernel32

LRESULT = ctypes.c_long

LPARAM = ctypes.c_longlong

WNDPROC = ctypes.WINFUNCTYPE(LRESULT, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, LPARAM)

WM_DESTROY = 0x0002
WS_EX_TRANSPARENT = 0x20
WS_EX_LAYERED = 0x80000
WS_EX_TOPMOST = 0x08
WS_EX_TOOLWINDOW = 0x00000080
WS_POPUP = 0x80000000
SW_SHOW = 5
ULW_ALPHA = 0x00000002
AC_SRC_ALPHA = 0x01

class POINT(ctypes.Structure):
    _fields_ = [('x', wintypes.LONG), ('y', wintypes.LONG)]

class SIZE(ctypes.Structure):
    _fields_ = [('cx', wintypes.LONG), ('cy', wintypes.LONG)]

class BLENDFUNCTION(ctypes.Structure):
    _fields_ = [('BlendOp', ctypes.c_byte), ('BlendFlags', ctypes.c_byte),
                ('SourceConstantAlpha', ctypes.c_byte), ('AlphaFormat', ctypes.c_byte)]

class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [('biSize', wintypes.DWORD), ('biWidth', wintypes.LONG), ('biHeight', wintypes.LONG),
                ('biPlanes', wintypes.WORD), ('biBitCount', wintypes.WORD),
                ('biCompression', wintypes.DWORD), ('biSizeImage', wintypes.DWORD),
                ('biXPelsPerMeter', wintypes.LONG), ('biYPelsPerMeter', wintypes.LONG),
                ('biClrUsed', wintypes.DWORD), ('biClrImportant', wintypes.DWORD)]

class BITMAPINFO(ctypes.Structure):
    _fields_ = [('bmiHeader', BITMAPINFOHEADER), ('bmiColors', wintypes.DWORD * 3)]

@WNDPROC
def wnd_proc(hwnd, msg, wparam, lparam):
    if msg == WM_DESTROY:
        user32.PostQuitMessage(0)
        return 0
    return user32.DefWindowProcW(hwnd, msg, wparam, lparam)

def get_screen_size():
    return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

class Overlay:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.bits = ctypes.c_void_p()
        self._init_window()
        self._init_bitmap()
        self.click_through_enabled = True

    def _init_window(self):
        hInstance = kernel32.GetModuleHandleW(None)
        className = 'OverlayWinClass'

        class WNDCLASS(ctypes.Structure):
            _fields_ = [('style', wintypes.UINT), ('lpfnWndProc', WNDPROC), ('cbClsExtra', ctypes.c_int),
                        ('cbWndExtra', ctypes.c_int), ('hInstance', wintypes.HINSTANCE),
                        ('hIcon', wintypes.HICON), ('hCursor', wintypes.HICON),
                        ('hbrBackground', wintypes.HBRUSH), ('lpszMenuName', wintypes.LPCWSTR),
                        ('lpszClassName', wintypes.LPCWSTR)]

        wndClass = WNDCLASS()
        wndClass.style = 0
        wndClass.lpfnWndProc = wnd_proc
        wndClass.cbClsExtra = 0
        wndClass.cbWndExtra = 0
        wndClass.hInstance = hInstance
        wndClass.hIcon = wndClass.hCursor = wndClass.hbrBackground = None
        wndClass.lpszMenuName = None
        wndClass.lpszClassName = className

        user32.RegisterClassW(ctypes.byref(wndClass))

        exstyle = WS_EX_LAYERED | WS_EX_TOPMOST | WS_EX_TOOLWINDOW | WS_EX_TRANSPARENT
        self.hwnd = user32.CreateWindowExW(
            exstyle, className, None, WS_POPUP,
            0, 0, self.width, self.height,
            None, None, hInstance, None
        )
        user32.ShowWindow(self.hwnd, SW_SHOW)
        self.hdc_screen = user32.GetDC(0)
        self.hdc_mem = gdi32.CreateCompatibleDC(self.hdc_screen)

    def _init_bitmap(self):
        bmi = BITMAPINFO()
        bmi.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
        bmi.bmiHeader.biWidth = self.width
        bmi.bmiHeader.biHeight = -self.height
        bmi.bmiHeader.biPlanes = 1
        bmi.bmiHeader.biBitCount = 32
        bmi.bmiHeader.biCompression = 0

        self.hbitmap = gdi32.CreateDIBSection(self.hdc_screen, ctypes.byref(bmi), 0,
                                               ctypes.byref(self.bits), None, 0)
        gdi32.SelectObject(self.hdc_mem, self.hbitmap)

    def draw_box(self, x, y, w, h, r, g, b, a):
        arr = (ctypes.c_ubyte * (self.width * self.height * 4)).from_address(self.bits.value)
        for j in range(h):
            for i in range(w):
                px = x + i
                py = y + j
                if 0 <= px < self.width and 0 <= py < self.height:
                    idx = (py * self.width + px) * 4
                    arr[idx] = b
                    arr[idx + 1] = g
                    arr[idx + 2] = r
                    arr[idx + 3] = a

    def draw_text(self, x, y, text, r=255, g=255, b=255, a=255, font_size=20):
        try:
            img = Image.frombuffer('RGBA', (self.width, self.height), ctypes.string_at(self.bits, self.width * self.height * 4), 'raw', 'BGRA', 0, 1)
            draw = ImageDraw.Draw(img)
            font = ImageFont.truetype("arial.ttf", font_size)
            draw.text((x, y), text, fill=(r, g, b, a), font=font)
            ctypes.memmove(self.bits, img.tobytes("raw", "BGRA"), self.width * self.height * 4)
        except Exception as e:
            print("draw_text error:", e)

    def draw_image(self, x, y, image_path):
        try:
            img = Image.open(image_path).convert("RGBA")
            img = img.resize((img.width, img.height))
            raw = img.tobytes("raw", "BGRA")
            arr = (ctypes.c_ubyte * (self.width * self.height * 4)).from_address(self.bits.value)
            for j in range(img.height):
                for i in range(img.width):
                    px = x + i
                    py = y + j
                    if 0 <= px < self.width and 0 <= py < self.height:
                        idx_src = (j * img.width + i) * 4
                        idx_dst = (py * self.width + px) * 4
                        arr[idx_dst:idx_dst+4] = raw[idx_src:idx_src+4]
        except Exception as e:
            print("draw_image error:", e)

    def set_click_through(self, enable=True):
        style = WS_EX_LAYERED | WS_EX_TOPMOST | WS_EX_TOOLWINDOW
        if enable:
            style |= WS_EX_TRANSPARENT
        user32.SetWindowLongW(self.hwnd, -20, style)

    def clear(self):
        ctypes.memset(self.bits, 0, self.width * self.height * 4)

    def update(self):
        ptSrc = POINT(0, 0)
        ptDst = POINT(0, 0)
        size = SIZE(self.width, self.height)
        blend = BLENDFUNCTION(0, 0, 255, AC_SRC_ALPHA)
        user32.UpdateLayeredWindow(self.hwnd, self.hdc_screen, ctypes.byref(ptDst),
                                   ctypes.byref(size), self.hdc_mem,
                                   ctypes.byref(ptSrc), 0, ctypes.byref(blend), ULW_ALPHA)

    def get_mouse(self):
        pt = POINT()
        user32.GetCursorPos(ctypes.byref(pt))
        return pt.x, pt.y
