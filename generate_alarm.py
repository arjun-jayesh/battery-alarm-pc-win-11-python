"""
Alarm Sound Generator
Creates a simple alarm WAV file procedurally (no external assets needed).
Run this script once to generate assets/alarm.wav.
"""

import math
import struct
import wave
import os


def generate_alarm_wav(path: str, duration_s: float = 3.0,
                       sample_rate: int = 44100):
    """Generate a pleasant two-tone alarm beep."""
    os.makedirs(os.path.dirname(path), exist_ok=True)

    n_samples = int(sample_rate * duration_s)
    samples = []

    freq1, freq2 = 880.0, 1108.73  # A5, C#6
    beep_on = 0.25    # seconds per beep
    beep_off = 0.12   # gap between beeps

    for i in range(n_samples):
        t = i / sample_rate
        cycle = t % (beep_on + beep_off)
        if cycle < beep_on:
            # Alternate between two tones every other beep
            beep_index = int(t / (beep_on + beep_off))
            freq = freq1 if beep_index % 2 == 0 else freq2
            # Envelope: quick fade-in / fade-out
            env_t = cycle / beep_on
            envelope = min(env_t * 8, 1.0) * min((1 - env_t) * 8, 1.0)
            val = envelope * 0.45 * math.sin(2 * math.pi * freq * t)
        else:
            val = 0.0
        samples.append(int(val * 32767))

    with wave.open(path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(struct.pack(f"<{len(samples)}h", *samples))


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "assets", "alarm.wav")
    generate_alarm_wav(out)
    print(f"Generated → {out}")
