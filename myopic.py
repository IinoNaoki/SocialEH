'''
Created on 15 Apr, 2015

@author: yzhang28
'''

from util import Util
import numpy as np
import random

# from parameters import Parameters

class BaseLineScheme(object):
    '''
    classdocs
    '''
    def __init__(self, paras, mode, transitions, reward, discount, epsilon=0.01, max_iter=1000):            
        self.policy = np.zeros(transitions[0].shape[0],int)
        self.V = np.zeros(transitions[0].shape[0])
        self.iter = 0
            
        self.A = transitions.shape[0]
        self.SET_A = [i for i in range(self.A)]
        self.S = transitions.shape[1]
        
        self.TransMat = transitions
        self.RewardMat = reward
        self.disc = discount
        
        self.SET_NOTHING = paras.SET_NOTHING
        self.SET_CHARGER = paras.SET_CHARGER
        self.SET_MESSENGER = paras.SET_MESSENGER
        self.CON_CSIZE = paras.CON_CSIZE
        self.CON_ESIZE = paras.CON_ESIZE
        self.CON_QSIZE = paras.CON_QSIZE
        self.CON_DIM = self.CON_CSIZE * self.CON_ESIZE * self.CON_QSIZE
        self.CON_inj_prob = paras.CON_inj_prob
        self.CON_DISCOUNT = paras.CON_DISCOUNT
        
        self.MODE = mode
        
        self.util = Util(paras)
        
        if self.disc < 1:
            self.epsi = epsilon * (1 - self.disc) / self.disc
        else: # discount == 1
            self.epsi = epsilon
        
        
    def _charge_and_send_actions(self):
        pol = np.zeros(self.S, int)
        for ic in range(self.CON_CSIZE):
            for ie in range(self.CON_ESIZE):
                for iq in range(self.CON_QSIZE):
                    ind = self.util.Trans_tuple_to_index([ic, ie, iq])
                    if (ic in self.SET_CHARGER) and (ie<self.CON_ESIZE-1):
                        pol[ind] = 1 # charge
                    elif (ic in self.SET_MESSENGER) and (iq>0) and (ie>0):
                        pol[ind] = 2 # sending content
        return pol
    
    def _random_actions(self):
        for ic in range(self.CON_CSIZE):
            for ie in range(self.CON_ESIZE):
                for iq in range(self.CON_QSIZE):
                    ind = self.util.Trans_tuple_to_index([ic, ie, iq])
                    if (ic in self.SET_CHARGER) and (ie<self.CON_ESIZE-1):
                        self.policy[ind] = random.choice([0,1]) # charge
                    elif (ic in self.SET_MESSENGER) and (iq>0) and (ie>0):
                        self.policy[ind] = random.choice([0,2]) # sending content
    
    def _greedy_actions(self):
        for ic in range(self.CON_CSIZE):
            for ie in range(self.CON_ESIZE):
                for iq in range(self.CON_QSIZE):
                    ind = self.util.Trans_tuple_to_index([ic, ie, iq])
                    rew = [0.0 for _ in range(len(self.SET_A))]
                    for act in self.SET_A:
                        rew[act] = self.RewardMat[ind][act]
                    max_a = np.argmax(rew)
                    if (ic in self.SET_CHARGER) and (rew[0]==rew[1]):
                        max_a = 1
                    if (ic in self.SET_MESSENGER) and (rew[0]==rew[2]):
                        max_a = 2
                    self.policy[ind] = max_a
                    
    
    def run(self):
        if self.MODE=="GREEDY":
            self._greedy_actions()
        elif self.MODE=="RANDOM":
            self._random_actions()
        elif self.MODE=="CAS":
            self.policy = self._charge_and_send_actions()
        else:
            print "ERROR IN myopic.BaseLineScheme.run()"
            exit(0)
        if self.MODE != 'RANDOM':
            while True:
                self.iter += 1
                Vprev = self.V.copy()
                for _s in range(self.S):
                    for _s1 in range(self.S):
                        _a = self.policy[_s]
                        self.V[_s] = self.RewardMat[_s][_a] + self.disc*self.TransMat[_a][_s][_s1]
                variation = np.fabs((self.V - Vprev).max())
                if variation < self.epsi:
                    break
        else:
            V_avg_for_rand_scheme = np.zeros(self.CON_DIM)
            _RND_COUNT = 10
            for _ in range(_RND_COUNT):
                while True:
                    self.iter += 1
                    Vprev = self.V.copy()
                    for _s in range(self.S):
                        for _s1 in range(self.S):
                            _a = self.policy[_s]
                            self.V[_s] = self.RewardMat[_s][_a] + self.disc*self.TransMat[_a][_s][_s1] 
                    variation = np.fabs((self.V - Vprev).max())
                    if variation < self.epsi: 
                        V_avg_for_rand_scheme += self.V
                        break
            V_avg_for_rand_scheme /= (1.0*_RND_COUNT)
            self.V = V_avg_for_rand_scheme
            
        self.policy = tuple(self.policy.tolist())
        self.V = tuple(self.V.tolist())
            