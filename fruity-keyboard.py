# import threading
# import time
# import sys

import pygame
import mido
import time

MIDI_PORT_NAME = 'port1 1'
DEFAULT_VELOCITY = 100
PITCH_BEND_RANGE = 8192
ARP_INTERVAL = 0.2

# def keep_pygame_on_top():
#     if sys.platform.startswith('win'):
#         import ctypes
#         hwnd = pygame.display.get_wm_info()['window']
#         while running:
#             ctypes.windll.user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0,
#                                               0x0001 | 0x0002)
#             time.sleep(1)  # Actualiza cada 1 segundo
#     elif sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
#         # Opcional: esto se puede hacer con wmctrl o Tkinter si querés soporte cross-platform real
#         print("El modo persistente 'always on top' solo está activo en Windows por ahora.")


SCALES = {
    'major': [0, 2, 4, 5, 7, 9, 11],
    'minor': [0, 2, 3, 5, 7, 8, 10],
    'pentatonic': [0, 2, 4, 7, 9],
    'chromatic': list(range(12))
}

NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

root_note = 60
current_scale = 'chromatic'
scale_root_offset = 0
scale_names = list(SCALES.keys())
scale_index = scale_names.index(current_scale)

rows = [
    [pygame.K_z, pygame.K_x, pygame.K_c, pygame.K_v, pygame.K_b, pygame.K_n, pygame.K_m, pygame.K_COMMA, pygame.K_PERIOD],
    [pygame.K_a, pygame.K_s, pygame.K_d, pygame.K_f, pygame.K_g, pygame.K_h, pygame.K_j, pygame.K_k, pygame.K_l, pygame.K_SEMICOLON],
    [pygame.K_q, pygame.K_w, pygame.K_e, pygame.K_r, pygame.K_t, pygame.K_y, pygame.K_u, pygame.K_i, pygame.K_o, pygame.K_p]
]

# key_map = {}
# for octave_index, row in enumerate(rows):
#     for i, key in enumerate(row):
#         key_map[key] = (octave_index, i)

# Definimos un mapa manual de desplazamientos de octava si se quiere un comportamiento más específico
custom_octave_shift_map = {
    pygame.K_k: 1,  # igual que Q
    pygame.K_i: 1,  # una octava arriba de Q
}

key_map = {}
for row_index, row in enumerate(rows):
    for i, key in enumerate(row):
        # Aplica shift manual si existe para esa tecla
        octave_shift = custom_octave_shift_map.get(key, 1 if i >= len(row) - 2 else 0)
        key_map[key] = (row_index + octave_shift, i)

try:
    midi_out = mido.open_output(MIDI_PORT_NAME)
except IOError:
    print(f"No se encontró el puerto MIDI '{MIDI_PORT_NAME}'.")
    exit(1)

pygame.init()
screen = pygame.display.set_mode((300, 300))
pygame.display.set_caption("Super Piano para Ableton")
font = pygame.font.SysFont("Arial", 20)

pressed_keys = set()
sustain_active = False
arp_active = False
chord_memory = False
velocity = DEFAULT_VELOCITY
current_bend = 0
arp_notes = []
active_notes = []

def draw_ui():
    screen.fill((10, 10, 10))
    scale_text = font.render(f"Escala: {current_scale}", True, (255, 255, 255))
    note_text = font.render(f"Nota raíz: {NOTE_NAMES[scale_root_offset]}", True, (200, 200, 100))
    velocity_text = font.render(f"Velocidad: {velocity}", True, (100, 200, 100))
    arp_text = font.render(f"Arpegiador: {'ON' if arp_active else 'OFF'}", True, (100, 150, 250))

    notes_str = ', '.join([f"{NOTE_NAMES[n % 12]}{(n // 12) - 1}" for n in active_notes])
    notes_text = font.render(f"Notas activas: {notes_str if notes_str else 'Ninguna'}", True, (255, 255, 255))

    screen.blit(scale_text, (20, 20))
    screen.blit(note_text, (20, 60))
    screen.blit(velocity_text, (20, 100))
    screen.blit(arp_text, (20, 140))
    screen.blit(notes_text, (20, 220))

    pygame.draw.rect(screen, (100, 200, 100), (20, 180, velocity, 20))
    pygame.display.flip()

