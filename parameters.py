'''
Created on 17 Apr, 2015

@author: yzhang28
'''

class Parameters(object):
    '''
    classdocs
    '''
    def __init__(self, s_nothing, s_charger, s_messenger, \
                 charging_price, sending_prob, sending_gain,\
                 csize, esize, qsize, \
                 inj_prob, charge_prob, \
                 discount, extra_para_lis=[]):
        
        self.SET_NOTHING = s_nothing
        self.SET_CHARGER = s_charger
        self.SET_MESSENGER = s_messenger
        self.LIST_CHARGING_PRICE = charging_price
        self.LIST_SENDING_PROB = sending_prob
        self.CON_SENDING_GAIN = sending_gain
        self.CON_CSIZE = csize
        self.CON_ESIZE = esize
        self.CON_QSIZE = qsize
        self.CON_DIM = self.CON_CSIZE * self.CON_ESIZE * self.CON_QSIZE
        self.CON_inj_prob = inj_prob
        self.CON_charge_prob = charge_prob
        self.CON_DISCOUNT = discount
        
        self.LIST_EXTRA_PARA = extra_para_lis