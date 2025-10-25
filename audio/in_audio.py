import os
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

    _default_frame_length = int(os.getenv('DEFAULT_AUDIO_IN_FRAME_LENGTH', '1536'))
    _default_selected_device = os.getenv('DEFAULT_AUDIO_IN_DEVICE', 'pulse' ) 
    _default_sample_rate = int(os.getenv('DEFAULT_AUDIO_IN_RATE', '16000'))
    _default_channels = int(os.getenv('DEFAULT_AUDIO_IN_CHANNELS', '1'))
    _default_format = os.getenv('DEFAULT_AUDIO_IN_FORMAT', 'float32')
    _stream: Optional[sd.InputStream] = None
    
    @classmethod
    def read(cls, callback,
             frame_length: Optional[int] = None, 
             device: Optional[str] = None,
             sample_rate: Optional[int] = None,
             channels: Optional[int] = None,
             format: Optional[str] = None):
        """
        Read audio frames from the microphone.
        
        Args:
            callback: Function to call with audio data
            frame_length: Number of frames to read
            device: Input device name (defaults to DEFAULT_AUDIO_IN_DEVICE)
            sample_rate: Sample rate in Hz (defaults to DEFAULT_AUDIO_IN_RATE)
            channels: Number of audio channels (defaults to DEFAULT_AUDIO_IN_CHANNELS)
            format: Data format (int16 or float32, defaults to DEFAULT_AUDIO_IN_FORMAT)
        """
        frame_length = frame_length or cls._default_frame_length
        device = device or cls._default_selected_device
        sample_rate = sample_rate or cls._default_sample_rate
        channels = channels or cls._default_channels
        format = format or cls._default_format
        device_index = cls._get_device_index(device)
        
        cls._stream = sd.InputStream(
            samplerate=sample_rate,
            channels=channels,
            dtype=format,
            device=device_index,
            blocksize=frame_length,
            callback=callback,
        )

        cls._stream.start()
    
    @classmethod
    def stop(cls) -> None:
        """Cleanup on exit."""
        if cls._stream is not None:
            cls._stream.stop()
            cls._stream.close()
            cls._stream = None
        logging.info("Microphone terminated gracefully")
    
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
            name = str(device_info['name'])  # type: ignore
            max_input = int(device_info['max_input_channels'])  # type: ignore
            
            if device_name.lower() in name.lower():
                if max_input > 0:
                    logging.info(f"Selected audio input device: {name} (index: {idx})")
                    return idx
        
        logging.warning(f"Device '{device_name}' not found, using default")
        return None
