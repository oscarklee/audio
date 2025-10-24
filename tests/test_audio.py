import pytest
import numpy as np
import sounddevice as sd
from unittest.mock import Mock, patch, MagicMock
from audio.out_audio import Out
from audio.in_audio import In


class TestAudioProcessing:
    """Test audio data processing and conversion."""
    
    def test_process_data_int16_to_float32(self):
        """Test conversion from int16 to normalized float32."""
        int16_data = np.array([0, 16384, -16384, 32767, -32768], dtype=np.int16)
        audio_bytes = int16_data.tobytes()
        
        result = Out._process_data(audio_bytes, Out.int16, 1, Out._default_rate)
        
        assert result.dtype == np.float32
        assert result.shape == (5, 2)
        assert np.all(result >= -1.0) and np.all(result <= 1.0)
    
    def test_process_data_float32_passthrough(self):
        """Test that float32 data is processed correctly."""
        float32_data = np.array([0.0, 0.5, -0.5, 1.0, -1.0], dtype=np.float32)
        audio_bytes = float32_data.tobytes()
        
        result = Out._process_data(audio_bytes, Out.float32, 1, Out._default_rate)
        
        assert result.dtype == np.float32
        assert result.shape == (5, 2)
        np.testing.assert_array_almost_equal(result[:, 0], float32_data)
    
    def test_process_data_with_resampling(self):
        """Test audio resampling from 48kHz to 44.1kHz (default)."""
        audio_data = np.random.rand(4800).astype(np.float32)
        audio_bytes = audio_data.tobytes()
        
        result = Out._process_data(audio_bytes, Out.float32, 1, 48000)
        
        expected_samples = int(4800 * Out._default_rate / 48000)
        assert result.shape[0] == expected_samples
        assert result.shape[1] == 2


class TestChannelConversion:
    """Test channel conversion logic."""
    
    def test_mono_to_stereo(self):
        """Test converting mono to stereo duplicates the channel."""
        mono = np.array([[1.0], [2.0], [3.0]], dtype=np.float32)
        
        result = Out._convert_channels(mono, 1, 2)
        
        assert result.shape == (3, 2)
        np.testing.assert_array_equal(result[:, 0], result[:, 1])
    
    def test_stereo_to_mono(self):
        """Test converting stereo to mono averages channels."""
        stereo = np.array([[1.0, 3.0], [2.0, 4.0], [3.0, 5.0]], dtype=np.float32)
        
        result = Out._convert_channels(stereo, 2, 1)
        
        assert result.shape == (3, 1)
        expected = np.array([[2.0], [3.0], [4.0]], dtype=np.float32)
        np.testing.assert_array_almost_equal(result, expected)
    
    def test_same_channels_no_conversion(self):
        """Test that same channel count returns unchanged data."""
        stereo = np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32)
        
        result = Out._convert_channels(stereo, 2, 2)
        
        np.testing.assert_array_equal(result, stereo)


class TestResampling:
    """Test audio resampling."""
    
    def test_no_resampling_needed(self):
        """Test that same rate returns unchanged data."""
        audio = np.random.rand(100, 2).astype(np.float32)
        
        result = Out._resample(audio, 48000, 48000)
        
        np.testing.assert_array_equal(result, audio)
    
    def test_upsample_44100_to_48000(self):
        """Test upsampling from 44.1kHz to 48kHz."""
        audio = np.random.rand(4410, 2).astype(np.float32)
        
        result = Out._resample(audio, 44100, 48000)
        
        expected_samples = int(4410 * 48000 / 44100)
        assert result.shape == (expected_samples, 2)
    
    def test_downsample_48000_to_44100(self):
        """Test downsampling from 48kHz to 44.1kHz."""
        audio = np.random.rand(4800, 2).astype(np.float32)
        
        result = Out._resample(audio, 48000, 44100)
        
        expected_samples = int(4800 * 44100 / 48000)
        assert result.shape == (expected_samples, 2)


