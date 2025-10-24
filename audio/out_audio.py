import os
import logging
import atexit
import inspect
import base64
import numpy as np
import threading
import sounddevice as sd

from typing import Optional
from collections import defaultdict
from scipy import signal
from pathlib import Path

from dotenv import load_dotenv

env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

class Out:
    int16 = np.int16
    float32 = np.float32

    _playback_finished: threading.Event = threading.Event()
    _default_channels = int(os.getenv('DEFAULT_AUDIO_OUT_CHANNELS', '2'))
    _default_rate = int(os.getenv('DEFAULT_AUDIO_OUT_RATE', '44100'))
    _default_format = float32 if os.getenv('DEFAULT_AUDIO_OUT_FORMAT', 'float32') == 'float32' else int16
    _sources = defaultdict(list)
    _lock: threading.Lock = threading.Lock()
    _stream: Optional[sd.OutputStream] = None

    @classmethod
    def write(cls, data: bytes, format = _default_format, channels = _default_channels, rate = _default_rate) -> None:
        """Play audio data."""
        cls._initiate_stream()
        source_id = cls._get_source_id()
        audio_data = cls._process_data(data, format, channels, rate)
        with cls._lock:
            cls._sources[source_id].append(audio_data)
            cls._playback_finished.clear()

    @classmethod
    def wait_until_finished(cls, timeout: Optional[float] = None) -> bool:
        """
        Block until all audio sources finish playing.
        
        Args:
            timeout: Maximum time to wait in seconds. None means wait indefinitely.
            
        Returns:
            True if playback finished, False if timeout occurred.
        """
        return cls._playback_finished.wait(timeout=timeout)

    @classmethod
    def _callback(cls, outdata, frames, time, status):
        """Mix and play audio from all sources."""
        if status:
            logging.warning(f"Audio callback status: {status}")
        
        with cls._lock:
            if not cls._sources:
                outdata.fill(0)
                cls._playback_finished.set()
                return
            
            mixed = np.zeros((frames, cls._default_channels), dtype=np.float32)
            sources_to_remove = []
            
            for source_id, chunks in cls._sources.items():
                if not chunks:
                    sources_to_remove.append(source_id)
                    continue
                
                frames_needed = frames
                source_audio = []
                
                while frames_needed > 0 and chunks:
                    chunk = chunks[0]
                    chunk_frames = len(chunk)
                    
                    if chunk_frames <= frames_needed:
                        source_audio.append(chunk)
                        chunks.pop(0)
                        frames_needed -= chunk_frames
                    else:
                        source_audio.append(chunk[:frames_needed])
                        chunks[0] = chunk[frames_needed:]
                        frames_needed = 0
                
                if source_audio:
                    source_data = np.concatenate(source_audio)
                    if len(source_data) < frames:
                        padding = np.zeros((frames - len(source_data), cls._default_channels), dtype=np.float32)
                        source_data = np.concatenate([source_data, padding])
                    
                    mixed += source_data
                
                if not chunks:
                    sources_to_remove.append(source_id)
            
            for source_id in sources_to_remove:
                del cls._sources[source_id]

            if not cls._sources:
                cls._playback_finished.set()
            
            mixed = np.clip(mixed, -1.0, 1.0)
            mixed = cls._convert_format(mixed, cls._default_format)
            
            outdata[:] = mixed

    @classmethod
    def _initiate_stream(cls):
        if cls._stream is not None:
            return 

        with cls._lock:
            if cls._stream is not None:
                return
            
            cls._stream = sd.OutputStream(
                samplerate=cls._default_rate,
                channels=cls._default_channels,
                dtype=cls._default_format,
                callback=cls._callback
            )

            cls._stream.start()

    @classmethod
    def _process_data(cls, data: bytes, format, channels, rate) -> np.ndarray:
        """
        Process raw audio data into normalized float32 array.
        
        Converts from input format/channels/rate to float32/_default_channels/_default_rate.
        Output is always float32 in range [-1.0, 1.0] for efficient mixing.
        """
        audio_data = np.frombuffer(data, dtype=format)
        
        if np.issubdtype(format, np.integer):
            audio_data = audio_data.astype(np.float32)
            max_val = float(np.iinfo(format).max)
            audio_data = np.where(audio_data > 0, audio_data / max_val, audio_data / (max_val + 1))
        else:
            audio_data = audio_data.astype(np.float32)
        
        if channels > 1:
            audio_data = audio_data.reshape(-1, channels)
        else:
            audio_data = audio_data.reshape(-1, 1)
        
        audio_data = cls._convert_channels(audio_data, channels, cls._default_channels)
        if rate != cls._default_rate:
            audio_data = cls._resample(audio_data, rate, cls._default_rate)
        
        return audio_data
    
    @classmethod
    def _convert_channels(cls, audio_data: np.ndarray, input_channels: int, output_channels: int) -> np.ndarray:
        """Convert between different channel configurations."""
        if input_channels == output_channels:
            return audio_data
        
        if input_channels == 1 and output_channels == 2:
            return np.repeat(audio_data, 2, axis=1)
        
        if input_channels == 2 and output_channels == 1:
            return np.mean(audio_data, axis=1, keepdims=True)
        
        if input_channels > output_channels:
            return audio_data[:, :output_channels]
        else:
            n_samples = audio_data.shape[0]
            result = np.zeros((n_samples, output_channels), dtype=audio_data.dtype)
            result[:, :input_channels] = audio_data
            return result

    @classmethod
    def _resample(cls, audio_data: np.ndarray, input_rate: int, output_rate: int) -> np.ndarray:
        """Resample using scipy for better quality."""
        if input_rate == output_rate:
            return audio_data
        
        n_samples_input = audio_data.shape[0]
        n_channels = audio_data.shape[1]
        n_samples_output = int(n_samples_input * output_rate / input_rate)
        
        resampled = np.zeros((n_samples_output, n_channels), dtype=audio_data.dtype)
        
        for ch in range(n_channels):
            resampled[:, ch] = signal.resample(audio_data[:, ch], n_samples_output)
        
        return resampled

    @classmethod
    def _convert_format(cls, audio_data: np.ndarray, output_format) -> np.ndarray:
        """Convert audio to output format (int16 or float32)."""
        if output_format == np.float32:
            return audio_data
        else:
            audio_data = np.clip(audio_data, -1.0, 1.0)
            return (audio_data * np.iinfo(cls.int16).max).astype(np.int16)

    @classmethod
    def _get_source_id(cls) -> str:
        """Get unique source ID."""
        stack = inspect.stack()
        caller = stack[2]
        source_string = f"{caller.filename}:{caller.lineno}"
        return base64.b64encode(source_string.encode('utf-8')).decode('utf-8')

    @classmethod
    def _cleanup(cls) -> None:
        """Cleanup on exit."""
        logging.info("Speakers terminated gracefully")

# Register cleanup function to run on exit
atexit.register(Out._cleanup)