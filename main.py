import pygame
import random
import sys
import json
import os
import asyncio
import math
import struct
import io

pygame.init()

# Change directory to script's directory to resolve relative paths for web assets
try:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
except:
    pass

# --- Audio Synthesis & Mixer Setup ---
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

def create_sweep_wav(start_freq, end_freq, duration, volume=0.5):
    sample_rate = 22050
    num_samples = int(sample_rate * duration)
    raw_data = bytearray()
    for i in range(num_samples):
        t = i / sample_rate
        phase = 2 * math.pi * (start_freq * t + 0.5 * (end_freq - start_freq) * (t**2 / duration))
        val = math.sin(phase)
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
        val = curr - prev_val
        prev_val = curr
        envelope = (num_samples - i) / num_samples
        val *= envelope
        val_int = int(val * volume * 16384)
        raw_data.extend(struct.pack("<h", val_int))
    return make_wav_header(raw_data, sample_rate)

def create_rattle_wav(duration, volume=0.5):
    sample_rate = 22050
    num_samples = int(sample_rate * duration)
    raw_data = bytearray()
    prev_val = 0
    for i in range(num_samples):
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
        freq = 150 + 400 * math.sin(t * math.pi / duration)
        phase = 2 * math.pi * freq * t
        val = math.sin(phase)
        envelope = (num_samples - i) / num_samples
        val *= envelope
        val_int = int(val * volume * 32767)
        raw_data.extend(struct.pack("<h", val_int))
    return make_wav_header(raw_data, sample_rate)

def create_thump_wav(duration, volume=0.7):
    sample_rate = 22050
    num_samples = int(sample_rate * duration)
    raw_data = bytearray()
    for i in range(num_samples):
        t = i / sample_rate
        freq = 150 * (1.0 - t/duration) + 20 * (t/duration)
        phase = 2 * math.pi * freq * t
        noise = random.uniform(-1.0, 1.0) * 0.18
        val = math.sin(phase) + noise
        env = math.exp(-6.0 * t / duration)
        val *= env
        val = max(-1.0, min(1.0, val))
        val_int = int(val * volume * 32767)
        raw_data.extend(struct.pack("<h", val_int))
    return make_wav_header(raw_data, sample_rate)

def create_music_wav():
    sample_rate = 22050
    freqs = {
        'C3': 130.81, 'E3': 164.81, 'F3': 174.61, 'G3': 196.00, 'A3': 220.00,
        'B3': 246.94, 'C4': 261.63, 'D4': 293.66, 'E4': 329.63, 'G4': 392.00,
        'A4': 440.00, 'C5': 523.25, 'D5': 587.33, 'E5': 659.25, 'G5': 783.99,
        'A5': 880.00, 'C6': 1046.50
    }
    beat_dur = 0.4
    total_duration = 16 * beat_dur
    num_samples = int(sample_rate * total_duration)
    
    melody = [
        (0, 1.0, 'E5'), (1, 1.0, 'G5'), (2, 1.0, 'A5'), (3, 1.0, 'G5'),
        (4, 1.0, 'E5'), (5, 1.0, 'D5'), (6, 1.0, 'C5'), (7, 1.0, 'D5'),
        (8, 1.0, 'E5'), (9, 1.0, 'G5'), (10, 1.0, 'C6'), (11, 1.0, 'A5'),
        (12, 1.0, 'G5'), (13, 1.0, 'E5'), (14, 1.0, 'D5'), (15, 1.0, 'C5'),
    ]
    
    chords = [
        (0, 4.0, ['C3', 'E3', 'G3']),
        (4, 4.0, ['F3', 'A3', 'C4']),
        (8, 4.0, ['A3', 'C4', 'E4']),
        (12, 4.0, ['G3', 'B3', 'D4']),
    ]
    
    raw_data = bytearray()
    for i in range(num_samples):
        t = i / sample_rate
        curr_beat = t / beat_dur
        melody_sample = 0.0
        for start, length, note in melody:
            if start <= curr_beat < (start + length):
                f = freqs.get(note, 0.0)
                if f > 0:
                    note_t = t - (start * beat_dur)
                    env = math.sin(note_t / (length * beat_dur) * math.pi)
                    cycles = f * note_t
                    tri_val = (abs((cycles % 1.0) - 0.5) * 4.0 - 1.0)
                    melody_sample = tri_val * env * 0.25
                break
                
        chord_sample = 0.0
        for start, length, chord_notes in chords:
            if start <= curr_beat < (start + length):
                note_t = t - (start * beat_dur)
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
                
        mix = melody_sample + chord_sample
        mix = max(-1.0, min(1.0, mix))
        val_int = int(mix * 32767)
        raw_data.extend(struct.pack("<h", val_int))
        
    return make_wav_header(raw_data, sample_rate)

eat_sound = None
hit_sound = None
click_sound = None
sound_corn = None
sound_garter = None
sound_blackberry = None
bg_music = None
capybara_land_sound = None

try:
    pygame.mixer.init()
    eat_sound = pygame.mixer.Sound(io.BytesIO(create_sweep_wav(523, 880, 0.15)))
    hit_sound = pygame.mixer.Sound(io.BytesIO(create_sweep_wav(150, 40, 0.5, volume=0.8)))
    click_sound = pygame.mixer.Sound(io.BytesIO(create_sweep_wav(600, 400, 0.05)))
    sound_corn = pygame.mixer.Sound(io.BytesIO(create_rattle_wav(0.4)))
    sound_garter = pygame.mixer.Sound(io.BytesIO(create_hiss_wav(0.5)))
    sound_blackberry = pygame.mixer.Sound(io.BytesIO(create_bubble_wav(0.35)))
    bg_music = pygame.mixer.Sound(io.BytesIO(create_music_wav()))
    capybara_land_sound = pygame.mixer.Sound(io.BytesIO(create_thump_wav(0.4, volume=0.85)))
    
    bg_music.set_volume(0.15)
    eat_sound.set_volume(0.5)
    hit_sound.set_volume(0.6)
    click_sound.set_volume(0.4)
    sound_corn.set_volume(0.5)
    sound_garter.set_volume(0.5)
    sound_blackberry.set_volume(0.5)
    capybara_land_sound.set_volume(0.7)
except Exception as e:
    pass

def play_sound(sound):
    if sound and sound_on:
        try:
            sound.play()
        except:
            pass

def play_snake_sound(snake_id):
    if snake_id == "cobra":
        play_sound(sound_corn)
    elif snake_id == "taipan":
        play_sound(sound_garter)
    elif snake_id == "mamba":
        play_sound(sound_blackberry)

# --- Stardew Valley Theme Colors ---
BG_COLOR = (34, 112, 63)      # Cozy grass green
GRID_COLOR = (50, 80, 50)     # Subtle moss green
FOOD_COLOR = (231, 76, 60)    # Red apple/berry
OBSTACLE_COLOR = (105, 55, 25) # Wood brown
OBSTACLE_INNER = (65, 30, 10)  # Darker wood
SCORE_BG = (78, 41, 16)       # Wooden header brown
SCORE_LINE = (243, 175, 59)   # Gold border accent
TEXT_COLOR = (78, 41, 16)     # Dark brown wood text
GOLD_COLOR = (243, 175, 59)   # Gold highlight
PARCHMENT_COLOR = (247, 235, 198) # Cream parchment panel

SNAKE_PROFILES = {
    "cobra": {
        "name": "Gold Corn Snake",
        "body": (231, 145, 47),   # Warm orange
        "body_alt": (243, 175, 59), # Warm gold-yellow
        "head": (200, 115, 30)    # Warm gold-brown
    },
    "taipan": {
        "name": "Garden Garter",
        "body": (68, 122, 60),    # Moss green
        "body_alt": (120, 175, 90), # Light green
        "head": (50, 95, 43)      # Leaf green
    },
    "mamba": {
        "name": "Wild Blackberry",
        "body": (54, 43, 68),     # Deep purple
        "body_alt": (110, 80, 130), # Soft magenta/purple
        "head": (38, 29, 50)      # Dark purple
    }
}

# Current Snake Colors (Default)
SNAKE_BODY = SNAKE_PROFILES["cobra"]["body"]
SNAKE_BODY_ALT = SNAKE_PROFILES["cobra"]["body_alt"]
SNAKE_HEAD = SNAKE_PROFILES["cobra"]["head"]
current_snake_name = SNAKE_PROFILES["cobra"]["name"]
current_snake_id = "cobra"

# --- Dimensions ---
WIDTH = 800
HEIGHT = 600
BLOCK_SIZE = 20
PLAY_Y_START = 40

dis = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Sneak the Snake')

clock = pygame.time.Clock()
SNAKE_SPEED = 15
sound_on = True
music_on = True

# App State
app_state = "menu"
SCORE_FILE = "scores.json"
SETTINGS_FILE = "settings.json"

