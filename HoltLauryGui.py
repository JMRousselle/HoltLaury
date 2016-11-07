# -*- coding: utf-8 -*-
"""
Ce module contient les boites de dialogue du programme.
"""

import logging
import random

from PyQt4 import QtGui, QtCore

from client.cltgui.cltguidialogs import GuiHistorique
from util.utili18n import le2mtrans
from client import clttexts as textes_main
import HoltLauryParams as pms
import HoltLauryTexts as texts
from HoltLauryGuiSrc import HoltLauryDecision


logger = logging.getLogger("le2m")


class GuiDecision(QtGui.QDialog):
    def __init__(self, defered, automatique, parent, periode, historique):
        super(GuiDecision, self).__init__(parent)

        # variables
        self._defered = defered
        self._automatique = automatique
        self._historique = GuiHistorique(self, historique)

        # gui
        self.ui = HoltLauryDecision.Ui_Dialog()
        self.ui.setupUi(self)
        
        self.ui.pushButton_valider.clicked.connect(self._accept)
        self.ui.pushButton_valider.setEnabled(True)        

        self.ui.te_consignes.setText(u"Pour chacune des 11 questions ci-dessous veuillez indiquer l'option que vous choisissez.\n\
Vous devez pour cela saisir 'A' ou 'B' dans la zone de texte correspondant à la question.")
        
        # Remplissage des libelles options A et B
        for i in range(11):
            zea = getattr(self.ui,  'HL_Q%dOA' % (i+1, ))
            zea.setText(u"{} {} avec {}% de chances ou \n{} {} avec {}% de chances".format( \
                        pms.GAIN_OPTION_A[0],  \
                        pms.GAIN_OPTION_A[0] > 1 and "{}s".format(pms.MONNAIE) or pms.MONNAIE,   \
                        pms.PROBAS[i][0],  \
                        pms.GAIN_OPTION_A[1],  \
                        pms.GAIN_OPTION_A[1] > 1 and "{}s".format(pms.MONNAIE) or pms.MONNAIE,  \
                        pms.PROBAS[i][1]))
            zeb = getattr(self.ui,  'HL_Q%dOB' % (i+1, ))
            zeb.setText(u"{} {} avec {}% de chances ou \n{} {} avec {}% de chances".format( \
                        pms.GAIN_OPTION_B[0],  \
                        pms.GAIN_OPTION_B[0] > 1 and "{}s".format(pms.MONNAIE) or pms.MONNAIE,   \
                        pms.PROBAS[i][0],  \
                        pms.GAIN_OPTION_B[1],  \
                        pms.GAIN_OPTION_B[1] > 1 and "{}s".format(pms.MONNAIE) or pms.MONNAIE,  \
                        pms.PROBAS[i][1])) 

        # automatic
        if self._automatique:
            for i in range(11):
                rea = getattr(self.ui,  'HL_R%d' % (i+1, ))
                rea.setText(random.choice([u"A",  u"B"])) 
            self._timer_automatique = QtCore.QTimer()
            self._timer_automatique.timeout.connect(self._accept)
            self._timer_automatique.start(7000)
                
    def reject(self):
        pass
    
    def _accept(self):
        self.ui.pushButton_valider.setEnabled(False)
        decision = {}        
        try:
            for i in range(11):
                lineEdit = getattr(self.ui,  'HL_R%d' % (i+1, ))
                choix = str(lineEdit.text())
                if choix != u"A" and choix != u"B":
                    raise ValueError
                if choix == u"A": decision[u"HL_question_%d" % (i+1, )] = pms.OPTION_A
                else: decision[u"HL_question_%d" % (i+1, )] = pms.OPTION_B
        except ValueError:
            QtGui.QMessageBox.warning(self, "ATTENTION" , u"Pour chaque question vous devez saisir soit A soit B.",  QtGui.QMessageBox.Ok)
            self.ui.pushButton_valider.setEnabled(True)
            return        
        if not self._automatique:
#            confirmation = QtGui.QMessageBox.question(self, u"Confirmation", u"Confirmez-vous vos choix ?", \
#            QtGui.QMessageBox.No | QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            confirmation = QtGui.QMessageBox.question(
                self, texts.DECISION_confirmation.titre,
                texts.DECISION_confirmation.message,
                QtGui.QMessageBox.No | QtGui.QMessageBox.Yes
            )
            if confirmation != QtGui.QMessageBox.Yes: 
                return
        self._defered.callback(decision)
        self.accept()
