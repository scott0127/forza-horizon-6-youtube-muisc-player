# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import asyncio
import base64
import ctypes
from ctypes import wintypes
import io
import json
import os
from pathlib import Path
import queue
import sys
import threading
import time
import tkinter as tk
import warnings
from dataclasses import dataclass
from tkinter import messagebox
import webbrowser

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
warnings.filterwarnings("ignore", category=UserWarning)

try:
    from PIL import Image, ImageDraw, ImageTk
except Exception as exc:  # pragma: no cover - shown in GUI at runtime
    Image = None
    ImageDraw = None
    ImageTk = None
    PIL_IMPORT_ERROR = exc
else:
    PIL_IMPORT_ERROR = None


APP_TITLE = "Forza 音樂懸浮播放器"
APP_VERSION = "2.0.0"
YOUTUBE_MUSIC_URL = "https://music.youtube.com"
SPOTIFY_URL = "https://open.spotify.com"
APPLE_MUSIC_URL = "https://music.apple.com"
SUPPORTED_MUSIC_LABEL = "YouTube Music / Spotify / Apple Music"
APP_DIR = Path(__file__).resolve().parent
APP_DATA_DIR = Path(os.environ.get("LOCALAPPDATA", str(APP_DIR))) / "ForzaMusicOverlay"
SETTINGS_PATH = APP_DATA_DIR / "settings.json"
DEFAULT_SETTINGS = {
    "overlay_x": 24,
    "overlay_y": 24,
    "music_service": "youtube",
}

MUSIC_SERVICES = {
    "youtube": {
        "display": "YouTube Music",
        "overlay": "YOUTUBE MUSIC",
        "accent": "#ff0033",
        "url": YOUTUBE_MUSIC_URL,
    },
    "spotify": {
        "display": "Spotify",
        "overlay": "SPOTIFY",
        "accent": "#1ed760",
        "url": SPOTIFY_URL,
    },
    "apple": {
        "display": "Apple Music",
        "overlay": "APPLE MUSIC",
        "accent": "#111111",
        "url": APPLE_MUSIC_URL,
    },
}


@dataclass(frozen=True)
class TrackInfo:
    title: str = ""
    artist: str = ""
    album: str = ""
    app_id: str = ""
    status: str = "UNKNOWN"
    artwork_bytes: bytes | None = None
    position_seconds: float = 0.0
    duration_seconds: float = 0.0
    timeline_updated_at: float = 0.0
    playback_rate: float = 1.0
    error: str = ""

    @property
    def is_empty(self) -> bool:
        return not self.title and not self.artist and not self.album and not self.error

    @property
    def fingerprint(self) -> str:
        return "|".join(
            [
                self.title,
                self.artist,
                self.album,
                self.app_id,
                self.status,
                f"{self.position_seconds:.1f}",
                f"{self.duration_seconds:.1f}",
            ]
        )


class Win32:
    user32 = ctypes.WinDLL("user32", use_last_error=True)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

    MOD_ALT = 0x0001
    MOD_CONTROL = 0x0002
    MOD_NOREPEAT = 0x4000

    WM_HOTKEY = 0x0312
    WM_QUIT = 0x0012

    VK_SPACE = 0x20
    VK_END = 0x23
    VK_HOME = 0x24
    VK_LEFT = 0x25
    VK_UP = 0x26
    VK_RIGHT = 0x27
    VK_DOWN = 0x28
    VK_H = 0x48
    VK_P = 0x50
    VK_Q = 0x51

    VK_VOLUME_MUTE = 0xAD
    VK_VOLUME_DOWN = 0xAE
    VK_VOLUME_UP = 0xAF
    VK_MEDIA_NEXT_TRACK = 0xB0
    VK_MEDIA_PREV_TRACK = 0xB1
    VK_MEDIA_PLAY_PAUSE = 0xB3

    KEYEVENTF_KEYUP = 0x0002

    GWL_EXSTYLE = -20
    WS_EX_TRANSPARENT = 0x00000020
    WS_EX_TOOLWINDOW = 0x00000080
    WS_EX_LAYERED = 0x00080000
    WS_EX_NOACTIVATE = 0x08000000

    HWND_TOPMOST = -1
    SWP_NOSIZE = 0x0001
    SWP_NOMOVE = 0x0002
    SWP_NOACTIVATE = 0x0010
    SWP_SHOWWINDOW = 0x0040

    ERROR_ALREADY_EXISTS = 183


