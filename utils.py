import pygame
import math
import os
import sys
import importlib
import subprocess
import random
from state import control_all_boats, toggle_control_all_boats

# Initialisation de Pygame (une seule fois)
pygame.init()
pygame.key.set_repeat(100, 50)  # Délai initial de 100ms, puis répétition toutes les 50ms

# Dimensions de la fenêtre
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Couleurs
RED = (255, 120, 0)
BLUE = (0, 120, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
MAGENTA = (255, 0, 255)
DARK_GRAY = (100, 100, 100)

# Police pour le texte
FONT = pygame.font.SysFont(None, 32)
SMALL_FONT = pygame.font.SysFont(None, 24)  # Police plus petite pour certains textes
SYMBOL_FONT = pygame.font.SysFont("Segoe UI Symbol", 32)  # Police pour les symboles Unicode

# Variable globale pour l'affichage des laylines
show_laylines = True

# Variables pour les micro-variations du vent
micro_variation = 0
micro_variation_target = 0
micro_variation_timer = 0
micro_variation_duration = 60  # Durée de la phase stable en frames
micro_variation_transition = 20  # Durée de la transition en frames
micro_variations_active = False  # Par défaut, les micro-variations sont désactivées
micro_variation_phase = "stable"  # "stable", "transition_in", "transition_out"

class BateauPersonnalite:
    def __init__(self, type_perso):
        self.type = type_perso
        self.last_tack_time = pygame.time.get_ticks()
        self.tack_cooldown = 0
        # Délai initial plus long pour le bateau aléatoire
        self.next_tack_delay = random.randint(2000, 5000) if type_perso == "aleatoire" else random.randint(500, 2000)

    def decide_virement(self, bateau, vent_angle, vent_angle_precedent):
        if bateau.tack_cooldown > 0:
            return False

        current_time = pygame.time.get_ticks()
        
        if self.type == "adonnante":
            # Vire quand le vent change de direction
            if vent_angle < vent_angle_precedent and bateau.amure == 1:  # Vent diminue, on veut être tribord
                return True
            elif vent_angle > vent_angle_precedent and bateau.amure == -1:  # Vent augmente, on veut être bâbord
                return True

        elif self.type == "rapprochant":
            # Vire en fonction de l'angle du vent
            if vent_angle < 90 and bateau.amure == 1:  # Vent < 90°, on veut être tribord
                return True
            elif vent_angle >= 90 and bateau.amure == -1:  # Vent >= 90°, on veut être bâbord
                return True

        elif self.type == "aleatoire":
            # Vire aléatoirement après le délai défini
            if current_time - self.last_tack_time > self.next_tack_delay:
                self.last_tack_time = current_time
                self.next_tack_delay = random.randint(2000, 5000)  # Délai beaucoup plus long entre les virements
                return True

        return False

class Bateau:
    def __init__(self, position, couleur, sprites, is_player=False):
        self.position = list(position)  # [x, y]
        self.couleur = couleur
        self.sprites = sprites
        self.trajectoire = []
        self.amure = -1  # -1 = tribord, 1 = bâbord
        self.angle_base = 45  # 45 = près, 190 = portant
        self.angle_bateau = 0
        self.frame_index = "Pr"
        self.speed_mult = 1
        self.vitesse = 0.4
        self.manual_tack_pending = False
        self.tack_cooldown = 0
        self.is_player = is_player
        self.vent_angle_precedent = 90  # Pour suivre les changements de vent
        self.layline_depassee = False  # Flag pour indiquer si une layline a été dépassée
        
        # Comportements activés par défaut
        self.comportements = {
            'virement_manuel': True,
            'virement_laylines': True,
            'virement_bords': True,
            'changement_allure_bords': True
        }

    def _gerer_virements(self, all_laylines, bouee_pos):
        """Gère tous les types de virements du bateau."""
        
        # Virement manuel prioritaire
        if self.comportements['virement_manuel'] and self.manual_tack_pending and self.tack_cooldown == 0:
            self.amure = -self.amure
            self.manual_tack_pending = False
            self.tack_cooldown = 60
            return

        # Virement automatique sur les laylines
        if self.comportements['virement_laylines'] and all_laylines:
            laylines = all_laylines[0]
            
            # Ne pas virer automatiquement si c'est le bateau joueur
            if self.is_player and not control_all_boats:
                return

            # Vérifier si le bateau est dans le cadre des laylines
            lh = next((l for l in laylines if l['id'] == 'lh'), None)
            rc = next((l for l in laylines if l['id'] == 'rc'), None)
            
            if lh and rc:  # Vérifier que les laylines existent
                cadreDroite = side(self.position[0], self.position[1],
                            rc['start'][0], rc['start'][1],
                            rc['end'][0], rc['end'][1])
                
                cadreGauche = side(self.position[0], self.position[1],
                            lh['start'][0], lh['start'][1],
                            lh['end'][0], lh['end'][1])

                if cadreDroite > 0 and cadreGauche < 0:
                    self.layline_depassee = False
            
            # Virement avant layline gauche
            if lh and self.amure != 1 and self.position[1] > bouee_pos[1]:
                s = side(self.position[0], self.position[1], 
                        lh['start'][0], lh['start'][1], 
                        lh['end'][0], lh['end'][1])
                if s > 0:
                    if self.tack_cooldown == 0:
                        self.amure = 1
                        self.tack_cooldown = 60
                    self.layline_depassee = True
                    return

            # Virement après layline droite
            rh = next((l for l in laylines if l['id'] == 'rh'), None)
            if rh and self.amure != -1:
                s = side(self.position[0], self.position[1], 
                        rh['start'][0], rh['start'][1], 
                        rh['end'][0], rh['end'][1])
                if s < 0:
                    if self.tack_cooldown == 0:
                        self.amure = -1
                        self.tack_cooldown = 60
                    self.layline_depassee = True
                    return

            # Vérifier si le bateau dépasse la layline basse
            lc = next((l for l in laylines if l['id'] == 'lc'), None)
            if lc and self.angle_base == 45:
                s = side(self.position[0], self.position[1],
                        lc['start'][0], lc['start'][1],
                        lc['end'][0], lc['end'][1])
                if s > 0:  # Si le bateau est au-delà de la layline basse
                    self.angle_base = 55  # Changer l'angle de base à 55
                    self.layline_depassee = True

            if lh and self.angle_base == 55:
                s = side(self.position[0], self.position[1],
                        lh['start'][0], lh['start'][1],
                        lh['end'][0], lh['end'][1])
                if s < 0:
                    self.angle_base = 45

    def update(self, vent_angle, all_laylines=None):
        """Met à jour la position et l'état du bateau."""
        # Calcul de l'angle du bateau
        angle_au_vent = self.amure * self.angle_base
        self.angle_bateau = (vent_angle - angle_au_vent) % 360

        # Déterminer la frame et le multiplicateur de vitesse
        if 45 <= self.angle_base <= 55:  # Près
            self.frame_index = "Pr"
            self.speed_mult = 1
        elif 55 < self.angle_base < 155:  # Travers
            self.frame_index = "Tr"
            self.speed_mult = 1.5
        elif 155 <= self.angle_base <= 180:  # Vent arrière
            self.frame_index = "VA"
            self.speed_mult = 1
        elif self.angle_base > 180:  # Fausse panne
            self.frame_index = "FP"
            self.speed_mult = 1.2
        else:
            self.frame_index = "Pr"
            self.speed_mult = 1

        # Décrémenter le cooldown de virement
        if self.tack_cooldown > 0:
            self.tack_cooldown -= 1

        # Gestion des virements
        if all_laylines:
            bouee_pos = all_laylines[0][0]['start']  # La position de la bouée est le point de départ de la première layline
            self._gerer_virements(all_laylines, bouee_pos)

        # Virement selon la personnalité (si ce n'est pas le bateau joueur et qu'aucune layline n'a été dépassée)
        if not self.is_player and hasattr(self, 'personnalite') and self.personnalite is not None and not self.layline_depassee:
            if self.personnalite.decide_virement(self, vent_angle, self.vent_angle_precedent):
                self.amure = -self.amure
                self.tack_cooldown = 60

        # Mise à jour de l'angle du vent précédent
        self.vent_angle_precedent = vent_angle

        # Calcul de la vitesse en x et y avec multiplicateur
        dx = self.vitesse * self.speed_mult * math.cos(math.radians(self.angle_bateau))
        dy = -self.vitesse * self.speed_mult * math.sin(math.radians(self.angle_bateau))

        # Ajouter la position actuelle à la trajectoire
        self.trajectoire.append(tuple(self.position))
        if len(self.trajectoire) > 1000:  # Limiter la longueur des trajectoires
            self.trajectoire.pop(0)

        # Mise à jour de la position
        self.position[0] += dx
        self.position[1] += dy

        # Gestion des collisions avec les bords de l'écran
        if self.comportements['virement_bords']:
            if self.position[0] <= 0 or self.position[0] >= WIDTH:
                self.amure = -self.amure  # Inversion d'amure

        if self.comportements['changement_allure_bords']:
            if self.position[1] <= 0:
                self.angle_base = 190  # Passer au portant
            if self.position[1] >= HEIGHT:
                self.angle_base = 45  # Revenir au près

        # Limiter la position
        self.position[0] = max(0, min(WIDTH, self.position[0]))
        self.position[1] = max(0, min(HEIGHT, self.position[1]))

    def dessiner(self, screen):
        """Dessine le bateau et sa trajectoire."""
        # Dessiner la trajectoire
        if len(self.trajectoire) > 1:
            pygame.draw.lines(screen, self.couleur, False, self.trajectoire, 2)

        # Dessiner le bateau
        amure_str = "B" if self.amure == 1 else "T"
        sprite_key = f"{self.frame_index}_{amure_str}"
        bateau_sprite = self.sprites[sprite_key]
        bateau_oriente = pygame.transform.rotate(bateau_sprite, self.angle_bateau - 90)
        rect = bateau_oriente.get_rect(center=self.position)
        screen.blit(bateau_oriente, rect.topleft)

    def virement_manuel(self):
        """Déclenche un virement de bord manuel."""
        if self.tack_cooldown == 0:
            self.manual_tack_pending = True

    def toggle_laylines(self):
        """Active/désactive l'affichage des laylines."""
        self.comportements['virement_laylines'] = not self.comportements['virement_laylines']

    def ajuster_angle(self, delta):
        """Ajuste l'angle au vent du bateau."""
        if self.is_player:
            # Inverser le delta en fonction de l'amure
            delta_ajuste = delta if self.amure == 1 else -delta
            nouveau_angle = self.angle_base + delta_ajuste
            # Limiter l'angle entre 45 et 190 degrés
            self.angle_base = max(45, min(190, nouveau_angle))
            # Mettre à jour la frame et le multiplicateur de vitesse
            if 45 <= self.angle_base <= 55:  # Près
                self.frame_index = "Pr"
                self.speed_mult = 1
            elif 55 < self.angle_base < 155:  # Travers
                self.frame_index = "Tr"
                self.speed_mult = 1.5
            elif 155 <= self.angle_base <= 180:  # Vent arrière
                self.frame_index = "VA"
                self.speed_mult = 1
            elif self.angle_base > 180:  # Fausse panne
                self.frame_index = "FP"
                self.speed_mult = 1.2

def coloriser_frame(frame, couleur):
    """Colorise une frame avec la couleur spécifiée."""
    frame_colorisee = frame.copy()
    frame_colorisee.fill(couleur, special_flags=pygame.BLEND_MULT)
    return frame_colorisee

def dessiner_laylines(screen, bouee, vent_angle, distance=150, offset=20, draw=True):
    """
    Dessine toutes les lay-lines (centrale, haute, basse) de chaque côté de la bouée en fonction de l'angle du vent.
    Centrale = blanc (toujours affichée), haute = magenta, basse = jaune.
    Retourne les coordonnées de toutes les lay-lines.
    """
    x, y = bouee
    laylines = []
    for angle, side in zip([45, -45], ['r', 'l']):
        angle_central = (vent_angle + 180 + angle) % 360
        long_dist = max(WIDTH, HEIGHT) * 2
        # Centrale (toujours affichée)
        x_central = x + long_dist * math.cos(math.radians(angle_central))
        y_central = y - long_dist * math.sin(math.radians(angle_central))
        pygame.draw.line(screen, WHITE, (x, y), (x_central, y_central), 2)
        laylines.append({
            'type': 'central',
            'start': (x, y),
            'end': (x_central, y_central),
            'angle': angle_central,
            'id': f'{side}c'
        })
        # Haute et basse (affichées seulement si draw=True)
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

def side(px, py, x1, y1, x2, y2):
    """Calcule de quel côté d'une ligne se trouve un point."""
    return (x2 - x1)*(py - y1) - (y2 - y1)*(px - x1)

def charger_sprites():
    """Charge et retourne les sprites des bateaux."""
    sprite_folder = "sprites/Laser"
    player_folder = "sprites/Laser/Player"
    frames_dict = {}
    player_frames = {}

    # Charger les sprites normaux
    for filename in sorted(os.listdir(sprite_folder)):
        if filename.endswith(".png"):
            path = os.path.join(sprite_folder, filename)
            key = filename.replace(".png", "")  # e.g., "Pr_T"
            frames_dict[key] = pygame.image.load(path).convert_alpha()

    # Charger les sprites du joueur
    for filename in sorted(os.listdir(player_folder)):
        if filename.endswith(".png"):
            path = os.path.join(player_folder, filename)
            key = filename.replace(".png", "")  # e.g., "Pr_T"
            player_frames[key] = pygame.image.load(path).convert_alpha()

    # Définir les couleurs des bateaux
    couleurs_bateaux = [
        (255, 0, 0),   # Rouge
        (0, 255, 0),   # Vert
        (0, 0, 255),   # Bleu
        (255, 255, 0)  # Jaune
    ]

    # Créer les frames colorisées pour chaque bateau
    sprites = [
        {key: coloriser_frame(frames_dict[key], couleur) for key in frames_dict}
        for couleur in couleurs_bateaux
    ]

    # Ajouter les sprites du joueur
    sprites.append(player_frames)
    
    return sprites

def creer_bateaux():
    """Crée et retourne une liste de bateaux avec leurs positions initiales."""
    sprites = charger_sprites()
    bateaux = []
    
    # Définir les positions initiales possibles
    positions_initiales = [
        [100, HEIGHT - 100],
        [300, HEIGHT - 100],
        [500, HEIGHT - 100],
        [700, HEIGHT - 100]
    ]
    
    # Mélanger les positions
    random.shuffle(positions_initiales)
    
    # Définir les personnalités et leurs couleurs
    personnalites = [
        ("adonnante", (255, 0, 0)),      # Rouge
        ("rapprochant", (0, 255, 0)),    # Vert
        ("aleatoire", (0, 0, 255)),      # Bleu
        ("normal", (255, 255, 0))        # Jaune
    ]
    
    # Créer les bateaux normaux avec leurs personnalités
    for i, (pos, (type_perso, couleur), sprite) in enumerate(zip(positions_initiales, personnalites, sprites[:-1])):
        bateau = Bateau(pos, couleur, sprite, is_player=False)
        bateau.personnalite = BateauPersonnalite(type_perso)
        bateaux.append(bateau)
    
    # Créer le bateau joueur avec les sprites originaux
    player_bateau = Bateau([WIDTH//2, HEIGHT - 100], (255, 255, 255), sprites[-1], is_player=True)
    bateaux.append(player_bateau)
    
    return bateaux

def dessiner_vent(screen, vent_angle):
    """Dessine la flèche du vent."""
    x_centre, y_centre = WIDTH - 100, 100
    longueur = 50
    x1 = x_centre - longueur * math.cos(math.radians(vent_angle))
    y1 = y_centre + longueur * math.sin(math.radians(vent_angle))
    x2 = x_centre + longueur * math.cos(math.radians(vent_angle))
    y2 = y_centre - longueur * math.sin(math.radians(vent_angle))
    x_p1 = x1 - 10 * math.cos(math.radians(vent_angle + 150))
    y_p1 = y1 + 10 * math.sin(math.radians(vent_angle + 150))
    x_p2 = x1 - 10 * math.cos(math.radians(vent_angle - 150))
    y_p2 = y1 + 10 * math.sin(math.radians(vent_angle - 150))
    pygame.draw.line(screen, YELLOW, (x2, y2), (x1, y1), 3)
    pygame.draw.polygon(screen, YELLOW, [(x1, y1), (x_p1, y_p1), (x_p2, y_p2)])

def changer_scene(nom_fichier):
    """Change de scène en rechargeant le module correspondant."""
    # Sauvegarder l'état de control_all_boats
    global control_all_boats
    saved_control_state = control_all_boats
    
    # Nettoyer l'écran
    screen.fill(BLUE)
    pygame.display.flip()
    
    # Recharger le module
    if nom_fichier.endswith('.py'):
        nom_fichier = nom_fichier[:-3]
    module = importlib.import_module(nom_fichier)
    importlib.reload(module)
    
    # Restaurer l'état de control_all_boats
    control_all_boats = saved_control_state
    
    # Lancer la nouvelle scène
    module.main()

def dessiner_bouton_menu(screen):
    """Dessine un bouton 'Retour au menu' et retourne son rectangle."""
    texte = FONT.render("Retour au menu", True, WHITE)
    rect = pygame.Rect(10, 10, texte.get_width() + 20, texte.get_height() + 10)
    
    # Dessiner le fond du bouton
    pygame.draw.rect(screen, DARK_GRAY, rect)
    pygame.draw.rect(screen, WHITE, rect, 2)  # Bordure blanche
    
    # Dessiner le texte
    screen.blit(texte, (rect.x + 10, rect.y + 5))
    
    return rect

def retour_au_menu():
    """Retourne au menu principal."""
    changer_scene("menu")

def toggle_laylines():
    """Active/désactive l'affichage des laylines."""
    global show_laylines
    show_laylines = not show_laylines
    print(f"Laylines visibility: {show_laylines}")  # Debug print 

def activer_micro_variations(actif=True):
    """Active ou désactive les micro-variations du vent."""
    global micro_variations_active
    micro_variations_active = actif

def calculer_angle_vent(angle_base):
    """Calcule l'angle final du vent en incluant les micro-variations si activées."""
    global micro_variation, micro_variation_target, micro_variation_timer, micro_variation_phase
    
    if not micro_variations_active:
        return angle_base
        
    # Gestion des micro-variations
    if micro_variation_phase == "stable":
        if micro_variation_timer > 0:
            micro_variation_timer -= 1
        else:
            # Passer en phase de transition sortante
            micro_variation_phase = "transition_out"
            micro_variation_target = 0
            micro_variation_timer = micro_variation_transition
            
    elif micro_variation_phase == "transition_out":
        if micro_variation_timer > 0:
            # Transition douce vers 0
            progress = 1 - (micro_variation_timer / micro_variation_transition)
            micro_variation = micro_variation * (1 - progress)
            micro_variation_timer -= 1
        else:
            # 10% de chance de générer une nouvelle micro-variation
            if random.random() < 0.1:
                micro_variation_phase = "transition_in"
                micro_variation_target = random.uniform(-5, 5)
                micro_variation_timer = micro_variation_transition
            else:
                micro_variation_phase = "stable"
                micro_variation_timer = micro_variation_duration
                
    elif micro_variation_phase == "transition_in":
        if micro_variation_timer > 0:
            # Transition douce vers la nouvelle valeur
            progress = 1 - (micro_variation_timer / micro_variation_transition)
            micro_variation = micro_variation_target * progress
            micro_variation_timer -= 1
        else:
            # Passer en phase stable
            micro_variation = micro_variation_target
            micro_variation_phase = "stable"
            micro_variation_timer = micro_variation_duration

    # Angle final du vent = angle de base + micro-variation
    return angle_base + micro_variation 

def toggle_control_all_boats():
    """Active/désactive le contrôle de tous les bateaux."""
    global control_all_boats
    control_all_boats = not control_all_boats
    print(f"Toggling control_all_boats to: {control_all_boats}")  # Debug print

def get_controllable_boats(bateaux):
    """Retourne la liste des bateaux contrôlables."""
    if control_all_boats:
        return bateaux
    return [bateaux[-1]]  # Par défaut, seul le bateau joueur est contrôlable 

def dessiner_lignes_egalite(screen, bouee, vent_angle, draw=True):
    """
    Dessine des lignes d'égalité perpendiculaires au vent, à intervalles réguliers.
    Ces lignes sont des bandes blanches transparentes qui partent de la bouée jusqu'en bas de l'écran.
    """
    if not draw:
        return

    x, y = bouee
    # Angle perpendiculaire au vent
    angle_perp = -(vent_angle + 90) % 360
    
    # Créer une surface pour les lignes avec transparence
    surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    
    # Espacement entre les lignes
    espacement = 50
    
    # Calculer le nombre de lignes nécessaires
    nb_lignes = HEIGHT // espacement
    
    # Dessiner les lignes
    for i in range(nb_lignes):
        # Position de départ (sur la ligne du vent)
        start_x = x + i * espacement * math.cos(math.radians(vent_angle))
        start_y = y + i * espacement * math.sin(math.radians(vent_angle))
        
        # Points de la ligne perpendiculaire
        x1 = start_x - WIDTH * math.cos(math.radians(angle_perp))
        y1 = start_y - WIDTH * math.sin(math.radians(angle_perp))
        x2 = start_x + WIDTH * math.cos(math.radians(angle_perp))
        y2 = start_y + WIDTH * math.sin(math.radians(angle_perp))
        
        # Dessiner la ligne avec transparence
        pygame.draw.line(surface, (255, 255, 255, 50), (x1, y1), (x2, y2), 2)
    
    # Appliquer la surface sur l'écran
    screen.blit(surface, (0, 0))

class Scenario:
    def __init__(self):
        self.running = True
        self.vent_angle = 90
        self.bouee = (WIDTH // 2, 100)
        self.bateaux = creer_bateaux()
        self.laylines = []
        self.clock = pygame.time.Clock()
        self.show_laylines = False  # Laylines désactivées par défaut
        self.show_lignes_egalite = False  # Lignes d'égalité désactivées par défaut
        self.laylines_button = pygame.Rect(WIDTH - 200, 10, 180, 30)
        self.lignes_egalite_button = pygame.Rect(WIDTH - 200, 50, 180, 30)
        self.pause_button = pygame.Rect(10, 50, 40, 40)  # Bouton pause en haut à gauche
        self.paused = False  # État de pause
        
        # Créer les boutons de personnalité pour chaque bateau (sauf le joueur)
        self.personnalite_buttons = []
        button_radius = 15
        spacing = 40
        start_x = WIDTH - 200
        start_y = 100
        for i, bateau in enumerate(self.bateaux[:-1]):  # Exclure le dernier bateau (joueur)
            button = {
                'rect': pygame.Rect(start_x, start_y + i * spacing, button_radius * 2, button_radius * 2),
                'color': bateau.couleur,
                'active': True,
                'bateau_index': i
            }
            self.personnalite_buttons.append(button)

    def get_controllable_boats(self):
        """Retourne la liste des bateaux contrôlables. Par défaut, seul le bateau joueur est contrôlable."""
        return [self.bateaux[-1]]  # Par défaut, seul le dernier bateau (joueur) est contrôlable

    def handle_events(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    retour_au_menu()
                elif event.key == pygame.K_SPACE:
                    # Virement de bord pour le bateau joueur
                    self.bateaux[-1].virement_manuel()
                elif event.key == pygame.K_LEFT:
                    # Diminuer l'angle au vent
                    self.bateaux[-1].ajuster_angle(-1)
                elif event.key == pygame.K_RIGHT:
                    # Augmenter l'angle au vent
                    self.bateaux[-1].ajuster_angle(1)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Clic gauche
                    if dessiner_bouton_menu(screen).collidepoint(event.pos):
                        retour_au_menu()
                    elif self.laylines_button.collidepoint(event.pos):
                        self.show_laylines = not self.show_laylines
                    elif self.lignes_egalite_button.collidepoint(event.pos):
                        self.show_lignes_egalite = not self.show_lignes_egalite
                    elif self.pause_button.collidepoint(event.pos):
                        self.paused = not self.paused
                    else:
                        # Vérifier les clics sur les boutons de personnalité
                        for button in self.personnalite_buttons:
                            if button['rect'].collidepoint(event.pos):
                                button['active'] = not button['active']
                                # Désactiver/activer la personnalité du bateau
                                self.bateaux[button['bateau_index']].personnalite = None if not button['active'] else BateauPersonnalite("normal")
        return events

    def update(self):
        if not self.paused:  # Ne mettre à jour que si pas en pause
            self.laylines = dessiner_laylines(screen, self.bouee, self.vent_angle, draw=self.show_laylines)
            for bateau in self.bateaux:
                bateau.update(self.vent_angle, [self.laylines])

    def draw(self):
        screen.fill(BLUE)
        
        # Dessiner les laylines
        if self.show_laylines:
            dessiner_laylines(screen, self.bouee, self.vent_angle, draw=True)
        else:
            dessiner_laylines(screen, self.bouee, self.vent_angle, draw=False)
        
        # Dessiner les lignes d'égalité
        dessiner_lignes_egalite(screen, self.bouee, self.vent_angle, draw=self.show_lignes_egalite)
        
        # Dessiner les bateaux
        for bateau in self.bateaux:
            bateau.dessiner(screen)
        
        # Dessiner la bouée
        pygame.draw.circle(screen, YELLOW, self.bouee, 10)
        
        # Dessiner le vent
        dessiner_vent(screen, self.vent_angle)
        
        # Afficher l'angle du vent
        angle_text = FONT.render(f"Vent: {-int(self.vent_angle - 90)}°", True, WHITE)
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

        # Dessiner le bouton des lignes d'égalité
        pygame.draw.rect(screen, DARK_GRAY, self.lignes_egalite_button)
        pygame.draw.rect(screen, WHITE, self.lignes_egalite_button, 2)
        egalite_text = SMALL_FONT.render(
            "Lignes égalité: " + ("ON" if self.show_lignes_egalite else "OFF"),
            True, WHITE
        )
        screen.blit(egalite_text, (self.lignes_egalite_button.x + 10, self.lignes_egalite_button.y + 5))

        # Dessiner les boutons de personnalité
        for button in self.personnalite_buttons:
            # Dessiner le cercle avec la couleur du bateau
            pygame.draw.circle(screen, button['color'], button['rect'].center, button['rect'].width // 2)
            # Dessiner un contour blanc
            pygame.draw.circle(screen, WHITE, button['rect'].center, button['rect'].width // 2, 2)
            # Si le bouton est inactif, dessiner une croix
            if not button['active']:
                center = button['rect'].center
                pygame.draw.line(screen, WHITE, 
                               (center[0] - 8, center[1] - 8),
                               (center[0] + 8, center[1] + 8), 2)
                pygame.draw.line(screen, WHITE,
                               (center[0] + 8, center[1] - 8),
                               (center[0] - 8, center[1] + 8), 2)

        # Dessiner le bouton pause
        pygame.draw.rect(screen, DARK_GRAY, self.pause_button)
        pygame.draw.rect(screen, WHITE, self.pause_button, 2)
        pause_text = FONT.render("II" if not self.paused else "▶", True, WHITE)
        text_rect = pause_text.get_rect(center=self.pause_button.center)
        screen.blit(pause_text, text_rect)
        
        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60) 