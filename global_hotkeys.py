# global_hotkeys.py (Windows only)
import sys
if not sys.platform.startswith("win"):
    raise RuntimeError("Global hotkeys solo en Windows")

import ctypes
from ctypes import wintypes

user32 = ctypes.windll.user32

MOD_ALT     = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT   = 0x0004
MOD_WIN     = 0x0008

WM_HOTKEY = 0x0312

VK_F      = 0x46  # 'F'
VK_G      = 0x47  # 'G'
VK_T      = 0x54  # 'T'

class MSG(ctypes.Structure):
    _fields_ = [("hwnd",    wintypes.HWND),
                ("message", wintypes.UINT),
                ("wParam",  wintypes.WPARAM),
                ("lParam",  wintypes.LPARAM),
                ("time",    wintypes.DWORD),
                ("pt",      wintypes.POINT)]

def register_hotkey(id_: int, modifiers: int, vk: int):
    if not user32.RegisterHotKey(None, id_, modifiers, vk):
        raise OSError("RegisterHotKey falló")

def unregister_hotkey(id_: int):
    user32.UnregisterHotKey(None, id_)

def pump_once(dispatch: dict[int, callable]):
    """
    Procesa un mensaje (no bloqueante). Llamalo cada frame en tu loop.
    dispatch: {id: callback}
    """
    msg = MSG()
    PM_REMOVE = 0x0001
    while user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, PM_REMOVE):
        if msg.message == WM_HOTKEY:
            hotkey_id = msg.wParam
            cb = dispatch.get(hotkey_id)
            if cb:
                try:
                    cb()
                except Exception:
                    pass
        user32.TranslateMessage(ctypes.byref(msg))
        user32.DispatchMessageW(ctypes.byref(msg))
