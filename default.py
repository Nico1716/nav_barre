import pygame
import math
import os
from utils import *

# Initialisation de Pygame
pygame.init()
pygame.key.set_repeat(0)

# Dimensions de la fenêtre
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Voiliers")

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

class SliderScenario(Scenario):
    def __init__(self):
        super().__init__()
        self.slider_rect = pygame.Rect(150, 550, 500, 10)
        self.slider_pos = 400
        self.slider_dragging = False
        self.vent_angle = 90  # Angle initial du vent

    def get_controllable_boats(self):
        """Dans le scénario par défaut, tous les bateaux sont contrôlables."""
        return self.bateaux

    def handle_events(self):
        events = super().handle_events()
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Clic gauche
                    mouse_pos = pygame.mouse.get_pos()
                    if self.slider_rect.collidepoint(mouse_pos):
                        self.slider_dragging = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Relâchement du clic gauche
                    self.slider_dragging = False
            elif event.type == pygame.MOUSEMOTION:
                if self.slider_dragging:
                    mouse_x = pygame.mouse.get_pos()[0]
                    self.slider_pos = max(self.slider_rect.left, min(self.slider_rect.right, mouse_x))
                    slider_angle = -20 + (self.slider_pos - self.slider_rect.left) / self.slider_rect.width * 40
                    self.vent_angle = slider_angle + 90
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Virement de bord pour tous les bateaux contrôlables
                    for bateau in self.get_controllable_boats():
                        bateau.virement_manuel()

    def draw(self):
        screen.fill(BLUE)
        
        # Dessiner les laylines
        if self.show_laylines:
            dessiner_laylines(screen, self.bouee, self.vent_angle, draw=True)
        else:
            dessiner_laylines(screen, self.bouee, self.vent_angle, draw=False)
        
        # Dessiner les bateaux
        for bateau in self.bateaux:
            bateau.dessiner(screen)
        
        # Dessiner la bouée
        pygame.draw.circle(screen, YELLOW, self.bouee, 10)
        
        # Dessiner le vent
        dessiner_vent(screen, self.vent_angle)
        
        # Afficher l'angle du vent
        angle_text = FONT.render(f"Vent: {int(self.vent_angle - 90)}°", True, WHITE)
        screen.blit(angle_text, (10, HEIGHT - 80))
        
        # Dessiner le bouton menu
        dessiner_bouton_menu(screen)

        # Dessiner le bouton des laylines
        pygame.draw.rect(screen, DARK_GRAY, self.laylines_button)
        pygame.draw.rect(screen, WHITE, self.laylines_button, 2)
        laylines_text = SMALL_FONT.render(
            "Debug laylines: " + ("ON" if self.show_laylines else "OFF"),
            True, WHITE
        )
        screen.blit(laylines_text, (self.laylines_button.x + 10, self.laylines_button.y + 5))

        # Dessiner le slider
        pygame.draw.rect(screen, GRAY, self.slider_rect)
        pygame.draw.circle(screen, WHITE, (self.slider_pos, self.slider_rect.centery), 10)
        
        # Ajouter le texte pour le slider
        slider_text = SMALL_FONT.render("Angle du vent", True, WHITE)
        screen.blit(slider_text, (self.slider_rect.x, self.slider_rect.y - 25))
        
        # Afficher la valeur actuelle de l'angle
        angle_value = int(self.vent_angle - 90)
        angle_text = SMALL_FONT.render(f"{angle_value}°", True, WHITE)
        screen.blit(angle_text, (self.slider_rect.right + 10, self.slider_rect.y - 5))
        
        pygame.display.flip()

def main():
    scenario = SliderScenario()
    scenario.run()

if __name__ == "__main__":
    main()
    pygame.quit()