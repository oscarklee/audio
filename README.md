# Audio Library

A high-performance audio input/output library for NVIDIA Jetson Orin Nano, optimized for Nothing Ear (open) and DJI Mic 2 devices.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- 🎤 **Audio Input** - Real-time audio capture from microphones
- 🔊 **Audio Output** - Multi-source audio playback with automatic mixing
- 🎛️ **Format Support** - int16 and float32 audio formats
- 🔄 **Automatic Resampling** - Seamless conversion between sample rates
- 🎚️ **Channel Conversion** - Mono/stereo conversion on the fly
- 🎯 **Device Selection** - Intelligent device matching by name
- ⚡ **Low Latency** - Optimized for real-time audio processing
- 🧵 **Thread-Safe** - Safe concurrent audio operations

## Hardware Support

### Tested Devices
- **Input**: DJI Mic 2 (Wireless Microphone RX)
- **Output**: Nothing Ear (open) via Bluetooth
- **Platform**: NVIDIA Jetson Orin Nano Super

### Compatible Devices
Any ALSA/PulseAudio compatible audio device should work.

## Installation

### Prerequisites

```bash
# Ensure Python 3.11+ is installed
python --version

# Install system dependencies (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y portaudio19-dev python3-dev
```

### Install from Source

```bash
# Clone the repository
git clone <repository-url>
cd audio

# Install in development mode
pip install -e .

# Or install with dev dependencies
pip install -e ".[dev]"
```

## Quick Start

### Audio Input (Microphone)

```python
from audio import In
import numpy as np

# Read audio from default microphone
audio_data = In.read(frame_length=512)

# Read from specific device
audio_data = In.read(
    frame_length=1024,
    device='DJI',
    sample_rate=48000,
    channels=2,
    format=In.float32
)

print(f"Captured {audio_data.shape[0]} frames")
print(f"Audio level: {np.abs(audio_data).max()}")
```

### Audio Output (Speakers)

```python
from audio import Out
import numpy as np

# Generate a simple tone
sample_rate = 44100
frequency = 440  # A4 note
duration = 1.0
t = np.linspace(0, duration, int(sample_rate * duration))
audio_data = np.sin(2 * np.pi * frequency * t).astype(np.float32)

# Play audio
Out.write(audio_data.tobytes(), format=Out.float32, channels=1, rate=sample_rate)

# Wait for playback to finish
Out.wait_until_finished()
```

## Examples

### Real-time Microphone Level Meter

```bash
python examples/microphone.py
```

Features:
- Visual level bar (0-100%)
- Color-coded indicators (green/yellow/red)
- Saturation warnings
- Real-time RMS and peak detection

### Play Audio File

```bash
python examples/speakers.py
```

Demonstrates:
- Multi-format audio playback
- Automatic resampling
- Non-blocking playback

### DJI Microphone Test

```bash
python examples/dji_microphone.py
```

Shows:
- Device-specific audio capture
- Audio statistics (min, max, mean, RMS)
- Multi-frame capture

## Configuration

Create a `.env` file in the `audio/` directory:

```bash
# Audio Input Configuration
DEFAULT_AUDIO_IN_DEVICE=Wireless Microphone
DEFAULT_AUDIO_IN_RATE=48000
DEFAULT_AUDIO_IN_CHANNELS=2
DEFAULT_AUDIO_IN_FORMAT=float32

# Audio Output Configuration
DEFAULT_AUDIO_OUT_CHANNELS=2
DEFAULT_AUDIO_OUT_RATE=44100
DEFAULT_AUDIO_OUT_FORMAT=float32
```

## API Reference

### Input (`In` class)

#### `In.read()`

Read audio frames from microphone.

**Parameters:**
- `frame_length` (int): Number of frames to read (default: 512)
- `device` (str, optional): Device name or partial match (default: from config)
- `sample_rate` (int, optional): Sample rate in Hz (default: from config)
- `channels` (int, optional): Number of channels (default: from config)
- `format` (type, optional): Data format - `In.int16` or `In.float32` (default: from config)

**Returns:**
- `NDArray`: Audio data with shape (frame_length, channels)

