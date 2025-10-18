from src.settings import SETTINGS, NOTE_NAMES
import pygame

class PianoUI:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font

    def draw(self):
        self.screen.fill((10, 10, 10))
        self.render_text(f"Escala: {SETTINGS['current_scale']}", (20, 20))
        self.render_text(f"Nota raíz: {NOTE_NAMES[SETTINGS['scale_root_offset']]}", (20, 60))
        self.render_text(f"Velocidad: {SETTINGS['velocity']}", (20, 100))
        self.render_text(f"Arpegiador: {'ON' if SETTINGS['arp_active'] else 'OFF'}", (20, 140))

        notes_str = ', '.join([f"{NOTE_NAMES[n % 12]}{(n // 12) - 1}" for n in SETTINGS['active_notes']])
        self.render_text(f"Notas activas: {notes_str if notes_str else 'Ninguna'}", (20, 220))

        pygame.draw.rect(self.screen, (100, 200, 100), (20, 180, SETTINGS['velocity'], 20))
        pygame.display.flip()

    def render_text(self, text, pos):
        surface = self.font.render(text, True, (255, 255, 255))
        self.screen.blit(surface, pos)