# --- Fonts ---
try:
    font_style = pygame.font.Font("Roboto.ttf", 50)
    score_font = pygame.font.Font("Roboto.ttf", 24)
    btn_font = pygame.font.Font("Roboto.ttf", 25)
except:
    pass

# --- Background Image ---
bg_img = None
bg_img_menu = None
try:
    bg_img = pygame.image.load("stardew_bg.png")
    bg_img_menu = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))
except Exception as e:
    pass

# --- Checkerboard Background for In-Game ---
bg_game_surf = pygame.Surface((WIDTH, HEIGHT - PLAY_Y_START))
for x in range(0, WIDTH, BLOCK_SIZE):
    for y in range(0, HEIGHT - PLAY_Y_START, BLOCK_SIZE):
        col = x // BLOCK_SIZE
        row = y // BLOCK_SIZE
        if (col + row) % 2 == 0:
            color = (170, 215, 81)   # Light green checker
        else:
            color = (162, 209, 73)   # Darker green checker
        pygame.draw.rect(bg_game_surf, color, [x, y, BLOCK_SIZE, BLOCK_SIZE])

def draw_game_background():
    dis.blit(bg_game_surf, (0, PLAY_Y_START))

def load_scores():
    if sys.platform == "emscripten":
        try:
            from platform import window
            saved_data = window.localStorage.getItem("sneak_snake_scores")
            if saved_data:
                return json.loads(saved_data)
        except Exception as e:
            pass
        return []
    else:
        if not os.path.exists(SCORE_FILE):
            return []
        try:
            with open(SCORE_FILE, "r") as f:
                return json.load(f)
        except:
            return []

def save_score(score, snake_name):
    scores = load_scores()
    scores.append({"score": score, "snake": snake_name})
    # Sort by score descending
    scores = sorted(scores, key=lambda x: x["score"], reverse=True)
    # Keep top 5
    scores = scores[:5]
    
    if sys.platform == "emscripten":
        try:
            from platform import window
            window.localStorage.setItem("sneak_snake_scores", json.dumps(scores))
        except Exception as e:
            pass
    else:
        try:
            with open(SCORE_FILE, "w") as f:
                json.dump(scores, f)
        except:
            pass

def load_settings():
    global SNAKE_SPEED, SNAKE_BODY, SNAKE_BODY_ALT, SNAKE_HEAD, current_snake_name, current_snake_id, sound_on, music_on
    data = None
    if sys.platform == "emscripten":
        try:
            from platform import window
            saved_data = window.localStorage.getItem("sneak_snake_settings")
            if saved_data:
                data = json.loads(saved_data)
        except:
            pass
    else:
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r") as f:
                     data = json.load(f)
            except:
                pass
    if data:
        if "speed" in data:
            SNAKE_SPEED = data["speed"]
        if "sound_on" in data:
            sound_on = data["sound_on"]
        if "music_on" in data:
            music_on = data["music_on"]
        if "snake_id" in data:
            snake_id = data["snake_id"]
            if snake_id in SNAKE_PROFILES:
                SNAKE_BODY = SNAKE_PROFILES[snake_id]["body"]
                SNAKE_BODY_ALT = SNAKE_PROFILES[snake_id]["body_alt"]
                SNAKE_HEAD = SNAKE_PROFILES[snake_id]["head"]
                current_snake_name = SNAKE_PROFILES[snake_id]["name"]
                current_snake_id = snake_id

def save_settings():
    data = {
        "speed": SNAKE_SPEED,
        "snake_id": current_snake_id,
        "sound_on": sound_on,
        "music_on": music_on
    }
    if sys.platform == "emscripten":
        try:
            from platform import window
            window.localStorage.setItem("sneak_snake_settings", json.dumps(data))
        except:
            pass
    else:
        try:
            with open(SETTINGS_FILE, "w") as f:
                json.dump(data, f)
        except:
            pass

def draw_text_shadow(msg, font, color, center_pos, shadow_color=(78, 41, 16), offset=2):
    text_surf = font.render(msg, True, shadow_color)
    text_rect = text_surf.get_rect(center=(center_pos[0] + offset, center_pos[1] + offset))
    dis.blit(text_surf, text_rect)
    text_surf = font.render(msg, True, color)
    text_rect = text_surf.get_rect(center=center_pos)
    dis.blit(text_surf, text_rect)

def draw_rust_panel(rect):
    # Draw dark brown border
    pygame.draw.rect(dis, (78, 41, 16), rect, border_radius=6)
    # Draw gold outline inside
    inner_gold = [rect[0] + 3, rect[1] + 3, rect[2] - 6, rect[3] - 6]
    pygame.draw.rect(dis, (243, 175, 59), inner_gold, width=2, border_radius=4)
    # Fill interior with parchment
    inner_fill = [rect[0] + 5, rect[1] + 5, rect[2] - 10, rect[3] - 10]
    pygame.draw.rect(dis, (247, 235, 198), inner_fill, border_radius=3)

def draw_grid():
    # Grid lines are replaced by the checkerboard pattern
    pass

def draw_instruction_graphic(cx, cy):
    # Main panel (dark green rounded rectangle, 120x100)
    pygame.draw.rect(dis, (48, 85, 33), [cx - 60, cy - 50, 120, 100], border_radius=20)
    
    # Keyboard center for arrows
    kx = cx - 12
    ky = cy
    
    # Draw arrow keys (white squares with dark green triangles)
    keys = {
        'up': [kx, ky - 26, 24, 24],
        'down': [kx, ky + 2, 24, 24],
        'left': [kx - 26, ky + 2, 24, 24],
        'right': [kx + 26, ky + 2, 24, 24]
    }
    
    for key_dir, rect in keys.items():
        pygame.draw.rect(dis, (255, 255, 255), rect, border_radius=5)
        
        # Triangles pointing in respective directions
        rx, ry, rw, rh = rect
        kx_c = rx + rw // 2
        ky_c = ry + rh // 2
        
        if key_dir == 'up':
            pts = [(kx_c, ky_c - 6), (kx_c - 5, ky_c + 4), (kx_c + 5, ky_c + 4)]
        elif key_dir == 'down':
            pts = [(kx_c, ky_c + 6), (kx_c - 5, ky_c - 4), (kx_c + 5, ky_c - 4)]
        elif key_dir == 'left':
            pts = [(kx_c - 6, ky_c), (kx_c + 4, ky_c - 5), (kx_c + 4, ky_c + 5)]
        elif key_dir == 'right':
            pts = [(kx_c + 6, ky_c), (kx_c - 4, ky_c - 5), (kx_c - 4, ky_c + 5)]
            
        pygame.draw.polygon(dis, (48, 85, 33), pts)