**Example:**
```python
audio = In.read(frame_length=1024, device='DJI', sample_rate=48000)
```

### Output (`Out` class)

#### `Out.write()`

Play audio data.

**Parameters:**
- `data` (bytes): Audio data as bytes
- `format` (type): Source format - `Out.int16` or `Out.float32` (default: float32)
- `channels` (int): Number of channels (default: 2)
- `rate` (int): Sample rate in Hz (default: 44100)

**Example:**
```python
Out.write(audio_bytes, format=Out.float32, channels=2, rate=44100)
```

#### `Out.wait_until_finished()`

Block until all audio playback completes.

**Parameters:**
- `timeout` (float, optional): Maximum time to wait in seconds (default: None)

**Returns:**
- `bool`: True if playback finished, False if timeout occurred

**Example:**
```python
Out.write(audio_data)
if Out.wait_until_finished(timeout=5.0):
    print("Playback completed")
else:
    print("Timeout")
```

## Architecture

### Audio Input Pipeline
```
Microphone → ALSA/PulseAudio → sounddevice → numpy array → User
```

### Audio Output Pipeline
```
User → bytes → Processing (resample/convert) → Mixing → sounddevice → Speakers
```

### Key Features

#### Automatic Processing
- **Resampling**: Converts any input rate to output device rate
- **Channel Conversion**: Mono↔Stereo conversion
- **Format Conversion**: int16↔float32 with proper normalization

#### Multi-Source Mixing
- Multiple audio sources can play simultaneously
- Automatic level mixing with clipping prevention
- Thread-safe source management

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=audio --cov-report=html

# Run specific test class
pytest tests/test_audio.py::TestAudioInput -v

# Run with verbose output
pytest -vv
```

### Test Coverage

- ✅ Audio input/output operations
- ✅ Format conversions (int16/float32)
- ✅ Channel conversions (mono/stereo)
- ✅ Resampling (various sample rates)
- ✅ Multi-source mixing
- ✅ Device selection
- ✅ Error handling

## Troubleshooting

### No audio input/output

```bash
# List available devices
python -c "import sounddevice as sd; print(sd.query_devices())"

# Test default device
python -c "from audio import In; print(In.read().shape)"
```

### Device not found

Update device name in `.env` file or pass explicitly:
```python
In.read(device='Wireless')  # Partial match works
```

### Audio clipping/distortion

Reduce input gain or adjust RMS multiplier in level calculations.

### Bluetooth audio issues

See `docs/BLUETOOTH_AUDIO_TROUBLESHOOTING.md` for detailed troubleshooting.

## Performance

### Typical Latency
- **Input**: ~10-20ms (512 frames @ 48kHz)
- **Output**: ~20-30ms (depends on buffer size)

### Resource Usage
- **CPU**: <5% on Jetson Orin Nano (idle)
- **Memory**: ~50MB (typical usage)

## Development

### Code Style

Follow PEP 8 guidelines with:
- Line length: 88 characters
- Use type hints
- Minimal comments (self-documenting code)
- Modular design

### Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for new features
4. Ensure all tests pass
5. Submit a pull request

### Pre-commit Checks

```bash
# Format code
black audio/ tests/

# Sort imports
isort audio/ tests/

# Type checking
mypy audio/

# Linting
ruff check audio/ tests/
```

## Documentation

- `docs/AAC_SETUP_SUCCESS.md` - AAC codec configuration
- `docs/BLUETOOTH_AUDIO_TROUBLESHOOTING.md` - Bluetooth audio issues
- `docs/QUICK_REFERENCE.md` - Quick command reference

## License

MIT License - see LICENSE file for details.

## Author

Oscar Klee - oscarklee@hotmail.com

## Acknowledgments

- Built with [sounddevice](https://python-sounddevice.readthedocs.io/)
- Powered by [NumPy](https://numpy.org/) and [SciPy](https://scipy.org/)
- Optimized for NVIDIA Jetson platform

---

**Note**: This library is optimized for NVIDIA Jetson Orin Nano but should work on any Linux system with ALSA/PulseAudio support.
