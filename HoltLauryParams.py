# -*- coding: utf-8 -*-
"""
Ce module contient les variables et les paramètres de la partie
Les variables ne doivent pas être changées
Les paramètres peuvent être changés, mais, par sécurité, demander au développeur
"""

# variables
BASELINE = 0

# paramètres
TREATMENT = BASELINE
TAUX_CONVERSION = 1
NOMBRE_PERIODES = 0
TAILLE_GROUPES = 0
GROUPES_CHAQUE_PERIODE = False
MONNAIE = u"ecu"

# DECISION
DECISION_MIN = 0
DECISION_MAX = 100
DECISION_STEP = 1

# paramètres
GAIN_OPTION_A = (16, 20)
GAIN_OPTION_B = (1.0, 38.5)
PROBAS = [(100-i,  i) for i in range(0,  101,  10)]

# variables
OPTION_A = 0
OPTION_B = 1
