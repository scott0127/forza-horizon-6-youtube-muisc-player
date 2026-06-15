import math
import random
import struct
import wave
from pathlib import Path

SAMPLE_RATE = 44100
DURATION = 54
TOTAL = SAMPLE_RATE * DURATION
OUTPUT = Path(__file__).parent / "public" / "promo-pulse.wav"
random.seed(5497)


def envelope(t: float, length: float, power: float = 2.0) -> float:
    if t < 0 or t > length:
        return 0.0
    return (1.0 - t / length) ** power


def synth_sample(time: float) -> float:
    beat = 60.0 / 126.0
    beat_index = int(time / beat)
    beat_phase = time % beat
    eighth_phase = time % (beat / 2.0)

    kick = math.sin(2 * math.pi * (72 - 36 * beat_phase) * beat_phase)
    kick *= envelope(beat_phase, 0.19, 3.1) * (0.78 if beat_index % 4 in (0, 2) else 0.43)

    hat = (random.random() * 2 - 1) * envelope(eighth_phase, 0.045, 5.0) * 0.08

    root = [55.0, 65.41, 73.42, 49.0][(beat_index // 8) % 4]
    bass_phase = time % (beat * 2)
    bass = math.sin(2 * math.pi * root * time)
    bass += 0.28 * math.sin(2 * math.pi * root * 2 * time)
    bass *= envelope(bass_phase, beat * 1.8, 1.3) * 0.22

    shimmer = math.sin(2 * math.pi * (220 + 24 * math.sin(time * 0.38)) * time) * 0.023
    shimmer += math.sin(2 * math.pi * 330 * time) * 0.014

    energy = 0.72
    if 30 <= time < 38:
        energy = 0.86
    elif 38 <= time < 48:
        energy = 1.06
    elif time >= 48:
        energy = max(0.18, 1.0 - (time - 48) / 7)

    impact = 0.0
    for hit in (4.6, 11.0, 17.5, 24.0, 30.5, 38.0, 39.33, 40.66, 42.0, 43.33, 44.66, 46.0, 48.2):
        phase = time - hit
        if 0 <= phase <= 0.42:
            impact += math.sin(2 * math.pi * (126 - 92 * phase) * phase) * envelope(phase, 0.42, 2.4) * 0.35
        if 0 <= phase <= 0.14:
            impact += (random.random() * 2 - 1) * envelope(phase, 0.14, 2.1) * 0.18

    return max(-1.0, min(1.0, (kick + hat + bass + shimmer + impact) * energy))


OUTPUT.parent.mkdir(parents=True, exist_ok=True)
with wave.open(str(OUTPUT), "wb") as output:
    output.setnchannels(2)
    output.setsampwidth(2)
    output.setframerate(SAMPLE_RATE)
    for sample_index in range(TOTAL):
        value = synth_sample(sample_index / SAMPLE_RATE)
        left = int(value * 28500)
        right = int(value * 27400)
        output.writeframesraw(struct.pack("<hh", left, right))