def draw_score(score):
    # Background
    pygame.draw.rect(dis, (78, 41, 16), [0, 0, WIDTH, PLAY_Y_START])
    # Gold separator line
    pygame.draw.line(dis, (243, 175, 59), (0, PLAY_Y_START - 2), (WIDTH, PLAY_Y_START - 2), 3)
    
    # Score Text (shadowed)
    draw_text_shadow(f"SCORE: {score}", score_font, (243, 175, 59), (80, PLAY_Y_START // 2), shadow_color=(30, 15, 5), offset=2)
    # Breed Text (shadowed)
    draw_text_shadow(f"BREED: {current_snake_name.upper()}", score_font, (243, 175, 59), (WIDTH // 2, PLAY_Y_START // 2), shadow_color=(30, 15, 5), offset=2)
    # Speed Text (shadowed)
    draw_text_shadow(f"SPEED: {SNAKE_SPEED}", score_font, (243, 175, 59), (WIDTH - 120, PLAY_Y_START // 2), shadow_color=(30, 15, 5), offset=2)

    # Pause Button
    mouse_pos = pygame.mouse.get_pos()
    pause_hover = (755 <= mouse_pos[0] <= 785 and 5 <= mouse_pos[1] <= 35)
    draw_pause_icon(755, 5, size=30, hover=pause_hover)

def draw_snake(block_size, snake_list, prev_snake_list, t, x_change=0, y_change=0, food_pos=None, dead=False):
    n = len(snake_list)
    m = len(prev_snake_list)
    
    for i, x in enumerate(snake_list):
        is_head = (i == n - 1)
        is_tail = (i == 0)
        
        # Calculate interpolated position for smooth drawing
        if m > 0:
            d = (n - 1) - i
            j = (m - 1) - d
            if j >= 0:
                prev_pos = prev_snake_list[j]
            else:
                prev_pos = x
            draw_x = prev_pos[0] + (x[0] - prev_pos[0]) * t
            draw_y = prev_pos[1] + (x[1] - prev_pos[1]) * t
        else:
            draw_x = x[0]
            draw_y = x[1]
            
        cx = draw_x + block_size / 2.0
        cy = draw_y + block_size / 2.0
        rect = [int(draw_x), int(draw_y), block_size, block_size]
        
        # Head direction
        dx, dy = 0, -1
        if n > 1:
            if is_head:
                prev = snake_list[-2]
                dx = x[0] - prev[0]
                dy = x[1] - prev[1]
            else:
                nxt = snake_list[i+1]
                dx = nxt[0] - x[0]
                dy = nxt[1] - x[1]
                
            if dx != 0: dx = dx / abs(dx)
            if dy != 0: dy = dy / abs(dy)
        else:
            if x_change != 0: 
                dx = x_change / abs(x_change)
                dy = 0
            elif y_change != 0: 
                dx = 0
                dy = y_change / abs(y_change)

        if is_head:
            # Bullet-shaped head: front corners rounded 11, back corners rounded 4
            if dx > 0:
                r_tl, r_tr, r_br, r_bl = 4, 11, 11, 4
            elif dx < 0:
                r_tl, r_tr, r_br, r_bl = 11, 4, 4, 11
            elif dy > 0:
                r_tl, r_tr, r_br, r_bl = 4, 4, 11, 11
            else:  # dy < 0
                r_tl, r_tr, r_br, r_bl = 11, 11, 4, 4

            if current_snake_id == "cobra":
                hood_color = (185, 100, 20)
                hood_rect = None
                if dx > 0:
                    hood_rect = [int(draw_x) - 5, int(draw_y) - 8, block_size, block_size + 16]
                elif dx < 0:
                    hood_rect = [int(draw_x) + 5, int(draw_y) - 8, block_size, block_size + 16]
                elif dy > 0:
                    hood_rect = [int(draw_x) - 8, int(draw_y) - 5, block_size + 16, block_size]
                elif dy < 0:
                    hood_rect = [int(draw_x) - 8, int(draw_y) + 5, block_size + 16, block_size]
                
                if hood_rect:
                    pygame.draw.ellipse(dis, hood_color, hood_rect)

            pygame.draw.rect(
                dis, 
                SNAKE_HEAD, 
                rect, 
                border_top_left_radius=r_tl,
                border_top_right_radius=r_tr,
                border_bottom_left_radius=r_bl,
                border_bottom_right_radius=r_br
            )
            
            # Position eyes perpendicular to travel direction
            if dx > 0:
                ex1, ey1 = cx + 4, cy - 5
                ex2, ey2 = cx + 4, cy + 5
            elif dx < 0:
                ex1, ey1 = cx - 4, cy - 5
                ex2, ey2 = cx - 4, cy + 5
            elif dy > 0:
                ex1, ey1 = cx - 5, cy + 4
                ex2, ey2 = cx + 5, cy + 4
            else:
                ex1, ey1 = cx - 5, cy - 4
                ex2, ey2 = cx + 5, cy - 4

            if dead:
                # Dazed cross eyes on game over
                for ex, ey in [(ex1, ey1), (ex2, ey2)]:
                    pygame.draw.line(dis, (78, 41, 16), (int(ex) - 3, int(ey) - 3), (int(ex) + 3, int(ey) + 3), 2)
                    pygame.draw.line(dis, (78, 41, 16), (int(ex) + 3, int(ey) - 3), (int(ex) - 3, int(ey) + 3), 2)
            else:
                # Blink every 3 seconds for 150ms
                is_blinking = (pygame.time.get_ticks() % 3000) < 150
                if is_blinking:
                    for ex, ey in [(ex1, ey1), (ex2, ey2)]:
                        pygame.draw.line(dis, (78, 41, 16), (int(ex) - 3, int(ey)), (int(ex) + 3, int(ey)), 2)
                else:
                    # Draw eye whites
                    pygame.draw.circle(dis, (255, 255, 255), (int(ex1), int(ey1)), 4)
                    pygame.draw.circle(dis, (255, 255, 255), (int(ex2), int(ey2)), 4)
                    
                    # Pupil tracking food position
                    if food_pos is not None:
                        fx, fy = food_pos
                        fcx, fcy = fx + 10, fy + 10
                        
                        vx1, vy1 = fcx - ex1, fcy - ey1
                        d1 = (vx1**2 + vy1**2)**0.5
                        px1 = ex1 + (vx1 / d1) * 1.5 if d1 > 0 else ex1
                        py1 = ey1 + (vy1 / d1) * 1.5 if d1 > 0 else ey1

                        vx2, vy2 = fcx - ex2, fcy - ey2
                        d2 = (vx2**2 + vy2**2)**0.5
                        px2 = ex2 + (vx2 / d2) * 1.5 if d2 > 0 else ex2
                        py2 = ey2 + (vy2 / d2) * 1.5 if d2 > 0 else ey2
                    else:
                        px1, py1 = ex1 + dx, ey1 + dy
                        px2, py2 = ex2 + dx, ey2 + dy
                        
                    # Draw pupils
                    pygame.draw.circle(dis, (0, 0, 0), (int(px1), int(py1)), 1)
                    pygame.draw.circle(dis, (0, 0, 0), (int(px2), int(py2)), 1)

            # Open mouth and flick tongue when close to food
            dist_to_food = 999.0
            if food_pos is not None:
                fx, fy = food_pos
                dist_to_food = ((draw_x - fx)**2 + (draw_y - fy)**2)**0.5

            if dist_to_food <= 80 and not dead:
                # Draw open mouth
                mx = cx + dx * 7
                my = cy + dy * 7
                if dx != 0:
                    pygame.draw.ellipse(dis, (65, 30, 10), [int(mx) - 2, int(my) - 3, 4, 6])
                else:
                    pygame.draw.ellipse(dis, (65, 30, 10), [int(mx) - 3, int(my) - 2, 6, 4])
                
                # Active flicking tongue
                ticks = pygame.time.get_ticks()
                if ticks % 300 < 200:
                    flick_t = (ticks % 300) / 300.0
                    t_len = 6 + 10 * math.sin(flick_t * math.pi)
                    tx = cx + dx * (8 + t_len)
                    ty = cy + dy * (8 + t_len)
                    
                    perp_x, perp_y = -dy, dx
                    wiggle = math.sin(ticks * 0.05) * 3.5
                    tx_w = tx + perp_x * wiggle
                    ty_w = ty + perp_y * wiggle
                    
                    pygame.draw.line(dis, (255, 60, 60), (int(cx + dx * 8), int(cy + dy * 8)), (int(tx_w), int(ty_w)), 2)
                    tip1_x = tx_w + dx * 3 + perp_x * 2.5
                    tip1_y = ty_w + dy * 3 + perp_y * 2.5
                    tip2_x = tx_w + dx * 3 - perp_x * 2.5
                    tip2_y = ty_w + dy * 3 - perp_y * 2.5
                    pygame.draw.line(dis, (255, 60, 60), (int(tx_w), int(ty_w)), (int(tip1_x), int(tip1_y)), 1)
                    pygame.draw.line(dis, (255, 60, 60), (int(tx_w), int(ty_w)), (int(tip2_x), int(tip2_y)), 1)
            else:
                # Standard tongue flicking
                ticks = pygame.time.get_ticks()
                if (ticks % 2000 < 300) and not dead:
                    flick_t = (ticks % 300) / 300.0
                    t_len = 6 + 8 * math.sin(flick_t * math.pi)
                    tx = cx + dx * (8 + t_len)
                    ty = cy + dy * (8 + t_len)
                    perp_x, perp_y = -dy, dx
                    wiggle = math.sin(ticks * 0.03) * 2
                    tx_w = tx + perp_x * wiggle
                    ty_w = ty + perp_y * wiggle
                    pygame.draw.line(dis, (255, 60, 60), (int(cx + dx * 8), int(cy + dy * 8)), (int(tx_w), int(ty_w)), 2)
                    tip1_x = tx_w + dx * 2 + perp_x * 2
                    tip1_y = ty_w + dy * 2 + perp_y * 2
                    tip2_x = tx_w + dx * 2 - perp_x * 2
                    tip2_y = ty_w + dy * 2 - perp_y * 2
                    pygame.draw.line(dis, (255, 60, 60), (int(tx_w), int(ty_w)), (int(tip1_x), int(tip1_y)), 1)
                    pygame.draw.line(dis, (255, 60, 60), (int(tx_w), int(ty_w)), (int(tip2_x), int(tip2_y)), 1)

        else:
            # Body segment: overlapping circles tapering from tail tip
            # radius values: 6.0, 8.0, 9.5, then 12.0 for segments >= 3
            if i == 0:
                radius = 6.0
            elif i == 1:
                radius = 8.0
            elif i == 2:
                radius = 9.5
            else:
                radius = 12.0
                
            color = SNAKE_BODY if (i % 2 == 0) else SNAKE_BODY_ALT
            pygame.draw.circle(dis, color, (int(cx), int(cy)), int(radius))
            
            # Breed-specific spots
            if current_snake_id == "cobra":
                spot_color = (253, 220, 100)
                spot_radius = radius * 0.35
                pygame.draw.circle(dis, spot_color, (int(cx), int(cy)), int(spot_radius))
            elif current_snake_id == "taipan":
                spot_color = (235, 225, 170)
                spot_radius = radius * 0.3
                pygame.draw.circle(dis, spot_color, (int(cx), int(cy)), int(spot_radius))
            elif current_snake_id == "mamba":
                spot_color = (200, 80, 120)
                spot_radius = radius * 0.3
                pygame.draw.circle(dis, spot_color, (int(cx), int(cy)), int(spot_radius))

def draw_capybara_character(cx, cy, y_offset=0, alpha=255, capy_type='leaf'):
    surf = pygame.Surface((60, 60), pygame.SRCALPHA)
    
    # 1. Draw Backpack first if capy_type is 'backpack' (so it's behind/on the back)
    if capy_type == 'backpack':
        # Blue backpack on the back
        pygame.draw.rect(surf, (41, 128, 185), [8, 20, 12, 18], border_radius=3)
        # Small flap
        pygame.draw.rect(surf, (52, 152, 219), [8, 20, 12, 6], border_radius=1)
        # Strap
        pygame.draw.ellipse(surf, (30, 90, 140), [16, 22, 6, 12], 1)
        
    # 2. Body (chubby brown oval)
    pygame.draw.ellipse(surf, (130, 85, 45), [6, 16, 48, 36])
    
    # 3. Head (rounded rectangle/oval at front-right)
    pygame.draw.ellipse(surf, (155, 110, 70), [36, 12, 20, 22])
    
    # 4. Ears (tiny brown circles)
    pygame.draw.circle(surf, (110, 70, 35), (38, 12), 4)
    
    # 5. Snout / Nose area
    pygame.draw.ellipse(surf, (140, 95, 55), [42, 22, 14, 12])
    pygame.draw.circle(surf, (60, 40, 25), (52, 26), 3) # Nose tip
    
    # 6. Eyes: Closed smiling eyes (happy curves)
    pygame.draw.line(surf, (60, 35, 20), (38, 20), (40, 18), 2)
    pygame.draw.line(surf, (60, 35, 20), (40, 18), (42, 20), 2)
    
    pygame.draw.line(surf, (60, 35, 20), (46, 20), (48, 18), 2)
    pygame.draw.line(surf, (60, 35, 20), (48, 18), (50, 20), 2)
    
    # 7. Mouth: Cute smile
    pygame.draw.line(surf, (60, 35, 20), (43, 30), (46, 32), 2)
    pygame.draw.line(surf, (60, 35, 20), (46, 32), (48, 30), 2)
    
    # 8. Legs (four tiny brown stumps)
    pygame.draw.rect(surf, (110, 75, 40), [14, 48, 6, 8], border_radius=2)
    pygame.draw.rect(surf, (110, 75, 40), [24, 48, 6, 8], border_radius=2)
    pygame.draw.rect(surf, (110, 75, 40), [36, 48, 6, 8], border_radius=2)
    pygame.draw.rect(surf, (110, 75, 40), [44, 48, 6, 8], border_radius=2)
    
    # 9. Draw Red Bandana if capy_type is 'bandana'
    if capy_type == 'bandana':
        # Red bandana tied around head (forehead area)
        pygame.draw.polygon(surf, (210, 50, 40), [(36, 15), (48, 13), (52, 17), (40, 19)])
        # Knot/tails at the back left of the head
        pygame.draw.polygon(surf, (190, 40, 30), [(33, 14), (36, 15), (31, 19)])
        pygame.draw.polygon(surf, (190, 40, 30), [(34, 17), (36, 16), (32, 22)])
        
    # 10. Draw Leaf if capy_type is 'leaf'
    elif capy_type == 'leaf':
        # Green leaf on head
        leaf_surf = pygame.Surface((16, 10), pygame.SRCALPHA)
        pygame.draw.ellipse(leaf_surf, (46, 170, 80), [2, 2, 12, 6])
        pygame.draw.line(leaf_surf, (100, 70, 40), (0, 5), (3, 5), 1)
        surf.blit(leaf_surf, (40, 6))

    if alpha < 255:
        surf.set_alpha(alpha)
        
    dis.blit(surf, (int(cx - 30), int(cy - 30 + y_offset)))

def draw_capybaras(capybaras, now):
    for capy in capybaras:
        cx, cy = capy['x'], capy['y']
        spawn_time = capy['spawn_time']
        if capy['state'] == 'warning':
            age = now - spawn_time
            pct = min(1.0, age / 1500.0)
            pygame.draw.circle(dis, (231, 76, 60), (int(cx), int(cy)), 50, 2)
            warn_surf = pygame.Surface((100, 100), pygame.SRCALPHA)
            pygame.draw.circle(warn_surf, (231, 76, 60, 90), (50, 50), int(50 * pct))
            dis.blit(warn_surf, (int(cx - 50), int(cy - 50)))
        elif capy['state'] == 'falling':
            age = now - spawn_time - 1500
            pct = min(1.0, age / 300.0)
            pygame.draw.circle(dis, (231, 76, 60), (int(cx), int(cy)), 50, 1)
            shadow_surf = pygame.Surface((60, 20), pygame.SRCALPHA)
            shadow_alpha = int(100 * pct)
            pygame.draw.ellipse(shadow_surf, (40, 25, 10, shadow_alpha), [0, 0, 60, 20])
            dis.blit(shadow_surf, (int(cx - 30), int(cy - 10)))
            y_offset = -250 * (1.0 - pct)
            draw_capybara_character(cx, cy, y_offset, 255, capy['type'])
        elif capy['state'] in ['landed', 'fading']:
            shadow_surf = pygame.Surface((60, 20), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow_surf, (40, 25, 10, 120), [0, 0, 60, 20])
            dis.blit(shadow_surf, (int(cx - 30), int(cy - 10)))
            alpha = 255
            if capy['state'] == 'fading':
                age = now - spawn_time - 1500 - 300 - 1500
                fade_pct = 1.0 - min(1.0, age / 500.0)
                alpha = int(255 * fade_pct)
            draw_capybara_character(cx, cy, 0, alpha, capy['type'])

def draw_fading_segments(fading_segments, now):
    for seg in fading_segments[:]:
        age = now - seg['spawn_ticks']
        duration = seg['duration']
        if age >= duration:
            fading_segments.remove(seg)
            continue
        pct = 1.0 - (age / duration)
        cx = seg['x'] + BLOCK_SIZE / 2.0
        cy = seg['y'] + BLOCK_SIZE / 2.0
        idx = seg['index']
        if idx == 0:
            radius = 6.0
        elif idx == 1:
            radius = 8.0
        elif idx == 2:
            radius = 9.5
        else:
            radius = 12.0
        shrunk_radius = radius * pct
        profile = SNAKE_PROFILES[seg['breed_id']]
        color = profile['body'] if (idx % 2 == 0) else profile['body_alt']
        bg_col = (170, 215, 81)
        mixed_color = (
            int(color[0] * pct + bg_col[0] * (1.0 - pct)),
            int(color[1] * pct + bg_col[1] * (1.0 - pct)),
            int(color[2] * pct + bg_col[2] * (1.0 - pct))
        )
        pygame.draw.circle(dis, mixed_color, (int(cx), int(cy)), int(shrunk_radius))
        if seg['breed_id'] == 'cobra':
            spot_color = (253, 220, 100)
            spot_radius = shrunk_radius * 0.35
        elif seg['breed_id'] == 'taipan':
            spot_color = (235, 225, 170)
            spot_radius = shrunk_radius * 0.3
        else:
            spot_color = (200, 80, 120)
            spot_radius = shrunk_radius * 0.3
        mixed_spot = (
            int(spot_color[0] * pct + bg_col[0] * (1.0 - pct)),
            int(spot_color[1] * pct + bg_col[1] * (1.0 - pct)),
            int(spot_color[2] * pct + bg_col[2] * (1.0 - pct))
        )
        if spot_radius > 0.5:
            pygame.draw.circle(dis, mixed_spot, (int(cx), int(cy)), int(spot_radius))

def spawn_capybara(now, snake_list=None):
    bx_min, bx_max = 2, 37
    by_min, by_max = 4, 27
    if snake_list and random.random() < 0.7:
        target_segment = random.choice(snake_list)
        target_bx = int(target_segment[0] / 20)
        target_by = int(target_segment[1] / 20)
        bx = target_bx + random.randint(-2, 2)
        by = target_by + random.randint(-2, 2)
        bx = max(bx_min, min(bx_max, bx))
        by = max(by_min, min(by_max, by))
    else:
        bx = random.randint(bx_min, bx_max)
        by = random.randint(by_min, by_max)
    cx = bx * 20 + 10
    cy = by * 20 + 10
    return {
        'x': cx,
        'y': cy,
        'spawn_time': now,
        'state': 'warning',
        'type': random.choice(['bandana', 'leaf', 'backpack'])
    }

def draw_obstacles(block_size, obstacles_data):
    for obj in obstacles_data:
        t = obj['type']
        rx, ry = obj['x'], obj['y']
        rw, rh = obj['rw'], obj['rh']
        w_cells, h_cells = obj['w_cells'], obj['h_cells']
        
        if t == 'rock':
            # Grey granite rock with cracks and highlight/shadow
            pygame.draw.rect(dis, (120, 115, 110), [rx, ry, rw, rh], border_radius=4)
            if rw >= 20 and rh >= 20:
                inner_rect = [rx + 3, ry + 3, rw - 6, rh - 6]
                pygame.draw.rect(dis, (90, 85, 80), inner_rect, border_radius=3)
                if rw > 20 or rh > 20:
                    # Highlight edge
                    pygame.draw.line(dis, (160, 155, 150), (rx + 4, ry + 4), (rx + rw - 5, ry + 4), 2)
                    pygame.draw.line(dis, (160, 155, 150), (rx + 4, ry + 4), (rx + 4, ry + rh - 5), 2)
                    # Crack line
                    pygame.draw.line(dis, (50, 45, 45), (rx + rw//2, ry + 5), (rx + rw//2 - 4, ry + 12), 1)
        
        elif t == 'pond':
            # Water pond with Stardew brown/rocky shoreline
            pygame.draw.rect(dis, (120, 95, 75), [rx, ry, rw, rh], border_radius=8)
            inner_pond = [rx + 4, ry + 4, rw - 8, rh - 8]
            pygame.draw.rect(dis, (40, 110, 140), inner_pond, border_radius=6)
            if rw >= 40 and rh >= 40:
                # Add light blue ripples
                pygame.draw.ellipse(dis, (90, 160, 190), [rx + 10, ry + 10, rw - 20, rh - 20], width=1)
                pygame.draw.circle(dis, (34, 112, 63), (int(rx + 10), int(ry + 10)), 3) # Lilypad
                pygame.draw.circle(dis, (34, 112, 63), (int(rx + rw - 12), int(ry + rh - 12)), 2)
                
        elif t == 'log':
            # Cozy wood log
            pygame.draw.rect(dis, (78, 41, 16), [rx, ry, rw, rh], border_radius=4)
            pygame.draw.rect(dis, (105, 55, 25), [rx + 2, ry + 2, rw - 4, rh - 4], border_radius=3)
            if w_cells > h_cells:
                # Horizontal log: draw end-ring rings
                pygame.draw.ellipse(dis, (200, 160, 120), [rx, ry + 2, 4, rh - 4])
                pygame.draw.ellipse(dis, (200, 160, 120), [rx + rw - 4, ry + 2, 4, rh - 4])
                pygame.draw.line(dis, (78, 41, 16), (rx + 5, ry + rh/2), (rx + rw - 6, ry + rh/2), 1)
            else:
                # Vertical log
                pygame.draw.ellipse(dis, (200, 160, 120), [rx + 2, ry, rw - 4, 4])
                pygame.draw.ellipse(dis, (200, 160, 120), [rx + 2, ry + rh - 4, rw - 4, 4])
                pygame.draw.line(dis, (78, 41, 16), (rx + rw/2, ry + 5), (rx + rw/2, ry + rh - 6), 1)
                
        elif t == 'tree':
            # Stardew tree: warm trunk + layered pine canopy
            if w_cells == 1 and h_cells == 2:
                # Trunk
                pygame.draw.rect(dis, (78, 41, 16), [rx + 7, ry + 18, 6, 22], border_radius=1)
                # Forest green canopy circles
                pygame.draw.circle(dis, (20, 75, 40), (int(rx + 10), int(ry + 12)), 11)
                pygame.draw.circle(dis, (34, 112, 63), (int(rx + 10), int(ry + 10)), 9)
                pygame.draw.circle(dis, (55, 145, 80), (int(rx + 9), int(ry + 8)), 6)
            elif w_cells == 2 and h_cells == 2:
                # Trunk
                pygame.draw.rect(dis, (78, 41, 16), [rx + 15, ry + 22, 10, 18], border_radius=2)
                # Multi-layered rounded green canopy
                pygame.draw.circle(dis, (20, 75, 40), (int(rx + 12), int(ry + 14)), 13)
                pygame.draw.circle(dis, (20, 75, 40), (int(rx + 28), int(ry + 14)), 13)
                pygame.draw.circle(dis, (34, 112, 63), (int(rx + 20), int(ry + 12)), 14)
                pygame.draw.circle(dis, (55, 145, 80), (int(rx + 18), int(ry + 9)), 9)

def draw_food(x, y, block_size):
    cx = int(x + block_size/2)
    cy = int(y + block_size/2)
    # Cozy pixel-art red apple body
    pygame.draw.circle(dis, (190, 35, 35), (cx, cy + 1), 7)
    # Darker red shadow at bottom right
    pygame.draw.circle(dis, (140, 20, 20), (cx + 1, cy + 2), 6)
    # Brown stem
    pygame.draw.line(dis, (78, 41, 16), (cx, cy - 6), (cx + 2, cy - 10), 2)
    # Green leaf
    pygame.draw.ellipse(dis, (34, 112, 63), [cx + 1, cy - 11, 5, 3])
    # Pixel shine
    pygame.draw.rect(dis, (255, 180, 180), [cx - 4, cy - 3, 2, 2])

def message(msg, color, y_offset=0):
    mesg = font_style.render(msg, True, (255, 255, 255))
    text_rect = mesg.get_rect(center=(WIDTH/2, HEIGHT/2 + y_offset))
    bg_rect = text_rect.copy()
    bg_rect.inflate_ip(30, 15)
    
    # Wooden banner backing
    pygame.draw.rect(dis, (78, 41, 16), bg_rect, border_radius=6)
    inner_rect = [bg_rect[0] + 3, bg_rect[1] + 3, bg_rect[2] - 6, bg_rect[3] - 6]
    pygame.draw.rect(dis, (183, 105, 47), inner_rect, border_radius=4)
    pygame.draw.rect(dis, (243, 175, 59), inner_rect, width=1, border_radius=4)
    
    draw_text_shadow(msg, font_style, (247, 235, 198), (WIDTH/2, HEIGHT/2 + y_offset), shadow_color=(50, 25, 10), offset=2)

def draw_pause_icon(x, y, size=30, hover=False):
    bg_color = (219, 137, 54) if hover else (183, 105, 47)
    rect = pygame.Rect(x, y, size, size)
    pygame.draw.rect(dis, (78, 41, 16), rect, border_radius=6)
    pygame.draw.rect(dis, bg_color, (x + 2, y + 2, size - 4, size - 4), border_radius=4)
    pygame.draw.rect(dis, (243, 175, 59), (x + 3, y + 3, size - 6, size - 6), width=1, border_radius=3)
    
    bar_w = 4
    bar_h = 14
    bar_y = y + (size - bar_h) // 2
    bar1_x = x + (size // 2) - 5
    bar2_x = x + (size // 2) + 1
    
    pygame.draw.rect(dis, (255, 255, 255), [bar1_x, bar_y, bar_w, bar_h], border_radius=1)
    pygame.draw.rect(dis, (255, 255, 255), [bar2_x, bar_y, bar_w, bar_h], border_radius=1)

def draw_button(msg, x, y, w, h, ic, ac, mouse_clicked, action=None):
    mouse = pygame.mouse.get_pos()
    is_hovered = (x + w > mouse[0] > x and y + h > mouse[1] > y)
    
    if ic == (39, 174, 96): # green
        bg_color = (80, 160, 70) if is_hovered else (60, 130, 50)
    elif ic == (192, 57, 43): # red
        bg_color = (210, 80, 70) if is_hovered else (170, 55, 45)
    elif ic == (127, 140, 141): # gray
        bg_color = (150, 145, 140) if is_hovered else (120, 115, 110)
    elif ic == (243, 175, 59): # gold (active highlight)
        bg_color = (250, 200, 80) if is_hovered else (243, 175, 59)
    else:
        bg_color = (219, 137, 54) if is_hovered else (183, 105, 47)
        
    pygame.draw.rect(dis, (78, 41, 16), (x, y, w, h), border_radius=6)
    pygame.draw.rect(dis, bg_color, (x + 3, y + 3, w - 6, h - 6), border_radius=4)
    pygame.draw.rect(dis, (243, 175, 59), (x + 4, y + 4, w - 8, h - 8), width=1, border_radius=3)
    
    if is_hovered and mouse_clicked and action is not None:
        play_sound(click_sound)
        action()
        
    draw_text_shadow(msg, btn_font, (255, 255, 255), (x + w/2, y + h/2), shadow_color=(50, 25, 10), offset=2)

def quit_game():
    global app_state
    app_state = "quit"

def change_state(new_state):
    global app_state
    app_state = new_state

def set_speed(speed):
    global SNAKE_SPEED
    SNAKE_SPEED = speed
    save_settings()

def set_sound(val):
    global sound_on
    sound_on = val
    save_settings()

def set_music(val):
    global music_on
    music_on = val
    save_settings()
    if bg_music:
        if music_on:
            try:
                bg_music.stop()
                bg_music.play(loops=-1)
            except:
                pass
        else:
            try:
                bg_music.stop()
            except:
                pass

def select_snake(snake_id):
    global SNAKE_BODY, SNAKE_BODY_ALT, SNAKE_HEAD, current_snake_name, current_snake_id, app_state
    SNAKE_BODY = SNAKE_PROFILES[snake_id]["body"]
    SNAKE_BODY_ALT = SNAKE_PROFILES[snake_id]["body_alt"]
    SNAKE_HEAD = SNAKE_PROFILES[snake_id]["head"]
    current_snake_name = SNAKE_PROFILES[snake_id]["name"]
    current_snake_id = snake_id
    save_settings()
    play_snake_sound(snake_id)
    app_state = "game"

def get_random_pos():
    x = round(random.randrange(0, WIDTH - BLOCK_SIZE) / 20.0) * 20.0
    y = round(random.randrange(PLAY_Y_START, HEIGHT - BLOCK_SIZE) / 20.0) * 20.0
    return x, y

def draw_breed_preview(x, y, snake_id):
    body_color = SNAKE_PROFILES[snake_id]["body"]
    body_alt_color = SNAKE_PROFILES[snake_id]["body_alt"]
    head_color = SNAKE_PROFILES[snake_id]["head"]
    
    # Segment 0 (tail tip) - color: body
    r0 = 4.2
    cx0, cy0 = x + 6, y + 7
    pygame.draw.circle(dis, body_color, (int(cx0), int(cy0)), int(r0))
    
    # Segment 1 (body) - color: body_alt
    r1 = 5.6
    cx1, cy1 = x + 18, y + 7
    pygame.draw.circle(dis, body_alt_color, (int(cx1), int(cy1)), int(r1))
    
    # Spots on preview segments
    if snake_id == "cobra":
        pygame.draw.circle(dis, (253, 220, 100), (int(cx0), int(cy0)), int(r0 * 0.35))
        pygame.draw.circle(dis, (253, 220, 100), (int(cx1), int(cy1)), int(r1 * 0.35))
    elif snake_id == "taipan":
        pygame.draw.circle(dis, (235, 225, 170), (int(cx0), int(cy0)), int(r0 * 0.3))
        pygame.draw.circle(dis, (235, 225, 170), (int(cx1), int(cy1)), int(r1 * 0.3))
    elif snake_id == "mamba":
        pygame.draw.circle(dis, (200, 80, 120), (int(cx0), int(cy0)), int(r0 * 0.3))
        pygame.draw.circle(dis, (200, 80, 120), (int(cx1), int(cy1)), int(r1 * 0.3))
        
    # Segment 2 (head) - rect 14x14 at x+26, y, moving right
    rect = [x + 26, y, 14, 14]
    pygame.draw.rect(
        dis, 
        head_color, 
        rect, 
        border_top_left_radius=3,
        border_top_right_radius=8,
        border_bottom_left_radius=3,
        border_bottom_right_radius=8
    )
    
    # Eye
    pygame.draw.circle(dis, (255, 255, 255), (x + 34, y + 4), 2)
    pygame.draw.circle(dis, (0, 0, 0), (x + 34, y + 4), 1)

async def mainMenu():
    global app_state
    while app_state == "menu":
        mouse_clicked = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_clicked = True

        if bg_img_menu:
            dis.blit(bg_img_menu, (0, 0))
        else:
            dis.fill(BG_COLOR)
            
        # Large central parchment panel
        draw_rust_panel([WIDTH/2 - 220, HEIGHT/2 - 240, 440, 480])
        
        # Rebranded title header sign
        message("SNEAK THE SNAKE", GOLD_COLOR, -180)

        # Main wood-plank buttons
        draw_button("START", 325, 180, 150, 50, (39, 174, 96), (46, 204, 113), mouse_clicked, lambda: change_state("selection"))
        draw_button("SCORES", 325, 250, 150, 50, (127, 140, 141), (149, 165, 166), mouse_clicked, lambda: change_state("scores"))
        draw_button("SETTINGS", 325, 320, 150, 50, (127, 140, 141), (149, 165, 166), mouse_clicked, lambda: change_state("settings"))
        draw_button("EXIT", 325, 390, 150, 50, (192, 57, 43), (231, 76, 60), mouse_clicked, quit_game)

        pygame.display.update()
        await asyncio.sleep(0)

async def scoresMenu():
    global app_state
    while app_state == "scores":
        mouse_clicked = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_clicked = True

        if bg_img_menu:
            dis.blit(bg_img_menu, (0, 0))
        else:
            dis.fill(BG_COLOR)
            
        draw_rust_panel([WIDTH/2 - 250, HEIGHT/2 - 260, 500, 520])
        message("TOP 5 SCORES", GOLD_COLOR, -220)

        scores = load_scores()
        start_y = 150
        if not scores:
            try:
                msg = score_font.render("No scores yet!", True, (78, 41, 16))
                dis.blit(msg, (WIDTH/2 - msg.get_width()/2, 220))
            except: pass
        else:
            for i, s in enumerate(scores):
                try:
                    msg = score_font.render(f"{i+1}. {s['snake']} - Score: {s['score']}", True, (78, 41, 16))
                    dis.blit(msg, (WIDTH/2 - msg.get_width()/2, start_y + (i * 45)))
                except: pass

        draw_button("BACK", 350, 450, 100, 50, (127, 140, 141), (149, 165, 166), mouse_clicked, lambda: change_state("menu"))

        pygame.display.update()
        await asyncio.sleep(0)

async def snakeSelectionMenu():
    global app_state
    while app_state == "selection":
        mouse_clicked = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_clicked = True

        if bg_img_menu:
            dis.blit(bg_img_menu, (0, 0))
        else:
            dis.fill(BG_COLOR)
            
        draw_rust_panel([WIDTH/2 - 250, HEIGHT/2 - 260, 500, 520])
        message("CHOOSE YOUR BREED", GOLD_COLOR, -220)

        # Wood buttons
        draw_button("GOLD CORN", 300, 180, 200, 50, (127, 140, 141), (149, 165, 166), mouse_clicked, lambda: select_snake("cobra"))
        draw_button("GARDEN GARTER", 300, 250, 200, 50, (127, 140, 141), (149, 165, 166), mouse_clicked, lambda: select_snake("taipan"))
        draw_button("WILD BLACKBERRY", 300, 320, 200, 50, (127, 140, 141), (149, 165, 166), mouse_clicked, lambda: select_snake("mamba"))
        
        # Previews
        draw_breed_preview(240, 198, "cobra")
        draw_breed_preview(240, 268, "taipan")
        draw_breed_preview(240, 338, "mamba")
        
        draw_button("BACK", 350, 420, 100, 50, (127, 140, 141), (149, 165, 166), mouse_clicked, lambda: change_state("menu"))

        pygame.display.update()
        await asyncio.sleep(0)

async def settingsMenu():
    global app_state
    while app_state == "settings":
        mouse_clicked = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_clicked = True

        if bg_img_menu:
            dis.blit(bg_img_menu, (0, 0))
        else:
            dis.fill(BG_COLOR)
            
        draw_rust_panel([WIDTH/2 - 320, HEIGHT/2 - 240, 640, 480])
        message("SETTINGS", GOLD_COLOR, -180)

        # SPEED Section
        draw_text_shadow("SPEED", score_font, GOLD_COLOR, (WIDTH/2, HEIGHT/2 - 120), shadow_color=(50, 25, 10))
        draw_button("V. SLOW", 120, 210, 100, 40, (243, 175, 59) if SNAKE_SPEED == 5 else (39, 174, 96), (46, 204, 113), mouse_clicked, lambda: set_speed(5))
        draw_button("SLOW", 235, 210, 100, 40, (243, 175, 59) if SNAKE_SPEED == 10 else (39, 174, 96), (46, 204, 113), mouse_clicked, lambda: set_speed(10))
        draw_button("NORMAL", 350, 210, 100, 40, (243, 175, 59) if SNAKE_SPEED == 15 else (39, 174, 96), (46, 204, 113), mouse_clicked, lambda: set_speed(15))
        draw_button("FAST", 465, 210, 100, 40, (243, 175, 59) if SNAKE_SPEED == 20 else (39, 174, 96), (46, 204, 113), mouse_clicked, lambda: set_speed(20))
        draw_button("V. FAST", 580, 210, 100, 40, (243, 175, 59) if SNAKE_SPEED == 25 else (39, 174, 96), (46, 204, 113), mouse_clicked, lambda: set_speed(25))

        # SOUND Section
        draw_text_shadow("SOUND EFFECTS", score_font, GOLD_COLOR, (WIDTH/2, HEIGHT/2 - 15), shadow_color=(50, 25, 10))
        draw_button("ON", 265, 315, 120, 40, (243, 175, 59) if sound_on else (127, 140, 141), (149, 165, 166), mouse_clicked, lambda: set_sound(True))
        draw_button("OFF", 415, 315, 120, 40, (192, 57, 43) if not sound_on else (127, 140, 141), (149, 165, 166), mouse_clicked, lambda: set_sound(False))

        # MUSIC Section
        draw_text_shadow("BACKGROUND MUSIC", score_font, GOLD_COLOR, (WIDTH/2, HEIGHT/2 + 90), shadow_color=(50, 25, 10))
        draw_button("ON", 265, 420, 120, 40, (243, 175, 59) if music_on else (127, 140, 141), (149, 165, 166), mouse_clicked, lambda: set_music(True))
        draw_button("OFF", 415, 420, 120, 40, (192, 57, 43) if not music_on else (127, 140, 141), (149, 165, 166), mouse_clicked, lambda: set_music(False))

        # BACK Button
        draw_button("BACK", 330, 490, 140, 40, (127, 140, 141), (149, 165, 166), mouse_clicked, lambda: change_state("menu"))

        pygame.display.update()
        await asyncio.sleep(0)

def is_opposite(dir1, dir2):
    return dir1[0] * dir2[0] + dir1[1] * dir2[1] < 0

async def gameLoop():
    global app_state, dis
    game_over = False
    game_close = False

    x1 = round((WIDTH / 2) / 20.0) * 20.0
    y1 = round((HEIGHT / 2) / 20.0) * 20.0

    x1_change = 0
    y1_change = 0
    direction_queue = []

    snake_List = [[x1, y1]]
    prev_snake_List = [[x1, y1]]
    Length_of_snake = 1

    obstacles_data = []
    obstacles = []
    num_obstacles = 9
    
    types_pool = ['pond', 'pond', 'tree', 'tree', 'log', 'log', 'rock', 'rock', 'rock']
    
    for obj_type in types_pool:
        if obj_type == 'pond':
            w_cells, h_cells = 2, 2
        elif obj_type == 'tree':
            w_cells, h_cells = random.choice([(1, 2), (2, 2)])
        elif obj_type == 'log':
            w_cells, h_cells = random.choice([(2, 1), (1, 2)])
        else: # rock
            w_cells, h_cells = random.choice([(1, 1), (2, 1), (1, 2), (2, 2)])
            
        rw = w_cells * BLOCK_SIZE
        rh = h_cells * BLOCK_SIZE
        
        placed = False
        for _ in range(150):
            rx = round(random.randrange(BLOCK_SIZE, WIDTH - rw - BLOCK_SIZE) / 20.0) * 20.0
            ry = round(random.randrange(PLAY_Y_START + BLOCK_SIZE, HEIGHT - rh - BLOCK_SIZE) / 20.0) * 20.0
            
            too_close = False
            for cx in range(w_cells):
                for cy in range(h_cells):
                    px = rx + cx * BLOCK_SIZE
                    py = ry + cy * BLOCK_SIZE
                    dist_to_center = abs(px - x1) + abs(py - y1)
                    if dist_to_center < 120:
                        too_close = True
                        break
                if too_close:
                    break
                    
            if too_close:
                continue
                
            conflict = False
            for cx in range(-1, w_cells + 1):
                for cy in range(-1, h_cells + 1):
                    check_x = rx + cx * BLOCK_SIZE
                    check_y = ry + cy * BLOCK_SIZE
                    if [check_x, check_y] in obstacles:
                        conflict = True
                        break
                if conflict:
                    break
                    
            if not conflict:
                obstacles_data.append({
                    'type': obj_type,
                    'x': rx,
                    'y': ry,
                    'w_cells': w_cells,
                    'h_cells': h_cells,
                    'rw': rw,
                    'rh': rh
                })
                for cx in range(w_cells):
                    for cy in range(h_cells):
                        obstacles.append([rx + cx * BLOCK_SIZE, ry + cy * BLOCK_SIZE])
                placed = True
                break

    while True:
        foodx, foody = get_random_pos()
        if [foodx, foody] not in obstacles and (foodx != x1 or foody != y1):
            break

    last_move_time = pygame.time.get_ticks()
    game_started = False
    t = 0.0

    capybaras = []
    fading_segments = []
    last_capybara_spawn = 0
    capybara_active_mode = False
    shake_until = 0

    real_dis = dis
    game_surface = pygame.Surface((WIDTH, HEIGHT))

    try:
        while app_state == "game":
            dis = game_surface

            while game_close == True:
                mouse_clicked = False
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        quit_game()
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        mouse_clicked = True

                draw_game_background()
                draw_grid()
                draw_food(foodx, foody, BLOCK_SIZE)
                draw_obstacles(BLOCK_SIZE, obstacles_data)
                
                # Draw fading segments while game close is active
                draw_fading_segments(fading_segments, pygame.time.get_ticks())
                
                draw_snake(BLOCK_SIZE, snake_List, prev_snake_List, 1.0, x1_change, y1_change, food_pos=(foodx, foody), dead=True)
                
                # Draw capybaras while game close is active
                draw_capybaras(capybaras, pygame.time.get_ticks())
                
                draw_score(Length_of_snake - 1)
                
                # Central parchment Game Over panel
                draw_rust_panel([WIDTH/2 - 200, HEIGHT/2 - 150, 400, 300])
                draw_text_shadow("GAME OVER", font_style, (231, 76, 60), (WIDTH/2, HEIGHT/2 - 80), shadow_color=(78, 41, 16), offset=2)
                draw_text_shadow(f"Final Score: {Length_of_snake - 1}", btn_font, (78, 41, 16), (WIDTH/2, HEIGHT/2 - 10), shadow_color=(243, 175, 59), offset=1)

                draw_button("PLAY AGAIN", WIDTH/2 - 160, HEIGHT/2 + 50, 140, 50, (39, 174, 96), (46, 204, 113), mouse_clicked, lambda: change_state("restart_game"))
                draw_button("MAIN MENU", WIDTH/2 + 20, HEIGHT/2 + 50, 140, 50, (211, 84, 0), (230, 126, 34), mouse_clicked, lambda: change_state("menu"))

                # Screen shake check for Game Over
                dx, dy = 0, 0
                if pygame.time.get_ticks() < shake_until:
                    dx = random.randint(-6, 6)
                    dy = random.randint(-6, 6)

                real_dis.fill((78, 41, 16))
                real_dis.blit(game_surface, (dx, dy))
                pygame.display.update()
                await asyncio.sleep(0)

                if app_state != "game":
                    if app_state == "restart_game":
                        change_state("game") 
                    return

            trigger_pause = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit_game()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    if 755 <= mouse_pos[0] <= 785 and 5 <= mouse_pos[1] <= 35:
                        trigger_pause = True
                        play_sound(click_sound)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        trigger_pause = True
                        play_sound(click_sound)
                    else:
                        proposed_dir = None
                        if event.key == pygame.K_LEFT:
                            proposed_dir = (-BLOCK_SIZE, 0)
                        elif event.key == pygame.K_RIGHT:
                            proposed_dir = (BLOCK_SIZE, 0)
                        elif event.key == pygame.K_UP:
                            proposed_dir = (0, -BLOCK_SIZE)
                        elif event.key == pygame.K_DOWN:
                            proposed_dir = (0, BLOCK_SIZE)

                        if proposed_dir is not None:
                            if direction_queue:
                                ref_dir = direction_queue[-1]
                            else:
                                ref_dir = (x1_change, y1_change)
                            
                            if not is_opposite(proposed_dir, ref_dir):
                                if len(direction_queue) < 2:
                                    direction_queue.append(proposed_dir)

            if trigger_pause:
                pause_start_ticks = pygame.time.get_ticks()
                loop_state = {'paused': True}
                
                while loop_state['paused'] and app_state == "game":
                    mouse_clicked = False
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            quit_game()
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_p:
                                loop_state['paused'] = False
                                play_sound(click_sound)
                        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                            mouse_clicked = True
                            mouse_pos = pygame.mouse.get_pos()
                            if 755 <= mouse_pos[0] <= 785 and 5 <= mouse_pos[1] <= 35:
                                loop_state['paused'] = False
                                play_sound(click_sound)
                                
                    # Draw current game state frozen
                    draw_game_background()
                    draw_grid()
                    draw_food(foodx, foody, BLOCK_SIZE)
                    draw_obstacles(BLOCK_SIZE, obstacles_data)
                    draw_fading_segments(fading_segments, pause_start_ticks)
                    draw_snake(BLOCK_SIZE, snake_List, prev_snake_List, t, x1_change, y1_change, food_pos=(foodx, foody), dead=False)
                    draw_capybaras(capybaras, pause_start_ticks)
                    
                    # Header
                    draw_score(Length_of_snake - 1)
                    
                    # Pause Button (drawn as hovered/active)
                    mouse_pos = pygame.mouse.get_pos()
                    pause_hover = (755 <= mouse_pos[0] <= 785 and 5 <= mouse_pos[1] <= 35)
                    draw_pause_icon(755, 5, size=30, hover=pause_hover)
                    
                    # Overlay panel
                    draw_rust_panel([WIDTH/2 - 200, HEIGHT/2 - 120, 400, 240])
                    draw_text_shadow("GAME PAUSED", font_style, GOLD_COLOR, (WIDTH/2, HEIGHT/2 - 60), shadow_color=(78, 41, 16), offset=2)
                    
                    draw_button("CONTINUE", WIDTH/2 - 160, HEIGHT/2 + 20, 140, 50, (39, 174, 96), (46, 204, 113), mouse_clicked, lambda: loop_state.update({'paused': False}))
                    draw_button("RETURN", WIDTH/2 + 20, HEIGHT/2 + 20, 140, 50, (211, 84, 0), (230, 126, 34), mouse_clicked, lambda: change_state("selection"))
                    
                    real_dis.fill((78, 41, 16))
                    real_dis.blit(game_surface, (0, 0))
                    pygame.display.update()
                    await asyncio.sleep(0)
                    
                # Calculate pause duration and shift all timers
                pause_duration = pygame.time.get_ticks() - pause_start_ticks
                last_move_time += pause_duration
                if last_capybara_spawn > 0:
                    last_capybara_spawn += pause_duration
                if shake_until > 0:
                    shake_until += pause_duration
                for capy in capybaras:
                    capy['spawn_time'] += pause_duration
                for segment in fading_segments:
                    segment['spawn_ticks'] += pause_duration
                    
                if app_state != "game":
                    return

            # Non-blocking timer for snake speed
            now = pygame.time.get_ticks()
            if now - last_move_time > (1000 / SNAKE_SPEED):
                last_move_time = now
                
                # Save previous state for smooth interpolation
                prev_snake_List = [list(pos) for pos in snake_List]
                
                if direction_queue:
                    x1_change, y1_change = direction_queue.pop(0)
                
                if (x1_change != 0 or y1_change != 0) and not game_started:
                    play_snake_sound(current_snake_id)
                    game_started = True

                # Boundary collision
                if x1 >= WIDTH or x1 < 0 or y1 >= HEIGHT or y1 < PLAY_Y_START:
                    if not game_close:
                        save_score(Length_of_snake - 1, current_snake_name)
                        game_close = True
                        play_sound(hit_sound)
                    
                x1 += x1_change
                y1 += y1_change

                # Obstacle collision
                if not game_close and [x1, y1] in obstacles:
                    save_score(Length_of_snake - 1, current_snake_name)
                    game_close = True
                    play_sound(hit_sound)

                snake_Head = []
                snake_Head.append(x1)
                snake_Head.append(y1)
                snake_List.append(snake_Head)
                
                if len(snake_List) > Length_of_snake:
                    del snake_List[0]

                # Self collision
                for x in snake_List[:-1]:
                    if x == snake_Head:
                        if not game_close:
                            save_score(Length_of_snake - 1, current_snake_name)
                            game_close = True
                            play_sound(hit_sound)
                            
                if x1 == foodx and y1 == foody:
                    play_sound(eat_sound)
                    while True:
                        foodx, foody = get_random_pos()
                        if [foodx, foody] not in obstacles and [foodx, foody] not in snake_List:
                            break
                    Length_of_snake += 1

                # Capybara Spawning & State Updates (only if not game_close)
                if not game_close:
                    if Length_of_snake - 1 >= 10:
                        if not capybara_active_mode:
                            capybara_active_mode = True
                            last_capybara_spawn = now  # starts warning in 5 seconds
                            
                    if capybara_active_mode:
                        if now - last_capybara_spawn >= 5000:
                            capybaras.append(spawn_capybara(now, snake_List))
                            last_capybara_spawn = now

                    for capy in capybaras[:]:
                        spawn_time = capy['spawn_time']
                        age = now - spawn_time
                        if capy['state'] == 'warning' and age >= 1500:
                            capy['state'] = 'falling'
                        elif capy['state'] == 'falling' and age >= 1800:
                            capy['state'] = 'landed'
                            play_sound(capybara_land_sound)
                            shake_until = now + 150
                            
                            # Landing impact collision check
                            cx, cy = capy['x'], capy['y']
                            head_x, head_y = snake_List[-1]
                            hcx, hcy = head_x + BLOCK_SIZE/2, head_y + BLOCK_SIZE/2
                            
                            # Head collision
                            if (hcx - cx)**2 + (hcy - cy)**2 <= 2500:
                                if not game_close:
                                    save_score(Length_of_snake - 1, current_snake_name)
                                    game_close = True
                                    play_sound(hit_sound)
                            else:
                                # Body collision
                                hit_idx = -1
                                for idx in range(len(snake_List) - 1):
                                    scx = snake_List[idx][0] + BLOCK_SIZE/2
                                    scy = snake_List[idx][1] + BLOCK_SIZE/2
                                    if (scx - cx)**2 + (scy - cy)**2 <= 2500:
                                        hit_idx = idx
                                        
                                if hit_idx != -1:
                                    # Move hit segments to fading list
                                    for idx in range(hit_idx + 1):
                                        fading_segments.append({
                                            'x': snake_List[idx][0],
                                            'y': snake_List[idx][1],
                                            'index': idx,
                                            'breed_id': current_snake_id,
                                            'spawn_ticks': now,
                                            'duration': 800
                                        })
                                    snake_List = snake_List[hit_idx+1:]
                                    prev_snake_List = prev_snake_List[hit_idx+1:]
                                    Length_of_snake = len(snake_List)
                        elif capy['state'] == 'landed' and age >= 3300:
                            capy['state'] = 'fading'
                        elif capy['state'] == 'fading' and age >= 3800:
                            capy['state'] = 'done'
                            capybaras.remove(capy)

            # Calculate interpolation factor
            step_duration = 1000.0 / SNAKE_SPEED
            t = (now - last_move_time) / step_duration
            t = max(0.0, min(1.0, t))

            draw_game_background()
            draw_grid()
            
            draw_food(foodx, foody, BLOCK_SIZE)
            draw_obstacles(BLOCK_SIZE, obstacles_data)
            
            # Draw fading segments below the live snake
            draw_fading_segments(fading_segments, now)
            
            draw_snake(BLOCK_SIZE, snake_List, prev_snake_List, t, x1_change, y1_change, food_pos=(foodx, foody), dead=False)
            
            # Draw capybaras on top of segments
            draw_capybaras(capybaras, now)
            
            # Show instruction overlay if snake is stationary
            if x1_change == 0 and y1_change == 0:
                draw_instruction_graphic(WIDTH // 2, 160)

            draw_score(Length_of_snake - 1)

            # Render offscreen buffer to real screen with shake
            dx, dy = 0, 0
            if pygame.time.get_ticks() < shake_until:
                dx = random.randint(-6, 6)
                dy = random.randint(-6, 6)

            real_dis.fill((78, 41, 16))
            real_dis.blit(game_surface, (dx, dy))
            pygame.display.update()
            await asyncio.sleep(0)
    finally:
        dis = real_dis

async def main():
    try:
        global app_state
        load_settings()
        if bg_music and music_on:
            try:
                bg_music.play(loops=-1)
            except:
                pass
        while app_state != "quit":
            if app_state == "menu":
                await mainMenu()
            elif app_state == "selection":
                await snakeSelectionMenu()
            elif app_state == "scores":
                await scoresMenu()
            elif app_state == "settings":
                await settingsMenu()
            elif app_state == "game":
                await gameLoop()
            
            await asyncio.sleep(0)
    except Exception as e:
        import traceback
        err = traceback.format_exc()
        dis.fill((200, 0, 0))
        try:
            sys_font = pygame.font.Font(None, 20)
            y = 10
            for line in err.split('\n'):
                dis.blit(sys_font.render(line, True, (255, 255, 255)), (10, y))
                y += 20
        except:
            pass
        pygame.display.update()
        while True:
            await asyncio.sleep(0)

    return

if __name__ == '__main__':
    asyncio.run(main())
