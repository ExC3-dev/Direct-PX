// main.c

#include <windows.h>
#include <string.h>
#include <wingdi.h>
#include <dwmapi.h>
#define STB_IMAGE_IMPLEMENTATION
#include "stb_image.h"

#pragma comment(lib, "dwmapi.lib")

#define ERR_OK 0
#define ERR_INVALID_SIZE -1
#define ERR_NOT_INITIALIZED -2
#define ERR_LOAD_IMAGE -3
#define ERR_DRAW_TEXT -4

static int screenW = 0, screenH = 0;
static HINSTANCE hInst;
static HWND hwnd;
static HDC hdcScreen, hdcMem;
static HBITMAP hBitmap;
static void* bits = NULL;

typedef struct {
    int targetIndex;
    int currentIndex;
    int found;
    int width;
    int height;
} MonitorEnumData;

BOOL CALLBACK EnumMonitorCallback(HMONITOR hMonitor, HDC hdcMonitor, LPRECT lprcMonitor, LPARAM dwData) {
    MonitorEnumData* data = (MonitorEnumData*)dwData;
    if (data->currentIndex == data->targetIndex) {
        data->width = lprcMonitor->right - lprcMonitor->left;
        data->height = lprcMonitor->bottom - lprcMonitor->top;
        data->found = 1;
        return FALSE;
    }
    data->currentIndex++;
    return TRUE;
}

__declspec(dllexport) int init(int width, int height) {
    if (width <= 0 || height <= 0) return ERR_INVALID_SIZE;
    screenW = width;
    screenH = height;
    hInst = GetModuleHandle(NULL);

    WNDCLASS wc = { 0 };
    wc.lpfnWndProc = DefWindowProc;
    wc.hInstance = hInst;
    wc.lpszClassName = "OverlayWindowClass";
    RegisterClass(&wc);

    hwnd = CreateWindowEx(
        WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_TOPMOST | WS_EX_TOOLWINDOW,
        "OverlayWindowClass", "", WS_POPUP,
        0, 0, screenW, screenH,
        NULL, NULL, hInst, NULL
    );
    if (!hwnd) return ERR_NOT_INITIALIZED;

    ShowWindow(hwnd, SW_SHOW);
    hdcScreen = GetDC(NULL);
    hdcMem = CreateCompatibleDC(hdcScreen);

    BITMAPINFO bmi = { 0 };
    bmi.bmiHeader.biSize = sizeof(BITMAPINFOHEADER);
    bmi.bmiHeader.biWidth = screenW;
    bmi.bmiHeader.biHeight = -screenH;
    bmi.bmiHeader.biPlanes = 1;
    bmi.bmiHeader.biBitCount = 32;
    bmi.bmiHeader.biCompression = BI_RGB;

    hBitmap = CreateDIBSection(hdcScreen, &bmi, DIB_RGB_COLORS, &bits, NULL, 0);
    if (!hBitmap) return ERR_NOT_INITIALIZED;

    SelectObject(hdcMem, hBitmap);
    memset(bits, 0, screenW * screenH * 4);
    return ERR_OK;
}

__declspec(dllexport) int clear() {
    if (!bits) return ERR_NOT_INITIALIZED;
    memset(bits, 0, screenW * screenH * 4);
    return ERR_OK;
}

__declspec(dllexport) int draw_box(int x, int y, int w, int h, int r, int g, int b, int a) {
    if (!bits) return ERR_NOT_INITIALIZED;
    if (w <= 0 || h <= 0) return ERR_INVALID_SIZE;
    for (int j = 0; j < h; ++j) {
        for (int i = 0; i < w; ++i) {
            int px = x + i;
            int py = y + j;
            if (px < 0 || px >= screenW || py < 0 || py >= screenH) continue;
            unsigned char* pixel = (unsigned char*)bits + (py * screenW + px) * 4;
            pixel[0] = b;
            pixel[1] = g;
            pixel[2] = r;
            pixel[3] = a;
        }
    }
    return ERR_OK;
}

__declspec(dllexport) int draw_text(int x, int y, const char* text, int r, int g, int b) {
    if (!hdcMem || !text) return ERR_NOT_INITIALIZED;
    SetTextColor(hdcMem, RGB(r, g, b));
    SetBkMode(hdcMem, TRANSPARENT);
    TextOutA(hdcMem, x, y, text, (int)strlen(text));
    return ERR_OK;
}

__declspec(dllexport) int draw_image(int x, int y, int w, int h, const char* path) {
    if (!hdcMem || !path) return ERR_NOT_INITIALIZED;

    int imgW, imgH, channels;
    unsigned char* data = stbi_load(path, &imgW, &imgH, &channels, 4);
    if (!data) return ERR_LOAD_IMAGE;

    BITMAPINFO bmi = { 0 };
    bmi.bmiHeader.biSize = sizeof(BITMAPINFOHEADER);
    bmi.bmiHeader.biWidth = imgW;
    bmi.bmiHeader.biHeight = -imgH;
    bmi.bmiHeader.biPlanes = 1;
    bmi.bmiHeader.biBitCount = 32;
    bmi.bmiHeader.biCompression = BI_RGB;

    void* dibData = NULL;
    HBITMAP hBmp = CreateDIBSection(hdcMem, &bmi, DIB_RGB_COLORS, &dibData, NULL, 0);
    if (!hBmp || !dibData) {
        stbi_image_free(data);
        return ERR_LOAD_IMAGE;
    }

    memcpy(dibData, data, imgW * imgH * 4);
    stbi_image_free(data);

    HDC hdcTemp = CreateCompatibleDC(hdcMem);
    SelectObject(hdcTemp, hBmp);
    StretchBlt(hdcMem, x, y, w, h, hdcTemp, 0, 0, imgW, imgH, SRCCOPY);
    DeleteDC(hdcTemp);
    DeleteObject(hBmp);

    return ERR_OK;
}

