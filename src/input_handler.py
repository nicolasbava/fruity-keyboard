from src.settings import SETTINGS
import pygame

custom_shift = {
    pygame.K_k: 1,
    pygame.K_i: 1
}

rows = [
    [pygame.K_z, pygame.K_x, pygame.K_c, pygame.K_v, pygame.K_b, pygame.K_n, pygame.K_m, pygame.K_COMMA, pygame.K_PERIOD],
    [pygame.K_a, pygame.K_s, pygame.K_d, pygame.K_f, pygame.K_g, pygame.K_h, pygame.K_j, pygame.K_k, pygame.K_l, pygame.K_SEMICOLON],
    [pygame.K_q, pygame.K_w, pygame.K_e, pygame.K_r, pygame.K_t, pygame.K_y, pygame.K_u, pygame.K_i, pygame.K_o, pygame.K_p]
]

key_map = {}
for row_index, row in enumerate(rows):
    for i, key in enumerate(row):
        octave_shift = custom_shift.get(key, 1 if i >= len(row) - 2 else 0)
        key_map[key] = (row_index + octave_shift, i)

from src.midi_handler import MidiHandler

def handle_events(pygame, midi: MidiHandler, ui):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False

        if event.type == pygame.KEYDOWN:
            key = event.key

            if key == pygame.K_ESCAPE:
                return False
            elif key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                SETTINGS['sustain_active'] = True
            elif key == pygame.K_TAB:
                SETTINGS['arp_active'] = not SETTINGS['arp_active']
            elif key == pygame.K_LEFT:
                SETTINGS['scale_index'] = (SETTINGS['scale_index'] - 1) % len(SETTINGS['scale_names'])
                SETTINGS['current_scale'] = SETTINGS['scale_names'][SETTINGS['scale_index']]
            elif key == pygame.K_RIGHT:
                SETTINGS['scale_index'] = (SETTINGS['scale_index'] + 1) % len(SETTINGS['scale_names'])
                SETTINGS['current_scale'] = SETTINGS['scale_names'][SETTINGS['scale_index']]
            elif key == pygame.K_UP:
                SETTINGS['scale_root_offset'] = (SETTINGS['scale_root_offset'] + 1) % 12
            elif key == pygame.K_DOWN:
                SETTINGS['scale_root_offset'] = (SETTINGS['scale_root_offset'] - 1) % 12
            elif key == pygame.K_LEFTBRACKET:
                SETTINGS['current_bend'] = max(-8192, SETTINGS['current_bend'] - 1024)
                midi.out.send(mido.Message('pitchwheel', pitch=SETTINGS['current_bend']))
            elif key == pygame.K_RIGHTBRACKET:
                SETTINGS['current_bend'] = min(8191, SETTINGS['current_bend'] + 1024)
                midi.out.send(mido.Message('pitchwheel', pitch=SETTINGS['current_bend']))
            elif pygame.K_1 <= key <= pygame.K_9:
                SETTINGS['velocity'] = min(127, (key - pygame.K_0) * 12 + 20)
            elif key in key_map and key not in SETTINGS['pressed_keys']:
                octave_offset, scale_index = key_map[key]
                note = midi.get_note(octave_offset, scale_index)
                if SETTINGS['chord_memory']:
                    midi.send_chord(note)
                else:
                    midi.send_note_on(note)
                if SETTINGS['arp_active']:
                    SETTINGS['arp_notes'].append((note, time.time()))
                SETTINGS['pressed_keys'].add(key)

        elif event.type == pygame.KEYUP:
            key = event.key
            if key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                SETTINGS['sustain_active'] = False
                for k in list(SETTINGS['pressed_keys']):
                    octave_offset, scale_index = key_map[k]
                    note = midi.get_note(octave_offset, scale_index)
                    if SETTINGS['chord_memory']:
                        midi.stop_chord(note)
                    else:
                        midi.send_note_off(note)
                    SETTINGS['pressed_keys'].discard(k)
            elif key in key_map and not SETTINGS['sustain_active']:
                octave_offset, scale_index = key_map[key]
                note = midi.get_note(octave_offset, scale_index)
                if SETTINGS['chord_memory']:
                    midi.stop_chord(note)
                else:
                    midi.send_note_off(note)
                SETTINGS['pressed_keys'].discard(key)
    return True