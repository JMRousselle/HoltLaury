# -*- coding: utf-8 -*-

import logging
from datetime import datetime
from collections import OrderedDict
from twisted.internet import defer
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, Float, ForeignKey, String

from server.servbase import Base
from server.servparties import Partie
from util.utili18n import le2mtrans
from util.utiltools import get_module_attributes
import HoltLauryParams as pms
import HoltLauryTexts as texts


logger = logging.getLogger("le2m")


class PartieHL(Partie):
    __tablename__ = "partie_HoltLaury"
    __mapper_args__ = {'polymorphic_identity': 'HoltLaury'}
    partie_id = Column(Integer, ForeignKey('parties.id'), primary_key=True)
    repetitions = relationship('RepetitionsHL')

    def __init__(self, le2mserv, joueur):
        super(PartieHL, self).__init__("HoltLaury", "HL")
        self._le2mserv = le2mserv
        self.joueur = joueur
        self._texte_recapitulatif = u""
        self._texte_final = u""
        self.HL_gain_ecus = 0
        self.HL_gain_euros = 0
#        self._histo_build = OrderedDict()
#        self._histo_build[le2mtrans(u"Period")] = "HL_period"
#        self._histo_build[le2mtrans(u"Decision")] = "HL_decision"
#        self._histo_build[le2mtrans(u"Period\npayoff")] = "HL_periodpayoff"
#        self._histo_build[le2mtrans(u"Cumulative\npayoff")] = "HL_cumulativepayoff"
#        self._histo_content = [list(self._histo_build.viewkeys())]
        self.periods = {}
        self._currentperiod = None

    @property
    def currentperiod(self):
        return self._currentperiod

    @defer.inlineCallbacks
    def configure(self):
        logger.debug(u"{} Configure".format(self.joueur))
        yield (self.remote.callRemote("configure", get_module_attributes(pms)))
        self.joueur.info(u"Ok")

    @defer.inlineCallbacks
    def newperiod(self, period):
        """
        Create a new period and inform the remote
        If this is the first period then empty the historic
        :param periode:
        :return:
        """
        logger.debug(u"{} New Period".format(self.joueur))
        if period == 1:
            del self._histo_content[1:]
        self._currentperiod = RepetitionsHL(period)
        self._le2mserv.gestionnaire_base.ajouter(self.currentperiod)
        self.repetitions.append(self.currentperiod)
        yield (self.remote.callRemote("newperiod", period))
        logger.info(u"{} Ready for period {}".format(self.joueur, period))

    @defer.inlineCallbacks
    def display_decision(self):
        """
        Display the decision screen on the remote
        Get back the decision
        :return:
        """
        logger.debug(u"{} Decision".format(self.joueur))
        debut = datetime.now()
        les_decisions = yield(self.remote.callRemote("display_decision"))
        self.currentperiod.HL_decisiontime = (datetime.now() - debut).seconds
        for k,  v in les_decisions.iteritems():
            if "HL_question" in k: setattr(self.currentperiod,  k,  v)
        decisions = [getattr(self.currentperiod, 'HL_question_{}'.format(i)) for i in range(1,  12)]            
        self.joueur.info(u"{}".format(les_decisions.values()))
        self.joueur.remove_waitmode()

    def compute_periodpayoff(self):
        """
        Compute the payoff for the period
        :return:
        """
        logger.debug(u"{} Period Payoff".format(self.joueur))
        self.currentperiod.HL_periodpayoff = 0

        # cumulative payoff since the first period
        if self.currentperiod.HL_period < 2:
            self.currentperiod.HL_cumulativepayoff = \
                self.currentperiod.HL_periodpayoff
        else: 
            previousperiod = self.periods[self.currentperiod.HL_period - 1]
            self.currentperiod.HL_cumulativepayoff = \
                previousperiod.HL_cumulativepayoff + \
                self.currentperiod.HL_periodpayoff

        # we store the period in the self.periodes dictionnary
        self.periods[self.currentperiod.HL_period] = self.currentperiod

        logger.debug(u"{} Period Payoff {}".format(
            self.joueur,
            self.currentperiod.HL_periodpayoff))

#    @defer.inlineCallbacks
#    def display_summary(self, *args):
#        """
#        Create the summary (txt and historic) and then display it on the
#        remote
#        :param args:
#        :return:
#        """
#        logger.debug(u"{} Summary".format(self.joueur))
#        self._texte_recapitulatif = texts.get_recapitulatif(self.currentperiod)
#        self._histo_content.append(
#            [getattr(self.currentperiod, e) for e
#             in self._histo_build.viewvalues()])
#        yield(self.remote.callRemote(
#            "display_summary", self._texte_recapitulatif, self._histo_content))
#        self.joueur.info("Ok")
#        self.joueur.remove_waitmode()
    
    def compute_partpayoff(self):
        """
        Compute the payoff of the part
        :return:
        """
        logger.debug(u"{} Part Payoff".format(self.joueur))
        # gain partie
        self.HL_gain_ecus = self.currentperiod.HL_cumulativepayoff
        self.HL_gain_euros = \
            float(self.HL_gain_ecus) * float(pms.TAUX_CONVERSION)

        # texte final
        self._texte_final = texts.get_texte_final(
            self.HL_gain_ecus,
            self.HL_gain_euros)

        logger.debug(u"{} Final text {}".format(self.joueur, self._texte_final))
        logger.info(u'{} Payoff ecus {} Payoff euros {:.2f}'.format(
            self.joueur, self.HL_gain_ecus, self.HL_gain_euros))


class RepetitionsHL(Base):
    __tablename__ = 'partie_HoltLaury_repetitions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    partie_partie_id = Column(
        Integer,
        ForeignKey("partie_HoltLaury.partie_id"))

    HL_period = Column(Integer)
    HL_treatment = Column(Integer)
    HL_group = Column(Integer)
    HL_decision = Column(Integer)
    HL_decisiontime = Column(Integer)
    HL_periodpayoff = Column(Float)
    HL_cumulativepayoff = Column(Float)
    
    HL_question_1 = Column(Integer)
    HL_question_2 = Column(Integer)
    HL_question_3 = Column(Integer)
    HL_question_4 = Column(Integer)
    HL_question_5 = Column(Integer)
    HL_question_6 = Column(Integer)
    HL_question_7 = Column(Integer)
    HL_question_8 = Column(Integer)
    HL_question_9 = Column(Integer)
    HL_question_10 = Column(Integer)
    HL_question_11 = Column(Integer)
    HL_question_tiree = Column(Integer)
    HL_tirage = Column(Integer)    

    def __init__(self, period):
        self.HL_treatment = pms.TREATMENT
        self.HL_period = period
        self.HL_decisiontime = 0
        self.HL_periodpayoff = 0
        self.HL_cumulativepayoff = 0

    def todict(self, joueur):
        temp = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        temp["joueur"] = joueur
        return temp

