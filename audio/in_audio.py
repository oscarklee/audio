import os
import atexit
import logging
import numpy as np

from pathlib import Path
from typing import Optional
from numpy.typing import NDArray
import sounddevice as sd

from dotenv import load_dotenv

env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

class In:
    int16 = np.int16
    float32 = np.float32

    _default_selected_device = os.getenv('DEFAULT_AUDIO_IN_DEVICE', 'Wireless Microphone' ) 
    _default_sample_rate = int(os.getenv('DEFAULT_AUDIO_IN_RATE', '48000'))
    _default_channels = int(os.getenv('DEFAULT_AUDIO_IN_CHANNELS', '2'))
    _default_format = float32 if os.getenv('DEFAULT_AUDIO_IN_FORMAT', 'float32') == 'float32' else int16
    _stream: Optional[sd.InputStream] = None
    
    @classmethod
    def read(cls, frame_length: int = 512, 
             device: Optional[str] = None,
             sample_rate: Optional[int] = None,
             channels: Optional[int] = None,
             format: Optional[type] = None) -> NDArray:
        """
        Read audio frames from the microphone.
        
        Args:
            frame_length: Number of frames to read
            device: Input device name (defaults to DEFAULT_AUDIO_IN_DEVICE)
            sample_rate: Sample rate in Hz (defaults to DEFAULT_AUDIO_IN_RATE)
            channels: Number of audio channels (defaults to DEFAULT_AUDIO_IN_CHANNELS)
            format: Data format (int16 or float32, defaults to DEFAULT_AUDIO_IN_FORMAT)
            
        Returns:
            NDArray: Audio data as numpy array with shape (frame_length, channels)
        """
        device = device or cls._default_selected_device
        sample_rate = sample_rate or cls._default_sample_rate
        channels = channels or cls._default_channels
        format = format or cls._default_format
        
        device_index = cls._get_device_index(device)
        dtype = 'int16' if format == cls.int16 else 'float32'
        
        audio_data = sd.rec(
            frames=frame_length,
            samplerate=sample_rate,
            channels=channels,
            dtype=dtype,
            device=device_index,
            blocking=True
        )
        
        return audio_data
    
    @classmethod
    def _get_device_index(cls, device_name: Optional[str]) -> Optional[int]:
        """
        Get device index from device name.
        
        Args:
            device_name: Name or partial name of the audio device
            
        Returns:
            Device index or None for default device
        """
        if device_name is None:
            return None
            
        devices = sd.query_devices()
        for idx, device_info in enumerate(devices):
            device_dict = dict(device_info)
            if device_name.lower() in device_dict['name'].lower():
                if device_dict['max_input_channels'] > 0:
                    logging.info(f"Selected audio input device: {device_dict['name']} (index: {idx})")
                    return idx
        
        logging.warning(f"Device '{device_name}' not found, using default")
        return None

    @classmethod
    def _cleanup(cls) -> None:
        """Cleanup on exit."""
        if cls._stream is not None:
            cls._stream.stop()
            cls._stream.close()
            cls._stream = None
        logging.info("Microphone terminated gracefully")


# Register cleanup function to run on exit
atexit.register(In._cleanup)