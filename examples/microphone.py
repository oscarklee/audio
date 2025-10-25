"""
Real-time microphone level meter with saturation indicator.

Displays a visual bar showing the audio level from 0% to 100%.
The bar turns red when approaching saturation levels.
"""
import sys
import numpy as np
from audio import In
import signal
import threading


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def get_audio_level(audio_data: np.ndarray) -> float:
    """
    Calculate the audio level as a percentage.
    
    Args:
        audio_data: Audio samples (float32 in range [-1.0, 1.0])
        
    Returns:
        Audio level percentage (0-100)
    """
    rms = np.sqrt(np.mean(audio_data ** 2))
    peak = np.abs(audio_data).max()
    
    # Amplify RMS for better visual feedback (normal speech ~50%)
    # Use peak when it exceeds RMS to show real saturation risk
    level = max(rms * 15, peak)
    return min(level * 100, 100)


def get_bar_color(level: float) -> str:
    """
    Get the appropriate color based on audio level.
    
    Args:
        level: Audio level percentage (0-100)
        
    Returns:
        ANSI color code
    """
    if level >= 85:
        return Colors.RED
    elif level >= 70:
        return Colors.YELLOW
    else:
        return Colors.GREEN


def draw_level_bar(level: float, bar_width: int = 50) -> str:
    """
    Create a visual level bar.
    
    Args:
        level: Audio level percentage (0-100)
        bar_width: Width of the bar in characters
        
    Returns:
        Formatted bar string with colors
    """
    filled_width = int((level / 100) * bar_width)
    empty_width = bar_width - filled_width
    
    color = get_bar_color(level)
    bar = f"{color}{'█' * filled_width}{Colors.RESET}{'░' * empty_width}"
    
    level_text = f"{level:5.1f}%"
    status = ""
    
    if level >= 95:
        status = f" {Colors.RED}{Colors.BOLD}⚠ SATURATING!{Colors.RESET}"
    elif level >= 85:
        status = f" {Colors.RED}⚠ Near saturation{Colors.RESET}"
    elif level >= 70:
        status = f" {Colors.YELLOW}⚡ High level{Colors.RESET}"
    
    return f"[{bar}] {color}{level_text}{Colors.RESET}{status}"


def audio_callback(indata, frames, time, status):
    level = get_audio_level(indata)
    bar = draw_level_bar(level)
    
    # Clear line and print bar
    sys.stdout.write(f"\r{bar}")
    sys.stdout.flush()


def main():
    """Run the real-time microphone level meter."""
    print(f"{Colors.BOLD}🎤 Microphone Level Meter{Colors.RESET}")
    print(f"Device: {In._default_selected_device}")
    print(f"Sample rate: {In._default_sample_rate} Hz")
    print(f"Channels: {In._default_channels}")
    print(f"\nPress Ctrl+C to stop\n")
    
    In.read(audio_callback)
    stop_event = threading.Event()
    
    def cleanup_handler(sig, frame):
        print(f"\n{Colors.BOLD}Stopping...{Colors.RESET}")
        In.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, cleanup_handler)
    signal.signal(signal.SIGTERM, cleanup_handler)
    stop_event.wait()


if __name__ == "__main__":
    main()