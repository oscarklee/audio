import wave
import threading

from audio import Out
from pathlib import Path
from typing import List, Tuple
import time

TIMING_FILE = Path('examples/song/timing.txt')

def log(message: str, level: str = "INFO") -> None:
    symbols = {
        "INFO": "ℹ️ ",
        "SUCCESS": "✅",
        "PLAY": "🎵",
        "WAIT": "⏳",
        "START": "🚀",
        "DONE": "🎉"
    }
    symbol = symbols.get(level, "  ")
    timestamp = time.strftime("%H:%M:%S.%f")[:-3]
    print(f"[{timestamp}] {symbol} {message}")

def load_timing_info(timing_file: Path) -> List[Tuple[Path, int]]:
    log(f"Loading timing configuration from {timing_file.name}", "INFO")
    instruments = []
    with open(timing_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) == 2:
                file_path = Path("song") / parts[0]
                offset_ms = int(parts[1])
                instruments.append((file_path, offset_ms))
                log(f"  • {file_path.name}: offset {offset_ms}ms", "INFO")
    log(f"Loaded {len(instruments)} tracks", "SUCCESS")
    return instruments

def get_wav_params(file_path: Path):
    with wave.open(str("examples" / file_path), 'rb') as wav_file:
        samplerate = wav_file.getframerate()
        n_frames = wav_file.getnframes()
        n_channels = wav_file.getnchannels()
        sampwidth = wav_file.getsampwidth()
        frames = wav_file.readframes(n_frames)
        format = Out.int16 if sampwidth == 2 else Out.float32

    return frames, format, n_channels, samplerate

def _wait_for_offset(start_time: float, offset_ms: int) -> None:
    target_time = start_time + (offset_ms / 1000.0)
    wait_time = target_time - time.time()
    
    if wait_time > 0:
        time.sleep(wait_time)

def play_bass(file_path: Path, start_time: float, offset_ms: int) -> None:
    log(f"🎸 Bass waiting {offset_ms}ms", "WAIT")
    _wait_for_offset(start_time, offset_ms)
    log(f"🎸 Bass playing: {file_path.name}", "PLAY")
    frames, format, n_channels, samplerate = get_wav_params(file_path)
    Out.write(frames, format=format, channels=n_channels, rate=samplerate)

def play_drums(file_path: Path, start_time: float, offset_ms: int) -> None:
    log(f"🥁 Drums waiting {offset_ms}ms", "WAIT")
    _wait_for_offset(start_time, offset_ms)
    log(f"🥁 Drums playing: {file_path.name}", "PLAY")
    frames, format, n_channels, samplerate = get_wav_params(file_path)
    Out.write(frames, format=format, channels=n_channels, rate=samplerate)

def play_guitar(file_path: Path, start_time: float, offset_ms: int) -> None:
    log(f"🎸 Guitar waiting {offset_ms}ms", "WAIT")
    _wait_for_offset(start_time, offset_ms)
    log(f"🎸 Guitar playing: {file_path.name}", "PLAY")
    frames, format, n_channels, samplerate = get_wav_params(file_path)
    Out.write(frames, format=format, channels=n_channels, rate=samplerate)

def play_samples(file_path: Path, start_time: float, offset_ms: int) -> None:
    log(f"🎹 Samples waiting {offset_ms}ms", "WAIT")
    _wait_for_offset(start_time, offset_ms)
    log(f"🎹 Samples playing: {file_path.name}", "PLAY")
    frames, format, n_channels, samplerate = get_wav_params(file_path)
    Out.write(frames, format=format, channels=n_channels, rate=samplerate)

def play_vocals(file_path: Path, start_time: float, offset_ms: int) -> None:
    log(f"🎤 Vocals waiting {offset_ms}ms", "WAIT")
    _wait_for_offset(start_time, offset_ms)
    log(f"🎤 Vocals playing: {file_path.name}", "PLAY")
    frames, format, n_channels, samplerate = get_wav_params(file_path)
    Out.write(frames, format=format, channels=n_channels, rate=samplerate)

def get_play_function(file_path: Path):
    filename = file_path.name.lower()
    
    if 'bass' in filename:
        return play_bass
    elif 'drum' in filename:
        return play_drums
    elif 'guitar' in filename:
        return play_guitar
    elif 'sample' in filename:
        return play_samples
    elif 'vocal' in filename:
        return play_vocals
    else:
        raise ValueError(f"Unknown instrument type in filename: {filename}")

def play_instruments_realtime(instruments: List[Tuple[Path, int]]) -> None:
    log("Initializing playback threads", "START")
    start_time = time.time() + 0.1
    threads = []
    
    for file_path, offset_ms in instruments:
        play_function = get_play_function(file_path)
        thread = threading.Thread(
            target=play_function,
            args=(file_path, start_time, offset_ms)
        )
        thread.start()
        threads.append(thread)
    
    log(f"All {len(threads)} threads started, waiting for synchronization...", "INFO")
    
    for thread in threads:
        thread.join()
    
    log("All tracks have been queued for playback", "SUCCESS")

def main():
    log("🎼 Multi-track Synchronized Audio Playback", "START")
    print()
    
    instruments = load_timing_info(TIMING_FILE)
    print()
    
    play_instruments_realtime(instruments)
    print()
    
    log("Waiting for audio playback to complete...", "INFO")
    Out.wait_until_finished()
    print()
    
    log("Playback completed successfully!", "DONE")

if __name__ == "__main__":
    main()