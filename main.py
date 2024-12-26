import pygame
import math

# Initialisation de Pygame
pygame.init()

# Dimensions de la fenêtre
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Voiliers avec valeurs indépendantes")

# Couleurs
BLUE = (0, 120, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)

# Charger les frames en niveaux de gris
frames_gris = [pygame.image.load(f"Laser_sprite-{i}.png").convert_alpha() for i in range(1, 9)]

def coloriser_frame(frame, couleur):
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
bateaux = [
    [coloriser_frame(frame, couleur) for frame in frames_gris]
    for couleur in couleurs_bateaux
]

# Positions initiales des bateaux
positions = [[100, 200], [300, 200], [500, 200], [700, 200]]

# Trajectoires
trajectoires = [[] for _ in positions]

# Variables de navigation : amure et allure indépendantes pour chaque bateau
amures = [1 for _ in positions]         # Amures (1 = tribord, -1 = bâbord)
angles_base = [45 for _ in positions]   # Allures (45 = près, 190 = portant)

# Vitesse constante des bateaux
vitesse = 1

# Angle du vent (modifiable)
vent_angle = 90

# Variables spécifiques pour chaque bateau
angle_bateau = [0 for _ in positions]   # Orientation de chaque bateau
frame_index = [0 for _ in positions]    # Frame utilisée par chaque bateau
speed_mult = [1 for _ in positions]     # Multiplicateur de vitesse pour chaque bateau

# Slider
slider_rect = pygame.Rect(150, 550, 500, 10)
slider_pos = 400
slider_dragging = False

clock = pygame.time.Clock()

# Boucle principale
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if slider_rect.collidepoint(event.pos):
                slider_dragging = True
        if event.type == pygame.MOUSEBUTTONUP:
            slider_dragging = False
        if event.type == pygame.MOUSEMOTION:
            if slider_dragging:
                slider_pos = max(slider_rect.left, min(slider_rect.right, event.pos[0]))
                # Calculer l'angle du vent en fonction de la position du curseur
                slider_angle = -20 + (slider_pos - slider_rect.left) / slider_rect.width * 40
                vent_angle = slider_angle + 90
        if event.type == pygame.KEYDOWN:
            # Change de bord (inversion de l'amure)
            if event.key == pygame.K_SPACE:
                amures = [-amure for amure in amures]
    # Fond de la fenêtre
    screen.fill(BLUE)

    # Dessiner le slider
    pygame.draw.rect(screen, GRAY, slider_rect)
    pygame.draw.circle(screen, WHITE, (slider_pos, slider_rect.centery), 10)

    # Dessiner la flèche du vent
    x_centre, y_centre = WIDTH - 100, 100
    longueur = 50
    x1 = x_centre - longueur * math.cos(math.radians(vent_angle))
    y1 = y_centre + longueur * math.sin(math.radians(vent_angle))
    x2 = x_centre + longueur * math.cos(math.radians(vent_angle))
    y2 = y_centre - longueur * math.sin(math.radians(vent_angle))
    x_p1 = x2 + 10 * math.cos(math.radians(vent_angle + 150))
    y_p1 = y2 - 10 * math.sin(math.radians(vent_angle + 150))
    x_p2 = x2 + 10 * math.cos(math.radians(vent_angle - 150))
    y_p2 = y2 - 10 * math.sin(math.radians(vent_angle - 150))
    pygame.draw.line(screen, YELLOW, (x2, y2), (x1, y1), 3)
    pygame.draw.polygon(screen, YELLOW, [(x2, y2), (x_p1, y_p1), (x_p2, y_p2)])

    # Calcul des déplacements pour chaque bateau
    for i, position in enumerate(positions):
        angle_au_vent = amures[i] * angles_base[i]
        angle_bateau[i] = (vent_angle - angle_au_vent) % 360

        # Déterminer la frame et le multiplicateur de vitesse
        if 45 <= angles_base[i] <= 55:  # Près
            frame_index[i] = 1 if amures[i] == 1 else 0
            speed_mult[i] = 1
        elif 55 < angles_base[i] < 155:  # Travers
            frame_index[i] = 5 if amures[i] == 1 else 4
            speed_mult[i] = 1.5
        elif 155 <= angles_base[i] <= 180:  # Vent arrière
            frame_index[i] = 7 if amures[i] == 1 else 6
            speed_mult[i] = 1
        elif angles_base[i] > 180:  # Fausse panne
            frame_index[i] = 3 if amures[i] == 1 else 2
            speed_mult[i] = 1.2
        else:
            frame_index[i] = 1
            speed_mult[i] = 1

        # Calcul de la vitesse en x et y avec multiplicateur
        dx = vitesse * speed_mult[i] * math.cos(math.radians(angle_bateau[i]))
        dy = -vitesse * speed_mult[i] * math.sin(math.radians(angle_bateau[i]))

        # Ajouter la position actuelle à la trajectoire
        trajectoires[i].append(tuple(position))
        if len(trajectoires[i]) > 1000:  # Limiter la longueur des trajectoires
            trajectoires[i].pop(0)

        # Mise à jour de la position
        position[0] += dx
        position[1] += dy

        # Gestion des collisions avec les bords de l'écran
        if position[0] <= 0 or position[0] >= WIDTH:
            amures[i] = -amures[i]  # Inversion d'amure
        if position[1] <= 0:
            angles_base[i] = 190  # Passer au portant
        if position[1] >= HEIGHT:
            angles_base[i] = 45  # Revenir au près

        # Limiter la position
        position[0] = max(0, min(WIDTH, position[0]))
        position[1] = max(0, min(HEIGHT, position[1]))

    # Dessiner les trajectoires
    for i, trajectoire in enumerate(trajectoires):
        if len(trajectoire) > 1:
            pygame.draw.lines(screen, couleurs_bateaux[i], False, trajectoire, 2)

    # Dessiner les bateaux
    for i, position in enumerate(positions):
        bateau_oriente = pygame.transform.rotate(bateaux[i][frame_index[i]], angle_bateau[i] - 90)
        rect = bateau_oriente.get_rect(center=position)
        screen.blit(bateau_oriente, rect.topleft)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()