def get_note_in_scale(octave_offset, index_in_scale):
    scale = SCALES[current_scale]
    degree = index_in_scale % len(scale)
    note = root_note + scale_root_offset + (12 * octave_offset) + scale[degree]
    return note

def send_chord(note):
    for interval in [0, 4, 7]:
        midi_out.send(mido.Message('note_on', note=note + interval, velocity=velocity))
        active_notes.append(note + interval)

def stop_chord(note):
    for interval in [0, 4, 7]:
        midi_out.send(mido.Message('note_off', note=note + interval, velocity=velocity))
        if note + interval in active_notes:
            active_notes.remove(note + interval)

running = True
# threading.Thread(target=keep_pygame_on_top, daemon=True).start()

while running:
    draw_ui()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            elif event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                sustain_active = True

            elif event.key == pygame.K_TAB:
                arp_active = not arp_active

            elif event.key == pygame.K_LEFT:
                scale_index = (scale_index - 1) % len(scale_names)
                current_scale = scale_names[scale_index]

            elif event.key == pygame.K_RIGHT:
                scale_index = (scale_index + 1) % len(scale_names)
                current_scale = scale_names[scale_index]

            elif event.key == pygame.K_UP:
                scale_root_offset = (scale_root_offset + 1) % 12

            elif event.key == pygame.K_DOWN:
                scale_root_offset = (scale_root_offset - 1) % 12

            elif event.key == pygame.K_LEFTBRACKET:
                current_bend = max(-8192, current_bend - 1024)
                midi_out.send(mido.Message('pitchwheel', pitch=current_bend))

            elif event.key == pygame.K_RIGHTBRACKET:
                current_bend = min(8191, current_bend + 1024)
                midi_out.send(mido.Message('pitchwheel', pitch=current_bend))

            elif pygame.K_1 <= event.key <= pygame.K_9:
                raw_velocity = (event.key - pygame.K_0) * 12 + 20
                velocity = min(127, raw_velocity)

            elif event.key in key_map and event.key not in pressed_keys:
                octave_offset, scale_index = key_map[event.key]
                note = get_note_in_scale(octave_offset, scale_index)
                if chord_memory:
                    send_chord(note)
                else:
                    midi_out.send(mido.Message('note_on', note=note, velocity=velocity))
                    active_notes.append(note)
                if arp_active:
                    arp_notes.append((note, time.time()))
                pressed_keys.add(event.key)

        elif event.type == pygame.KEYUP:
            if event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                sustain_active = False
                for k in list(pressed_keys):
                    octave_offset, scale_index = key_map[k]
                    note = get_note_in_scale(octave_offset, scale_index)
                    if chord_memory:
                        stop_chord(note)
                    else:
                        midi_out.send(mido.Message('note_off', note=note, velocity=velocity))
                        if note in active_notes:
                            active_notes.remove(note)
                    pressed_keys.discard(k)

            elif event.key in key_map and not sustain_active:
                octave_offset, scale_index = key_map[event.key]
                note = get_note_in_scale(octave_offset, scale_index)
                if chord_memory:
                    stop_chord(note)
                else:
                    midi_out.send(mido.Message('note_off', note=note, velocity=velocity))
                    if note in active_notes:
                        active_notes.remove(note)
                pressed_keys.discard(event.key)

    if arp_active:
        now = time.time()
        for note, t in list(arp_notes):
            if now - t > ARP_INTERVAL:
                midi_out.send(mido.Message('note_off', note=note, velocity=velocity))
                if note in active_notes:
                    active_notes.remove(note)
                arp_notes.remove((note, t))

pygame.quit()