def _configure_win32_prototypes() -> None:
    Win32.user32.RegisterHotKey.argtypes = [wintypes.HWND, ctypes.c_int, wintypes.UINT, wintypes.UINT]
    Win32.user32.RegisterHotKey.restype = wintypes.BOOL
    Win32.user32.UnregisterHotKey.argtypes = [wintypes.HWND, ctypes.c_int]
    Win32.user32.UnregisterHotKey.restype = wintypes.BOOL
    Win32.user32.GetMessageW.argtypes = [ctypes.POINTER(wintypes.MSG), wintypes.HWND, wintypes.UINT, wintypes.UINT]
    Win32.user32.GetMessageW.restype = wintypes.BOOL
    Win32.user32.PostThreadMessageW.argtypes = [wintypes.DWORD, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
    Win32.user32.PostThreadMessageW.restype = wintypes.BOOL
    Win32.kernel32.GetCurrentThreadId.restype = wintypes.DWORD
    Win32.user32.keybd_event.argtypes = [wintypes.BYTE, wintypes.BYTE, wintypes.DWORD, wintypes.ULONG]
    Win32.user32.keybd_event.restype = None
    Win32.user32.SetWindowPos.argtypes = [
        wintypes.HWND,
        wintypes.HWND,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        wintypes.UINT,
    ]
    Win32.user32.SetWindowPos.restype = wintypes.BOOL
    Win32.kernel32.CreateMutexW.argtypes = [wintypes.LPVOID, wintypes.BOOL, wintypes.LPCWSTR]
    Win32.kernel32.CreateMutexW.restype = wintypes.HANDLE
    Win32.kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    Win32.kernel32.CloseHandle.restype = wintypes.BOOL


_configure_win32_prototypes()

if ctypes.sizeof(ctypes.c_void_p) == 8:
    GetWindowLong = Win32.user32.GetWindowLongPtrW
    SetWindowLong = Win32.user32.SetWindowLongPtrW
else:
    GetWindowLong = Win32.user32.GetWindowLongW
    SetWindowLong = Win32.user32.SetWindowLongW

GetWindowLong.argtypes = [wintypes.HWND, ctypes.c_int]
GetWindowLong.restype = ctypes.c_longlong if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_long
SetWindowLong.argtypes = [wintypes.HWND, ctypes.c_int, GetWindowLong.restype]
SetWindowLong.restype = GetWindowLong.restype


def send_media_key(virtual_key: int) -> None:
    Win32.user32.keybd_event(virtual_key, 0, 0, 0)
    Win32.user32.keybd_event(virtual_key, 0, Win32.KEYEVENTF_KEYUP, 0)


def acquire_single_instance_mutex() -> wintypes.HANDLE | None:
    handle = Win32.kernel32.CreateMutexW(None, True, "Global\\ForzaMusicOverlayPython")
    if not handle:
        return None
    if ctypes.get_last_error() == Win32.ERROR_ALREADY_EXISTS:
        Win32.kernel32.CloseHandle(handle)
        return None
    return handle


def apply_overlay_window_style(window: tk.Toplevel) -> None:
    window.update_idletasks()
    hwnd = window.winfo_id()
    style = GetWindowLong(hwnd, Win32.GWL_EXSTYLE)
    # Tk child controls can render as a black rectangle on Windows when the
    # same toplevel is both layered and click-through. Keep the player visible
    # first; click-through can be added later as an opt-in mode.
    style &= ~Win32.WS_EX_LAYERED
    style &= ~Win32.WS_EX_TRANSPARENT
    style |= Win32.WS_EX_TOOLWINDOW | Win32.WS_EX_NOACTIVATE
    SetWindowLong(hwnd, Win32.GWL_EXSTYLE, style)
    Win32.user32.SetWindowPos(
        hwnd,
        Win32.HWND_TOPMOST,
        0,
        0,
        0,
        0,
        Win32.SWP_NOMOVE | Win32.SWP_NOSIZE | Win32.SWP_NOACTIVATE | Win32.SWP_SHOWWINDOW,
    )


async def read_thumbnail_bytes(thumbnail) -> bytes | None:
    if thumbnail is None:
        return None

    from winsdk.windows.storage.streams import DataReader

    try:
        stream = await asyncio.wait_for(thumbnail.open_read_async(), timeout=1.8)
        if stream is None or stream.size == 0:
            return None

        reader = DataReader(stream.get_input_stream_at(0))
        await asyncio.wait_for(reader.load_async(stream.size), timeout=1.8)
        return bytes(reader.read_buffer(stream.size))
    except Exception:
        return None


async def get_current_track(read_artwork: bool = True) -> TrackInfo:
    try:
        from winsdk.windows.media.control import (
            GlobalSystemMediaTransportControlsSessionManager as MediaManager,
        )

        manager = await asyncio.wait_for(MediaManager.request_async(), timeout=1.8)
        session = manager.get_current_session()
        if session is None:
            return TrackInfo(status="NO_SESSION")

        props = await asyncio.wait_for(session.try_get_media_properties_async(), timeout=1.8)
        playback = session.get_playback_info()
        status = getattr(playback.playback_status, "name", str(playback.playback_status))
        timeline = session.get_timeline_properties()
        start_seconds = timeline.start_time.total_seconds()
        end_seconds = timeline.end_time.total_seconds()
        position_seconds = max(0.0, timeline.position.total_seconds() - start_seconds)
        duration_seconds = max(0.0, end_seconds - start_seconds)
        timeline_updated_at = timeline.last_updated_time.timestamp()
        playback_rate = getattr(playback, "playback_rate", 1.0) or 1.0
        
        artwork_bytes = None
        if read_artwork and props.thumbnail:
            try:
                artwork_bytes = await asyncio.wait_for(read_thumbnail_bytes(props.thumbnail), timeout=2.2)
            except Exception:
                pass

        return TrackInfo(
            title=(props.title or "").strip(),
            artist=(props.artist or "").strip(),
            album=(props.album_title or "").strip(),
            app_id=(session.source_app_user_model_id or "").strip(),
            status=status,
            artwork_bytes=artwork_bytes,
            position_seconds=position_seconds,
            duration_seconds=duration_seconds,
            timeline_updated_at=timeline_updated_at,
            playback_rate=float(playback_rate),
        )
    except asyncio.TimeoutError:
        return TrackInfo(status="ERROR", error="讀取 Windows 媒體逾時")
    except Exception as exc:
        return TrackInfo(status="ERROR", error=str(exc))


def get_artwork_key(track: TrackInfo) -> str:
    return "|".join([track.title, track.artist, track.album, track.app_id])


def is_probably_browser_app_icon(track: TrackInfo, artwork_bytes: bytes) -> bool:
    app_id = (track.app_id or "").lower()
    if not any(browser in app_id for browser in ("chrome", "msedge", "edge", "firefox")):
        return False

    if not track.title or Image is None:
        return False

    try:
        image = Image.open(io.BytesIO(artwork_bytes)).convert("RGBA")
    except Exception:
        return False

    width, height = image.size
    if width <= 0 or height <= 0:
        return False

    square_ratio = min(width, height) / max(width, height)
    if square_ratio < 0.92:
        return False

    alpha = image.getchannel("A")
    transparent_pixels = sum(1 for value in alpha.getdata() if value < 245)
    transparent_ratio = transparent_pixels / float(width * height)
    return transparent_ratio > 0.08


async def media_poll_loop(output: queue.Queue, stop_event: threading.Event, interval: float = 0.8) -> None:
    last_fingerprint = ""
    last_metadata_key = ""
    last_artwork_bytes: bytes | None = None
    pending_artwork_key = ""
    artwork_retries_remaining = 0

    while not stop_event.is_set():
        try:
            current = await get_current_track(read_artwork=False)
            metadata_key = get_artwork_key(current)
            metadata_changed = metadata_key != last_metadata_key

            if metadata_changed:
                last_metadata_key = metadata_key
                pending_artwork_key = metadata_key
                artwork_retries_remaining = 10

            if current.fingerprint != last_fingerprint:
                last_fingerprint = current.fingerprint
                output.put(("track", current))

            if metadata_changed:
                await asyncio.sleep(0.35)

            if pending_artwork_key and artwork_retries_remaining > 0:
                with_artwork = await get_current_track(read_artwork=True)
                if get_artwork_key(with_artwork) == pending_artwork_key:
                    artwork_retries_remaining -= 1

                    if (
                        with_artwork.artwork_bytes is not None
                        and with_artwork.artwork_bytes != last_artwork_bytes
                        and not is_probably_browser_app_icon(with_artwork, with_artwork.artwork_bytes)
                    ):
                        last_artwork_bytes = with_artwork.artwork_bytes
                        artwork_retries_remaining = 0
                        output.put(("track", with_artwork))
                else:
                    pending_artwork_key = ""
                    artwork_retries_remaining = 0
        except Exception as exc:
            output.put(("track", TrackInfo(status="ERROR", error=str(exc))))

        await asyncio.sleep(interval)


class HotkeyThread(threading.Thread):
    HOTKEYS = {
        1: ("play_pause", Win32.VK_SPACE, Win32.VK_MEDIA_PLAY_PAUSE),
        2: ("next", Win32.VK_RIGHT, Win32.VK_MEDIA_NEXT_TRACK),
        3: ("previous", Win32.VK_LEFT, Win32.VK_MEDIA_PREV_TRACK),
        4: ("volume_up", Win32.VK_UP, Win32.VK_VOLUME_UP),
        5: ("volume_down", Win32.VK_DOWN, Win32.VK_VOLUME_DOWN),
        6: ("mute", Win32.VK_END, Win32.VK_VOLUME_MUTE),
        7: ("toggle_overlay", Win32.VK_HOME, None),
        8: ("toggle_control", Win32.VK_H, None),
        9: ("toggle_position_mode", Win32.VK_P, None),
        10: ("quit", Win32.VK_Q, None),
    }

    LABELS = {
        "play_pause": "Ctrl+Alt+Space",
        "next": "Ctrl+Alt+Right",
        "previous": "Ctrl+Alt+Left",
        "volume_up": "Ctrl+Alt+Up",
        "volume_down": "Ctrl+Alt+Down",
        "mute": "Ctrl+Alt+End",
        "toggle_overlay": "Ctrl+Alt+Home",
        "toggle_control": "Ctrl+Alt+H",
        "toggle_position_mode": "Ctrl+Alt+P",
        "quit": "Ctrl+Alt+Q",
    }

    def __init__(self, output: queue.Queue, stop_event: threading.Event):
        super().__init__(daemon=True)
        self.output = output
        self.stop_event = stop_event
        self.thread_id = 0

    def stop(self) -> None:
        self.stop_event.set()
        if self.thread_id:
            Win32.user32.PostThreadMessageW(self.thread_id, Win32.WM_QUIT, 0, 0)

    def run(self) -> None:
        self.thread_id = Win32.kernel32.GetCurrentThreadId()
        registered: list[int] = []
        modifiers = Win32.MOD_CONTROL | Win32.MOD_ALT | Win32.MOD_NOREPEAT

        for hotkey_id, (command, virtual_key, _media_key) in self.HOTKEYS.items():
            if Win32.user32.RegisterHotKey(None, hotkey_id, modifiers, virtual_key):
                registered.append(hotkey_id)
            else:
                error_code = ctypes.get_last_error()
                self.output.put(
                    (
                        "hotkey_error",
                        f"{self.LABELS.get(command, command)} registration failed: Windows error {error_code}",
                    )
                )

        msg = wintypes.MSG()
        while not self.stop_event.is_set():
            result = Win32.user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
            if result == 0:
                break
            if result == -1:
                error_code = ctypes.get_last_error()
                self.output.put(("hotkey_error", f"Hotkey message loop failed: Windows error {error_code}"))
                break

            if msg.message == Win32.WM_HOTKEY:
                hotkey_id = int(msg.wParam)
                command, _virtual_key, media_key = self.HOTKEYS.get(hotkey_id, ("", 0, None))
                if media_key is not None:
                    send_media_key(media_key)
                elif command:
                    self.output.put(("command", command))

        for hotkey_id in registered:
            Win32.user32.UnregisterHotKey(None, hotkey_id)


class GamepadThread(threading.Thread):
    # L3（左搖桿按下）作為修飾鍵，避免與 Forza 的 LB（離合器）衝突。
    # Xbox: L3 = 按鈕索引 8, PlayStation: L3 = 按鈕索引 11。
    L3_BUTTONS = (8, 11)

    BUTTON_COMBOS = (
        ("L3 + A", L3_BUTTONS, 0, Win32.VK_MEDIA_PLAY_PAUSE),
        ("L3 + B", L3_BUTTONS, 1, Win32.VK_MEDIA_NEXT_TRACK),
        ("L3 + X", L3_BUTTONS, 2, Win32.VK_MEDIA_PREV_TRACK),
    )
    HAT_COMBOS = (
        ("L3 + 上鍵", L3_BUTTONS, (0, 1), Win32.VK_VOLUME_UP),
        ("L3 + 下鍵", L3_BUTTONS, (0, -1), Win32.VK_VOLUME_DOWN),
    )
    # PlayStation 手把的 D-Pad 通常映射為按鈕而非 hat，
    # 以下為常見的 DualSense / DualShock 4 D-Pad 按鈕索引。
    # 注意：僅在 hat_count == 0 時使用此 fallback，
    # 避免與 L3 的 PS 索引 (11) 衝突。
    PS_DPAD_BUTTONS: dict[tuple[int, int], tuple[int, ...]] = {
        (0, 1): (11,),    # 上
        (0, -1): (12,),   # 下
        (-1, 0): (13,),   # 左
        (1, 0): (14,),    # 右
    }

    def __init__(self, output: queue.Queue, stop_event: threading.Event):
        super().__init__(daemon=True)
        self.output = output
        self.stop_event = stop_event

    def run(self) -> None:
        try:
            import pygame
        except Exception as exc:
            self.output.put(("gamepad_status", f"手把控制未啟用：pygame 尚未安裝 ({exc})"))
            return

        pressed_combos: set[tuple[int, str]] = set()
        joysticks = []
        last_count = -1
        last_pressed_inputs = set()

        try:
            pygame.init()
            pygame.joystick.init()

            while not self.stop_event.is_set():
                pygame.event.pump()
                count = pygame.joystick.get_count()

                if count != last_count:
                    joysticks = []
                    for index in range(count):
                        joystick = pygame.joystick.Joystick(index)
                        joystick.init()
                        joysticks.append(joystick)

                    if count:
                        info_parts = []
                        for joystick in joysticks:
                            name = joystick.get_name()
                            n_buttons = joystick.get_numbuttons()
                            n_hats = joystick.get_numhats()
                            info_parts.append(f"{name} (按鈕:{n_buttons} hat:{n_hats})")
                        self.output.put(("gamepad_status", f"手把控制已啟用：{', '.join(info_parts)}"))
                    else:
                        self.output.put(("gamepad_status", "手把控制：未偵測到控制器"))

                    last_count = count

                pressed_this_tick = set()
                for joy_index, joystick in enumerate(joysticks):
                    button_count = joystick.get_numbuttons()
                    hat_count = joystick.get_numhats()

                    # 1. 偵測 L3
                    for btn in self.L3_BUTTONS:
                        if btn < button_count and joystick.get_button(btn):
                            pressed_this_tick.add("L3")
                            break

                    # 2. 偵測 A
                    if 0 < button_count and joystick.get_button(0):
                        pressed_this_tick.add("A")

                    # 3. 偵測 B
                    if 1 < button_count and joystick.get_button(1):
                        pressed_this_tick.add("B")

                    # 4. 偵測 X
                    if 2 < button_count and joystick.get_button(2):
                        pressed_this_tick.add("X")

                    # 5. 偵測 UP
                    is_up = False
                    for hat_index in range(hat_count):
                        if joystick.get_hat(hat_index)[1] == 1:
                            is_up = True
                            break
                    if not is_up and hat_count == 0:
                        if 11 < button_count and joystick.get_button(11):
                            is_up = True
                    if is_up:
                        pressed_this_tick.add("UP")

                    # 6. 偵測 DOWN
                    is_down = False
                    for hat_index in range(hat_count):
                        if joystick.get_hat(hat_index)[1] == -1:
                            is_down = True
                            break
                    if not is_down and hat_count == 0:
                        if 12 < button_count and joystick.get_button(12):
                            is_down = True
                    if is_down:
                        pressed_this_tick.add("DOWN")
                    for label, modifier_buttons, action_button, media_key in self.BUTTON_COMBOS:
                        combo_id = (joy_index, label)
                        modifier_pressed = any(
                            btn < button_count and joystick.get_button(btn)
                            for btn in modifier_buttons
                        )
                        is_pressed = (
                            modifier_pressed
                            and action_button < button_count
                            and joystick.get_button(action_button)
                        )

                        if is_pressed and combo_id not in pressed_combos:
                            pressed_combos.add(combo_id)
                            send_media_key(media_key)
                        elif not is_pressed and combo_id in pressed_combos:
                            pressed_combos.remove(combo_id)

                    for label, modifier_buttons, hat_value, media_key in self.HAT_COMBOS:
                        combo_id = (joy_index, label)
                        modifier_pressed = any(
                            btn < button_count and joystick.get_button(btn)
                            for btn in modifier_buttons
                        )

                        # Xbox 風格：D-Pad 透過 hat 報告
                        is_hat_pressed = any(
                            joystick.get_hat(hat_index) == hat_value
                            for hat_index in range(hat_count)
                        )

                        # PS 風格：D-Pad 透過 button 報告（fallback）
                        # 僅在 hat_count == 0 時啟用，避免與 L3 索引 (11) 衝突
                        is_dpad_button_pressed = False
                        if hat_count == 0:
                            is_dpad_button_pressed = any(
                                btn < button_count and joystick.get_button(btn)
                                for btn in self.PS_DPAD_BUTTONS.get(hat_value, ())
                            )

                        is_pressed = (
                            modifier_pressed
                            and (is_hat_pressed or is_dpad_button_pressed)
                        )

                        if is_pressed and combo_id not in pressed_combos:
                            pressed_combos.add(combo_id)
                            send_media_key(media_key)
                        elif not is_pressed and combo_id in pressed_combos:
                            pressed_combos.remove(combo_id)

                if pressed_this_tick != last_pressed_inputs:
                    self.output.put(("gamepad_inputs", list(pressed_this_tick)))
                    last_pressed_inputs = pressed_this_tick

                time.sleep(0.04)
        except Exception as exc:
            self.output.put(("gamepad_status", f"手把控制發生錯誤：{exc}"))
        finally:
            try:
                pygame.quit()
            except Exception as exc:
                self.output.put(("gamepad_status", f"手把控制關閉時發生錯誤：{exc}"))


def rounded_rectangle_points(x1: int, y1: int, x2: int, y2: int, radius: int) -> list[int]:
    points: list[int] = []
    for x, y in [
        (x1 + radius, y1),
        (x2 - radius, y1),
        (x2, y1),
        (x2, y1 + radius),
        (x2, y2 - radius),
        (x2, y2),
        (x2 - radius, y2),
        (x1 + radius, y2),
        (x1, y2),
        (x1, y2 - radius),
        (x1, y1 + radius),
        (x1, y1),
    ]:
        points.extend([x, y])
    return points


def ellipsize(text: str, limit: int) -> str:
    text = " ".join((text or "").split())
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 1)].rstrip() + "…"


