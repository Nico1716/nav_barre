import pygame
import math
import os
from utils import *

class EvolutifScenario(Scenario):
    def __init__(self):
        super().__init__()
        self.vent_speed = 0.005  # Vitesse de rotation très lente du vent
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
            # Mise à jour de l'angle du vent avec rotation lente
            self.temps += self.vent_speed
            vent_angle_base = 90 + self.temps  # Rotation continue dans un sens
            self.vent_angle = calculer_angle_vent(vent_angle_base)
            super().update()  # Appeler update du parent seulement si pas en pause

def main():
    scenario = EvolutifScenario()
    scenario.run()

if __name__ == "__main__":
    main() 