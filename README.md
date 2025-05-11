# Nav Barre - Simulateur de Régate

Un simulateur de régate de voile en Python utilisant Pygame, permettant de simuler le comportement de plusieurs bateaux avec différentes personnalités.

## Fonctionnalités

### Scénarios
- **Scénario par défaut** : Contrôle de tous les bateaux avec la barre d'espace
- **Scénario oscillant** : Vent oscillant avec micro-variations, contrôle uniquement du bateau joueur
- **Scénario évolutif** : Vent qui tourne lentement dans un sens avec micro-variations, contrôle uniquement du bateau joueur

### Bateaux
- 5 bateaux avec des personnalités distinctes :
  - **Rouge** : Adonnante - Vire quand le vent change de direction
  - **Vert** : Rapprochant - Vire en fonction de l'angle du vent
  - **Bleu** : Aléatoire - Vire aléatoirement toutes les 2-5 secondes
  - **Jaune** : Normal - Pas de comportement spécial
  - **Blanc** : Joueur - Contrôlable par l'utilisateur

### Contrôles
- **Barre d'espace** : Virement de bord
- **Slider** (scénario par défaut) : Contrôle de l'angle du vent
- **Bouton "Debug laylines"** : Affiche/masque les laylines de debug
- **Échap** : Retour au menu principal

### Caractéristiques
- Simulation réaliste des virements de bord
- Visualisation des laylines
- Différents cas de conditions ET de stratégies
- Trajectoires des bateaux
- Interface utilisateur intuitive

## Installation

1. Assurez-vous d'avoir Python 3.x installé
2. Installez les dépendances :
```bash
pip install pygame
```

## Lancement

```bash
python menu.py
```

## Structure du Projet
- `menu.py` : Menu principal et sélection des scénarios
- `utils.py` : Classes et fonctions utilitaires
- `default.py` : Scénario par défaut avec slider
- `oscillant.py` : Scénario avec vent oscillant
- `evolutif.py` : Scénario avec vent qui tourne lentement
- `sprites/` : Dossier contenant les sprites des bateaux

## Développement
Le projet utilise une architecture orientée objet avec :
- Classe `Scenario` comme base pour tous les scénarios
- Classe `Bateau` pour la gestion des bateaux
- Classe `BateauPersonnalite` pour les différents comportements

## Contribution
Les contributions sont les bienvenues ! N'hésitez pas à :
1. Fork le projet
2. Créer une branche pour votre fonctionnalité
3. Commiter vos changements
4. Pousser vers la branche
5. Ouvrir une Pull Request