def format_time(seconds: float) -> str:
    seconds = max(0, int(seconds))
    minutes, remaining_seconds = divmod(seconds, 60)
    hours, remaining_minutes = divmod(minutes, 60)

    if hours:
        return f"{hours}:{remaining_minutes:02d}:{remaining_seconds:02d}"

    return f"{remaining_minutes}:{remaining_seconds:02d}"


def get_track_source_theme(track: TrackInfo, preferred_service: str | None = None) -> tuple[str, str, str]:
    app_id = (track.app_id or "").lower()
    title_lower = (track.title or "").lower()
    album_lower = (track.album or "").lower()
    artist_lower = (track.artist or "").lower()

    # 1. Native application matching
    if "spotify" in app_id:
        return "spotify", "SPOTIFY", MUSIC_SERVICES["spotify"]["accent"]

    if "apple" in app_id:
        return "apple", "APPLE MUSIC", MUSIC_SERVICES["apple"]["accent"]

    if "youtube" in app_id:
        return "youtube", "YOUTUBE MUSIC", MUSIC_SERVICES["youtube"]["accent"]

    # 2. Browser session auto-detection (Chrome, Edge, Firefox, Brave, Opera, etc.)
    is_browser = any(b in app_id for b in ("chrome", "edge", "firefox", "opera", "brave", "vivaldi", "browser"))
    if is_browser:
        # YouTube / YouTube Music heuristics
        if (
            "youtube" in title_lower
            or "youtube" in album_lower
            or "youtube" in artist_lower
        ):
            return "youtube", "YOUTUBE MUSIC", MUSIC_SERVICES["youtube"]["accent"]

        # Spotify heuristics
        if (
            "spotify" in title_lower
            or "spotify" in album_lower
            or "spotify" in artist_lower
        ):
            return "spotify", "SPOTIFY", MUSIC_SERVICES["spotify"]["accent"]

        # Apple Music heuristics
        if (
            "apple" in title_lower
            or "apple" in album_lower
            or "apple" in artist_lower
        ):
            return "apple", "APPLE MUSIC", MUSIC_SERVICES["apple"]["accent"]

        # Fallback to manually selected preferred service if browser media matches no keywords
        service_key = normalize_music_service(preferred_service)
        config = MUSIC_SERVICES[service_key]
        return service_key, config["overlay"], config["accent"]

    if track.app_id:
        return "windows", track.app_id.upper(), "#5eead4"

    service_key = normalize_music_service(preferred_service)
    config = MUSIC_SERVICES[service_key]
    return service_key, config["overlay"], config["accent"]