__declspec(dllexport) int update() {
    if (!hwnd) return ERR_NOT_INITIALIZED;
    POINT ptSrc = { 0, 0 };
    SIZE sizeWnd = { screenW, screenH };
    BLENDFUNCTION blend = { AC_SRC_OVER, 0, 255, AC_SRC_ALPHA };
    POINT ptDst = { 0, 0 };
    BOOL res = UpdateLayeredWindow(hwnd, hdcScreen, &ptDst, &sizeWnd, hdcMem, &ptSrc, 0, &blend, ULW_ALPHA);
    return res ? ERR_OK : ERR_NOT_INITIALIZED;
}

__declspec(dllexport) int close() {
    if (hBitmap) DeleteObject(hBitmap);
    if (hdcMem) DeleteDC(hdcMem);
    if (hdcScreen) ReleaseDC(NULL, hdcScreen);
    if (hwnd) DestroyWindow(hwnd);
    hBitmap = NULL; hdcMem = NULL; hdcScreen = NULL; hwnd = NULL;
    bits = NULL;
    screenW = screenH = 0;
    return ERR_OK;
}

__declspec(dllexport) int show() {
    if (!hwnd) return ERR_NOT_INITIALIZED;
    ShowWindow(hwnd, SW_SHOW);
    return ERR_OK;
}

__declspec(dllexport) int hide() {
    if (!hwnd) return ERR_NOT_INITIALIZED;
    ShowWindow(hwnd, SW_HIDE);
    return ERR_OK;
}

__declspec(dllexport) int get_mouse(int* x, int* y) {
    if (!x || !y) return ERR_INVALID_SIZE;
    POINT pt;
    if (GetCursorPos(&pt)) {
        *x = pt.x;
        *y = pt.y;
        return ERR_OK;
    }
    return ERR_NOT_INITIALIZED;
}

__declspec(dllexport) int get_screen_size(int monitor, int* width, int* height) {
    if (!width || !height) return ERR_INVALID_SIZE;

    if (monitor == 0) {
        *width = GetSystemMetrics(SM_CXVIRTUALSCREEN);
        *height = GetSystemMetrics(SM_CYVIRTUALSCREEN);
        return ERR_OK;
    }
    else if (monitor == 1) {
        *width = GetSystemMetrics(SM_CXSCREEN);
        *height = GetSystemMetrics(SM_CYSCREEN);
        return ERR_OK;
    }
    else if (monitor > 1) {
        MonitorEnumData data = { .targetIndex = monitor - 1, .currentIndex = 0, .found = 0 };
        if (!EnumDisplayMonitors(NULL, NULL, EnumMonitorCallback, (LPARAM)&data) || !data.found) {
            return ERR_INVALID_SIZE;
        }
        *width = data.width;
        *height = data.height;
        return ERR_OK;
    }
    return ERR_INVALID_SIZE;
}

__declspec(dllexport) int get_screen(unsigned char* outBuffer, int bufferSize) {
    if (!bits || !outBuffer) return ERR_NOT_INITIALIZED;
    int dataSize = screenW * screenH * 4;
    if (bufferSize < dataSize) return ERR_INVALID_SIZE;
    memcpy(outBuffer, bits, dataSize);
    return ERR_OK;
}

__declspec(dllexport) int get_screen_unedited(unsigned char* outBuffer, int bufferSize) {
    if (!hwnd) return ERR_NOT_INITIALIZED;

    BOOL exclude = TRUE;
    DwmSetWindowAttribute(hwnd, 17, &exclude, sizeof(exclude));
    Sleep(10);

    HDC hdcSrc = GetDC(NULL);
    HDC hdcTmp = CreateCompatibleDC(hdcSrc);

    BITMAPINFO bmi = { 0 };
    bmi.bmiHeader.biSize = sizeof(BITMAPINFOHEADER);
    bmi.bmiHeader.biWidth = screenW;
    bmi.bmiHeader.biHeight = -screenH;
    bmi.bmiHeader.biPlanes = 1;
    bmi.bmiHeader.biBitCount = 32;
    bmi.bmiHeader.biCompression = BI_RGB;

    void* tempBits;
    HBITMAP hTmpBmp = CreateDIBSection(hdcSrc, &bmi, DIB_RGB_COLORS, &tempBits, NULL, 0);
    if (!hTmpBmp) {
        DeleteDC(hdcTmp);
        ReleaseDC(NULL, hdcSrc);
        return ERR_NOT_INITIALIZED;
    }

    SelectObject(hdcTmp, hTmpBmp);
    BitBlt(hdcTmp, 0, 0, screenW, screenH, hdcSrc, 0, 0, SRCCOPY);

    int dataSize = screenW * screenH * 4;
    if (bufferSize < dataSize) {
        DeleteObject(hTmpBmp);
        DeleteDC(hdcTmp);
        ReleaseDC(NULL, hdcSrc);
        BOOL excludeOff = FALSE;
        DwmSetWindowAttribute(hwnd, 17, &excludeOff, sizeof(excludeOff));
        return ERR_INVALID_SIZE;
    }

    memcpy(outBuffer, tempBits, dataSize);

    DeleteObject(hTmpBmp);
    DeleteDC(hdcTmp);
    ReleaseDC(NULL, hdcSrc);

    BOOL excludeOff = FALSE;
    DwmSetWindowAttribute(hwnd, 17, &excludeOff, sizeof(excludeOff));

    return ERR_OK;
}