class TestFormatConversion:
    """Test format conversion between int16 and float32."""
    
    def test_float32_to_float32(self):
        """Test that float32 returns unchanged."""
        audio = np.array([[0.5, -0.5], [1.0, -1.0]], dtype=np.float32)
        
        result = Out._convert_format(audio, Out.float32)
        
        np.testing.assert_array_equal(result, audio)
    
    def test_float32_to_int16(self):
        """Test conversion from float32 to int16."""
        audio = np.array([[0.0, 0.5], [-0.5, 1.0]], dtype=np.float32)
        
        result = Out._convert_format(audio, Out.int16)
        
        assert result.dtype == np.int16
        assert result[0, 0] == 0
        assert 16383 <= result[0, 1] <= 16384
        assert result[1, 1] == 32767
    
    def test_clipping_on_conversion(self):
        """Test that values outside [-1, 1] are clipped."""
        audio = np.array([[1.5, -1.5], [2.0, -2.0]], dtype=np.float32)
        
        result = Out._convert_format(audio, Out.int16)
        
        assert np.all(result <= 32767)
        assert np.all(result >= -32768)


class TestSourceTracking:
    """Test source ID generation and tracking."""
    
    def test_source_id_generation(self):
        """Test that source IDs are unique per calling location."""
        source_id_1 = Out._get_source_id()
        source_id_2 = Out._get_source_id()
        
        assert isinstance(source_id_1, str)
        assert isinstance(source_id_2, str)
        assert source_id_1 == source_id_2
    
    def test_source_id_unique_across_locations(self):
        """Test that different call sites generate different IDs."""
        def caller_1():
            return Out._get_source_id()
        
        def caller_2():
            return Out._get_source_id()
        
        id_1 = caller_1()
        id_2 = caller_2()
        
        assert id_1 != id_2


class TestAudioWrite:
    """Test the main write method."""
    
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Reset Audio state before and after each test."""
        Out._sources.clear()
        if Out._stream is not None:
            Out._stream.stop()
            Out._stream.close()
            Out._stream = None
        yield
        Out._sources.clear()
        if Out._stream is not None:
            Out._stream.stop()
            Out._stream.close()
            Out._stream = None
    
    @patch('sounddevice.OutputStream')
    def test_write_initializes_stream(self, mock_stream_class):
        """Test that write initializes the audio stream."""
        mock_stream = MagicMock()
        mock_stream_class.return_value = mock_stream
        
        audio_data = np.zeros(100, dtype=np.float32).tobytes()
        Out.write(audio_data)
        
        mock_stream_class.assert_called_once()
        mock_stream.start.assert_called_once()
    
    @patch('sounddevice.OutputStream')
    def test_write_stores_processed_data(self, mock_stream_class):
        """Test that write stores processed audio data."""
        mock_stream = MagicMock()
        mock_stream_class.return_value = mock_stream
        
        audio_data = np.random.rand(100).astype(np.float32).tobytes()
        Out.write(audio_data, format=Out.float32, channels=1, rate=48000)
        
        assert len(Out._sources) > 0
        source_id = list(Out._sources.keys())[0]
        assert len(Out._sources[source_id]) == 1
        assert isinstance(Out._sources[source_id][0], np.ndarray)
    
    @patch('sounddevice.OutputStream')
    def test_write_multiple_sources(self, mock_stream_class):
        """Test writing from multiple sources."""
        mock_stream = MagicMock()
        mock_stream_class.return_value = mock_stream
        
        def source_1():
            audio_data = np.zeros(100, dtype=np.float32).tobytes()
            Out.write(audio_data)
        
        def source_2():
            audio_data = np.ones(100, dtype=np.float32).tobytes()
            Out.write(audio_data)
        
        source_1()
        source_2()
        
        assert len(Out._sources) == 2


class TestAudioCallback:
    """Test the audio callback mixing logic."""
    
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Reset Audio state before and after each test."""
        Out._sources.clear()
        if Out._stream is not None:
            Out._stream.stop()
            Out._stream.close()
            Out._stream = None
        yield
        Out._sources.clear()
        if Out._stream is not None:
            Out._stream.stop()
            Out._stream.close()
            Out._stream = None
    
    def test_callback_fills_silence_when_no_sources(self):
        """Test that callback outputs silence when no sources exist."""
        outdata = np.zeros((512, 2), dtype=Out._default_format)
        
        Out._callback(outdata, 512, None, None)
        
        assert np.all(outdata == 0)
    
    def test_callback_mixes_single_source(self):
        """Test callback processes single source correctly."""
        frames = 512
        source_audio = np.ones((frames, 2), dtype=np.float32) * 0.5
        Out._sources['test_source'] = [source_audio]
        
        outdata = np.zeros((frames, 2), dtype=Out._default_format)
        Out._callback(outdata, frames, None, None)
        
        assert not np.all(outdata == 0)
        assert len(Out._sources) == 0
    
    def test_callback_mixes_multiple_sources(self):
        """Test callback mixes multiple sources correctly."""
        frames = 512
        source1 = np.ones((frames, 2), dtype=np.float32) * 0.3
        source2 = np.ones((frames, 2), dtype=np.float32) * 0.2
        
        Out._sources['source1'] = [source1]
        Out._sources['source2'] = [source2]
        
        outdata = np.zeros((frames, 2), dtype=Out._default_format)
        Out._callback(outdata, frames, None, None)
        
        assert len(Out._sources) == 0
    
    def test_callback_handles_partial_chunks(self):
        """Test callback handles chunks smaller than requested frames."""
        frames = 512
        chunk1 = np.ones((256, 2), dtype=np.float32) * 0.5
        chunk2 = np.ones((256, 2), dtype=np.float32) * 0.5
        
        Out._sources['test'] = [chunk1, chunk2]
        
        outdata = np.zeros((frames, 2), dtype=Out._default_format)
        Out._callback(outdata, frames, None, None)
        
        assert len(Out._sources) == 0
    
    def test_callback_preserves_remaining_chunk_data(self):
        """Test that callback preserves data when chunk is larger than frames."""
        frames = 256
        large_chunk = np.ones((512, 2), dtype=np.float32)
        
        Out._sources['test'] = [large_chunk]
        
        outdata = np.zeros((frames, 2), dtype=Out._default_format)
        Out._callback(outdata, frames, None, None)
        
        assert len(Out._sources) == 1
        assert len(Out._sources['test']) == 1
        assert Out._sources['test'][0].shape[0] == 256
    
    def test_callback_clipping_prevents_overflow(self):
        """Test that mixing multiple loud sources gets clipped."""
        frames = 512
        loud_source1 = np.ones((frames, 2), dtype=np.float32) * 0.9
        loud_source2 = np.ones((frames, 2), dtype=np.float32) * 0.9
        
        Out._sources['source1'] = [loud_source1]
        Out._sources['source2'] = [loud_source2]
        
        outdata = np.zeros((frames, 2), dtype=np.float32)
        Out._callback(outdata, frames, None, None)
        
        assert np.all(outdata >= -1.0)
        assert np.all(outdata <= 1.0)


