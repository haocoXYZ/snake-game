import pygame
import struct
import io
import math
import random

pygame.init()
try:
    pygame.mixer.init()
    print("Mixer initialized successfully!")
except Exception as e:
    print(f"Failed to initialize mixer: {e}")

def create_sweep_wav(start_freq, end_freq, duration, volume=0.5):
    sample_rate = 22050
    num_samples = int(sample_rate * duration)
    raw_data = bytearray()
    
    for i in range(num_samples):
        t = i / sample_rate
        # Quadratic/linear sweep phase
        phase = 2 * math.pi * (start_freq * t + 0.5 * (end_freq - start_freq) * (t**2 / duration))
        val = math.sin(phase)
        
        # Exponential or linear fade out
        envelope = (num_samples - i) / num_samples
        val *= envelope
        
        val_int = int(val * volume * 32767)
        raw_data.extend(struct.pack("<h", val_int))
        
    return make_wav_header(raw_data, sample_rate)

def create_hiss_wav(duration, volume=0.5):
    sample_rate = 22050
    num_samples = int(sample_rate * duration)
    raw_data = bytearray()
    
    prev_val = 0
    for i in range(num_samples):
        curr = random.uniform(-1.0, 1.0)
        # High pass filter to make it sound like a hiss
        val = curr - prev_val
        prev_val = curr
        
        # Envelope: fade out
        envelope = (num_samples - i) / num_samples
        val *= envelope
        
        val_int = int(val * volume * 16384) # keep volume safe
        raw_data.extend(struct.pack("<h", val_int))
        
    return make_wav_header(raw_data, sample_rate)

def create_rattle_wav(duration, volume=0.5):
    sample_rate = 22050
    num_samples = int(sample_rate * duration)
    raw_data = bytearray()
    
    prev_val = 0
    for i in range(num_samples):
        # Bursts of high pass noise
        burst = 1.0 if (i % 1000 < 400) else 0.0
        curr = random.uniform(-1.0, 1.0) * burst
        val = curr - prev_val
        prev_val = curr
        
        envelope = (num_samples - i) / num_samples
        val *= envelope
        
        val_int = int(val * volume * 16384)
        raw_data.extend(struct.pack("<h", val_int))
        
    return make_wav_header(raw_data, sample_rate)

def create_bubble_wav(duration, volume=0.5):
    sample_rate = 22050
    num_samples = int(sample_rate * duration)
    raw_data = bytearray()
    
    for i in range(num_samples):
        t = i / sample_rate
        # Frequency modulation for a sci-fi bubble sound
        freq = 150 + 400 * math.sin(t * math.pi / duration)
        phase = 2 * math.pi * freq * t
        val = math.sin(phase)
        
        envelope = (num_samples - i) / num_samples
        val *= envelope
        
        val_int = int(val * volume * 32767)
        raw_data.extend(struct.pack("<h", val_int))
        
    return make_wav_header(raw_data, sample_rate)

def make_wav_header(raw_data, sample_rate):
    header = bytearray()
    header.extend(b"RIFF")
    header.extend(struct.pack("<I", 36 + len(raw_data)))
    header.extend(b"WAVE")
    header.extend(b"fmt ")
    header.extend(struct.pack("<I", 16))
    header.extend(struct.pack("<H", 1)) # PCM
    header.extend(struct.pack("<H", 1)) # Mono
    header.extend(struct.pack("<I", sample_rate))
    header.extend(struct.pack("<I", sample_rate * 2))
    header.extend(struct.pack("<H", 2)) # BlockAlign
    header.extend(struct.pack("<H", 16)) # BitsPerSample
    header.extend(b"data")
    header.extend(struct.pack("<I", len(raw_data)))
    return bytes(header + raw_data)

# Test creating sounds
try:
    eat_sound = pygame.mixer.Sound(io.BytesIO(create_sweep_wav(523, 880, 0.15)))
    hit_sound = pygame.mixer.Sound(io.BytesIO(create_sweep_wav(150, 40, 0.5, volume=0.8)))
    click_sound = pygame.mixer.Sound(io.BytesIO(create_sweep_wav(600, 400, 0.05)))
    
    sound_corn = pygame.mixer.Sound(io.BytesIO(create_rattle_wav(0.4)))
    sound_garter = pygame.mixer.Sound(io.BytesIO(create_hiss_wav(0.5)))
    sound_blackberry = pygame.mixer.Sound(io.BytesIO(create_bubble_wav(0.35)))
    
    print("All sounds generated and loaded successfully into Pygame Sound objects!")
except Exception as e:
    print(f"Error generating sounds: {e}")

pygame.quit()
