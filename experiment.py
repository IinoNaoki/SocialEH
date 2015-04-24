'''
Created on Mar 15, 2015

@author: yang
'''


import mdptoolbox
import numpy as np
from scipy.sparse import csr_matrix as sparse
from util import Util
import myopic
import random
# from parameters import Parameters


class Experiment(object):
    
    def __init__(self, para):
        self.PARAS = para
        
        self.SET_NOTHING = para.SET_NOTHING
        self.SET_CHARGER = para.SET_CHARGER
        self.SET_MESSENGER = para.SET_MESSENGER
        self.LIST_CHARGING_PRICE = para.LIST_CHARGING_PRICE
        self.LIST_SENDING_PROB = para.LIST_SENDING_PROB
        self.CON_SENDING_GAIN = para.CON_SENDING_GAIN
        self.CON_CSIZE = para.CON_CSIZE
        self.CON_ESIZE = para.CON_ESIZE
        self.CON_QSIZE = para.CON_QSIZE
        self.CON_DIM = self.CON_CSIZE * self.CON_ESIZE * self.CON_QSIZE
        self.CON_inj_prob = para.CON_inj_prob
        self.CON_charge_prob = para.CON_charge_prob
        self.CON_DISCOUNT = para.CON_DISCOUNT
        
        self.A_IDLE = 0 # 0: idle
        self.A_GETE = 1 # 1: get energy
        self.A_Q = 2 # 2: send Q
        self.SET_A = [self.A_IDLE, self.A_GETE, self.A_Q]
        
        self.util = Util(para)
    
    def Get_C_mat(self, act):
        # matrix for contacts
        C_mat = np.zeros((self.CON_CSIZE, self.CON_CSIZE))
        C_mat[:] = 1.0/self.CON_CSIZE
        return C_mat
    
    
    def Get_E_mat(self, act):
        def E_plus_mat(chg=1):
            _e_plus = np.zeros((self.CON_ESIZE, self.CON_ESIZE))
            for i in range(self.CON_ESIZE-1):
                _e_plus[i][i+1] = self.CON_charge_prob
                _e_plus[i][i] = 1.0 - self.CON_charge_prob
            _e_plus[self.CON_ESIZE-1][self.CON_ESIZE-1] = 1.0
            return _e_plus
        
        def E_zero_mat():
            return np.identity(self.CON_ESIZE, float)
        
        def E_minus_mat(dischg=1):
            _e_minus = np.zeros((self.CON_ESIZE,self.CON_ESIZE))
            for j in range(1,self.CON_ESIZE):
                _e_minus[j][j-1] = 1.0
            _e_minus[0][0] = 1.0
            return _e_minus
    
        if act == self.A_IDLE:
            return E_zero_mat()
        elif act == self.A_GETE:
            return E_plus_mat()
        elif act == self.A_Q:
            return E_minus_mat()
        
    
    def Get_Q_mat(self, act, inj_prob):
        def Q_plus_mat(getQ=1, inj=inj_prob):
            _q_plus = np.zeros((self.CON_QSIZE,self.CON_QSIZE))
            for i in range(self.CON_QSIZE-1):
                _q_plus[i][i+1] = inj
                _q_plus[i][i] = 1.0 - inj
            _q_plus[self.CON_QSIZE-1][self.CON_QSIZE-1] = 1.0
            return _q_plus
            
        def Q_minus_mat(sendQ=1):
            _q_minus = np.zeros((self.CON_QSIZE,self.CON_QSIZE))
            for j in range(1,self.CON_QSIZE):
                _q_minus[j][j-1] = 1.0
            _q_minus[0][0] = 1.0
            return _q_minus
    
        if act == self.A_IDLE:
            return Q_plus_mat()
        elif act == self.A_GETE:
            return Q_plus_mat()
        elif act == self.A_Q:
            ret = Q_minus_mat().dot(Q_plus_mat())
    #         ret[0][0] = 1.0
    #         ret[0][1] = 0.0
            return ret
    
    
    def Get_Overall_mat(self,act):
        _cmat = self.Get_C_mat(act)
        _emat = self.Get_E_mat(act)
        _qmat = self.Get_Q_mat(act, self.CON_inj_prob)
        overall_kron = np.kron(np.kron(_cmat, _emat), _qmat)
        return overall_kron
    
    
    def ElecPriceCost(self, _c):
        if _c<0 or _c>=self.CON_CSIZE:
            print "error in EPrice()"
            exit()
        
        if _c in self.SET_CHARGER:
            return self.LIST_CHARGING_PRICE[self.SET_CHARGER.index(_c)]
    #         return -np.power(_c, 0.5)*0.2
    #         return 0.0
        else:
            return -6553600000000000000000000000000.0
    
    def MessengerDeliveryProb(self, _c):
        if _c in self.SET_MESSENGER:
    #         _prob = np.power( (CON_CSIZE-1.0-_c)/(len(SET_MESSENGER)-1.0) , 0.8)
            _prob = self.LIST_SENDING_PROB[self.SET_MESSENGER.index(_c)]
    #         _prob = 0.5
            return _prob
        else:
            return 0.0
    
    def QDelayCost(self, _q):
    #     return -1.0*_q
        return -0.0
    
    
    
    def Reward(self, _c, _e, _q, action):    
        if action == self.A_IDLE:
            return self.QDelayCost(_q)
        elif action == self.A_GETE:
            return self.ElecPriceCost(_c) + self.QDelayCost(_q)
        elif action == self.A_Q:
            if _e>0 and _q>0 and (_c in self.SET_MESSENGER):
                return self.CON_SENDING_GAIN * self.MessengerDeliveryProb(_c) + self.QDelayCost(_q)
            else:
                return  -6553600000000000000000000000000.0 + self.QDelayCost(_q)
        else:
            print "error in Reward()"
            exit()
    
    
    def FormRewardFunc(self):
        '''
        Get the required form of reward matrix
        '''
        R = np.zeros((self.CON_DIM,len(self.SET_A)))
        # cnt = 0
        for ic in range(self.CON_CSIZE):
            for ie in range(self.CON_ESIZE):
                for iq in range(self.CON_QSIZE):
                    ind = self.util.Trans_tuple_to_index([ic, ie, iq])
                    for action in self.SET_A:
                        R[ind][action] = self.Reward(ic,ie,iq, action)
        return R

    def Build_Problem(self, mode):
        R = self.FormRewardFunc()
        P = np.array([ self.Get_Overall_mat(j) for j in self.SET_A])
        if mode=="MDP":
            vi = mdptoolbox.mdp.ValueIteration(P, R, self.CON_DISCOUNT)
        else:
            vi = myopic.BaseLineScheme(self.PARAS, mode, P, R, self.CON_DISCOUNT)
        return R, P, vi
        