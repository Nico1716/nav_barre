import pygame

# Initialisation de Pygame
pygame.init()

# Dimensions de la fenêtre
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Plusieurs bateaux colorisés")

# Charger les frames en niveaux de gris
frames_gris = [pygame.image.load(f"Laser_sprite-{i}.png").convert_alpha() for i in range(1, 4)]

def coloriser_frame(frame, couleur):
    """
    Applique une couleur sur une frame en niveaux de gris.
    :param frame: Surface d'une frame en niveaux de gris
    :param couleur: Tuple RGB de la couleur (ex: (255, 0, 0) pour rouge)
    :return: Nouvelle surface avec la couleur appliquée
    """
    frame_colorisee = frame.copy()
    frame_colorisee.fill(couleur, special_flags=pygame.BLEND_MULT)
    return frame_colorisee

# Définir les couleurs des bateaux
couleurs_bateaux = [
    (255, 0, 0),   # Rouge
    (0, 255, 0),   # Vert
    (0, 0, 255),   # Bleu
    (255, 255, 0)  # Jaune
]

# Créer les frames colorisées pour chaque bateau
bateaux = []
for couleur in couleurs_bateaux:
    frames_colorisees = [coloriser_frame(frame, couleur) for frame in frames_gris]
    bateaux.append(frames_colorisees)

# Positions initiales des bateaux
positions = [
    [100, 200],
    [300, 200],
    [500, 200],
    [700, 200]
]

# Frame actuelle pour l'animation
frame_actuelle = 0

clock = pygame.time.Clock()

# Boucle principale
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Mettre à jour l'animation
    # frame_actuelle = (frame_actuelle + 1) % len(frames_gris)

    # Affichage
    screen.fill((0, 120, 255))  # Fond bleu pour la mer

    # Dessiner chaque bateau
    for i, bateau in enumerate(bateaux):
        screen.blit(bateau[frame_actuelle], positions[i])

    pygame.display.flip()
    clock.tick(10)  # Limiter à 10 FPS pour l'animation

pygame.quit()