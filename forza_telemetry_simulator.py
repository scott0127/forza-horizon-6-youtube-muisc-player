"""Small Forza Horizon UDP telemetry simulator for visual-effect testing."""

from __future__ import annotations

import socket
import struct
import time
import tkinter as tk
from tkinter import ttk


UDP_HOST = "127.0.0.1"
UDP_PORT = 501
PACKET_SIZE = 324
SEND_INTERVAL_MS = 16
NEUTRAL_GEAR = 11


class TelemetrySimulator:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Forza UDP Telemetry Simulator")
        self.root.resizable(False, False)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.started_at = time.monotonic()

        self.sending = tk.BooleanVar(value=True)
        self.race_on = tk.BooleanVar(value=True)
        self.gear = tk.IntVar(value=1)
        self.speed_kph = tk.DoubleVar(value=72)
        self.rpm = tk.DoubleVar(value=4600)
        self.max_rpm = tk.DoubleVar(value=8000)
        self.status = tk.StringVar(value=f"Sending UDP telemetry to {UDP_HOST}:{UDP_PORT}")

        self._build_ui()
        self._refresh_labels()
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.after(SEND_INTERVAL_MS, self._send_loop)

    def _build_ui(self) -> None:
        frame = ttk.Frame(self.root, padding=18)
        frame.grid(sticky="nsew")

        ttk.Label(
            frame,
            text="Forza UDP Telemetry Simulator",
            font=("Segoe UI", 15, "bold"),
        ).grid(row=0, column=0, columnspan=3, sticky="w")
        ttk.Label(
            frame,
            text="Open GamingMusicOverlay first, then adjust values here to preview gear-shift effects.",
            foreground="#555555",
        ).grid(row=1, column=0, columnspan=3, sticky="w", pady=(2, 14))

        self.gear_label = self._add_slider(
            frame, 2, "Gear", self.gear, 0, NEUTRAL_GEAR, 1, self._refresh_labels
        )
        self.speed_label = self._add_slider(
            frame, 3, "Speed", self.speed_kph, 0, 420, 1, self._refresh_labels
        )
        self.rpm_label = self._add_slider(
            frame, 4, "RPM", self.rpm, 0, 10000, 50, self._refresh_labels
        )
        self.max_rpm_label = self._add_slider(
            frame, 5, "Max RPM", self.max_rpm, 3000, 12000, 50, self._refresh_labels
        )

        shift_row = ttk.Frame(frame)
        shift_row.grid(row=6, column=0, columnspan=3, sticky="ew", pady=(12, 6))
        ttk.Button(shift_row, text="Previous gear", command=lambda: self._shift(-1)).pack(
            side="left"
        )
        ttk.Button(shift_row, text="Next gear", command=lambda: self._shift(1)).pack(
            side="left", padx=8
        )
        ttk.Button(shift_row, text="Neutral", command=lambda: self.gear.set(NEUTRAL_GEAR)).pack(
            side="left"
        )

        option_row = ttk.Frame(frame)
        option_row.grid(row=7, column=0, columnspan=3, sticky="ew", pady=(4, 8))
        ttk.Checkbutton(option_row, text="Send UDP packets", variable=self.sending).pack(
            side="left"
        )
        ttk.Checkbutton(option_row, text="Race on", variable=self.race_on).pack(
            side="left", padx=14
        )

        ttk.Separator(frame).grid(row=8, column=0, columnspan=3, sticky="ew", pady=8)
        ttk.Label(frame, textvariable=self.status, foreground="#166534").grid(
            row=9, column=0, columnspan=3, sticky="w"
        )
        ttk.Label(
            frame,
            text="Tip: use the gear slider or buttons repeatedly to trigger the shift animation.",
            foreground="#555555",
        ).grid(row=10, column=0, columnspan=3, sticky="w", pady=(3, 0))

    def _add_slider(
        self,
        parent: ttk.Frame,
        row: int,
        title: str,
        variable: tk.Variable,
        minimum: float,
        maximum: float,
        resolution: float,
        command,
    ) -> ttk.Label:
        ttk.Label(parent, text=title, width=10).grid(row=row, column=0, sticky="w", pady=5)
        scale = tk.Scale(
            parent,
            from_=minimum,
            to=maximum,
            orient="horizontal",
            variable=variable,
            resolution=resolution,
            showvalue=False,
            length=360,
            command=command,
        )
        scale.grid(row=row, column=1, sticky="ew", padx=(0, 10), pady=5)
        value_label = ttk.Label(parent, width=14, anchor="e")
        value_label.grid(row=row, column=2, sticky="e")
        return value_label

    def _refresh_labels(self, _value: str | None = None) -> None:
        self.gear_label.configure(text=self._gear_label(self.gear.get()))
        self.speed_label.configure(text=f"{self.speed_kph.get():.0f} km/h")
        self.rpm_label.configure(text=f"{self.rpm.get():.0f} rpm")
        self.max_rpm_label.configure(text=f"{self.max_rpm.get():.0f} rpm")

    def _shift(self, amount: int) -> None:
        current = self.gear.get()
        if current == NEUTRAL_GEAR:
            next_gear = 1 if amount > 0 else 0
        else:
            next_gear = max(0, min(10, current + amount))
        self.gear.set(next_gear)
        self._refresh_labels()

    def _build_packet(self) -> bytes:
        packet = bytearray(PACKET_SIZE)
        speed_mps = self.speed_kph.get() / 3.6
        elapsed_ms = int((time.monotonic() - self.started_at) * 1000) & 0xFFFFFFFF

        struct.pack_into("<i", packet, 0, 1 if self.race_on.get() else 0)
        struct.pack_into("<I", packet, 4, elapsed_ms)
        struct.pack_into("<f", packet, 8, float(self.max_rpm.get()))
        struct.pack_into("<f", packet, 12, 850.0)
        struct.pack_into("<f", packet, 16, float(self.rpm.get()))
        struct.pack_into("<f", packet, 40, float(speed_mps))

        # Populate the Dash extension so the overlay reads an explicit gear value.
        struct.pack_into("<f", packet, 232, 1.0)
        struct.pack_into("<f", packet, 244, float(speed_mps))
        struct.pack_into("<B", packet, 307, int(self.gear.get()))
        struct.pack_into("<B", packet, 319, int(self.gear.get()))
        return bytes(packet)

    def _send_loop(self) -> None:
        if self.sending.get():
            try:
                self.sock.sendto(self._build_packet(), (UDP_HOST, UDP_PORT))
                self.status.set(
                    f"Sending: gear {self._gear_label(self.gear.get())}, "
                    f"{self.speed_kph.get():.0f} km/h, {self.rpm.get():.0f} rpm"
                )
            except OSError as error:
                self.status.set(f"UDP send failed: {error}")

        self.root.after(SEND_INTERVAL_MS, self._send_loop)

    def close(self) -> None:
        self.sock.close()
        self.root.destroy()

    @staticmethod
    def _gear_label(gear: int) -> str:
        if gear == 0:
            return "R"
        if gear == NEUTRAL_GEAR:
            return "N"
        return str(gear)


def main() -> None:
    root = tk.Tk()
    TelemetrySimulator(root)
    root.mainloop()


if __name__ == "__main__":
    main()

