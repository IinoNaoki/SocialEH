'''
Created on 15 Apr, 2015

@author: yzhang28
'''

from util import Util
import numpy as np
import random
import time

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
        
        self.LIST_EXTRA_PARA = paras.LIST_EXTRA_PARA
        
        self.MODE = mode
        
        self.util = Util(paras)
        
        self.run_time = 0.0
        
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
        t_start = time.time()
        pol = np.zeros(self.S, int)
        for ic in range(self.CON_CSIZE):
            for ie in range(self.CON_ESIZE):
                for iq in range(self.CON_QSIZE):
                    ind = self.util.Trans_tuple_to_index([ic, ie, iq])
                    if (ic in self.SET_CHARGER) and (ie<self.CON_ESIZE-1):
                        pol[ind] = random.choice([0,1]) # charge
                    elif (ic in self.SET_MESSENGER) and (iq>0) and (ie>0):
                        pol[ind] = random.choice([0,2]) # sending content
        self.run_time = time.time()-t_start
        return pol
    
    def _threshold_random(self):
        
        if len(self.LIST_EXTRA_PARA)!=0:
            SLACK_STATE = self.LIST_EXTRA_PARA[0] #slack state
            CHOICE_SET = self.LIST_EXTRA_PARA[1] # choice set
        else:
            SLACK_STATE = 2
            CHOICE_SET = range(self.S)

        act_lis = self._charge_and_send_actions()
        _V = np.zeros(self.S)
        _V[:] = 100.0
        
        cp_CHOICE_SET = [i for i in CHOICE_SET]
        random.shuffle(cp_CHOICE_SET)
        
        t_start = time.time()
        while len(cp_CHOICE_SET)!=0:
            _ind = cp_CHOICE_SET.pop()

            c1,e1,q1 = self.util.Trans_index_to_tuple(_ind)
            
            if (c1 in self.SET_CHARGER) and (e1<self.CON_ESIZE-1):
                # with charger
                # 0 and 1
                _sum0, _sum1 = 0.0, 0.0
                c_low, c_high = max(c1-SLACK_STATE,0), min(c1+SLACK_STATE,self.CON_CSIZE-1)
                e_low, e_high = max(e1-1,0), min(e1+SLACK_STATE,self.CON_ESIZE-1) # non-symmetric, since e only decreases by 1 in this case
                q_low, q_high = max(q1-1,0), min(q1+SLACK_STATE,self.CON_QSIZE-1) # same as above
                for _sc in range(c_low, c_high+1):
                    for _se in range(e_low, e_high+1):
                        for _sq in range(q_low, q_high+1):
                            _ind1 = self.util.Trans_tuple_to_index([_sc,_se,_sq])
                            _sum0 += self.TransMat[0][_ind][_ind1] * _V[_ind1]
                            _sum1 += self.TransMat[1][_ind][_ind1] * _V[_ind1]
                    
                v0 = self.RewardMat[_ind][0] + self.CON_DISCOUNT * _sum0
                v1 = self.RewardMat[_ind][1] + self.CON_DISCOUNT * _sum1
                
                if v0 > v1:
                    _V[_ind] = v0
                    for cp in range(c1,self.CON_CSIZE-len(self.SET_MESSENGER)):
                        for ep in range(e1,self.CON_ESIZE):
                            if (act_lis[self.util.Trans_tuple_to_index([cp,ep,q1])]) == 1:
                                if random.uniform(0,1)>0.5:
                                    act_lis[self.util.Trans_tuple_to_index([cp,ep,q1])] = 0
                                else:
                                    act_lis[self.util.Trans_tuple_to_index([cp,ep,q1])] = 1
                else:
                    _V[_ind] = v1
                    for cm in range(1,c1):
                        for em in range(0,e1):
                            if act_lis[self.util.Trans_tuple_to_index([cm,em,q1])] == 0:
                                if random.uniform(0,1)>0.5:
                                    act_lis[self.util.Trans_tuple_to_index([cm,em,q1])] = 1
                                else:
                                    act_lis[self.util.Trans_tuple_to_index([cm,em,q1])] = 0
                
            elif (c1 in self.SET_MESSENGER) and (q1>0) and (e1>0):
                # with msger
                # 0 and 2
                _sum0, _sum2 = 0.0, 0.0
                c_low, c_high = max(c1-SLACK_STATE,0), min(c1+SLACK_STATE,self.CON_CSIZE-1)
                e_low, e_high = max(e1-1,0), min(e1+SLACK_STATE,self.CON_ESIZE-1) # non-symmetric, since e only decreases by 1 in this case
                q_low, q_high = max(q1-1,0), min(q1+SLACK_STATE,self.CON_QSIZE-1) # same as above
                for _sc in range(c_low, c_high+1):
                    for _se in range(e_low, e_high+1):
                        for _sq in range(q_low, q_high+1):
                            _ind1 = self.util.Trans_tuple_to_index([_sc,_se,_sq])
                            _sum0 += self.TransMat[0][_ind][_ind1] * _V[_ind1]
                            _sum2 += self.TransMat[2][_ind][_ind1] * _V[_ind1]
                v0 = self.RewardMat[_ind][0] + self.CON_DISCOUNT * _sum0
                v2 = self.RewardMat[_ind][2] + self.CON_DISCOUNT * _sum2
                if v0 > v2:
                    _V[_ind] = v0
                    for em in range(0,e1):
                        for qm in range(0,q1):
                            if act_lis[self.util.Trans_tuple_to_index([c1,em,qm])] == 1:
                                if random.uniform(0,1)>0.5:
                                    act_lis[self.util.Trans_tuple_to_index([c1,em,qm])] = 0
                                else:
                                    act_lis[self.util.Trans_tuple_to_index([c1,em,qm])] = 1
                else:
                    _V[_ind] = v2
                    for ep in range(e1,self.CON_ESIZE):
                        for qp in range(q1,self.CON_QSIZE):
                            if act_lis[self.util.Trans_tuple_to_index([c1,ep,qp])] ==0:
                                if random.uniform(0,1)>0.5:
                                    act_lis[self.util.Trans_tuple_to_index([c1,ep,qp])] = 2
                                else:
                                    act_lis[self.util.Trans_tuple_to_index([c1,ep,qp])] = 0
        
