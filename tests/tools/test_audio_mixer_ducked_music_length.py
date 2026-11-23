"""Regression: ducked music must not be cut off when narration ends.

sidechaincompress ends at the first EOF on either input, so without padding the
speech key a music bed that outlasts the narration was truncated to the end of
the last speech track (75s music + speech ending at ~67.6s -> 67.6s mix).
"""

import shutil
import subprocess
from pathlib import Path

import pytest

from tools.audio.audio_mixer import AudioMixer


pytestmark = pytest.mark.skipif(
    shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None,
    reason="ffmpeg and ffprobe are required",
)


def _tone(path: Path, frequency: int, duration: float) -> None:
    subprocess.run(
        [
            "ffmpeg", "-y", "-f", "lavfi", "-i",
            f"sine=frequency={frequency}:duration={duration}", str(path),
        ],
        capture_output=True,
        check=True,
        timeout=30,
    )


def _duration(path: Path) -> float:
    result = subprocess.run(
        [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "csv=p=0", str(path),
        ],
        capture_output=True,
        check=True,
        text=True,
        timeout=30,
    )
    return float(result.stdout.strip())


@pytest.mark.parametrize("normalize", [False, True])
def test_ducked_music_outlasting_narration_is_not_truncated(tmp_path, normalize) -> None:
    speech_a = tmp_path / "speech_a.wav"
    speech_b = tmp_path / "speech_b.wav"
    music = tmp_path / "music.wav"
    output = tmp_path / "mix.wav"
    _tone(speech_a, 440, 1.0)
    _tone(speech_b, 660, 1.0)
    _tone(music, 220, 6.0)

    result = AudioMixer().execute({
        "operation": "full_mix",
        "tracks": [
            {"path": str(speech_a), "role": "speech", "start_seconds": 0},
            {"path": str(speech_b), "role": "speech", "start_seconds": 2.0},
            {"path": str(music), "role": "music", "volume": 0.3},
        ],
        "ducking": {"enabled": True},
        "normalize": normalize,
        "output_path": str(output),
    })

    assert result.success, result.error
    # Narration ends at 3.0s; the music bed (the longest input) runs to 6.0s.
    assert _duration(output) == pytest.approx(6.0, abs=0.15)


def test_narration_longer_than_music_still_sets_length(tmp_path) -> None:
    speech = tmp_path / "speech.wav"
    music = tmp_path / "music.wav"
    output = tmp_path / "mix.wav"
    _tone(speech, 440, 4.0)
    _tone(music, 220, 2.0)

    result = AudioMixer().execute({
        "operation": "full_mix",
        "tracks": [
            {"path": str(speech), "role": "speech"},
            {"path": str(music), "role": "music"},
        ],
        "ducking": {"enabled": True},
        "normalize": False,
        "output_path": str(output),
    })

    assert result.success, result.error
    assert _duration(output) == pytest.approx(4.0, abs=0.15)
