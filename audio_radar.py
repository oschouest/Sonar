"""
7.1 Channel Audio Radar System
Captures live 7.1 surround sound input and calculates volume levels for each channel.
Designed to work with VoiceMeeter or similar virtual audio devices.
"""

import sounddevice as sd
import numpy as np
import threading
import time
from typing import Dict, Callable, Optional


class AudioRadar:
    """
    Real-time 7.1 channel audio volume monitor.
    
    Channel mapping for 7.1 surround sound:
    0: FL (Front Left)
    1: FR (Front Right)  
    2: C  (Center)
    3: LFE (Low Frequency Effects/Subwoofer)
    4: RL (Rear Left)
    5: RR (Rear Right)
    6: SL (Side Left)
    7: SR (Side Right)
    """
    
    CHANNEL_NAMES = ["FL", "FR", "C", "LFE", "RL", "RR", "SL", "SR"]
    
    def __init__(self, 
                 sample_rate: int = 44100,
                 block_size: int = 1024,
                 device: Optional[int] = None,
                 volume_callback: Optional[Callable[[Dict[str, float]], None]] = None):
        """
        Initialize the AudioRadar.
        
        Args:
            sample_rate: Audio sample rate in Hz
            block_size: Number of frames per buffer
            device: Input device ID (None for default)
            volume_callback: Optional callback function for volume updates
        """
        self.sample_rate = sample_rate
        self.block_size = block_size
        self.device = device
        self.volume_callback = volume_callback
        
        # Current volume levels for each channel
        self.current_volumes = {name: 0.0 for name in self.CHANNEL_NAMES}
        
        # Threading controls
        self._running = False
        self._stream = None
        self._lock = threading.Lock()
        
        # Smoothing factor for volume averaging (0.0 = no smoothing, 1.0 = maximum smoothing)
        self.smoothing_factor = 0.8
        
    def _audio_callback(self, indata: np.ndarray, frames: int, time_info, status):
        """
        Callback function for audio stream processing.
        Handles both stereo (2-channel) and 7.1 (8-channel) audio intelligently.
        
        Args:
            indata: Input audio data array (frames, channels)
            frames: Number of frames in the buffer
            time_info: Timing information
            status: Stream status
        """
        if status:
            print(f"Audio stream status: {status}")
        
        num_channels = indata.shape[1]
        volumes = {}
        
        # Debug: Show raw audio activity
        raw_level = np.sqrt(np.mean(indata**2))
        if raw_level > 0.001:  # Only print if there's significant audio
            print(f"🎵 Raw audio detected: {raw_level:.4f} ({num_channels} channels)")
        
        if num_channels == 2:
            # Enhanced stereo-to-surround mapping with dynamic positioning
            left_channel = indata[:, 0]
            right_channel = indata[:, 1]
            
            # Calculate RMS for left and right
            left_rms = np.sqrt(np.mean(left_channel ** 2))
            right_rms = np.sqrt(np.mean(right_channel ** 2))
            
            # Enhanced stereo imaging calculations
            total_energy = left_rms + right_rms
            center_energy = min(left_rms, right_rms)
            side_energy = abs(left_rms - right_rms)
            
            # Calculate pan position: -1 (full left) to +1 (full right)
            if total_energy > 0:
                pan = (right_rms - left_rms) / total_energy
            else:
                pan = 0
            
            # Much lower threshold for better sensitivity to quiet sounds
            min_threshold = 0.004  # Significantly lowered
            
            if total_energy > min_threshold:
                # Advanced surround mapping based on stereo characteristics
                
                # Front channels - Enhanced positioning
                if abs(pan) > 0.2:  # Strong left/right bias
                    if pan < -0.2:  # Left dominant
                        volumes["FL"] = left_rms * 1.3  # Boost primary channel
                        volumes["FR"] = right_rms * 0.4  # Reduce secondary
                        # Add rear presence for immersion
                        volumes["RL"] = left_rms * 0.6
                        volumes["SL"] = left_rms * 0.8  # Strong side presence
                        volumes["SR"] = right_rms * 0.3
                    elif pan > 0.2:  # Right dominant
                        volumes["FR"] = right_rms * 1.3  # Boost primary channel
                        volumes["FL"] = left_rms * 0.4   # Reduce secondary
                        # Add rear presence for immersion
                        volumes["RR"] = right_rms * 0.6
                        volumes["SR"] = right_rms * 0.8  # Strong side presence
                        volumes["SL"] = left_rms * 0.3
                else:  # Center-ish positioning
                    volumes["FL"] = left_rms * 0.9
                    volumes["FR"] = right_rms * 0.9
                    volumes["SL"] = left_rms * 0.5
                    volumes["SR"] = right_rms * 0.5
                
                # Center channel - Enhanced for dialogue and central sounds
                if center_energy > min_threshold:
                    volumes["C"] = center_energy * 1.2
                
                # LFE - Enhanced bass presence
                volumes["LFE"] = total_energy * 0.4
                
                # Rear channel estimation using phase correlation
                try:
                    if len(left_channel) > 1 and len(right_channel) > 1:
                        # Calculate correlation between L/R channels
                        correlation = np.corrcoef(left_channel, right_channel)[0,1]
                        
                        # Low correlation suggests surround/ambient content
                        if correlation < 0.85:
                            rear_factor = (0.85 - correlation) * 2.0
                            base_rear = total_energy * rear_factor * 0.5
                            
                            # Distribute rear based on pan with enhancement
                            if pan < -0.1:
                                volumes["RL"] = max(volumes.get("RL", 0), base_rear * 1.4)
                                volumes["RR"] = max(volumes.get("RR", 0), base_rear * 0.6)
                            elif pan > 0.1:
                                volumes["RR"] = max(volumes.get("RR", 0), base_rear * 1.4)
                                volumes["RL"] = max(volumes.get("RL", 0), base_rear * 0.6)
                            else:
                                volumes["RL"] = max(volumes.get("RL", 0), base_rear)
                                volumes["RR"] = max(volumes.get("RR", 0), base_rear)
                except:
                    # Fallback rear channel mapping
                    rear_base = total_energy * 0.3
                    volumes["RL"] = max(volumes.get("RL", 0), rear_base)
                    volumes["RR"] = max(volumes.get("RR", 0), rear_base)
                
                # Dynamic range enhancement - boost subtle differences
                for channel in list(volumes.keys()):
                    if volumes[channel] < min_threshold * 3:
                        volumes[channel] *= 1.8  # Significantly boost quiet sounds
                    elif volumes[channel] < min_threshold * 6:
                        volumes[channel] *= 1.4  # Moderately boost medium sounds
            
        elif num_channels >= 8:
            # True 7.1 or higher - use actual channels
            for i, channel_name in enumerate(self.CHANNEL_NAMES):
                if i < num_channels:
                    rms = np.sqrt(np.mean(indata[:, i] ** 2))
                    volumes[channel_name] = rms
                else:
                    volumes[channel_name] = 0.0
                    
        else:
            # Mono or other configurations
            if num_channels == 1:
                # Mono - distribute to all channels
                mono_rms = np.sqrt(np.mean(indata[:, 0] ** 2))
                for channel_name in self.CHANNEL_NAMES:
                    volumes[channel_name] = mono_rms * 0.8
            else:
                # Unknown configuration - zero out
                for channel_name in self.CHANNEL_NAMES:
                    volumes[channel_name] = 0.0
        
        # Debug: Show mapped volumes if any are significant
        significant_volumes = {k: v for k, v in volumes.items() if v > 0.01}
        if significant_volumes:
            print(f"🎯 Mapped volumes: {significant_volumes}")
        
        # Apply smoothing to all channels
        with self._lock:
            for channel_name, raw_volume in volumes.items():
                if channel_name in self.current_volumes:
                    smoothed_volume = (self.smoothing_factor * self.current_volumes[channel_name] + 
                                     (1 - self.smoothing_factor) * raw_volume)
                else:
                    smoothed_volume = raw_volume
                
                volumes[channel_name] = smoothed_volume
                self.current_volumes[channel_name] = smoothed_volume
        
        # Call the user-provided callback if available
        if self.volume_callback:
            try:
                self.volume_callback(volumes.copy())
            except Exception as e:
                print(f"Error in volume callback: {e}")
    
    def start(self):
        """Start the audio capture and processing."""
        if self._running:
            print("AudioRadar is already running")
            return
            
        try:
            # List available devices for debugging
            self.list_audio_devices()
            
            print(f"Starting AudioRadar...")
            print(f"Sample rate: {self.sample_rate} Hz")
            print(f"Block size: {self.block_size} frames")
            print(f"Device: {self.device if self.device is not None else 'Default'}")
            
            # Try different channel configurations in order of preference
            channel_configs = [8, 2, 1]  # 7.1, stereo, mono
            
            for channels in channel_configs:
                try:
                    print(f"Trying {channels} channel(s)...")
                    
                    # Create and start the audio stream
                    self._stream = sd.InputStream(
                        device=self.device,
                        channels=channels,
                        samplerate=self.sample_rate,
                        blocksize=self.block_size,
                        callback=self._audio_callback,
                        dtype=np.float32
                    )
                    
                    self._stream.start()
                    self._running = True
                    print(f"AudioRadar started successfully with {channels} channel(s)!")
                    
                    if channels == 2:
                        print("📻 Stereo mode: Mapping L/R to 7.1 channels intelligently")
                    elif channels == 1:
                        print("🔊 Mono mode: Distributing signal to all channels")
                    else:
                        print("🎯 True 7.1 mode: Using actual surround channels")
                    
                    return  # Success, exit the retry loop
                    
                except Exception as channel_error:
                    print(f"   Failed with {channels} channels: {channel_error}")
                    if self._stream:
                        try:
                            self._stream.close()
                        except:
                            pass
                        self._stream = None
                    continue
            
            # If we get here, all channel configurations failed
            raise Exception("Could not start audio stream with any channel configuration")
            
        except Exception as e:
            print(f"Error starting AudioRadar: {e}")
            self._running = False
            raise
    
    def stop(self):
        """Stop the audio capture and processing."""
        if not self._running:
            return
            
        print("Stopping AudioRadar...")
        self._running = False
        
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None
            
        print("AudioRadar stopped")
    
    def get_volumes(self) -> Dict[str, float]:
        """
        Get the current volume levels for all channels.
        
        Returns:
            Dictionary with channel names as keys and volume levels as values
        """
        with self._lock:
            return self.current_volumes.copy()
    
    def is_running(self) -> bool:
        """Check if the AudioRadar is currently running."""
        return self._running
    
    @staticmethod
    def list_audio_devices():
        """List all available audio input devices."""
        print("\nAvailable audio devices:")
        devices = sd.query_devices()
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                print(f"  {i}: {device['name']} "
                      f"(Channels: {device['max_input_channels']}, "
                      f"Sample Rate: {device['default_samplerate']} Hz)")
    
    def set_smoothing(self, factor: float):
        """
        Set the volume smoothing factor.
        
        Args:
            factor: Smoothing factor between 0.0 (no smoothing) and 1.0 (maximum smoothing)
        """
        self.smoothing_factor = max(0.0, min(1.0, factor))
        print(f"Smoothing factor set to: {self.smoothing_factor}")