class TestStreamInitialization:
    """Test audio stream initialization."""
    
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Reset Audio state before and after each test."""
        if Out._stream is not None:
            Out._stream.stop()
            Out._stream.close()
            Out._stream = None
        yield
        if Out._stream is not None:
            Out._stream.stop()
            Out._stream.close()
            Out._stream = None
    
    @patch('sounddevice.OutputStream')
    def test_initiate_stream_creates_stream(self, mock_stream_class):
        """Test that stream is created with correct parameters."""
        mock_stream = MagicMock()
        mock_stream_class.return_value = mock_stream
        
        Out._initiate_stream()
        
        mock_stream_class.assert_called_once_with(
            samplerate=Out._default_rate,
            channels=Out._default_channels,
            dtype=Out._default_format,
            callback=Out._callback
        )
        mock_stream.start.assert_called_once()
    
    @patch('sounddevice.OutputStream')
    def test_initiate_stream_called_once(self, mock_stream_class):
        """Test that stream is only created once."""
        mock_stream = MagicMock()
        mock_stream_class.return_value = mock_stream
        
        Out._initiate_stream()
        Out._initiate_stream()
        Out._initiate_stream()
        
        mock_stream_class.assert_called_once()


class TestCleanup:
    """Test cleanup functionality."""
    
    def test_cleanup_logs_message(self, caplog):
        """Test that cleanup logs termination message."""
        import logging
        caplog.set_level(logging.INFO)
        
        Out._cleanup()
        
        assert "Speakers terminated gracefully" in caplog.text


class TestWaitUntilFinished:
    """Test wait_until_finished functionality."""
    
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Reset Audio state before and after each test."""
        Out._sources.clear()
        Out._playback_finished.set()
        if Out._stream is not None:
            Out._stream.stop()
            Out._stream.close()
            Out._stream = None
        yield
        Out._sources.clear()
        Out._playback_finished.set()
        if Out._stream is not None:
            Out._stream.stop()
            Out._stream.close()
            Out._stream = None
    
    def test_wait_returns_immediately_when_no_sources(self):
        """Test that wait returns immediately when there are no sources."""
        Out._playback_finished.set()
        
        result = Out.wait_until_finished(timeout=0.1)
        
        assert result is True
    
    @patch('sounddevice.OutputStream')
    def test_wait_blocks_until_playback_finishes(self, mock_stream_class):
        """Test that wait blocks until playback actually finishes."""
        import time
        mock_stream = MagicMock()
        mock_stream_class.return_value = mock_stream
        
        audio_data = np.random.rand(100).astype(np.float32).tobytes()
        Out.write(audio_data, format=Out.float32, channels=1, rate=48000)
        
        def finish_playback():
            time.sleep(0.1)
            with Out._lock:
                Out._sources.clear()
                Out._playback_finished.set()
        
        import threading
        thread = threading.Thread(target=finish_playback)
        thread.start()
        
        start_time = time.time()
        result = Out.wait_until_finished(timeout=2.0)
        elapsed = time.time() - start_time
        
        thread.join()
        
        assert result is True
        assert 0.08 < elapsed < 0.3
    
    def test_wait_returns_false_on_timeout(self):
        """Test that wait returns False when timeout occurs."""
        with Out._lock:
            Out._sources['test'] = [np.zeros((48000, 2), dtype=np.float32)]
            Out._playback_finished.clear()
        
        result = Out.wait_until_finished(timeout=0.1)
        
        assert result is False
    
    def test_wait_with_no_timeout_waits_indefinitely(self):
        """Test that wait without timeout waits until playback finishes."""
        import time
        import threading
        
        def finish_playback():
            time.sleep(0.1)
            with Out._lock:
                Out._sources.clear()
                Out._playback_finished.set()
        
        Out._playback_finished.clear()
        thread = threading.Thread(target=finish_playback)
        thread.start()
        
        start_time = time.time()
        result = Out.wait_until_finished()
        elapsed = time.time() - start_time
        
        thread.join()
        
        assert result is True
        assert 0.08 < elapsed < 0.3
    
    @patch('sounddevice.OutputStream')
    def test_event_is_cleared_on_write(self, mock_stream_class):
        """Test that the event is cleared when writing audio."""
        mock_stream = MagicMock()
        mock_stream_class.return_value = mock_stream
        
        Out._playback_finished.set()
        assert Out._playback_finished.is_set()
        
        audio_data = np.zeros(100, dtype=np.float32).tobytes()
        Out.write(audio_data)
        
        assert not Out._playback_finished.is_set()
    
    def test_event_is_set_when_callback_empties_sources(self):
        """Test that the event is set when callback empties all sources."""
        Out._sources.clear()
        Out._playback_finished.clear()
        
        outdata = np.zeros((512, 2), dtype=Out._default_format)
        Out._callback(outdata, 512, None, None)
        
        assert Out._playback_finished.is_set()
    
    def test_event_is_set_after_last_source_finishes(self):
        """Test that event is set after the last source finishes in callback."""
        small_chunk = np.ones((256, 2), dtype=np.float32)
        Out._sources['test'] = [small_chunk]
        Out._playback_finished.clear()
        
        outdata = np.zeros((512, 2), dtype=Out._default_format)
        Out._callback(outdata, 512, None, None)
        
        assert len(Out._sources) == 0
        assert Out._playback_finished.is_set()
    
    @patch('sounddevice.OutputStream')
    def test_multiple_writes_keep_event_cleared(self, mock_stream_class):
        """Test that multiple writes keep the event cleared."""
        mock_stream = MagicMock()
        mock_stream_class.return_value = mock_stream
        
        audio_data = np.zeros(100, dtype=np.float32).tobytes()
        
        Out.write(audio_data)
        assert not Out._playback_finished.is_set()
        
        Out.write(audio_data)
        assert not Out._playback_finished.is_set()
        
        Out.write(audio_data)
        assert not Out._playback_finished.is_set()


