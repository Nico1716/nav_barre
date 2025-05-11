import pygame
import sys
import subprocess
from utils import (
    WIDTH, HEIGHT, screen, FONT, SMALL_FONT, 
    control_all_boats, toggle_control_all_boats
)

pygame.init()
pygame.key.set_repeat(0)

# List of scenarios (add more as needed)
scenarios = [
    {"name": "Default", "file": "new_test.py"},
    {"name": "Oscillant", "file": "oscillant.py"},
    # {"name": "Autre scénario", "file": "autre.py"},
]
selected = 0

BG_COLOR = (30, 30, 60)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)

# Position de la case à cocher
checkbox_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 100, 20, 20)

def dessiner_checkbox(rect, texte, checked):
    """Dessine une case à cocher avec son texte."""
    pygame.draw.rect(screen, WHITE, rect, 2)
    if checked:
        pygame.draw.line(screen, WHITE, (rect.x + 5, rect.y + 10), (rect.x + 8, rect.y + 15), 2)
        pygame.draw.line(screen, WHITE, (rect.x + 8, rect.y + 15), (rect.x + 15, rect.y + 5), 2)
    texte_surface = SMALL_FONT.render(texte, True, WHITE)
    screen.blit(texte_surface, (rect.x + 30, rect.y))

running = True
while running:
    screen.fill(BG_COLOR)
    title = FONT.render("Choisissez un scénario", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))

    for i, scenario in enumerate(scenarios):
        color = YELLOW if i == selected else WHITE
        label = SMALL_FONT.render(scenario["name"], True, color)
        screen.blit(label, (WIDTH // 2 - label.get_width() // 2, 200 + i * 50))

    # Dessiner la case à cocher
    dessiner_checkbox(checkbox_rect, "Contrôler tous les bateaux", control_all_boats)

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                selected = (selected - 1) % len(scenarios)
            elif event.key == pygame.K_DOWN:
                selected = (selected + 1) % len(scenarios)
            elif event.key == pygame.K_RETURN:
                # Launch the selected scenario
                scenario_file = scenarios[selected]["file"]
                pygame.quit()
                subprocess.run([sys.executable, scenario_file])
                sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Clic gauche
                mouse_pos = pygame.mouse.get_pos()
                if checkbox_rect.collidepoint(mouse_pos):
                    toggle_control_all_boats()
                    print(f"Control all boats: {control_all_boats}")  # Debug print

pygame.quit() 