def example_volume_callback(volumes: Dict[str, float]):
    """
    Example callback function that prints volume levels.
    Replace this with your GUI update logic.
    """
    # Format volumes for display
    volume_str = " | ".join([f"{ch}: {vol:.3f}" for ch, vol in volumes.items()])
    print(f"\rVolumes: {volume_str}", end="", flush=True)


def main():
    """
    Example usage of the AudioRadar class.
    """
    print("7.1 Channel Audio Radar System")
    print("=" * 40)
    
    # Create AudioRadar instance with callback
    radar = AudioRadar(
        sample_rate=44100,
        block_size=1024,
        device=None,  # Use default device, or specify device ID
        volume_callback=example_volume_callback
    )
    
    try:
        # Start the audio capture
        radar.start()
        
        print("\nMonitoring audio... Press Ctrl+C to stop")
        print("Channel mapping: FL=Front Left, FR=Front Right, C=Center, LFE=Subwoofer,")
        print("                 RL=Rear Left, RR=Rear Right, SL=Side Left, SR=Side Right")
        print("-" * 80)
        
        # Keep the program running
        while radar.is_running():
            time.sleep(0.1)
            
            # You can also get volumes manually:
            # volumes = radar.get_volumes()
            # print(f"Manual check: {volumes}")
            
    except KeyboardInterrupt:
        print("\n\nStopping...")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        radar.stop()


if __name__ == "__main__":
    main()