class TestAudioInput:
    """Test audio input reading from microphone."""
    
    @patch('sounddevice.rec')
    @patch('sounddevice.query_devices')
    def test_read_default_parameters(self, mock_query_devices, mock_rec):
        """Test reading with default parameters."""
        mock_query_devices.return_value = [
            {'name': 'Built-in Microphone', 'max_input_channels': 2},
            {'name': 'Wireless Microphone RX', 'max_input_channels': 2}
        ]
        expected_audio = np.random.rand(512, 2).astype(np.float32)
        mock_rec.return_value = expected_audio
        
        result = In.read()
        
        assert result.shape == (512, 2)
        assert result.dtype == np.float32
        mock_rec.assert_called_once()
        assert mock_rec.call_args.kwargs['frames'] == 512
        assert mock_rec.call_args.kwargs['samplerate'] == In._default_sample_rate
        assert mock_rec.call_args.kwargs['channels'] == In._default_channels
        assert mock_rec.call_args.kwargs['dtype'] == 'float32'
        assert mock_rec.call_args.kwargs['blocking'] is True
    
    @patch('sounddevice.rec')
    def test_read_custom_frame_length(self, mock_rec):
        """Test reading with custom frame length."""
        expected_audio = np.random.rand(1024, 2).astype(np.float32)
        mock_rec.return_value = expected_audio
        
        result = In.read(frame_length=1024)
        
        assert result.shape == (1024, 2)
        mock_rec.assert_called_once()
        assert mock_rec.call_args.kwargs['frames'] == 1024
    
    @patch('sounddevice.rec')
    def test_read_int16_format(self, mock_rec):
        """Test reading with int16 format."""
        expected_audio = np.random.randint(-32768, 32767, (512, 2), dtype=np.int16)
        mock_rec.return_value = expected_audio
        
        result = In.read(format=In.int16)
        
        assert result.dtype == np.int16
        mock_rec.assert_called_once()
        assert mock_rec.call_args.kwargs['dtype'] == 'int16'
    
    @patch('sounddevice.rec')
    def test_read_mono_channel(self, mock_rec):
        """Test reading with mono channel."""
        expected_audio = np.random.rand(512, 1).astype(np.float32)
        mock_rec.return_value = expected_audio
        
        result = In.read(channels=1)
        
        assert result.shape == (512, 1)
        mock_rec.assert_called_once()
        assert mock_rec.call_args.kwargs['channels'] == 1
    
    @patch('sounddevice.rec')
    def test_read_custom_sample_rate(self, mock_rec):
        """Test reading with custom sample rate."""
        expected_audio = np.random.rand(512, 2).astype(np.float32)
        mock_rec.return_value = expected_audio
        
        result = In.read(sample_rate=44100)
        
        mock_rec.assert_called_once()
        assert mock_rec.call_args.kwargs['samplerate'] == 44100
    
    @patch('sounddevice.rec')
    @patch('sounddevice.query_devices')
    def test_read_with_device_name(self, mock_query_devices, mock_rec):
        """Test reading with specific device name."""
        mock_query_devices.return_value = [
            {'name': 'Built-in Microphone', 'max_input_channels': 2},
            {'name': 'DJI_Technology_Co.__Ltd._Wireless_Microphone_RX', 'max_input_channels': 2},
            {'name': 'USB Webcam', 'max_input_channels': 1}
        ]
        expected_audio = np.random.rand(512, 2).astype(np.float32)
        mock_rec.return_value = expected_audio
        
        result = In.read(device='DJI')
        
        mock_rec.assert_called_once()
        assert mock_rec.call_args.kwargs['device'] == 1
    
    @patch('sounddevice.query_devices')
    def test_get_device_index_found(self, mock_query_devices):
        """Test getting device index when device is found."""
        mock_query_devices.return_value = [
            {'name': 'Built-in Microphone', 'max_input_channels': 2},
            {'name': 'DJI Wireless Microphone RX', 'max_input_channels': 2}
        ]
        
        device_index = In._get_device_index('DJI')
        
        assert device_index == 1
    
    @patch('sounddevice.query_devices')
    def test_get_device_index_not_found(self, mock_query_devices):
        """Test getting device index when device is not found."""
        mock_query_devices.return_value = [
            {'name': 'Built-in Microphone', 'max_input_channels': 2}
        ]
        
        device_index = In._get_device_index('NonExistent')
        
        assert device_index is None
    
    @patch('sounddevice.query_devices')
    def test_get_device_index_no_input_channels(self, mock_query_devices):
        """Test that device with no input channels is skipped."""
        mock_query_devices.return_value = [
            {'name': 'DJI Speaker Output', 'max_input_channels': 0},
            {'name': 'DJI Microphone', 'max_input_channels': 2}
        ]
        
        device_index = In._get_device_index('DJI')
        
        assert device_index == 1
    
    def test_get_device_index_none(self):
        """Test that None device name returns None."""
        device_index = In._get_device_index(None)
        
        assert device_index is None
    
    @patch('sounddevice.rec')
    def test_read_returns_ndarray(self, mock_rec):
        """Test that read returns a numpy NDArray."""
        expected_audio = np.random.rand(512, 2).astype(np.float32)
        mock_rec.return_value = expected_audio
        
        result = In.read()
        
        assert isinstance(result, np.ndarray)
        assert hasattr(result, 'shape')
        assert hasattr(result, 'dtype')
