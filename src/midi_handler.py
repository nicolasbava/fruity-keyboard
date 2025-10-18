from src.settings import SETTINGS, SCALES, NOTE_NAMES, MIDI_PORT_NAME, ARP_INTERVAL
import mido, time

class MidiHandler:
    def __init__(self):
        try:
            self.out = mido.open_output(MIDI_PORT_NAME)
        except IOError:
            print(f"No se encontró el puerto MIDI '{MIDI_PORT_NAME}'")
            exit(1)

    def get_note(self, octave_offset, index_in_scale):
        scale = SCALES[SETTINGS['current_scale']]
        degree = index_in_scale % len(scale)
        return SETTINGS['root_note'] + SETTINGS['scale_root_offset'] + (12 * octave_offset) + scale[degree]

    def send_note_on(self, note):
        self.out.send(mido.Message('note_on', note=note, velocity=SETTINGS['velocity']))
        SETTINGS['active_notes'].append(note)

    def send_note_off(self, note):
        self.out.send(mido.Message('note_off', note=note, velocity=SETTINGS['velocity']))
        if note in SETTINGS['active_notes']:
            SETTINGS['active_notes'].remove(note)

    def send_chord(self, note):
        for interval in [0, 4, 7]:
            self.send_note_on(note + interval)

    def stop_chord(self, note):
        for interval in [0, 4, 7]:
            self.send_note_off(note + interval)

    def update_arp(self, now):
        if SETTINGS['arp_active']:
            for note, t in list(SETTINGS['arp_notes']):
                if now - t > ARP_INTERVAL:
                    self.send_note_off(note)
                    SETTINGS['arp_notes'].remove((note, t))