"""
Battery Monitor Module
Handles battery status polling using psutil and emits signals on state changes.
"""

import psutil
from PyQt6.QtCore import QObject, QTimer, pyqtSignal


class BatteryMonitor(QObject):
    """Monitors battery percentage and charging state using psutil."""

    # Signals
    battery_updated = pyqtSignal(int, bool)  # percent, is_charging
    battery_not_found = pyqtSignal()         # emitted when no battery detected

    POLL_INTERVAL_MS = 30_000  # 30 seconds

    def __init__(self, parent=None):
        super().__init__(parent)
        self._timer = QTimer(self)
        self._timer.setInterval(self.POLL_INTERVAL_MS)
        self._timer.timeout.connect(self._poll)
        self._last_percent: int = -1
        self._last_plugged: bool | None = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def start(self) -> bool:
        """Start monitoring. Returns False if no battery is found."""
        battery = psutil.sensors_battery()
        if battery is None:
            self.battery_not_found.emit()
            return False
        self._emit(battery)
        self._timer.start()
        return True

    def stop(self):
        """Stop monitoring."""
        self._timer.stop()

    def poll_now(self) -> tuple[int, bool] | None:
        """Force an immediate poll and return (percent, plugged)."""
        battery = psutil.sensors_battery()
        if battery is None:
            return None
        self._emit(battery)
        return int(battery.percent), bool(battery.power_plugged)

    @property
    def last_percent(self) -> int:
        return self._last_percent

    @property
    def last_plugged(self) -> bool | None:
        return self._last_plugged

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------
    def _poll(self):
        battery = psutil.sensors_battery()
        if battery is None:
            self.battery_not_found.emit()
            self._timer.stop()
            return
        self._emit(battery)

    def _emit(self, battery):
        percent = int(battery.percent)
        plugged = bool(battery.power_plugged)
        self._last_percent = percent
        self._last_plugged = plugged
        self.battery_updated.emit(percent, plugged)
