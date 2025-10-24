import pytest
import numpy as np


@pytest.fixture
def sample_int16_audio():
    """Provide sample int16 audio data."""
    return np.array([0, 8192, -8192, 16384, -16384], dtype=np.int16)


@pytest.fixture
def sample_float32_audio():
    """Provide sample float32 audio data."""
    return np.array([0.0, 0.25, -0.25, 0.5, -0.5], dtype=np.float32)


@pytest.fixture
def stereo_audio():
    """Provide sample stereo audio data."""
    return np.array([[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]], dtype=np.float32)


@pytest.fixture
def mono_audio():
    """Provide sample mono audio data."""
    return np.array([[0.1], [0.3], [0.5]], dtype=np.float32)
