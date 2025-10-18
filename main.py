from src.ui import PianoUI
from src.input_handler import handle_events
from src.midi_handler import MidiHandler
from src.settings import SETTINGS, SCREEN_DIMENSIONS
import pygame, time

pygame.init()
screen = pygame.display.set_mode(SCREEN_DIMENSIONS)
pygame.display.set_caption("Super Piano para Ableton")
font = pygame.font.SysFont("Arial", 16)
clock = pygame.time.Clock()

ui = PianoUI(screen, font)
midi = MidiHandler()

running = True

while running:
    now = time.time()
    running = handle_events(pygame, midi, ui)
    midi.update_arp(now)
    ui.draw()
    clock.tick(30)  # Controla FPS

pygame.quit()