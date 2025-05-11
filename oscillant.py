import pygame
import math
import os
import random
from utils import *

# Dimensions de la fenêtre
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Voiliers avec vent oscillant")

# Couleurs
RED = (255, 120, 0)
BLUE = (0, 120, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
MAGENTA = (255, 0, 255)

# Charger les frames en niveaux de gris
sprite_folder = "sprites/Laser"
frames_dict = {}

for filename in sorted(os.listdir(sprite_folder)):
    if filename.endswith(".png"):
        path = os.path.join(sprite_folder, filename)
        key = filename.replace(".png", "")  # e.g., "Pr_T"
        frames_dict[key] = pygame.image.load(path).convert_alpha()

def coloriser_frame(frame, couleur):
    frame_colorisee = frame.copy()
    frame_colorisee.fill(couleur, special_flags=pygame.BLEND_MULT)
    return frame_colorisee

# Variable pour afficher/masquer les laylines
show_laylines = True

def dessiner_laylines(screen, bouee, vent_angle, distance=150, offset=30, draw=True):
    """
    Dessine toutes les lay-lines (centrale, haute, basse) de chaque côté de la bouée en fonction de l'angle du vent.
    Centrale = blanc, haute = magenta, basse = jaune.
    Retourne les coordonnées de toutes les lay-lines.
    """
    x, y = bouee
    laylines = []
    for angle, side in zip([45, -45], ['r', 'l']):
        angle_central = (vent_angle + 180 + angle) % 360
        long_dist = max(WIDTH, HEIGHT) * 2
        # Centrale
        x_central = x + long_dist * math.cos(math.radians(angle_central))
        y_central = y - long_dist * math.sin(math.radians(angle_central))
        if draw:
            pygame.draw.line(screen, WHITE, (x, y), (x_central, y_central), 2)
        laylines.append({
            'type': 'central',
            'start': (x, y),
            'end': (x_central, y_central),
            'angle': angle_central,
            'id': f'{side}c'
        })
        # Haute et basse
        for direction, name, suffix in [(-1, 'haute', 'h'), (1, 'basse', 'b')]:
            x_offset = x + direction * offset * math.sin(math.radians(angle_central))
            y_offset = y + direction * offset * math.cos(math.radians(angle_central))
            x_end = x_offset + long_dist * math.cos(math.radians(angle_central))
            y_end = y_offset - long_dist * math.sin(math.radians(angle_central))
            color = MAGENTA if name == 'haute' else YELLOW
            if draw:
                pygame.draw.line(screen, color, (x_offset, y_offset), (x_end, y_end), 2)
            laylines.append({
                'type': name,
                'start': (x_offset, y_offset),
                'end': (x_end, y_end),
                'angle': angle_central,
                'id': f'{side}{suffix}'
            })
    return laylines

# Charger les sprites et créer les bateaux
sprites = charger_sprites()
bateaux = creer_bateaux()

# Placer la bouée par défaut vers le haut de l'écran
bouee = (WIDTH // 2, 100)

# Variables pour le vent
vent_angle = 90  # Angle initial du vent
vent_speed = 0.006  # Vitesse de l'oscillation du vent
temps = 0  # Compteur de temps pour l'oscillation

# Activer les micro-variations pour ce scénario
activer_micro_variations(True)

clock = pygame.time.Clock()

class OscillantScenario(Scenario):
    def __init__(self):
        super().__init__()
        self.vent_speed = 0.005
        self.temps = 0
        activer_micro_variations(True)

    def handle_events(self):
        events = super().handle_events()
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Virement de bord uniquement pour le bateau joueur
                    self.bateaux[-1].virement_manuel()

    def update(self):
        if not self.paused:  # Ne mettre à jour que si pas en pause
            # Mise à jour de l'angle du vent avec oscillation
            self.temps += self.vent_speed
            vent_angle_base = 90 + 10 * math.sin(self.temps)  # Oscillation entre 70° et 110°
            self.vent_angle = calculer_angle_vent(vent_angle_base)
        super().update()

def main():
    scenario = OscillantScenario()
    scenario.run()

if __name__ == "__main__":
    main() 