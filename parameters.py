'''
Created on 17 Apr, 2015

@author: yzhang28
'''

class Parameters(object):
    '''
    classdocs
    '''
    def __init__(self, s_nothing, s_charger, s_messenger, csize, esize, qsize, injprob, discount):
        
        self.SET_NOTHING = s_nothing
        self.SET_CHARGER = s_charger
        self.SET_MESSENGER = s_messenger
        self.CON_CSIZE = csize
        self.CON_ESIZE = esize
        self.CON_QSIZE = qsize
        self.CON_DIM = self.CON_CSIZE * self.CON_ESIZE * self.CON_QSIZE
        self.CON_inj_prob = injprob
        self.CON_DISCOUNT = discount