def artwork_data_url(artwork_bytes: bytes | None) -> str | None:
    if not artwork_bytes:
        return None

    if artwork_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        mime_type = "image/png"
    elif artwork_bytes.startswith(b"\xff\xd8"):
        mime_type = "image/jpeg"
    elif artwork_bytes.startswith(b"RIFF") and b"WEBP" in artwork_bytes[:16]:
        mime_type = "image/webp"
    else:
        mime_type = "image/jpeg"

    encoded = base64.b64encode(artwork_bytes).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def track_to_payload(track: TrackInfo, preferred_service: str | None = None) -> dict:
    service_key, source_label, accent = get_track_source_theme(track, preferred_service)
    position = track.position_seconds
    if track.duration_seconds > 0 and track.status.upper() == "PLAYING" and track.timeline_updated_at > 0:
        elapsed = max(0.0, time.time() - track.timeline_updated_at)
        position += elapsed * max(0.0, track.playback_rate)

    if track.duration_seconds > 0:
        position = min(max(position, 0.0), track.duration_seconds)
    else:
        position = 0.0

    return {
        "title": track.title,
        "artist": track.artist,
        "album": track.album,
        "appId": track.app_id,
        "status": track.status,
        "error": track.error,
        "isEmpty": track.is_empty,
        "positionSeconds": round(position, 3),
        "durationSeconds": round(track.duration_seconds, 3),
        "timelineUpdatedAt": round(track.timeline_updated_at, 3),
        "playbackRate": track.playback_rate,
        "sourceLabel": source_label,
        "service": service_key,
        "accent": accent,
        "artworkKey": get_artwork_key(track),
        "artworkDataUrl": artwork_data_url(track.artwork_bytes),
    }


def load_settings() -> dict:
    settings = DEFAULT_SETTINGS.copy()
    if not SETTINGS_PATH.exists():
        return settings

    try:
        loaded = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
    except Exception:
        return settings

    for key, value in loaded.items():
        if key in settings:
            settings[key] = value

    return settings