#         print act_lis
        self.run_time = time.time() - t_start
        return act_lis

    def _greedy_actions(self):
        pol = np.zeros(self.S, int)
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
                    pol[ind] = max_a
        return pol
                    
    
    def run(self):
        if self.MODE=="GREEDY":
            self.policy = self._greedy_actions()
        elif self.MODE=="CAS":
            self.policy = self._charge_and_send_actions()
        elif self.MODE=="RANDOM":
            pass # will generate policy later
        elif self.MODE=="THRESHOLDRANDOM":
            pass # will generate policy later
        else:
            print "ERROR IN myopic.BaseLineScheme.run()"
            exit(0)
        
        # random policies have to be tested for multiple times for average values
        if (self.MODE != 'RANDOM') and (self.MODE != "THRESHOLDRANDOM"):
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
        else: # random policies have to be tested for multiple times for average values
            V_avg_for_rand_scheme = np.zeros(self.CON_DIM)
            A_avg_for_rand_scheme = np.zeros(self.CON_DIM)
            _RND_COUNT = 5
#             print "Please change the _RND_COUNT back to 5 later"
            for _ in range(_RND_COUNT):
                # generating random policies
                if self.MODE=='RANDOM':
                    self.policy = self._random_actions()
                elif self.MODE=='THRESHOLDRANDOM':
                    self.policy = self._threshold_random()
                else:
                    print "error in run() in myopic.py"
                    exit()
                A_avg_for_rand_scheme += self.policy
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
            A_avg_for_rand_scheme /= (1.0*_RND_COUNT)
            self.V = V_avg_for_rand_scheme
            self.policy
            
        self.policy = tuple(self.policy.tolist())
        self.V = tuple(self.V.tolist())
            