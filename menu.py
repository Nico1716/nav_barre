import pygame
import sys
import subprocess
from utils import (
    WIDTH, HEIGHT, screen, FONT, SMALL_FONT
)

pygame.init()
pygame.key.set_repeat(0)

# List of scenarios (add more as needed)
scenarios = [
    {"name": "Default", "file": "default.py"},
    {"name": "Oscillant", "file": "oscillant.py"},
    {"name": "Évolutif", "file": "evolutif.py"},
    # {"name": "Autre scénario", "file": "autre.py"},
]
selected = 0

BG_COLOR = (30, 30, 60)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)

running = True
while running:
    screen.fill(BG_COLOR)
    title = FONT.render("Choisissez un scénario", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))

    for i, scenario in enumerate(scenarios):
        color = YELLOW if i == selected else WHITE
        label = SMALL_FONT.render(scenario["name"], True, color)
        screen.blit(label, (WIDTH // 2 - label.get_width() // 2, 200 + i * 50))

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

pygame.quit() 