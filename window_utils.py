# window_utils.py
import sys

IS_WINDOWS = sys.platform.startswith("win")

if IS_WINDOWS:
    import ctypes
    from ctypes import wintypes

    user32 = ctypes.windll.user32
    gdi32  = ctypes.windll.gdi32

    # --- SetWindowPos flags y z-order ---
    HWND_TOPMOST   = -1
    HWND_NOTOPMOST = -2
    SWP_NOMOVE     = 0x0002
    SWP_NOSIZE     = 0x0001
    SWP_NOZORDER   = 0x0004
    SWP_NOACTIVATE = 0x0010
    SWP_SHOWWINDOW = 0x0040

    # --- ShowWindow ---
    SW_HIDE     = 0
    SW_SHOWNOACTIVATE = 4
    SW_SHOW     = 5
    SW_MINIMIZE = 6
    SW_RESTORE  = 9

    # --- Estilos extendidos ---
    GWL_EXSTYLE = -20
    WS_EX_LAYERED     = 0x00080000
    WS_EX_TRANSPARENT = 0x00000020
    WS_EX_TOOLWINDOW  = 0x00000080     # no taskbar
    WS_EX_APPWINDOW   = 0x00040000     # sí taskbar
    WS_EX_NOACTIVATE  = 0x08000000     # no toma foco

    # Layered attrs
    LWA_COLORKEY = 0x00000001
    LWA_ALPHA    = 0x00000002

    SetWindowPos    = user32.SetWindowPos
    ShowWindow      = user32.ShowWindow
    SetForegroundWindow = user32.SetForegroundWindow
    GetWindowLongW  = user32.GetWindowLongW
    SetWindowLongW  = user32.SetWindowLongW
    SetLayeredWindowAttributes = user32.SetLayeredWindowAttributes

def _get_exstyle(hwnd: int) -> int:
    return GetWindowLongW(hwnd, GWL_EXSTYLE)

def _set_exstyle(hwnd: int, exstyle: int) -> None:
    SetWindowLongW(hwnd, GWL_EXSTYLE, exstyle)

def set_always_on_top(hwnd: int, enable: bool = True, no_activate: bool = True):
    """Pone/quita TOPMOST. Opcionalmente sin activar la ventana."""
    if not (IS_WINDOWS and hwnd):
        return
    insert_after = HWND_TOPMOST if enable else HWND_NOTOPMOST
    flags = SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW
    if no_activate:
        flags |= SWP_NOACTIVATE
    SetWindowPos(hwnd, insert_after, 0,0,0,0, flags)

def bring_to_front(hwnd: int, no_activate: bool = True):
    """Trae al frente. Reaplica topmost y no activa (para no robar foco a Ableton)."""
    if not (IS_WINDOWS and hwnd):
        return
    ShowWindow(hwnd, SW_SHOWNOACTIVATE if no_activate else SW_RESTORE)
    set_always_on_top(hwnd, True, no_activate=no_activate)

def set_click_through(hwnd: int, enable: bool, alpha: int = 200):
    """
    Activa/desactiva overlay 'fantasma':
    - WS_EX_LAYERED + WS_EX_TRANSPARENT => deja pasar el mouse
    - alpha: 0..255 (255 opaco). Requiere WS_EX_LAYERED.
    """
    if not (IS_WINDOWS and hwnd):
        return
    ex = _get_exstyle(hwnd)
    if enable:
        ex |= WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_NOACTIVATE
        _set_exstyle(hwnd, ex)
        # Establecer opacidad
        SetLayeredWindowAttributes(hwnd, 0, alpha, LWA_ALPHA)
        # Asegurar TOPMOST sin activar
        set_always_on_top(hwnd, True, no_activate=True)
    else:
        # Quitar TRANSPARENT/NOACTIVATE (dejamos LAYERED para poder manejar alpha, si querés)
        ex &= ~WS_EX_TRANSPARENT
        ex &= ~WS_EX_NOACTIVATE
        ex |= WS_EX_LAYERED  # seguimos layered para poder cambiar alpha si usás UI translúcida
        _set_exstyle(hwnd, ex)
        SetLayeredWindowAttributes(hwnd, 0, 255, LWA_ALPHA)

def set_opacity(hwnd: int, alpha: int):
    """Cambia opacidad sin tocar click-through."""
    if not (IS_WINDOWS and hwnd):
        return
    ex = _get_exstyle(hwnd) | WS_EX_LAYERED
    _set_exstyle(hwnd, ex)
    SetLayeredWindowAttributes(hwnd, 0, max(0, min(255, alpha)), LWA_ALPHA)

def hide_window(hwnd: int):
    if IS_WINDOWS and hwnd:
        ShowWindow(hwnd, SW_HIDE)

def show_window(hwnd: int, no_activate: bool = False):
    if IS_WINDOWS and hwnd:
        ShowWindow(hwnd, SW_SHOWNOACTIVATE if no_activate else SW_RESTORE)

def prefer_taskbar_icon(hwnd: int, prefer: bool = True):
    """Muestra/oculta en la barra de tareas."""
    if not (IS_WINDOWS and hwnd):
        return
    ex = _get_exstyle(hwnd)
    if prefer:
        ex = (ex | WS_EX_APPWINDOW) & ~WS_EX_TOOLWINDOW
    else:
        ex = (ex | WS_EX_TOOLWINDOW) & ~WS_EX_APPWINDOW
    _set_exstyle(hwnd, ex)