def save_settings(settings: dict) -> None:
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    SETTINGS_PATH.write_text(
        json.dumps(settings, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def normalize_music_service(value: str | None) -> str:
    if value in MUSIC_SERVICES:
        return str(value)

    return "youtube"



def looks_like_supported_music(track: TrackInfo) -> bool:
    if track.error or track.is_empty:
        return False

    app_id = (track.app_id or "").lower()
    spotify_source = "spotify" in app_id
    apple_source = "apple" in app_id
    browser_source = any(source in app_id for source in ("chrome", "edge", "firefox", "opera", "brave", "vivaldi", "browser", "youtube", "apple"))
    has_media_metadata = bool(track.title and (track.artist or track.duration_seconds > 0))
    return (spotify_source or apple_source or browser_source) and has_media_metadata

class OverlayUI:
    WIDTH = 450
    HEIGHT = 120

    def __init__(self, root: tk.Tk, output: queue.Queue, overlay_only: bool = False):
        if PIL_IMPORT_ERROR is not None:
            raise RuntimeError(f"Pillow is required: {PIL_IMPORT_ERROR}")

        self.root = root
        self.output = output
        self.overlay_only = overlay_only
        self.stop_event = threading.Event()
        self.settings = load_settings()
        self.current_track = TrackInfo()
        self.overlay_visible = True
        self.position_mode = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.last_artwork: bytes | None = None
        self.art_photo = self.make_placeholder_art()
        self.worker_thread: threading.Thread | None = None
        self.hotkey_thread: HotkeyThread | None = None
        self.gamepad_thread: GamepadThread | None = None
        self.setup_window: tk.Toplevel | None = None
        self.setup_status_var: tk.StringVar | None = None
        self.service_text: tk.StringVar | None = None
        self.service_status_label: tk.Label | None = None

        self.configure_root()
        self.build_control_panel()
        self.build_overlay()
        self.start_threads()
        self.root.after(150, self.process_queue)
        self.root.after(250, self.tick_progress)
        self.root.after(600, self.enforce_music_setup)

        if overlay_only:
            self.root.withdraw()

    def configure_root(self) -> None:
        self.root.title(f"{APP_TITLE} {APP_VERSION}")
        self.root.geometry("640x720")
        self.root.minsize(560, 620)
        self.root.protocol("WM_DELETE_WINDOW", self.quit)
        self.root.configure(bg="#0b0d10")

    def build_control_panel(self) -> None:
        header_font = ("Microsoft JhengHei UI", 22, "bold")
        section_font = ("Microsoft JhengHei UI", 11, "bold")
        body_font = ("Microsoft JhengHei UI", 10)
        button_font = ("Microsoft JhengHei UI", 10, "bold")
        page_bg = "#0d0d0f"
        panel_bg = "#171719"
        inner_bg = "#222226"
        border = "#303036"
        text = "#f8fafc"
        muted = "#a7a7ad"

        outer = tk.Frame(self.root, bg=page_bg)
        outer.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(outer, orient="vertical", width=14)
        scrollbar.pack(side="right", fill="y")

        self.control_canvas = tk.Canvas(
            outer,
            bg=page_bg,
            bd=0,
            highlightthickness=0,
            yscrollcommand=scrollbar.set,
        )
        self.control_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.configure(command=self.control_canvas.yview)

        wrapper = tk.Frame(self.control_canvas, bg=page_bg, padx=22, pady=20)
        wrapper_window = self.control_canvas.create_window((0, 0), window=wrapper, anchor="nw")

        def update_scroll_region(_event=None) -> None:
            self.control_canvas.configure(scrollregion=self.control_canvas.bbox("all"))

        def resize_scroll_content(event) -> None:
            self.control_canvas.itemconfigure(wrapper_window, width=event.width)

        def on_mousewheel(event) -> None:
            delta = -1 if event.delta > 0 else 1
            self.control_canvas.yview_scroll(delta * 3, "units")

        wrapper.bind("<Configure>", update_scroll_region)
        self.control_canvas.bind("<Configure>", resize_scroll_content)
        self.root.bind_all("<MouseWheel>", on_mousewheel)

        def make_section(title: str, accent: str = "#3f3f46") -> tk.Frame:
            section = tk.Frame(
                wrapper,
                bg=panel_bg,
                highlightbackground=border,
                highlightthickness=1,
            )
            section.pack(fill="x", pady=(0, 14))

            tk.Frame(section, bg=accent, height=3).pack(fill="x")

            body = tk.Frame(section, bg=panel_bg, padx=16, pady=14)
            body.pack(fill="x")

            tk.Label(
                body,
                text=title,
                font=section_font,
                fg=text,
                bg=panel_bg,
                anchor="w",
            ).pack(fill="x", pady=(0, 12))
            return body

        def make_button(
            parent: tk.Misc,
            label: str,
            command,
            bg: str = "#242a35",
            fg: str = text,
            active_bg: str = "#323a48",
            height: int = 2,
        ) -> tk.Button:
            return tk.Button(
                parent,
                text=label,
                command=command,
                font=button_font,
                bg=bg,
                fg=fg,
                activebackground=active_bg,
                activeforeground=fg,
                relief="flat",
                bd=0,
                padx=12,
                pady=8,
                height=height,
                width=1,
                cursor="hand2",
            )

        header = tk.Frame(wrapper, bg=page_bg)
        header.pack(fill="x", pady=(0, 16))

        title_row = tk.Frame(header, bg=page_bg)
        title_row.pack(fill="x")

        tk.Label(
            title_row,
            text=APP_TITLE,
            font=header_font,
            fg=text,
            bg=page_bg,
            anchor="w",
        ).pack(side="left", fill="x", expand=True)

        tk.Label(
            title_row,
            text=f"v{APP_VERSION}",
            font=("Segoe UI", 9, "bold"),
            fg="#cbd5e1",
            bg="#1f2937",
            padx=10,
            pady=4,
        ).pack(side="right", padx=(12, 0))

        guide = tk.Frame(header, bg="#151515", highlightbackground="#292929", highlightthickness=1)
        guide.pack(fill="x", pady=(10, 0))
        tk.Label(
            guide,
            text=f"先開啟並播放 {SUPPORTED_MUSIC_LABEL}，再進 Forza。懸浮播放器只讀取 Windows 目前媒體資訊，不會切換視窗。",
            font=body_font,
            fg=muted,
            bg="#151515",
            anchor="w",
            justify="left",
            wraplength=540,
            padx=14,
            pady=10,
        ).pack(fill="x")

        service_section = make_section("1. 選擇音樂來源", "#ff2d55")
        tk.Label(
            service_section,
            text="按哪個服務，就會開啟對應網站，並自動套用紅色、綠色或黑色主題。",
            font=body_font,
            fg=muted,
            bg=panel_bg,
            anchor="w",
            justify="left",
            wraplength=520,
        ).pack(fill="x", pady=(0, 10))

        service_buttons = tk.Frame(service_section, bg=panel_bg)
        service_buttons.pack(fill="x")
        make_button(
            service_buttons,
            "開啟 YouTube Music",
            self.open_youtube_music,
            bg="#ff0033",
            fg="#ffffff",
            active_bg="#d6002b",
            height=2,
        ).grid(row=0, column=0, sticky="nsew", padx=(0, 7), ipady=2)
        make_button(
            service_buttons,
            "開啟 Spotify",
            self.open_spotify,
            bg="#1ed760",
            fg="#07110b",
            active_bg="#19b957",
            height=2,
        ).grid(row=0, column=1, sticky="nsew", padx=7, ipady=2)
        make_button(
            service_buttons,
            "開啟 Apple Music",
            self.open_apple_music,
            bg="#111111",
            fg="#ffffff",
            active_bg="#2a2a2a",
            height=2,
        ).grid(row=0, column=2, sticky="nsew", padx=(7, 0), ipady=2)
        service_buttons.columnconfigure(0, weight=1, uniform="service")
        service_buttons.columnconfigure(1, weight=1, uniform="service")
        service_buttons.columnconfigure(2, weight=1, uniform="service")
        service_buttons.rowconfigure(0, weight=1)

        self.service_text = tk.StringVar(value=self.get_music_service_status())
        self.service_status_label = tk.Label(
            service_section,
            textvariable=self.service_text,
            font=("Microsoft JhengHei UI", 9, "bold"),
            fg=self.get_music_service_theme()[1],
            bg=inner_bg,
            padx=14,
            pady=10,
            justify="left",
            anchor="w",
        )
        self.service_status_label.pack(fill="x", pady=(12, 0))

        now_section = make_section("2. 目前播放", "#1ed760")
        self.status_text = tk.StringVar(value="正在等待媒體資訊…")
        status = tk.Label(
            now_section,
            textvariable=self.status_text,
            font=("Microsoft JhengHei UI", 10, "bold"),
            fg=text,
            bg=inner_bg,
            padx=14,
            pady=14,
            justify="left",
            anchor="w",
            wraplength=520,
        )
        status.pack(fill="x")

        self.gamepad_text = tk.StringVar(value="手把控制：正在偵測控制器…")
        gamepad_status = tk.Label(
            now_section,
            textvariable=self.gamepad_text,
            font=("Microsoft JhengHei UI", 9, "bold"),
            fg="#1ed760",
            bg="#111f17",
            padx=14,
            pady=9,
            justify="left",
            anchor="w",
        )
        gamepad_status.pack(fill="x", pady=(10, 0))

        control_section = make_section("3. 懸浮播放器控制", "#60a5fa")
        actions = tk.Frame(control_section, bg=panel_bg)
        actions.pack(fill="x")

        buttons = [
            ("最小化控制台", self.hide_control_panel),
            ("顯示 / 隱藏懸浮播放器", self.toggle_overlay),
            ("調整顯示位置", self.toggle_position_mode),
            ("儲存目前位置", self.save_overlay_position),
            ("退出程式", self.quit),
        ]

        for index, (label, command) in enumerate(buttons):
            is_quit = label == "退出程式"
            button = make_button(
                actions,
                label,
                command,
                bg="#3a1f25" if is_quit else "#242a35",
                fg="#fecdd3" if is_quit else text,
                active_bg="#4c2630" if is_quit else "#323a48",
                height=2,
            )
            if is_quit:
                button.grid(row=index // 2, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
            else:
                button.grid(row=index // 2, column=index % 2, sticky="ew", padx=5, pady=5)

        actions.columnconfigure(0, weight=1, uniform="actions")
        actions.columnconfigure(1, weight=1, uniform="actions")

        hotkey_section = make_section("遊戲中快捷鍵", "#a78bfa")
        hotkeys = (
            "Ctrl+Alt+Space    播放 / 暫停\n"
            "Ctrl+Alt+Right    下一首\n"
            "Ctrl+Alt+Left     上一首\n"
            "Ctrl+Alt+Up       音量加\n"
            "Ctrl+Alt+Down     音量減\n"
            "Ctrl+Alt+End      靜音\n"
            "Ctrl+Alt+Home     顯示 / 隱藏懸浮播放器\n"
            "Ctrl+Alt+H        顯示 / 隱藏控制台\n"
            "Ctrl+Alt+P        調整懸浮播放器位置\n"
            "Ctrl+Alt+Q        退出程式\n\n"
            "手把組合鍵（L3 = 左搖桿按下）\n"
            "L3 + A            播放 / 暫停\n"
            "L3 + B            下一首\n"
            "L3 + X            上一首\n"
            "L3 + 上鍵         音量加\n"
            "L3 + 下鍵         音量減"
        )
        tk.Label(
            hotkey_section,
            text=hotkeys,
            font=("Consolas", 10),
            fg="#dbeafe",
            bg=inner_bg,
            padx=12,
            pady=12,
            justify="left",
            anchor="w",
        ).pack(fill="x")

        tk.Label(
            wrapper,
            text="如果 Forza 使用獨佔全螢幕，懸浮播放器可能無法覆蓋；建議使用無邊框視窗。若 Forza 用系統管理員啟動，本程式也要用系統管理員啟動。",
            font=("Microsoft JhengHei UI", 9),
            fg=muted,
            bg=page_bg,
            wraplength=540,
            justify="left",
            pady=12,
        ).pack(fill="x")

    def build_overlay(self) -> None:
        self.overlay = tk.Toplevel(self.root)
        self.overlay.overrideredirect(True)
        x = int(self.settings.get("overlay_x", DEFAULT_SETTINGS["overlay_x"]))
        y = int(self.settings.get("overlay_y", DEFAULT_SETTINGS["overlay_y"]))
        self.overlay.geometry(f"{self.WIDTH}x{self.HEIGHT}+{x}+{y}")
        self.overlay.attributes("-topmost", True)
        self.overlay.configure(bg="#121212")

        self.overlay_card = tk.Frame(
            self.overlay,
            bg="#121212",
            highlightbackground="#2a2a2a",
            highlightthickness=1,
            padx=14,
            pady=12,
        )
        self.overlay_card.pack(fill="both", expand=True)

        self.art_label = tk.Label(
            self.overlay_card,
            image=self.art_photo,
            bg="#121212",
            width=72,
            height=72,
        )
        self.art_label.grid(row=0, column=0, rowspan=3, sticky="nw", padx=(0, 13))

        top_row = tk.Frame(self.overlay_card, bg="#121212")
        top_row.grid(row=0, column=1, sticky="ew")

        self.source_dot = tk.Label(
            top_row,
            text="●",
            fg="#ff0033",
            bg="#121212",
            font=("Segoe UI", 9, "bold"),
        )
        self.source_dot.pack(side="left")

        self.source_var = tk.StringVar(value="MUSIC")
        self.source_label = tk.Label(
            top_row,
            textvariable=self.source_var,
            fg="#ff0033",
            bg="#121212",
            font=("Segoe UI", 8, "bold"),
        )
        self.source_label.pack(side="left", padx=(5, 0))

        self.status_var = tk.StringVar(value="READY")
        self.overlay_status = tk.Label(
            top_row,
            textvariable=self.status_var,
            fg="#b3b3b3",
            bg="#121212",
            font=("Segoe UI", 8, "bold"),
        )
        self.overlay_status.pack(side="right")

        self.title_var = tk.StringVar(value="等待音樂播放…")
        self.title_label = tk.Label(
            self.overlay_card,
            textvariable=self.title_var,
            fg="#ffffff",
            bg="#121212",
            font=("Microsoft JhengHei UI", 13, "bold"),
            anchor="w",
        )
        self.title_label.grid(row=1, column=1, sticky="ew", pady=(7, 0))

        self.artist_var = tk.StringVar(value="請先在瀏覽器播放音樂")
        self.artist_label = tk.Label(
            self.overlay_card,
            textvariable=self.artist_var,
            fg="#b3b3b3",
            bg="#121212",
            font=("Microsoft JhengHei UI", 10),
            anchor="w",
        )
        self.artist_label.grid(row=2, column=1, sticky="ew", pady=(3, 0))

        self.progress_track = tk.Frame(self.overlay_card, bg="#333333", height=4)
        self.progress_track.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(11, 0))
        self.progress_track.grid_propagate(False)
        self.progress_bar = tk.Frame(self.progress_track, bg="#ff0033", width=0, height=4)
        self.progress_bar.place(x=0, y=0, relheight=1)

        self.overlay_card.columnconfigure(1, weight=1)
        self.bind_overlay_drag()
        apply_overlay_window_style(self.overlay)

    def bind_overlay_drag(self) -> None:
        for widget in (
            self.overlay,
            self.overlay_card,
            self.art_label,
            self.source_dot,
            self.source_label,
            self.overlay_status,
            self.title_label,
            self.artist_label,
            self.progress_track,
            self.progress_bar,
        ):
            widget.bind("<ButtonPress-1>", self.start_overlay_drag)
            widget.bind("<B1-Motion>", self.drag_overlay)
            widget.bind("<ButtonRelease-1>", self.finish_overlay_drag)

    def make_placeholder_art(self) -> ImageTk.PhotoImage:
        image = Image.new("RGBA", (72, 72), "#1f1f1f")
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle((0, 0, 71, 71), radius=12, fill="#1f1f1f", outline="#ff0033", width=2)
        draw.ellipse((23, 18, 48, 43), fill="#ff0033")
        draw.rectangle((38, 33, 45, 55), fill="#ff0033")
        return ImageTk.PhotoImage(image)

    def artwork_to_photo(self, data: bytes | None) -> ImageTk.PhotoImage:
        if not data:
            return self.make_placeholder_art()

        try:
            image = Image.open(io.BytesIO(data)).convert("RGBA")
            image.thumbnail((72, 72), Image.LANCZOS)
            square = Image.new("RGBA", (72, 72), "#1f1f1f")
            x = (72 - image.width) // 2
            y = (72 - image.height) // 2
            square.alpha_composite(image, (x, y))

            mask = Image.new("L", (72, 72), 0)
            draw = ImageDraw.Draw(mask)
            draw.rounded_rectangle((0, 0, 71, 71), radius=12, fill=255)
            square.putalpha(mask)
            return ImageTk.PhotoImage(square)
        except Exception:
            return self.make_placeholder_art()

    def start_threads(self) -> None:
        self.worker_thread = threading.Thread(target=self.run_media_worker, daemon=True)
        self.worker_thread.start()
        self.hotkey_thread = HotkeyThread(self.output, self.stop_event)
        self.hotkey_thread.start()
        self.gamepad_thread = GamepadThread(self.output, self.stop_event)
        self.gamepad_thread.start()

    def run_media_worker(self) -> None:
        asyncio.run(media_poll_loop(self.output, self.stop_event))

    def get_music_service(self) -> str:
        return normalize_music_service(str(self.settings.get("music_service", "youtube")))

    def get_music_service_theme(self) -> tuple[str, str, str]:
        service = self.get_music_service()
        config = MUSIC_SERVICES[service]
        return config["overlay"], config["accent"], config["display"]

    def get_music_service_status(self) -> str:
        _overlay, _accent, display = self.get_music_service_theme()
        return f"目前瀏覽器來源：{display} 主題（按上方服務按鈕可切換）"

    def set_music_service(self, service: str) -> None:
        self.settings["music_service"] = normalize_music_service(service)
        save_settings(self.settings)

        if self.service_text is not None:
            self.service_text.set(self.get_music_service_status())
        if self.service_status_label is not None:
            self.service_status_label.configure(fg=self.get_music_service_theme()[1])
        self.update_track(self.current_track)

    def check_music_ready(self) -> tuple[bool, str]:
        try:
            track = asyncio.run(get_current_track(read_artwork=False))
        except Exception as exc:
            return False, f"無法讀取 Windows 媒體資訊：{exc}"

        if looks_like_supported_music(track):
            return True, f"已偵測到：{track.title} - {track.artist or track.app_id}"

        if track.status == "NO_SESSION" or track.is_empty:
            return False, f"尚未偵測到 {SUPPORTED_MUSIC_LABEL} 播放。請登入後播放任一首歌曲。"

        return False, (
            f"目前偵測到其他媒體來源，請切到 {SUPPORTED_MUSIC_LABEL} 並開始播放。\n"
            f"偵測結果：{track.app_id or '未知來源'} / {track.title or '無標題'}"
        )

    def enforce_music_setup(self) -> None:
        ready, message = self.check_music_ready()
        if ready:
            return
        self.show_setup_window(message)

    def show_setup_window(self, message: str) -> None:
        if self.setup_window is not None and self.setup_window.winfo_exists():
            self.setup_status_var.set(message)
            self.setup_window.lift()
            return

        self.overlay.withdraw()
        self.overlay_visible = False

        setup = tk.Toplevel(self.root)
        self.setup_window = setup
        setup.title(f"設定 {APP_TITLE}")
        setup.geometry("580x440")
        setup.resizable(False, False)
        setup.configure(bg="#121212")
        setup.transient(self.root)
        setup.grab_set()
        setup.protocol("WM_DELETE_WINDOW", lambda: None)

        content = tk.Frame(setup, bg="#121212", padx=24, pady=24)
        content.pack(fill="both", expand=True)

        tk.Label(
            content,
            text="先選擇音樂服務",
            font=("Microsoft JhengHei UI", 18, "bold"),
            fg="#ffffff",
            bg="#121212",
            anchor="w",
        ).pack(fill="x")

        tk.Label(
            content,
            text=(
                "這個工具不會要求你輸入帳號密碼。\n"
                "請在官方音樂服務登入，播放任一首歌曲後，再回來按重新檢查。"
            ),
            font=("Microsoft JhengHei UI", 10),
            fg="#b3b3b3",
            bg="#121212",
            justify="left",
            anchor="w",
            pady=12,
        ).pack(fill="x")

        self.setup_status_var = tk.StringVar(value=message)
        tk.Label(
            content,
            textvariable=self.setup_status_var,
            font=("Microsoft JhengHei UI", 10, "bold"),
            fg="#ffffff",
            bg="#242424",
            padx=14,
            pady=14,
            justify="left",
            anchor="w",
            wraplength=440,
        ).pack(fill="x", pady=(0, 16))

        steps = (
            "1. 按下「開啟 YouTube Music」或「開啟 Spotify」。\n"
            "2. 在瀏覽器或 Spotify 桌面版登入。\n"
            "3. 播放任一首歌曲，讓播放器開始跑。\n"
            "4. 回到這裡按「我已登入並播放，重新檢查」。"
        )
        tk.Label(
            content,
            text=steps,
            font=("Microsoft JhengHei UI", 10),
            fg="#e5e7eb",
            bg="#181818",
            padx=14,
            pady=14,
            justify="left",
            anchor="w",
        ).pack(fill="x")

        actions = tk.Frame(content, bg="#121212")
        actions.pack(fill="x", pady=(18, 0))

        tk.Button(
            actions,
            text="開啟 YouTube Music",
            command=self.open_youtube_music,
            font=("Microsoft JhengHei UI", 10, "bold"),
            bg="#ff0033",
            fg="#ffffff",
            activebackground="#d6002b",
            activeforeground="#ffffff",
            relief="flat",
            padx=12,
            pady=10,
        ).pack(side="left", fill="x", expand=True, padx=(0, 8))

        tk.Button(
            actions,
            text="開啟 Spotify",
            command=self.open_spotify,
            font=("Microsoft JhengHei UI", 10, "bold"),
            bg="#1ed760",
            fg="#101010",
            activebackground="#19b957",
            activeforeground="#101010",
            relief="flat",
            padx=12,
            pady=10,
        ).pack(side="left", fill="x", expand=True, padx=(0, 8))

        tk.Button(
            actions,
            text="開啟 Apple Music",
            command=self.open_apple_music,
            font=("Microsoft JhengHei UI", 10, "bold"),
            bg="#111111",
            fg="#ffffff",
            activebackground="#2a2a2a",
            activeforeground="#ffffff",
            relief="flat",
            padx=12,
            pady=10,
        ).pack(side="left", fill="x", expand=True)

        tk.Button(
            content,
            text="我已登入並播放，重新檢查",
            command=self.recheck_music_setup,
            font=("Microsoft JhengHei UI", 10, "bold"),
            bg="#242424",
            fg="#ffffff",
            activebackground="#3a3a3a",
            activeforeground="#ffffff",
            relief="flat",
            padx=12,
            pady=10,
        ).pack(fill="x", pady=(12, 0))

        tk.Button(
            content,
            text="退出程式",
            command=self.quit,
            font=("Microsoft JhengHei UI", 9, "bold"),
            bg="#121212",
            fg="#b3b3b3",
            activebackground="#242424",
            activeforeground="#ffffff",
            relief="flat",
            pady=8,
        ).pack(fill="x", pady=(12, 0))

    def recheck_music_setup(self) -> None:
        ready, message = self.check_music_ready()
        if not ready:
            self.setup_status_var.set(message)
            return

        self.setup_status_var.set(message)
        if self.setup_window is not None and self.setup_window.winfo_exists():
            self.setup_window.grab_release()
            self.setup_window.destroy()

        self.overlay_visible = True
        self.overlay.deiconify()
        apply_overlay_window_style(self.overlay)

    def process_queue(self) -> None:
        try:
            while True:
                kind, payload = self.output.get_nowait()
                if kind == "track":
                    self.update_track(payload)
                elif kind == "command":
                    self.handle_command(payload)
                elif kind == "hotkey_error":
                    self.status_text.set(f"快捷鍵註冊失敗：{payload}")
                elif kind == "gamepad_status":
                    self.gamepad_text.set(payload)
                elif kind == "gamepad_inputs":
                    pass
        except queue.Empty:
            pass

        self.root.after(150, self.process_queue)

    def get_source_theme(self, track: TrackInfo) -> tuple[str, str]:
        app_id = (track.app_id or "").lower()

        if "spotify" in app_id:
            return "SPOTIFY", "#1ed760"

        if "apple" in app_id:
            return "APPLE MUSIC", "#111111"

        if "youtube" in app_id:
            return "YOUTUBE MUSIC", "#ff0033"

        if "chrome" in app_id or "edge" in app_id:
            label, accent, _display = self.get_music_service_theme()
            return label, accent

        if track.app_id:
            return track.app_id.upper(), "#5eead4"

        return "WINDOWS MEDIA", "#5eead4"

    def get_display_position(self, track: TrackInfo) -> float:
        if track.duration_seconds <= 0:
            return 0.0

        position = track.position_seconds
        if track.status.upper() == "PLAYING" and track.timeline_updated_at > 0:
            elapsed = max(0.0, time.time() - track.timeline_updated_at)
            position += elapsed * max(0.0, track.playback_rate)

        return min(max(position, 0.0), track.duration_seconds)

    def update_progress_bar(self) -> None:
        track = self.current_track
        duration = track.duration_seconds
        position = self.get_display_position(track)
        width = max(0, self.progress_track.winfo_width())

        if duration > 0 and width > 0:
            ratio = min(max(position / duration, 0.0), 1.0)
            self.progress_bar.place_configure(width=max(2, int(width * ratio)))
            self.status_var.set(f"{format_time(position)} / {format_time(duration)}")
        else:
            self.progress_bar.place_configure(width=0)
            if track.status:
                self.status_var.set(track.status.replace("_", " "))

    def tick_progress(self) -> None:
        if not self.position_mode:
            self.update_progress_bar()
        if self.root.winfo_exists():
            self.root.after(250, self.tick_progress)

    def update_track(self, track: TrackInfo) -> None:
        self.current_track = track
        source_name, accent = self.get_source_theme(track)

        if track.error:
            title = "讀取媒體資訊失敗"
            artist = track.error
            status = "ERROR"
        elif track.is_empty:
            title = "等待音樂播放…"
            artist = f"請先登入並播放 {SUPPORTED_MUSIC_LABEL}"
            status = "NO MEDIA"
        else:
            title = track.title or "未知歌曲"
            artist = track.artist or track.album or track.app_id or "未知來源"
            status = track.status.replace("_", " ")

        self.source_dot.configure(fg=accent)
        self.source_label.configure(fg=accent)
        self.progress_bar.configure(bg=accent)

        if not self.position_mode:
            self.source_var.set(source_name)
            self.title_var.set(ellipsize(title, 38))
            self.artist_var.set(ellipsize(artist, 46))
            self.update_progress_bar()

        if track.artwork_bytes is not None and track.artwork_bytes != self.last_artwork:
            self.last_artwork = track.artwork_bytes
            self.art_photo = self.artwork_to_photo(track.artwork_bytes)
            self.art_label.configure(image=self.art_photo)
        elif (track.error or track.is_empty) and self.last_artwork is not None:
            self.last_artwork = None
            self.art_photo = self.artwork_to_photo(None)
            self.art_label.configure(image=self.art_photo)

        app = track.app_id or "Windows media session"
        position = self.get_display_position(track)
        timeline = (
            f"{format_time(position)} / {format_time(track.duration_seconds)}"
            if track.duration_seconds > 0
            else "無時間資料"
        )
        self.status_text.set(
            f"目前播放：{title}\n"
            f"演出者：{artist}\n"
            f"來源：{app}    狀態：{status}    進度：{timeline}"
        )

    def handle_command(self, command: str) -> None:
        if command == "toggle_overlay":
            self.toggle_overlay()
        elif command == "toggle_control":
            self.toggle_control_panel()
        elif command == "toggle_position_mode":
            self.toggle_position_mode()
        elif command == "quit":
            self.quit()

    def open_youtube_music(self) -> None:
        self.set_music_service("youtube")
        webbrowser.open(YOUTUBE_MUSIC_URL)

    def open_spotify(self) -> None:
        self.set_music_service("spotify")
        webbrowser.open(SPOTIFY_URL)

    def open_apple_music(self) -> None:
        self.set_music_service("apple")
        webbrowser.open(APPLE_MUSIC_URL)

    def toggle_overlay(self) -> None:
        self.overlay_visible = not self.overlay_visible
        if self.overlay_visible:
            self.overlay.deiconify()
            apply_overlay_window_style(self.overlay)
        else:
            self.overlay.withdraw()

    def set_position_mode(self, enabled: bool) -> None:
        self.position_mode = enabled
        if enabled:
            self.overlay_visible = True
            self.overlay.deiconify()
            self.overlay_card.configure(highlightbackground="#ff0033", highlightthickness=2)
            self.source_var.set("移動位置")
            self.status_var.set("拖曳後放開")
        else:
            self.overlay_card.configure(highlightbackground="#2a2a2a", highlightthickness=1)
            self.save_overlay_position(show_message=False)
            self.update_track(self.current_track)

    def toggle_position_mode(self) -> None:
        self.set_position_mode(not self.position_mode)

    def start_overlay_drag(self, event) -> None:
        if not self.position_mode:
            return
        self.drag_offset_x = event.x_root - self.overlay.winfo_x()
        self.drag_offset_y = event.y_root - self.overlay.winfo_y()

    def drag_overlay(self, event) -> None:
        if not self.position_mode:
            return
        x = max(0, event.x_root - self.drag_offset_x)
        y = max(0, event.y_root - self.drag_offset_y)
        self.overlay.geometry(f"{self.WIDTH}x{self.HEIGHT}+{x}+{y}")

    def finish_overlay_drag(self, _event=None) -> None:
        if self.position_mode:
            self.save_overlay_position(show_message=False)

    def save_overlay_position(self, show_message: bool = True) -> None:
        self.settings["overlay_x"] = int(self.overlay.winfo_x())
        self.settings["overlay_y"] = int(self.overlay.winfo_y())
        save_settings(self.settings)
        if show_message:
            messagebox.showinfo(APP_TITLE, "懸浮播放器位置已儲存。")

    def hide_control_panel(self) -> None:
        self.root.iconify()

    def toggle_control_panel(self) -> None:
        if self.root.state() in ("withdrawn", "iconic"):
            self.root.deiconify()
            self.root.lift()
            self.root.focus_force()
        else:
            self.root.iconify()

    def quit(self) -> None:
        self.save_overlay_position(show_message=False)
        self.stop_event.set()
        if self.hotkey_thread is not None:
            self.hotkey_thread.stop()
        if self.setup_window is not None and self.setup_window.winfo_exists():
            try:
                self.setup_window.grab_release()
            except tk.TclError as exc:
                self.status_text.set(f"關閉設定視窗時發生錯誤：{exc}")
            self.setup_window.destroy()
        self.root.after(100, self.root.destroy)


def emit_backend_event(payload: dict) -> None:
    print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), flush=True)


def read_backend_commands(command_queue: queue.Queue, stop_event: threading.Event) -> None:
    while not stop_event.is_set():
        line = sys.stdin.readline()
        if line == "":
            stop_event.set()
            break

        line = line.strip()
        if not line:
            continue

        try:
            command_queue.put(json.loads(line))
        except json.JSONDecodeError as exc:
            command_queue.put({"type": "protocol:error", "message": str(exc)})


def handle_backend_command(command: dict, stop_event: threading.Event) -> None:
    command_type = str(command.get("type", ""))

    media_keys = {
        "media:playPause": Win32.VK_MEDIA_PLAY_PAUSE,
        "media:next": Win32.VK_MEDIA_NEXT_TRACK,
        "media:previous": Win32.VK_MEDIA_PREV_TRACK,
        "media:volumeUp": Win32.VK_VOLUME_UP,
        "media:volumeDown": Win32.VK_VOLUME_DOWN,
        "media:mute": Win32.VK_VOLUME_MUTE,
    }

    if command_type in media_keys:
        send_media_key(media_keys[command_type])
    elif command_type == "open:youtube":
        settings = load_settings()
        settings["music_service"] = "youtube"
        save_settings(settings)
        webbrowser.open(YOUTUBE_MUSIC_URL)
    elif command_type == "open:spotify":
        settings = load_settings()
        settings["music_service"] = "spotify"
        save_settings(settings)
        webbrowser.open(SPOTIFY_URL)
    elif command_type == "open:apple":
        settings = load_settings()
        settings["music_service"] = "apple"
        save_settings(settings)
        webbrowser.open(APPLE_MUSIC_URL)
    elif command_type == "settings:setService":
        service = normalize_music_service(command.get("service"))
        settings = load_settings()
        settings["music_service"] = service
        save_settings(settings)
    elif command_type == "app:quit":
        stop_event.set()
    elif command_type == "protocol:error":
        emit_backend_event({"type": "protocol:error", "message": command.get("message", "Invalid JSON")})


def run_stdio_backend() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
        sys.stderr.reconfigure(encoding="utf-8", line_buffering=True)
    except Exception:
        pass

    output: queue.Queue = queue.Queue()
    command_queue: queue.Queue = queue.Queue()
    stop_event = threading.Event()
    settings = load_settings()

    media_thread = threading.Thread(
        target=lambda: asyncio.run(media_poll_loop(output, stop_event)),
        daemon=True,
        name="media-poll",
    )
    hotkey_thread = HotkeyThread(output, stop_event)
    gamepad_thread = GamepadThread(output, stop_event)
    stdin_thread = threading.Thread(
        target=read_backend_commands,
        args=(command_queue, stop_event),
        daemon=True,
        name="backend-stdin",
    )

    media_thread.start()
    hotkey_thread.start()
    gamepad_thread.start()
    stdin_thread.start()

    emit_backend_event(
        {
            "type": "backend:ready",
            "version": APP_VERSION,
            "appTitle": APP_TITLE,
            "settings": settings,
            "services": MUSIC_SERVICES,
        }
    )

    try:
        while not stop_event.is_set():
            try:
                while True:
                    handle_backend_command(command_queue.get_nowait(), stop_event)
                    settings = load_settings()
            except queue.Empty:
                pass

            try:
                kind, payload = output.get(timeout=0.15)
            except queue.Empty:
                continue

            if kind == "track":
                emit_backend_event(
                    {
                        "type": "track:update",
                        "track": track_to_payload(payload, settings.get("music_service")),
                    }
                )
            elif kind == "command":
                emit_backend_event({"type": "command", "command": payload})
                if payload == "quit":
                    stop_event.set()
            elif kind == "hotkey_error":
                emit_backend_event({"type": "hotkey:error", "message": payload})
            elif kind == "gamepad_status":
                emit_backend_event({"type": "gamepad:status", "message": payload})
            elif kind == "gamepad_inputs":
                emit_backend_event({"type": "gamepad:inputs", "pressed": payload})
    finally:
        stop_event.set()
        hotkey_thread.stop()

    return 0


def run_check() -> int:
    missing: list[str] = []
    warnings: list[str] = []

    if PIL_IMPORT_ERROR is not None:
        missing.append(f"Pillow import failed: {PIL_IMPORT_ERROR}")

    try:
        import winsdk.windows.media.control  # noqa: F401
        import winsdk.windows.storage.streams  # noqa: F401
    except Exception as exc:
        missing.append(f"winsdk import failed: {exc}")

    try:
        import pygame  # noqa: F401
    except Exception as exc:
        warnings.append(f"pygame import failed: {exc}. Controller combos will be disabled until dependencies are installed.")

    if missing:
        for item in missing:
            print(item)
        return 1

    for warning in warnings:
        print(f"WARN: {warning}")

    print("OK: Python floating player dependencies are available.")
    return 0


def run_hotkey_check() -> int:
    modifiers = Win32.MOD_CONTROL | Win32.MOD_ALT | Win32.MOD_NOREPEAT
    registered: list[int] = []
    failures: list[str] = []

    for hotkey_id, (command, virtual_key, _media_key) in HotkeyThread.HOTKEYS.items():
        if Win32.user32.RegisterHotKey(None, hotkey_id, modifiers, virtual_key):
            registered.append(hotkey_id)
        else:
            failures.append(
                f"{HotkeyThread.LABELS.get(command, command)}: Windows error {ctypes.get_last_error()}"
            )

    for hotkey_id in registered:
        Win32.user32.UnregisterHotKey(None, hotkey_id)

    if failures:
        print("Hotkey registration failed:")
        for failure in failures:
            print(f"  {failure}")
        return 1

    print(f"OK: registered and released {len(registered)} hotkeys.")
    return 0


async def run_once() -> int:
    track = await get_current_track(read_artwork=False)
    payload = {
        "title": track.title,
        "artist": track.artist,
        "album": track.album,
        "app_id": track.app_id,
        "status": track.status,
        "position_seconds": round(track.position_seconds, 3),
        "duration_seconds": round(track.duration_seconds, 3),
        "playback_rate": track.playback_rate,
        "error": track.error,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=APP_TITLE)
    parser.add_argument("--check", action="store_true", help="check dependencies and exit")
    parser.add_argument("--hotkey-check", action="store_true", help="check global hotkey registration and exit")
    parser.add_argument("--once", action="store_true", help="print current media session metadata and exit")
    parser.add_argument("--stdio-backend", action="store_true", help="run JSON-lines backend for Electron")
    parser.add_argument("--overlay-only", action="store_true", help="start with the control panel hidden")
    parser.add_argument("--smoke-seconds", type=float, default=0.0, help="close automatically after N seconds")
    args = parser.parse_args()

    if args.check:
        return run_check()

    if args.hotkey_check:
        return run_hotkey_check()

    if args.once:
        return asyncio.run(run_once())

    if args.stdio_backend:
        return run_stdio_backend()

    if PIL_IMPORT_ERROR is not None:
        messagebox.showerror(APP_TITLE, f"Pillow is required.\n\n{PIL_IMPORT_ERROR}")
        return 1

    output: queue.Queue = queue.Queue()
    mutex_handle = acquire_single_instance_mutex()
    if mutex_handle is None:
        messagebox.showinfo(APP_TITLE, f"{APP_TITLE} 已經在執行。")
        return 0

    root = tk.Tk()
    try:
        ui = OverlayUI(root, output, overlay_only=args.overlay_only)
        if args.smoke_seconds > 0:
            root.after(int(args.smoke_seconds * 1000), ui.quit)
        root.mainloop()
    except Exception as exc:
        messagebox.showerror(APP_TITLE, str(exc))
        return 1
    finally:
        Win32.kernel32.CloseHandle(mutex_handle)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
