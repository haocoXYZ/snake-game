import pygame
import struct
import math
import io

pygame.init()
try:
    pygame.mixer.init()
    print("Mixer initialized!")
except Exception as e:
    print(f"Mixer initialization failed: {e}")

def create_music_wav():
    sample_rate = 22050
    # C major / Pentatonic notes
    freqs = {
        'C3': 130.81, 'E3': 164.81, 'F3': 174.61, 'G3': 196.00, 'A3': 220.00,
        'C4': 261.63, 'D4': 293.66, 'E4': 329.63, 'G4': 392.00, 'A4': 440.00,
        'C5': 523.25, 'D5': 587.33, 'E5': 659.25, 'G5': 783.99, 'A5': 880.00,
        'C6': 1046.50
    }
    
    # 16 beats total, 0.4 seconds per beat = 6.4 seconds loop
    beat_dur = 0.4
    total_duration = 16 * beat_dur
    num_samples = int(sample_rate * total_duration)
    
    # Define melody: (beat_start, beat_len, note_name)
    melody = [
        (0, 1.0, 'E5'), (1, 1.0, 'G5'), (2, 1.0, 'A5'), (3, 1.0, 'G5'),
        (4, 1.0, 'E5'), (5, 1.0, 'D5'), (6, 1.0, 'C5'), (7, 1.0, 'D5'),
        (8, 1.0, 'E5'), (9, 1.0, 'G5'), (10, 1.0, 'C6'), (11, 1.0, 'A5'),
        (12, 1.0, 'G5'), (13, 1.0, 'E5'), (14, 1.0, 'D5'), (15, 1.0, 'C5'),
    ]
    
    # Define chords: (beat_start, beat_len, [notes])
    chords = [
        # C major
        (0, 4.0, ['C3', 'E3', 'G3']),
        # F major
        (4, 4.0, ['F3', 'A3', 'C4']),
        # A minor
        (8, 4.0, ['A3', 'C4', 'E4']),
        # G major
        (12, 4.0, ['G3', 'B3', 'D4']), # Wait, B3 is ~247Hz. Let's approximate B3 with D4/G3
    ]
    
    raw_data = bytearray()
    
    # Precompute note phases or draw dynamically
    for i in range(num_samples):
        t = i / sample_rate
        curr_beat = t / beat_dur
        
        # 1. Melody voice (Triangle wave for flute sound)
        melody_sample = 0.0
        for start, length, note in melody:
            if start <= curr_beat < (start + length):
                f = freqs.get(note, 0.0)
                if f > 0:
                    # Note envelope (soft attack, decay)
                    note_t = t - (start * beat_dur)
                    env = math.sin(note_t / (length * beat_dur) * math.pi)
                    
                    # Triangle wave: abs(mod(t, 1) - 0.5) * 4 - 1
                    cycles = f * note_t
                    tri_val = (abs((cycles % 1.0) - 0.5) * 4.0 - 1.0)
                    melody_sample = tri_val * env * 0.25
                break
                
        # 2. Chord backing voice (Sine waves for soft organ/pad sound)
        chord_sample = 0.0
        for start, length, chord_notes in chords:
            if start <= curr_beat < (start + length):
                note_t = t - (start * beat_dur)
                # Soft pad envelope (slow attack, fade out)
                env = math.sin(note_t / (length * beat_dur) * math.pi)
                
                chord_sum = 0.0
                active_notes = 0
                for note in chord_notes:
                    f = freqs.get(note, 0.0)
                    if f > 0:
                        chord_sum += math.sin(2 * math.pi * f * note_t)
                        active_notes += 1
                if active_notes > 0:
                    chord_sample = (chord_sum / active_notes) * env * 0.15
                break
                
        # Combine
        mix = melody_sample + chord_sample
        # Master volume limit
        mix = max(-1.0, min(1.0, mix))
        val_int = int(mix * 32767)
        raw_data.extend(struct.pack("<h", val_int))
        
    # RIFF WAV header
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

try:
    music_bytes = create_music_wav()
    bg_music = pygame.mixer.Sound(io.BytesIO(music_bytes))
    print(f"Music synthesized successfully: {len(music_bytes)} bytes!")
except Exception as e:
    print(f"Error: {e}")

pygame.quit()
