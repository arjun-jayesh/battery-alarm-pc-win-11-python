"""
Alarm Manager Module
Handles alarm triggering, sound playback, snooze, and alarm state management.
"""

import os
import sys
from PyQt6.QtCore import QObject, QTimer, QUrl, pyqtSignal
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput


def _resource_path(relative: str) -> str:
    """Resolve path for both dev and PyInstaller bundled mode."""
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS  # type: ignore[attr-defined]
    else:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative)


class AlarmManager(QObject):
    """Manages alarm triggering, sound playback, and snooze logic."""

    alarm_triggered = pyqtSignal()   # emitted when alarm fires
    alarm_stopped = pyqtSignal()     # emitted when alarm is stopped/snoozed
    snooze_ended = pyqtSignal()      # emitted when snooze period ends

    SNOOZE_DURATION_MS = 5 * 60 * 1000  # 5 minutes

    def __init__(self, parent=None):
        super().__init__(parent)

        # Audio
        self._audio_output = QAudioOutput()
        self._audio_output.setVolume(0.8)
        self._player = QMediaPlayer(self)
        self._player.setAudioOutput(self._audio_output)

        sound_path = _resource_path(os.path.join("assets", "alarm.wav"))
        self._player.setSource(QUrl.fromLocalFile(sound_path))

        # Loop the alarm sound via mediaStatusChanged
        self._player.mediaStatusChanged.connect(self._on_media_status)

        # State
        self._is_ringing = False
        self._is_snoozed = False
        self._already_triggered = False  # prevent duplicate alarms

        # Snooze timer
        self._snooze_timer = QTimer(self)
        self._snooze_timer.setSingleShot(True)
        self._snooze_timer.timeout.connect(self._on_snooze_end)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    @property
    def is_ringing(self) -> bool:
        return self._is_ringing

    @property
    def is_snoozed(self) -> bool:
        return self._is_snoozed

    def check_and_trigger(self, percent: int, is_charging: bool,
                          target: int, alarm_enabled: bool) -> bool:
        """
        Evaluate whether the alarm should fire.
        Returns True if alarm was triggered.
        """
        if not alarm_enabled:
            return False

        if self._is_ringing or self._is_snoozed:
            return False

        should_fire = is_charging and percent >= target

        if should_fire and not self._already_triggered:
            self._trigger()
            return True

        # Reset the duplicate-prevention flag when battery drops below target
        # or charger is unplugged so alarm can fire again next time.
        if not should_fire:
            self._already_triggered = False

        return False

    def stop(self):
        """Stop the alarm sound and reset state."""
        self._player.stop()
        self._is_ringing = False
        self._is_snoozed = False
        self._snooze_timer.stop()
        self.alarm_stopped.emit()

    def snooze(self):
        """Snooze the alarm for SNOOZE_DURATION_MS."""
        self._player.stop()
        self._is_ringing = False
        self._is_snoozed = True
        self._already_triggered = False
        self._snooze_timer.start(self.SNOOZE_DURATION_MS)
        self.alarm_stopped.emit()

    def reset(self):
        """Full reset — use when target changes or alarm is toggled."""
        self.stop()
        self._already_triggered = False

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------
    def _trigger(self):
        self._is_ringing = True
        self._already_triggered = True
        self._player.setPosition(0)
        self._player.play()
        self.alarm_triggered.emit()

    def _on_media_status(self, status):
        """Loop the sound while the alarm is ringing."""
        if status == QMediaPlayer.MediaStatus.EndOfMedia and self._is_ringing:
            self._player.setPosition(0)
            self._player.play()

    def _on_snooze_end(self):
        self._is_snoozed = False
        self._already_triggered = False
        self.snooze_ended.emit()
