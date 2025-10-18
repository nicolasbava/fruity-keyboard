SCREEN_DIMENSIONS = (220, 270)
MIDI_PORT_NAME = 'port1 1'
DEFAULT_VELOCITY = 100
PITCH_BEND_RANGE = 8192
ARP_INTERVAL = 0.2

SCALES = {
    'major': [0, 2, 4, 5, 7, 9, 11],
    'minor': [0, 2, 3, 5, 7, 8, 10],
    'pentatonic': [0, 2, 4, 7, 9],
    'chromatic': list(range(12))
}

NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

SETTINGS = {
    'root_note': 60,
    'current_scale': 'chromatic',
    'scale_root_offset': 0,
    'scale_names': list(SCALES.keys()),
    'scale_index': 3,
    'velocity': DEFAULT_VELOCITY,
    'arp_active': False,
    'chord_memory': False,
    'sustain_active': False,
    'pressed_keys': set(),
    'active_notes': [],
    'arp_notes': [],
    'current_bend': 0
}